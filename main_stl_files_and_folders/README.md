# 3D-Printed Geotaxis Assay Device — STL File README

All STL files required to reproduce the device described in the associated manuscript are organized into the subfolders listed below. Print settings for each component are provided in the [Print Settings](#print-settings) section. Non-printed hardware requirements are listed in the [Bill of Materials](#bill-of-materials) section.

---

## Table of Contents

1. [Device Overview](#device-overview)
2. [How the Mechanism Works](#how-the-mechanism-works)
3. [File Structure](#file-structure)
4. [STL Files by Assembly](#stl-files-by-assembly)
   - [1. Curved Vial Holder](#1-curved-vial-holder)
   - [2. Arm / Middle Attachment](#2-arm--middle-attachment)
   - [3. Connecting Rod (Coupler)](#3-connecting-rod-coupler)
   - [4. Crank (Input Link)](#4-crank-input-link)
   - [5. Motor / Drive](#5-motor--drive)
   - [6. Base Frame](#6-base-frame)
   - [7. Cable Management Box](#7-cable-management-box)
5. [Assembly Order](#assembly-order)
6. [Print Settings](#print-settings)
7. [Bill of Materials](#bill-of-materials)

---

## Device Overview

This device automates the *Drosophila* geotaxis assay. It holds a set of fly vials in a curved arm, mechanically taps them to the bottom, and allows the flies to climb upward against gravity. A motorized crank-rocker mechanism converts continuous motor rotation into a repeating lift-and-tap oscillation of the vial arm at a consistent, user-controlled frequency.

The full mechanical system is 3D printed with the exception of two steel guide rods, bearings, screws, and the electric motor/gearbox unit.

---

## How the Mechanism Works

The device is a **crank-rocker four-bar linkage**. The key components and their roles are:

- **Base Frame** — The rigid black structure sitting on the bench, including two horizontal parallel steel rods. These rods connect the motor assembly to the pivot stand, keeping everything in alignment.
- **Motor & Gearbox** — An electric motor drives a printed gear pair to reduce rotational speed and increase torque.
- **Crank (Input Link)** — Attached directly to the gearbox output shaft. Rotates continuously in a full 360° circle.
- **Connecting Rod (Coupler)** — Links the crank's outer pin to the underside of the lever arm. An adjustable metal sleeve on this piece allows fine-tuning of the stroke length and resting height.
- **Lever Arm (Rocker)** — The long articulated arm spanning the top of the device. Pushed upward from below by the connecting rod and pinned at its right end to the fulcrum.
- **Pivot / Fulcrum** — The A-frame structure at the right end of the device. Houses a bearing and pin that act as the stationary hinge for the lever arm.
- **Vial Holder (End Effector)** — The curved vial holder at the left end of the lever arm. Swings upward when the crank pushes the arm, then drops back down to tap the flies to the bottom of the vials.

**Sequence of motion:**

1. The motor turns on, driving the gearbox and forcing the crank to rotate.
2. The crank's outer pin moves in a circle; the connecting rod transmits this motion upward.
3. The connecting rod pushes up on the mid-point of the lever arm.
4. Because the right end of the lever arm is fixed to the pivot point, the left end (carrying the vial holder) swings upward in an arc.
5. As the crank continues past the top of its rotation, it pulls the connecting rod down, which pulls the lever arm and vial holder back to the starting position — tapping the flies to the bottom.
6. This cycle repeats continuously at a frequency set by the motor speed.

---

## File Structure

```
main_files_and_folders_so_far/
├── curved_vial_holder/
│   ├── Curved_Vialholder.stl
│   ├── Curved_TopCover.stl
│   └── Gept_Arm_Backplate.stl
├── middle_parts_attach_holder/
│   ├── ArmSleve.stl
│   ├── CentrPS.stl
│   ├── ARM_B_end_d2.stl
│   ├── ArmInsert2.stl
│   └── GeoT_Fulcram.stl
├── connecting_rod/
│   ├── Bearing_Rod_PistonAdapter.stl
│   ├── Bearing_Rod_Piston_Cyl.stl
│   └── Bearing_Rod_Adapter.stl
├── crank_input_link/
│   ├── cranckside_D5.stl
│   ├── GeoT_Crank_Mount_final.stl
│   ├── GeoT_Crank_Mount_motorEnd_Final.stl
│   └── ND_CrankStand.stl
├── motor_drive/
│   ├── Big_Motor_Faceplate.stl
│   ├── Motor_Brace.stl
│   └── GeoT_gear_crank.stl
├── base_frame/
│   └── GeoT_Base_motor_D2.stl
└── cable_management_box/
    ├── drivermount.stl
    └── drivermount_top.stl
```

---

## STL Files by Assembly

### 1. Curved Vial Holder
**Subfolder:** `curved_vial_holder/`

This is the end effector — the outermost component of the device. It holds the fly vials and is the part that swings upward and taps downward during the assay.

| File | Description |
|---|---|
| `Curved_Vialholder.stl` | Main curved arm with 12 vial slots arranged in a fan. **Print with supports.** |
| `Curved_TopCover.stl` | Cover that clips over the 12 vial openings to prevent vials from jumping out when the arm drops. |
| `Gept_Arm_Backplate.stl` | Backplate that bridges the vial holder to the arm sleeve (`ArmSleve.stl`). Acts as the structural interface between the holder and the rest of the lever arm. |

---

### 2. Arm / Middle Attachment
**Subfolder:** `middle_parts_attach_holder/`

These parts form the lever arm — the long articulated arm that spans the top of the device. It is pinned at the right end (at the fulcrum) and free to swing at the left end where the vial holder attaches.

| File | Description |
|---|---|
| `ArmSleve.stl` | Sleeve that fits over the lever arm body. Connects to `Gept_Arm_Backplate.stl` at one end and `CentrPS.stl` at the other. |
| `CentrPS.stl` | Central connector piece. Interfaces between the arm sleeve, the lever arm body, and the crank-rocker mechanism below. |
| `ARM_B_end_d2.stl` | The body-end of the lever arm that connects to the fulcrum (`GeoT_Fulcram.stl`). |
| `ArmInsert2.stl` | Internal insert that provides stiffness and bearing surfaces at the pivot end of the arm. |
| `GeoT_Fulcram.stl` | The A-frame fulcrum stand on the right side of the device. This is the stationary anchor point — the lever arm rotates around a pin housed here. Two steel guide rods pass through its base to connect it rigidly to the motor assembly. |

---

### 3. Connecting Rod (Coupler)
**Subfolder:** `connecting_rod/`

The coupler link in the four-bar linkage. It transfers motion from the rotating crank up to the underside of the lever arm. The adjustable metal sleeve on this assembly (visible in the device photos) allows fine-tuning of stroke length and the arm's resting height.

| File | Description |
|---|---|
| `Bearing_Rod_PistonAdapter.stl` | Lower adapter that links the crank's outer pin to the connecting rod. |
| `Bearing_Rod_Piston_Cyl.stl` | Cylinder/slider portion of the connecting rod. Provides adjustability for stroke length. |
| `Bearing_Rod_Adapter.stl` | Upper adapter that links the connecting rod to the underside of the lever arm. |

---

### 4. Crank (Input Link)
**Subfolder:** `crank_input_link/`

The crank is the input link that attaches directly to the gearbox output shaft and rotates continuously in 360°. Its outer pin drives the connecting rod, generating the oscillating motion of the lever arm.

| File | Description |
|---|---|
| `cranckside_D5.stl` | The rotating crank disk/arm attached to the gearbox output shaft. |
| `GeoT_Crank_Mount_final.stl` | Mount that secures the crank to the gearbox on the crank side. |
| `GeoT_Crank_Mount_motorEnd_Final.stl` | Mount for the motor end of the crank shaft. |
| `ND_CrankStand.stl` | Stand that supports the crank by attaching to `cranckside_D5.stl`. |

---

### 5. Motor / Drive
**Subfolder:** `motor_drive/`

These parts house and secure the motor/gearbox unit and carry the printed gear reduction stage between the motor shaft and the crank shaft.

| File | Description |
|---|---|
| `Big_Motor_Faceplate.stl` | Faceplate that secures the motor to its seat. |
| `Motor_Brace.stl` | Secondary brace that prevents the motor from rotating or shifting under load. |
| `GeoT_gear_crank.stl` | Printed gear pair (motor-side and crank-side gears). Reduces motor speed and increases torque at the crank shaft. **Print in PETG or ABS** rather than PLA for durability. |

---

### 6. Base Frame
**Subfolder:** `base_frame/`

The base provides the rigid ground link of the four-bar linkage. Two parallel steel rods slide through bores in the motor-side base block and the A-frame fulcrum stand, holding everything in alignment.

| File | Description |
|---|---|
| `GeoT_Base_motor_D2.stl` | Motor-side base block. Sits on the bench and anchors the motor assembly at one end of the two guide rods. |

> **Assembly note:** Slide all components onto the guide rods before tightening any set-screws. Square up the assembly first, then tighten.

---

### 7. Cable Management Box
**Subfolder:** `cable_management_box/`

A standalone enclosure for the motor driver electronics. This box sits separately on the bench near the device and is not mechanically connected to the device frame.

| File | Description |
|---|---|
| `drivermount.stl` | Main enclosure body for the motor driver board. Ventilated dot pattern on the face. |
| `drivermount_top.stl` | Lid for the driver enclosure. |

---

## Assembly Order

Assemble the device in the following order to avoid having to disassemble completed sections:

1. **Base frame** — Insert the two steel guide rods through `GeoT_Base_motor_D2.stl`. Do not tighten set-screws yet.
2. **Motor / drive** — Seat the motor/gearbox into `Big_Motor_Faceplate.stl` and secure with `Motor_Brace.stl`. Mesh `GeoT_gear_crank.stl` with the motor pinion.
3. **Crank** — Attach `GeoT_Crank_Mount_final.stl` and `GeoT_Crank_Mount_motorEnd_Final.stl` to the gearbox output shaft. Mount `cranckside_D5.stl` and support with `ND_CrankStand.stl`.
4. **Connecting rod** — Assemble `Bearing_Rod_PistonAdapter.stl`, `Bearing_Rod_Piston_Cyl.stl`, and `Bearing_Rod_Adapter.stl`. Attach the lower end to the crank outer pin.
5. **Fulcrum / A-frame** — Slide `GeoT_Fulcram.stl` onto the free ends of the guide rods. Square to the motor assembly, then tighten all rod set-screws.
6. **Lever arm** — Assemble `ARM_B_end_d2.stl` with `ArmInsert2.stl` and pin it to the fulcrum. Attach `CentrPS.stl` and then `ArmSleve.stl` working outward along the arm. Connect the upper end of the connecting rod to the arm underside via `Bearing_Rod_Adapter.stl`.
7. **Vial holder** — Attach `Gept_Arm_Backplate.stl` to `ArmSleve.stl`, then clip `Curved_Vialholder.stl` to the backplate. Fit `Curved_TopCover.stl` over the vial slots.
8. **Cable management** — Wire the motor driver into `drivermount.stl` and close with `drivermount_top.stl`. Place the box on the bench and connect motor leads.
9. **Final check** — Power on briefly and confirm the arm oscillates smoothly through its full arc before loading vials.

---

## Print Settings

| Component | Material | Layer Height | Infill | Supports |
|---|---|---|---|---|
| `Curved_Vialholder.stl` | PLA | 0.2 mm | 40% | **Yes** |
| `Curved_TopCover.stl` | PLA | 0.2 mm | 20% | **Yes** |
| `Gept_Arm_Backplate.stl` | PLA | 0.2 mm | 40% | No |
| `ArmSleve.stl` | PLA | 0.2 mm | 40% | No |
| `CentrPS.stl` | PLA | 0.2 mm | 40% | No |
| `ARM_B_end_d2.stl` | PLA | 0.2 mm | 40% | No |
| `ArmInsert2.stl` | PLA | 0.2 mm | 60% | No |
| `GeoT_Fulcram.stl` | PLA | 0.2 mm | 60% | No — print upright so layer lines run parallel to load |
| `Bearing_Rod_PistonAdapter.stl` | PLA | 0.2 mm | 60% | No |
| `Bearing_Rod_Piston_Cyl.stl` | PLA | 0.2 mm | 60% | No |
| `Bearing_Rod_Adapter.stl` | PLA | 0.2 mm | 60% | No |
| `cranckside_D5.stl` | PLA | 0.2 mm | 60% | No |
| `GeoT_Crank_Mount_final.stl` | PLA | 0.2 mm | 40% | No |
| `GeoT_Crank_Mount_motorEnd_Final.stl` | PLA | 0.2 mm | 40% | No |
| `ND_CrankStand.stl` | PLA | 0.2 mm | 60% | No — print upright |
| `Big_Motor_Faceplate.stl` | PLA | 0.2 mm | 40% | No |
| `Motor_Brace.stl` | PLA | 0.2 mm | 40% | No |
| `GeoT_gear_crank.stl` | **PETG or ABS** | 0.15 mm | 60% | No |
| `GeoT_Base_motor_D2.stl` | PLA | 0.2 mm | 40% | No |
| `drivermount.stl` | PLA | 0.2 mm | 20% | No |
| `drivermount_top.stl` | PLA | 0.2 mm | 20% | No |

> **Note on gears:** `GeoT_gear_crank.stl` should be printed in PETG or ABS at a finer layer height (0.15 mm) for better dimensional accuracy and wear resistance. PLA gears will work initially but may wear quickly under continuous use.

> **Note on orientation:** Print `GeoT_Fulcram.stl` and `ND_CrankStand.stl` upright (standing on their base) so that layer lines run parallel to the primary load direction, maximizing inter-layer strength at the stress points.

---

## Bill of Materials

Non-printed hardware required for assembly:

| Item | Qty | Notes |
|---|---|---|
| Steel guide rods | 2 | Diameter must match bores in `GeoT_Base_motor_D2.stl` and `GeoT_Fulcram.stl` |
| Bearings | 2+ | At the pivot/fulcrum point and crank shaft ends |
| DC gear motor | 1 | The motor and gearbox unit visible in device photos |
| Motor driver board | 1 | Housed in `drivermount.stl` enclosure |
| M3/M4 screws and nuts | Assorted | For securing all printed-to-printed and printed-to-hardware interfaces |
| Set-screws | 4+ | For locking guide rods in base and fulcrum blocks |
| Hinge pin | 1 | Passes through bearing in `GeoT_Fulcram.stl` to pin the lever arm |
| Crank outer pin | 1 | Connects `cranckside_D5.stl` to `Bearing_Rod_PistonAdapter.stl` |
| Metal adjustable clamp/sleeve | 1 | On the connecting rod; used to fine-tune stroke length and resting height |
