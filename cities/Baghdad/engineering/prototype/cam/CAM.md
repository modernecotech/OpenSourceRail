# Cut the Airport vehicle blanks and run a CAM practice job

The 36-car Airport order calls for **2,016 plate blanks and 3,168 saw blanks**. A local plate shop can use the nested DXFs to price the plate supply. The vehicle works can use the bar schedule to price raw steel, handling and saw time. The only posted machine program in this packet cuts an L-slot in a machinable-wax training coupon.

| Opening supply | Nominal dimensions, mm | Pieces | Reference raw stock |
|---|---|---:|---|
| Body gusset | Right triangle with two 450 legs, thickness 8 | 1,440 | Forty 3,000 × 1,500 × 8 sheets |
| Primary underside pad | 180 × 140 × 12 | 288 | Four shared 3,000 × 1,500 × 12 sheets cover all three pad types |
| Secondary bogie top pad | 170 × 140 × 12 | 144 | Included above |
| Secondary body pad | 170 × 160 × 12 | 144 | Included above |
| Hollow sections | Ten nominal section sizes across the [stock patterns](saw-stock.csv) | 2,592 | 581 bars of 12 m and 238 of 12.5 m cover the hollow sections **and** liners |
| Flat jamb liners | 40 × 8, length 2,000 | 576 | Included above |

The nominal density is 7,850 kg/m³. The source proposes S355NH for hot-finished hollow sections and uses 355 MPa nominal yield in the frame model. Buyers should specify the plate/flat product grade, subgrade, toughness, certificate and traceability required by the approved material schedule. The frame model supplies gross dimensions. Machined pad finishes, tolerances, joining and fatigue details need the corresponding reviewed joint drawing.

## Plate supplier

1. Import the millimetre profiles for the [gusset](parts/gusset.dxf), [primary pad](parts/primary_underside.dxf), [secondary top pad](parts/secondary_top.dxf) and [secondary body pad](parts/secondary_body.dxf). Each file contains one closed XY outline of the nominal blank. Local XY starts at the lower-left corner, the gusset datum is its right-angle vertex and positive Z goes through the thickness. Corners are nominally sharp. The files contain no fastener holes, edge preparation, machining stock or extra bend lines.
2. Use [the sheet schedule](sheet-schedule.csv) to select the DXF in `sheets/`. Repeat the [8 mm gusset sheet](sheets/plate-8mm-1.dxf) forty times. Run each of the four 12 mm sheets once. A schedule row gives one part's quantity on that layout. A shared sheet appearing on several rows represents one physical sheet. The [placement register](sheet-placements.csv) gives the sheet origin of every blank and its rotation about +Z. Positive axes follow the long and short edges from the lower-left sheet corner when viewed from above.
3. Import only the closed part contours. Load the 3,000 × 1,500 stock rectangle separately in the supplier CAM system. The nests have a 10 mm minimum border and 7 mm minimum nominal contour-to-contour spacing. They use no common-line cuts. Nominal area yield is 81.0% at 8 mm and 81.12% at 12 mm. These are material estimates before piercing, edge cleanup, rejects or spares.
4. Price the local machine, gas, cut time, individual marking, deburring and heat traceability. Return the process, tested kerf, lead-in and heat-zone footprint, corner quality, flatness, pad finish allowance and remaining web. Apply external kerf compensation once. A 2 mm example kerf on each of two neighbouring parts leaves at least 3 mm between the outer edges of the two cuts. Revise the nest if the actual leads, edge clamps, finish allowance or retention tabs need more space.
5. Plan unloading of the sheet and the cut skeleton before freeing small blanks. A complete nominal sheet weighs about 283 kg at 8 mm or 424 kg at 12 mm. Use certified lift capacity covering the actual stock and rigging, a supported unloading table and a supplier-approved retention/cut order. Quote identification transfer and inspection while parts remain attributable to the heat. Record first-article dimensions, including the gusset leg and diagonal, pad squareness and the cut edge at the smallest corner.

The [car installation frames](plate-frames.json) locate 56 blank occurrences in one sealed car OBJ, including both bogies. Multiply a homogeneous local column vector in mm by `car_from_blank_mm` to obtain car coordinates. The car origin uses railhead Z=0, X forward and Y left. The generator rebuilds every extruded vertex and compares it with the OBJ. This verifies nominal blank shape and position. Fastener patterns, retained interfaces, insertion paths, applied loads and physical fit stay with their component acceptance records.

## Vehicle saw operator

Use [raw bar quantities](saw-stock.csv) to receive stock by section and [indexed cuts](saw-cuts.csv) to set up each pattern. There are 22 patterns. Repeat the entire sequence for each bar assigned to that pattern. The plan buys 9,947 m against 8,816.500 m of nominal cut lengths. Allow 3,987 blade strokes across the opening when each of the 819 bars receives its own front trim plus one cutoff for each of the 3,168 blanks. A supplier returning pre-trimmed, gauged stock should identify that scope in its price. The 12.5 m mill lengths cover the 12 m finished chords and improve yield for the associated section family. Confirm mill length, vehicle access, rack capacity and packaged freight before buying.

The raw infeed end is X=0. Increasing X follows the bar. The first good cut starts 10 mm from that end, including the front trim kerf. The near blade face sits at `near_blade_face_mm` and the 3 mm trial kerf advances toward +X. After each cut the next blank starts at that face plus one kerf. Each pattern retains at least 100 mm of clamped tail. The listed remaining tail includes this grip length. Actual jaws, blade width, roller supports, stock straightness and stop calibration determine shop settings.

One guarded saw, a positive length stop, stock clamps and aligned infeed/outfeed supports serve the proposed lane. A single 12 m RHS 200 × 150 × 10 bar has a nominal mass of about 622 kg using the cut schedule's unit mass. Size supports and lifting equipment for the delivered bar or bundle and rigging. Support both sides of the cut before release and use an accessible rack for reusable tails. The brace lengths carry the precision of the structural axis calculation. Handed end geometry, mitres, welding fit-up, squareness and any finishing allowance require the released cut drawing. Liner drilling, pad machining and welded assembly have separate operations.

## Practice job for CAM users

**Result.** Mill a 3 mm wide, 1 mm deep L-slot in 60 × 40 × 8 mm machinable wax. The horizontal and vertical centreline legs measure 28 and 16 mm. The round ends come from the 3 mm cutter. The job leaves 7 mm of stock under the slot. The coupon stays attached throughout. No coolant command, tool changer, machine homing or clamp actuation is included.

| Setup | Practice values |
|---|---|
| Machine and tool | Three-axis mill supporting the GRBL linear-motion subset, one centre-cutting 3 mm flat end mill, 12 mm projection, 20 mm holder diameter |
| Fixture | Support the whole coupon on parallels in a soft-jaw vise. Jaws occupy Y −6 to 0 and 40 to 46 mm in the simulation, with tops at Z −2 mm |
| Work coordinates | G54 at lower-left of the stock top, X along 60 mm, Y along 40 mm, Z up. The simulated start is X15 Y12 Z5 |
| Practice settings | 6,000 rpm, 180 mm/min cutting, 60 mm/min plunge, two passes at Z −0.5 and −1.0 mm. Check the actual cutter and spindle range for the wax |
| Cutting moves | Plunge at (15,12), cut to (43,12) then (43,28), retract vertically to Z5. Return at Z5 and repeat at full depth |

1. Compare the [tool-centre path](training/practice-path.txt) with the setup table, then open the [GRBL program](training/practice.nc) in the mill's preview. The NC produces absolute metric moves in the XY plane and feed per minute. Confirm actual travel, tool reach, holder, clamping force on wax, work offset and spindle direction.
2. Have the operator demonstrate homing, work-zero setting, guarded setup and stopping on the actual machine using its own instructions. Verify a dry traversal clear of the coupon and jaws before cutting. Return the verified G54 stock top for the actual cut. Start at the stated approach position. Inspect the first pass with the spindle stopped.
3. Measure slot width and depth, endpoint coordinates and floor thickness. Record the tool, fixture, machine/post version, dry-run result, measurements and any discrepancy. A mirrored L calls for investigation of axis orientation or the work offset. A uniformly over-wide slot calls for cutter diameter and runout checks before changing the geometry.

FreeCAD's GRBL post reproduced the published NC byte for byte. Its stock-removal simulator replayed all 11 linear endpoints with a 0.25 mm voxel pitch. It reported 150.19 mm³ of removed wax against 138.59 mm³ from the continuous cylindrical cutter sweep. The 8.37% excess is within the declared 15% coarse-voxel comparison band. FreeCAD also imported the four part drawings and five sheet layouts and checked their closed geometry and minimum spacing. Controller timing, actual workholding, verified spindle settings and cut measurements require a physical run. The [native replay receipt](training/freecad-receipt.json) identifies the exact post and NC. [FreeCAD CAM documentation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Workbench.md) · [FreeCAD stock simulator](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Simulator.md) · [GRBL controller command set](https://github.com/gnea/grbl)

## Reproduction and procurement

From the repository root, run the following commands. The standard-library check validates the sealed input member hashes, verifies placement in the car and rebuilds the exchange files. The final command also needs the FreeCAD 1.1.4 Flatpak and performs the independent native replay. The original Flatpak commit was `e63d66825c4daf9adb09283488c2bc2ace92ed8b24bcf81666933226ed082fd4`.

```sh
python3 cities/Baghdad/engineering/prototype/cam/build.py --check
python3 cities/Baghdad/engineering/prototype/cam/test_cam.py
flatpak run --command=sh org.freecad.FreeCAD -c 'PYTHONPATH=/app/freecad/lib:/app/freecad/Mod/CAM python3 cities/Baghdad/engineering/prototype/cam/verify_freecad.py'
```

The [CAM manifest](cam-manifest.json) binds the candidate, frame, input packet, generator and output hashes. A buyer can import these quantities into the existing `vehicle-plate-contract`, `vehicle-saw` and `vehicle-prep` records and compare installed or contracted offers. Ask suppliers to separate raw steel, setup, unit cutting, postprocessing, consumables, packing, delivery and rework. File the machine/post identifiers, accepted drawings, sample results, price basis, lead time and exclusions with each offer. This keeps a stock estimate traceable through quotation, first article and inspection.

Rebuild with `build.py` after a drawing or fleet revision, or pass `--out DIRECTORY` for an isolated comparison. Use `verify_freecad.py --write` only to record a fresh successful native run against that revision. The builder reads the sealed prototype and the frame's hash-bound `engineering/mechanical/vehicle/stock.toml` in the Baghdad city source tree. A cam-only supplier extract contains the exchange files and replay receipt. The full buyer issue includes the sealed prototype and a byte-identical copy of the frame stock specification in `cam/input/stock.toml`. Its hash must match the mechanical record in that prototype. The repository keeps the original specification in the city mechanical design.


After extracting the full buyer issue, open a shell beside its `START.html`. These commands check the shipped files, generate an independent set of cut files in a new directory, test the input boundary and replay the native verifier using the locally installed FreeCAD Flatpak. All inputs are in the issue and the replay requires no network.

```sh
python3 cam/build.py --check
python3 cam/build.py --out regenerated-cam
python3 cam/build.py --check --out regenerated-cam
python3 cam/test_cam.py
flatpak run --command=sh org.freecad.FreeCAD -c 'PYTHONPATH=/app/freecad/lib:/app/freecad/Mod/CAM python3 cam/verify_freecad.py'
```
