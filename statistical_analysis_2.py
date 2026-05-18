import os, warnings, csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import kruskal, mannwhitneyu
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import re


class Statistical_Analysis:
    def __init__(self, experiment, filter_time=8.0):
        self.experiment = experiment
        self.sex_list = ['male', 'female']
        self.data_type_list = ['position', 'velocity', 'low performer', 'middle performer', 'high performer']
        self.base_path = f'./{self.experiment}/'
        self.filter_time = filter_time
        warnings.filterwarnings('ignore', category=ConvergenceWarning)
        warnings.filterwarnings('ignore', category=UserWarning)
        # We will set self.stats_folder_name later in input_comps(), once we know sex and control genotype.

    def run_analysis(self):
        successful_sexs = 0
        
        for sex in self.sex_list:
            try:
                print(f"\nProcessing {sex} data from 0s to {int(self.filter_time)}s...\n")
                self.sex = sex
                # pick the correct output folder for this sex
                self.sex_folder = '_Output_Males' if self.sex == 'male' else '_Output_Females'
                self.sex_prefix = self.sex

                for data_type in self.data_type_list:
                    self.data_type = data_type
                    self.load_data()
                    self.prepare_data()
                    if data_type == 'position':
                        # ask for control + comparisons, and determine unique stats folder
                        self.input_comps()
                    else:
                        self.skip_stats = False  # Default to False for non-'position' data

                    self.select_genotypes()
                    if not self.skip_stats:
                        self.perform_mixedlm_analysis()
                    else:
                        self.combined_results = {}
                    self.plot_results()
                    if not self.skip_stats:
                        self.mannwhitney_analysis()

                successful_sexs += 1

            except Exception as e:
                print(f"Error processing {sex}: {e}")
                continue

        if successful_sexs == 0:
            raise ValueError("All male and female data missing. Cannot continue.")

    def load_data(self):
        file_map = {
            'position': f'{self.sex_prefix}_stats_pos_data.csv',
            'velocity': f'{self.sex_prefix}_stats_vel_data.csv',
            'low performer': f'{self.sex_prefix}_stats_lp_perc_data.csv',
            'middle performer': f'{self.sex_prefix}_stats_mp_perc_data.csv',
            'high performer': f'{self.sex_prefix}_stats_hp_perc_data.csv'
        }
        file_path = f'{self.base_path}{self.sex_folder}/{file_map[self.data_type]}'
        self.df = pd.read_csv(file_path)
        # drop any weird unnamed columns
        self.df = self.df.loc[:, ~self.df.columns.str.startswith('Unnamed: 0.1')]

    def prepare_data(self):
        start_range = 1
        end_range = len(self.df.columns)
        newdf = self.df.iloc[:, [0] + list(range(start_range, end_range))].copy()
        if 'Unnamed: 0' in newdf.columns:
            newdf[['Genotype', 'Replicate']] = newdf['Unnamed: 0'].str.split('_rep', expand=True)
        else:
            raise KeyError("'Unnamed: 0' column is missing in newdf.")
        self.df_long = newdf.melt(
            id_vars=['Genotype', 'Replicate'],
            value_vars=newdf.columns[1:],
            var_name='Time',
            value_name='Position'
        )
        self.df_long['Time'] = self.df_long['Time'].astype(float)
        self.df_long['Subject'] = self.df_long['Genotype'] + '_' + self.df_long['Replicate']

    def input_comps(self):
        print(f"dataframe unique genotypes: \n{list(self.df_long['Genotype'].unique())}\n")
        self.control_genotype = input(
            f"Input control genotype for {self.sex} {self.data_type}: "
        ).strip().strip("'").strip('"')

        comparison_genotype_input = input(
            f"Input comparison genotypes (comma-separated) for {self.sex} {self.data_type}: "
        ).strip()

        # If no input is given, only control is used
        if comparison_genotype_input == "":
            print(f"No comparison genotypes provided for {self.sex} {self.data_type}. Skipping statistical analysis.")
            self.comparison_genotypes = []
            self.skip_stats = True
        else:
            parsed = next(csv.reader([comparison_genotype_input], skipinitialspace=True))
            self.comparison_genotypes = [
                geno.strip().strip("'").strip('"') for geno in parsed
            ]
            self.skip_stats = False

        # Clean up any commas in genotype names
        all_genos = [self.control_genotype] + self.comparison_genotypes
        clean_map = {geno: geno.replace(',', '_') for geno in all_genos}
        self.df_long['Genotype'] = self.df_long['Genotype'].replace(clean_map)
        self.control_genotype = clean_map[self.control_genotype]
        self.comparison_genotypes = [clean_map[g] for g in self.comparison_genotypes]

        # --- determine a unique folder name for this set of stats ---
        parent_dir = os.path.join(self.base_path, self.sex_folder)
        base_folder = f"{self.sex}_stats_control_{self.control_genotype}"
        existing = [
            d for d in os.listdir(parent_dir)
            if os.path.isdir(os.path.join(parent_dir, d)) and d.startswith(base_folder)
        ]
        highest_suffix = 0
        pattern = re.compile(rf"^{re.escape(base_folder)}_(\d+)$")
        for d in existing:
            m = pattern.match(d)
            if m:
                num = int(m.group(1))
                if num > highest_suffix:
                    highest_suffix = num
        next_suffix = highest_suffix + 1
        self.stats_folder_name = f"{base_folder}_{next_suffix}"

    def select_genotypes(self):
        self.comb_genos = [self.control_genotype] + self.comparison_genotypes
        self.test_df = self.df_long[self.df_long['Genotype'].isin(self.comb_genos)].copy()
        self.original_df = self.test_df.copy()
        self.test_df = self.test_df.dropna(subset=["Position"]).reset_index(drop=True)
        self.test_df['Time_cat'] = self.test_df['Time'].astype(str)
        self.test_df = self.test_df[self.test_df['Time'] <= self.filter_time].reset_index(drop=True)
        self.replicate_counts = self.test_df.groupby('Genotype')['Replicate'].nunique().to_dict()

    def significance_stars(self, p):
        if p < 0.001:
            return "***"
        elif p < 0.01:
            return "**"
        elif p < 0.05:
            return "*"
        else:
            return "NS"

    def perform_mixedlm_analysis(self):
        model_rs = smf.mixedlm(
            f"Position ~ C(Genotype, Treatment(reference='{self.control_genotype}')) * Time_cat",
            self.test_df,
            groups=self.test_df["Subject"],
            re_formula="~Time"
        )
        if self.sex == 'male' and self.data_type == 'position':
            self.model_exog_names = model_rs.exog_names

        self.result = model_rs.fit(reml=True)
        self.pvalues_df = pd.DataFrame({
            "Term": self.result.pvalues.index,
            "P-Value": self.result.pvalues.values,
            "Significance": [self.significance_stars(p) for p in self.result.pvalues.values]
        })
        self.pvalues_df["P-Value"] = self.pvalues_df["P-Value"].apply(lambda x: f"{x:.6f}")

        def combine_pvalues_hmp(pvals):
            m = len(pvals)
            eps = np.finfo(float).tiny
            p_val = np.clip(pvals, eps, 1.0)
            hmp = m / np.sum(1.0 / p_val)
            return min(hmp, 1.0)

        self.combined_results = {}
        self.geno_terms = {}
        for geno in self.comparison_genotypes:
            main_term = f"C(Genotype, Treatment(reference='{self.control_genotype}'))[T.{geno}]"
            interaction_prefix = f"C(Genotype, Treatment(reference='{self.control_genotype}'))[T.{geno}]:Time_cat"
            interaction_terms = [term for term in self.result.pvalues.index if term.startswith(interaction_prefix)]
            terms = [main_term] + interaction_terms
            pvals = self.result.pvalues[terms].values
            self.geno_terms[geno] = pvals

        for geno, pvals in self.geno_terms.items():
            HMP_p = combine_pvalues_hmp(pvals)
            HMP_sig_p = self.significance_stars(HMP_p)
            print(f"{self.control_genotype} vs {geno} for {self.data_type}: {HMP_p}, {HMP_sig_p}")
            self.combined_results[geno] = {"Harm_Mean": HMP_p, "Harm_Mean_Sig": HMP_sig_p}

    # ------------------------------------------------------------------
    # Helper: axis-label unit strings
    # ------------------------------------------------------------------
    def _ylabel_for_datatype(self):
        if self.data_type == 'velocity':
            return 'Climbing Velocity (cm/s)'
        elif self.data_type == 'position':
            return 'Climbing Position (cm)'
        else:
            return f'Climbing {self.data_type.capitalize()} (%)'

    # ------------------------------------------------------------------
    # Main line-plot (LME trends)
    # ------------------------------------------------------------------
    def plot_results(self):
        using_list = [self.control_genotype] + self.comparison_genotypes
        legend_labels = {
            self.control_genotype: f"{self.control_genotype} (N={self.replicate_counts[self.control_genotype]})"
        }
        for comparison, pval_type in self.combined_results.items():
            star_sig_value = pval_type['Harm_Mean_Sig']
            p_value = "{:.6f}".format(pval_type['Harm_Mean'])
            legend_labels[comparison] = (
                f"{comparison} (N={self.replicate_counts[comparison]}): (p: {p_value}) {star_sig_value}"
            )

        df_filtered = self.original_df[self.original_df['Genotype'].isin(using_list)]
        color_palette = sns.color_palette(n_colors=len(using_list))

        fig, ax = plt.subplots()
        sns.lineplot(
            data=df_filtered,
            x="Time",
            y="Position",
            hue="Genotype",
            marker='o',
            err_style='band',
            errorbar='se',
            palette=color_palette,
            ax=ax
        )

        handles, labels = ax.get_legend_handles_labels()
        new_labels = [legend_labels[label] if label in legend_labels else label for label in labels]

        # ── Legend INSIDE the plot (upper-left, slightly inset) ──
        ax.legend(
            handles, new_labels,
            title="Genotype",
            loc='upper left',
            framealpha=0.85,
            edgecolor='grey'
        )

        if self.data_type == 'velocity':
            ax.axhline(y=0, color='red', linestyle='--')

        ax.set_ylabel(self._ylabel_for_datatype())
        ax.set_xlabel('Time (s)')
        ax.axvline(x=0, color='black', linestyle='--')
        ax.axvline(x=self.filter_time, color='black', linestyle='--')
        ax.set_title(
            f"{self.data_type.capitalize()} Trends Over Time "
            f"With Control {self.control_genotype} for {self.sex.capitalize()}"
        )
        ax.grid(axis='y')

        output_folder = os.path.join(self.base_path, self.sex_folder, self.stats_folder_name)
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, f'{self.sex}_stats_plot_{self.data_type}.png')
        fig.savefig(save_path, bbox_inches='tight')
        plt.close(fig)

        # ── Peak Position bar plot (position data only) ──
        if self.data_type == 'position':
            self.plot_peak_position(df_filtered, using_list, color_palette, output_folder)

    # ------------------------------------------------------------------
    # NEW: Mean ± SEM Peak Position bar chart
    # ------------------------------------------------------------------
    def plot_peak_position(self, df_filtered, using_list, color_palette, output_folder):
        """
        For each biological replicate (vial / Subject) compute its peak climbing
        position (max Position across time), then plot a grouped bar chart with
        Mean ± SEM per genotype and individual replicate points overlaid.
        """
        # -- compute per-vial peak --
        peak_df = (
            df_filtered
            .dropna(subset=['Position'])
            .groupby(['Genotype', 'Subject'])['Position']
            .max()
            .reset_index()
            .rename(columns={'Position': 'Peak_Position'})
        )

        # -- summary stats --
        summary = (
            peak_df
            .groupby('Genotype')['Peak_Position']
            .agg(Mean='mean', SEM=lambda x: x.sem())
            .reindex(using_list)          # preserve control-first order
            .reset_index()
        )

        # -- significance annotation between each comparison and control --
        sig_map = {}
        for geno, res in self.combined_results.items():
            sig_map[geno] = res['Harm_Mean_Sig']

        # -- plot --
        fig, ax = plt.subplots(figsize=(max(4, 2 * len(using_list)), 5))
        x_positions = np.arange(len(using_list))

        for i, (_, row) in enumerate(summary.iterrows()):
            geno = row['Genotype']
            color = color_palette[i]
            ax.bar(
                x_positions[i],
                row['Mean'],
                yerr=row['SEM'],
                color=color,
                width=0.55,
                alpha=0.65,
                error_kw=dict(elinewidth=1.5, capsize=5, ecolor='black'),
                zorder=2
            )
            # overlay individual vial points
            vial_peaks = peak_df.loc[peak_df['Genotype'] == geno, 'Peak_Position'].values
            jitter = np.random.uniform(-0.08, 0.08, size=len(vial_peaks))
            ax.scatter(
                x_positions[i] + jitter,
                vial_peaks,
                color='dimgrey',
                s=40,
                zorder=3,
                alpha=0.75,
                linewidths=0.5,
                edgecolors='black'
            )

        # -- significance brackets vs control --
        ctrl_idx = 0
        y_top = peak_df['Peak_Position'].max()
        bracket_step = (y_top * 0.12)
        for j, geno in enumerate(self.comparison_genotypes):
            if geno not in sig_map:
                continue
            sig = sig_map[geno]
            comp_idx = using_list.index(geno)
            y_line = y_top + bracket_step * (j + 1)
            x0, x1 = x_positions[ctrl_idx], x_positions[comp_idx]
            ax.plot([x0, x0, x1, x1], [y_line - bracket_step * 0.3,
                                         y_line, y_line,
                                         y_line - bracket_step * 0.3],
                    lw=1.2, color='black')
            p_val = self.combined_results[geno]['Harm_Mean']
            ax.text(
                (x0 + x1) / 2,
                y_line + bracket_step * 0.05,
                f"p={p_val:.3f} ({sig})",
                ha='center', va='bottom',
                fontsize=9, color='crimson', fontweight='bold'
            )

        ax.set_xticks(x_positions)
        ax.set_xticklabels(
            [f"{g}\n(N={self.replicate_counts.get(g, '?')})" for g in using_list],
            fontsize=10
        )
        ax.set_ylabel('Peak Position Value (cm)', fontsize=11)
        ax.set_xlabel('Genotype', fontsize=11)
        ax.set_title(
            f'Mean \u00b1 SEM Peak Position\n'
            f'{self.sex.capitalize()} — Control: {self.control_genotype}',
            fontsize=12
        )
        ax.grid(axis='y', alpha=0.4)
        ax.set_ylim(bottom=0)

        save_path = os.path.join(output_folder, f'{self.sex}_peak_position_barplot.png')
        fig.savefig(save_path, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved peak position bar plot → {save_path}")

    # ------------------------------------------------------------------
    # Mann-Whitney time-point tests
    # ------------------------------------------------------------------
    def mannwhitney_analysis(self):
        time_col = 'Time'
        genotype_col = 'Genotype'
        value_col = 'Position'
        times = sorted(self.test_df[time_col].unique())
        result = pd.DataFrame(index=times, columns=self.comparison_genotypes, dtype=object)
        df_ctrl = self.test_df[self.test_df[genotype_col] == self.control_genotype]

        for t in times:
            vals_ctrl = df_ctrl.loc[df_ctrl[time_col] == t, value_col].dropna().values
            for comp in self.comparison_genotypes:
                df_comp = self.test_df[self.test_df[genotype_col] == comp]
                vals_comp = df_comp.loc[df_comp[time_col] == t, value_col].dropna().values
                if len(vals_ctrl) < 2 or len(vals_comp) < 2:
                    p = np.nan
                else:
                    try:
                        _, p = mannwhitneyu(vals_ctrl, vals_comp, alternative='two-sided', method='auto')
                    except ValueError:
                        p = 1.0
                if np.isnan(p):
                    entry = np.nan
                else:
                    entry = [f"{p:.4f}", self.significance_stars(p)]
                result.at[t, comp] = entry

        result.index.name = time_col
        output_folder = os.path.join(self.base_path, self.sex_folder, self.stats_folder_name)
        os.makedirs(output_folder, exist_ok=True)

        save_path_csv = os.path.join(
            output_folder,
            f'{self.sex}_stats_mannwhitney_{self.data_type}_control_{self.control_genotype}.csv'
        )
        result.to_csv(save_path_csv)