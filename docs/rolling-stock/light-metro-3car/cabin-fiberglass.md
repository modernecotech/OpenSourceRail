# Cabin fiberglass and phenolic interior parts

This page controls the non-structural fiberglass, phenolic, and
glass/basalt-fibre composite parts inside the `light-metro-3car`
passenger cabin. The steel body remains the certified load path. These
parts are sacrificial, replaceable, fire-rated passenger liners and
fairings.

The design intent is simple: the same regional composite cell that can
make or repair the end cowls can also make the cabin liners, battery
strake covers, and vestibule trim without expensive rail-OEM tooling.

## Controlled cabin fiberglass items

| Product-tree ID | Item | Qty basis | Function | Parent |
|---|---|---:|---|---|
| `LM3-INT-P020` | FRP/phenolic ceiling liner, light trough, and HVAC plenum cover set | 1 car kit/car | Covers roof bows, carries lighting trough openings, and provides removable HVAC/service access | `LM3-INT-SA330` |
| `LM3-INT-P030` | FRP/phenolic sidewall liner, window reveal, and cable-cover panel set | 2 side kits/car | Hides secondary structure and cable trays while preserving window replacement access | `LM3-INT-SA330` |
| `LM3-INT-P040` | FRP battery strake covers, seat-base fairings, and service-hatch shells | 1 car kit/car | Covers under-seat battery strakes, protects passengers from HV bay covers, and keeps battery access removable | `LM3-INT-SA330` |
| `LM3-INT-P050` | FRP vestibule kick panels, PRM ramp/step covers, and door-pocket trims | 4 door-zone kits/car | Protects high-wear door/PRM transition zones and trims the low-floor/high-floor step faces | `LM3-INT-SA330` |

All items are non-structural. They may carry local light fittings,
labels, small service covers, or trim clips, but they do not carry
seat loads, grab-rail loads, jacking loads, crash loads, battery loads,
or door loads.

## Material system

Use one of these material routes per part family, frozen by the v2A
drawing and supplier evidence pack:

| Route | Use | Nominal construction | Notes |
|---|---|---|---|
| Hand lay-up or vacuum-infused FRP | Curved ceiling, sidewall, battery strake, and door-pocket shapes | Fire-retardant E-glass or basalt cloth with vinyl-ester or phenolic-compatible resin | Good for modest tooling and local repair |
| Flat phenolic composite board | Flat liners, cable covers, access doors, and kick panels | EN 45545 HL2 candidate phenolic/glass board, CNC trimmed | Lowest risk where single curvature is not required |
| Lightweight sandwich FRP | Broad ceiling or sidewall panels where oil-canning is visible | Thin FRP skins over fire-rated foam/honeycomb core | Keep solid laminate at all inserts and edges |

Passenger-facing materials need EN 45545-2 HL2 or the deployment
authority's accepted equivalent. Do not install uncertified decorative
films, foams, sealants, adhesives, or edge trims in the cabin.

## Design rules

- Minimum visible edge radius: 3 mm; 6 mm preferred in standing areas.
- No exposed glass fibres: all cut edges are sealed after trimming.
- Use removable panels wherever the panel covers lights, HVAC drops,
  cable trays, battery access, fire detection, or emergency equipment.
- Use potted stainless, brass, or GFRP inserts only in solid laminate
  pads. Do not put inserts directly into foam/honeycomb core.
- Keep panel gaps at 3-5 mm nominal with dark shadow seals; avoid tight
  cosmetic gaps that become rattles after thermal cycling.
- Use captive or retained fasteners in service panels so hardware does
  not fall into the saloon.
- Use anti-slip surfacing and yellow/contrast nosing on PRM ramp,
  threshold, and step-cover pieces.
- Keep HV warning labels and service-lock labels on the removable
  battery strake cover, not on separate loose trim.
- Do not bond cabin trim permanently across any battery, HV, fire,
  HVAC, door, or window service path.

## Tooling package

| Tooling ID | Tool | Applies to | Acceptance |
|---|---|---|---|
| `LM3-TL-INT-10` | Ceiling liner buck and trim fixture | `LM3-INT-P020` | Light trough and HVAC openings within ±1.0 mm |
| `LM3-TL-INT-11` | Sidewall/window reveal buck and drill fixture | `LM3-INT-P030` | Window reveal gap 3-5 mm; fastener pitch within ±0.75 mm |
| `LM3-TL-INT-12` | Battery strake cover mould and service-hatch gauge | `LM3-INT-P040` | Hatch opens without seat removal; HV label visible |
| `LM3-TL-INT-13` | Door/PRM transition trim fixture | `LM3-INT-P050` | PRM transition and anti-slip witness accepted |

The first article may use low-cost MDF/epoxy tooling or machined foam
patterns sealed with epoxy tooling coat. Production tooling should be
female moulds for curved visible parts and CNC trim nests for flat
phenolic panels.

## Making instructions

### 1. Release package

1. Freeze the panel envelope, insert map, visible gap, service-removal
   direction, and fire-rating route.
2. Check material certificates for resin, reinforcement, board stock,
   adhesive, sealant, decorative coating, and edge trim.
3. Issue the traveler and verify the parent carbody/interior datum.
4. Cut a witness coupon for every laminate batch and cure cycle.

Hold point: fire-material certificates and laminate/panel batch records
accepted before lay-up or CNC trimming.

### 2. Mould or board preparation

1. Clean the mould/fixture and inspect for scratches, release buildup,
   or previous repair.
2. Apply release wax/PVA/semi-permanent release per supplier procedure.
3. For phenolic boards, stage the CNC spoilboard and vacuum hold-down
   without contaminating passenger-facing surfaces.
4. Mark every blank with product ID, car number, side, and batch.

Hold point: mould/fixture release record complete.

### 3. Lay-up or trim

1. Cut dry reinforcement plies with fibre directions marked.
2. Lay visible gelcoat or interior finish coat where the process uses
   in-mould finish.
3. Lay outer plies, core where allowed, local solid-laminate pads, and
   inner plies.
4. Wet out by hand lay-up or vacuum infusion; avoid resin-rich pools
   around inserts and tight returns.
5. Cure under controlled temperature/time. Record ambient temperature,
   resin batch, pot life, vacuum level if used, and cure time.
6. Demould only after the resin supplier's minimum cure condition.
7. Trim, drill, and edge-radius the panel in its trim fixture.

Hold point: coupon, cure, visual void/dry-fibre inspection, and
trim-line gauge accepted.

### 4. Inserts, edges, and finish

1. Pot threaded inserts into solid laminate pads or bonded doubler pads.
2. Seal all drilled and trimmed edges.
3. Apply decorative paint/film only after fire-material compatibility
   is accepted.
4. Add anti-slip witness panels, yellow/contrast nosing, labels, and
   QR/part ID labels.
5. Fit gaskets, clips, retained fasteners, and access-panel tethers.

Hold point: insert pull-out sample, edge-seal inspection, and label
placement accepted.

### 5. Trial fit and release

1. Dry-fit each panel in the carbody/interior fixture before installing
   seats, grab rails, and lighting.
2. Check window replacement access, battery hatch removal, lighting
   service removal, HVAC access, cable-tray access, and emergency
   equipment visibility.
3. Shake/rattle check by hand before the first static electrical test.
4. Record shim packs, clip counts, fastener torque where applicable,
   and any approved deviations.

Hold point: egress gauge, sharp-edge inspection, service-removal trial,
rattle check, and fire-material pack complete.

## Repair instructions

- Cosmetic scratches: sand, clean, fill with compatible fire-rated
  repair resin/filler, refinish, and record repair location.
- Cracked non-service panel: remove and replace if crack crosses an
  insert, edge return, access door, or passenger touch zone.
- Battery strake or PRM panel damage: replace the panel, then repeat
  HV-label, service-hatch, anti-slip, and sharp-edge checks.
- Fire, smoke, or heat exposure: quarantine the panel and replace
  unless the material supplier provides a signed repair disposition.

## v2A drawing outputs

The v2A drawing pack shall release:

- panel envelope and visible-gap drawings,
- laminate/board schedule,
- insert and clip map,
- CNC trim DXF or mould trim curves,
- service-removal direction and access envelope,
- edge radius and edge-seal procedure,
- anti-slip/nosing/label map,
- first-article inspection form,
- repair and replacement limits.
