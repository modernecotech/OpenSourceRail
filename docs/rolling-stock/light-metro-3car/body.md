# Body structure — `light-metro-3car`

Aluminium large-profile extrusions bolted at end bulkheads — the
standard European light-metro body-build technique, chosen
because:

- Locally produced in every target region — aluminium extrusion
  mills exist in MENA, Latin America, South/Southeast Asia.
- Rivetable and weldable — no stainless-steel pressing line
  needed.
- Lighter than stainless-steel per equivalent stiffness (tare
  mass target 195 t for 65 m consist is attainable only with
  aluminium).

## Extrusion list

Each car is built from four standard extrusion profiles:

| Profile | Section | Function |
|---|---|---|
| OSR-A1 | 120 × 60 mm closed section | Side-wall panel vertical members |
| OSR-A2 | 80 × 40 mm closed section | Side-wall panel horizontal members |
| OSR-A3 | 200 × 40 mm C-section | Roof edge beam |
| OSR-A4 | 100 × 100 mm closed square | Corner post |

All four profiles are stock 6063-T6 or 6082-T6 alloy, available
from any regional extrusion mill with a 400 t press or larger.

## Side-wall panel assembly

Each car side is composed of:

- 2 corner posts (A4) × full-height (3 500 mm from floor to roof
  edge).
- 10 vertical members (A1) at 900 mm pitch.
- 7 horizontal members (A2) at 500 mm pitch.
- 2 door cut-outs at 5.0 m + 17.0 m (Car A / Car C) / 5.0 m +
  16.0 m (Car B) from cab end.
- 6 mm aluminium skin (alloy 5083 or equivalent) welded to the
  frame with MIG.

Panels are prefabricated at the shop (not on-car) — the car is
built by bolting four pre-built panels (2 side + roof + floor)
to the end bulkheads + corner posts.

## End bulkhead

- Pressed aluminium, 6 mm thick.
- Corrugated for stiffness (EN 12663 Cat P-III compressive end
  load 640 kN).
- Mounts the cab console frame (on Car A / Car C) or the
  articulation joint (Car B ends).

## Articulation joint (between Car A ↔ Car B, Car B ↔ Car C)

Commercial off-the-shelf bellows-type articulation joint sized
for 65 m consist. Reference: **Hübner RTS-B40** or local
equivalent.
- Bellow width: 2 400 mm (interior passable corridor).
- Vertical travel: ±100 mm.
- Horizontal travel (curve negotiation): ±250 mm at 1 800 mm
  turning radius.
- Roof cover: folding stainless-steel plate.
- Under-frame: rubber skirt + drainage gutter.

Sourced from a single supplier; no bespoke articulation design.

## Roof

- A3 C-section roof edge beam runs the full car length.
- Three transverse purlins per car (aluminium 60 × 40 mm box).
- Roof skin: 3 mm aluminium, painted white (solar reflectance).
- Roof penetrations:
  - Pantograph base (Car A and Car C): 800 × 400 mm mounting
    plate.
  - HVAC unit: 2 400 × 1 800 mm cut-out per car.
  - LED cab marker lights.
  - Antennas: 5G (TRG-1), LoRa (TRG-2), GNSS.
  - CCTV camera domes (2 per car).

## Floor

- 6 mm aluminium deck, supported on transverse purlins at 500 mm
  pitch.
- Vinyl floor covering, slip-resistant, EN 45545-2 R5.
- Fire-rated insulation (mineral wool, EN 45545 HL2 compliant)
  between deck and purlins.

## Windows

- Laminated safety glass per EN 15152.
- Fixed in seat windows, hopper-hinged at top for emergency
  ventilation (EN 45545).
- 900 × 1 200 mm typical.
- Emergency hammer per window (EN 45545-2 §6.5).

## Doors

Plug-outward doors, commercial off-the-shelf. Reference:
**IFE type 4 plug door** or local equivalent.
- Mechanism: electro-mechanical (no pneumatic).
- Door panel: aluminium leaf 40 mm thick with internal insulation.
- Clear opening 1 250 mm × 2 000 mm.
- Obstacle detection: motor-current monitoring + force-limit
  sensor — both consumed by `osr-door-control`'s interlock.
- Interior grab handles per EN 14752.

## Paint + livery

- Exterior: PPG-V170 polyester primer + 2K polyurethane topcoat.
- Livery colour: per-operator choice (not in upstream scope).
- Interior panels: powder-coated aluminium + melamine-faced
  laminate where specified by the operator.
- Anti-graffiti clear-coat on exterior: optional per-deployment.

## Fire compliance (EN 45545-2 HL2)

Every material in the body structure is classified under EN 45545
HL2 metro category:

| Item | Test | Class |
|---|---|---|
| Body extrusion + skin (aluminium) | inherent non-combustible | IEC 60584 N/A |
| Vinyl floor covering | R5 | HL2 compliant |
| Seat upholstery | R7 | HL2 compliant |
| Cable insulation | R15 / R24 | HL2 compliant |
| Interior GRP panels | R1 | HL2 compliant |
| Door rubber seal | R23 | HL2 compliant |

A certified test-house report per material is required before
v2 CAD release. The certification itself is a per-deployment
deliverable since national authorities may accept different
test-house accreditations.

## v2 deliverables (not in v1)

- STEP assembly of the car body + articulation.
- Dimensioned extrusion drawings per ISO 128.
- EN 15227 Cat C-II crashworthiness simulation report.
- Paint-process spec per PPG + local topcoat availability.
- EN 15085 weld-procedure register (CL1, CL2, CL3, CL4 welds
  enumerated).
