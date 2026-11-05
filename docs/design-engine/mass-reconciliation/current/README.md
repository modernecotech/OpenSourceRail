# v0.6 vehicle mass reconciliation

Physical candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`; selection `e56fd43277b64a1c40a30bc2f6c04b74498263b6e3945a6889b01af6f4394803`.

This report preserves every retained source-account occurrence in its system account, then assigns each candidate geometry occurrence to one parent account using explicit component-family rules. It distinguishes exact retained source-occurrence links, exact nested source-geometry links, and separately declared component groups that match a complete source-account mass. These provenance links trace model origin only; they do not establish physical installation, assembly completeness, or measured mass. Newly modelled underframe, bogie, and passive-secondary geometry is assigned once. This is an accounting reconciliation, not a complete installed-mass claim.

| Ledger result | Value |
|---|---:|
| Accounted tare | 19,221.998 kg/car |
| Candidate located geometry | 9,131.799 kg/car |
| Reference or unlocated account residual | 10,090.200 kg/car |
| Account rows | 12 |
| Located geometry occurrences assigned once | 2,482 |
| Exact retained source-occurrence ID links (geometry occurrences / source occurrences) | 750 / 750 |
| Mass under those exact source-occurrence ID links | 1,324.307 kg/car |
| Exact inherited source-geometry links (geometry parts / source occurrences) | 1,516 / 28 |
| Mass under those exact source-geometry links | 1,162.040 kg/car |
| Combined exact source identity links (disjoint geometry occurrences / mass) | 2,266 / 2,486.346 kg/car |
| Candidate geometry without either exact source identity link | 216 occurrences / 6,645.452 kg/car |
| Calculated source-component groups (geometry occurrences / groups) | 44 / 3 |
| Mass under calculated source-component groups | 478.763 kg/car |
| Closure worksheet rows (source / geometry / account) | 5,418 (2,924 / 2,482 / 12) |
| Separate non-additive analytical estimates | 1 (47.809 kg/car already represented in the scalar account) |
| Complete installed mass, CG, inertia, axle reactions | Unknown |

## Provisional roof-finish distribution estimate

The separate analytical estimate links the existing `white-roof-finish` account to 24 modelled roof upper-skin surfaces. Their combined plan area is 45.050 m²; the declared 0.800 mm thickness and 1326.56 kg/m³ density give 47.809 kg/car.
The estimated candidate-frame material centroid is (0.0000, 0.0000, 3.8058) m. It is derived from the roof-surface areas and the 1 m floor translation, with half the assumed coating thickness added vertically. This is not a verified installed position.
The coating mass is already included in the scalar roof-thermal account. This estimate adds 0 kg to accounted tare, adds no candidate CAD occurrence, and changes neither located geometry mass nor the account residual. Uniform coverage, material density, thickness, seams, openings, and solar-panel overlap require confirmation.

## Account groups

| Account group | Accounted kg | Geometry kg | Residual kg | Source occurrences | Geometry occurrences |
|---|---:|---:|---:|---:|---:|
| attachments | 180.000 | 0.000 | 180.000 | 1 | 0 |
| passive-bogie-pair | 6,730.000 | 4,965.818 | 1,764.182 | 0 | 60 |
| passive-secondary | 275.343 | 275.343 | 0.000 | 0 | 52 |
| retained-comfort/HVAC | 960.000 | 0.000 | 960.000 | 5 | 0 |
| retained-comfort/body | 7,196.087 | 2,323.011 | 4,873.077 | 754 | 1,482 |
| retained-comfort/doors | 127.867 | 29.100 | 98.767 | 4 | 48 |
| retained-comfort/frame-joints | 202.739 | 0.000 | 202.739 | 2,128 | 0 |
| retained-comfort/glazing | 431.625 | 411.143 | 20.482 | 5 | 36 |
| retained-comfort/seating | 800.000 | 201.856 | 598.144 | 25 | 744 |
| roof-thermal | 47.809 | 0.000 | 47.809 | 1 | 0 |
| services | 1,345.000 | 0.000 | 1,345.000 | 1 | 0 |
| wheel-underframe | 925.528 | 925.528 | 0.000 | 0 | 60 |

## Retained body account detail

This table groups the existing body source rows by evidence class and recorded role. It shows source-account mass, geometry already represented, and the resulting accounting difference; it does not add geometry or treat the reserve as installed hardware.

| Source scope | Evidence class | Source rows | Source mass (kg/car) | Candidate geometry (count / kg) | Residual (kg/car) |
|---|---|---:|---:|---:|---:|
| Unlocated body reserve; not a physical inventory | unlocated-allocation | 1 | 4,778.254 | 0 / 0.000 | 4,778.254 |
| Panel stock, edges, bonds and fasteners (partial geometry) | counted-component-with-partial-proposed-geometry | 2 | 1,025.907 | 724 / 931.084 | 94.823 |
| Side panels | located-material | 320 | 659.577 | 320 / 659.577 | 0.000 |
| Extrusion/frame stock | located-material | 252 | 557.391 | 252 / 557.391 | 0.000 |
| End panels | located-material | 40 | 93.094 | 40 / 93.094 | 0.000 |
| Door infill and aperture frames | unlocated-counted-material | 1 | 67.620 | 8 / 67.620 | 0.000 |
| Corner laps | located-material | 104 | 10.622 | 104 / 10.622 | 0.000 |
| Corner bonds | located-material | 34 | 3.623 | 34 / 3.623 | 0.000 |
| **Account total** |  | 754 | **7,196.087** | 1,482 / **2,323.011** | **4,873.077** |

The source account identifies 4,778.254 kg/car as a body reserve without a physical-equipment inventory. A further 94.823 kg/car is the difference between panel/edge/bond/fastener source rows and their partially represented candidate geometry. The combined 4,873.077 kg/car remains unlocated; component identity, material, installation and centre of gravity are not established.


## Passive-bogie geometry detail

The existing reference account is 6,730.000 kg for 2 passive bogies per car. The table decomposes only the candidate CAD solids; the per-bogie column evenly divides those totals for comparison and is not a measured assembly mass.

| Modelled component family | Candidate solids | Geometry mass (kg/car) | Even split (kg/bogie) |
|---|---:|---:|---:|
| Axle solids | 4 | 1,109.768 | 554.884 |
| Bolsters | 8 | 259.741 | 129.870 |
| Brake discs | 8 | 599.275 | 299.637 |
| Bogie sideframes | 16 | 376.800 | 188.400 |
| Wheel rims, webs and hubs | 24 | 2,620.235 | 1,310.118 |
| **Located CAD subtotal** | 60 | **4,965.818** | **2,482.909** |
| **Unallocated reference-account residual** | Not modelled | **1,764.182** | **882.091** |
| **Reference-account total** |  | **6,730.000** | **3,365.000** |

The CAD groups include axles, wheel rims/webs/hubs, brake discs, sideframes and bolsters. The 1,764.182 kg/car residual remains an unallocated account balance; individual suspension, bearing, brake-caliper, fastening and interface masses are not defined by the source account. The candidate's passive secondary-suspension description does not add geometry or mass. This account excludes traction motors and gearing, and it does not establish complete bogie mass or physical installation.


## Service-battery account detail

The candidate's existing 1,345 kg service-battery account is disaggregated from its selected electrical definition below. These rows sum within the account and do not create extra tare, CAD solids, or installed positions.

| Component | Quantity | Unit mass (kg) | Account mass (kg/car) | Evidence class |
|---|---:|---:|---:|---|
| Toshiba SCiB Type3-20 FM01202CCA04A | 75 modules | 14.000 | 1,050.000 | supplier-reference |
| enclosure and module racks | 1 per-car allowance | 135.000 | 135.000 | engineering-mass-assumption |
| DC protection, monitoring and busbars | 1 per-car allowance | 45.000 | 45.000 | engineering-mass-assumption |
| cooled enclosure circuit and heat exchanger | 1 per-car allowance | 55.000 | 55.000 | engineering-mass-assumption |
| isolated service DC/DC and low voltage supplies | 1 per-car allowance | 30.000 | 30.000 | engineering-mass-assumption |
| station charge connector and isolation | 1 per-car allowance | 20.000 | 20.000 | engineering-mass-assumption |
| isolation and retention mounts | 1 per-car allowance | 10.000 | 10.000 | engineering-mass-assumption |
| **Calculated account total** |  |  | **1,345.000** | Difference to source account: +0.000000000 kg |

The 75 Type3-20 modules contribute 1,050.000 kg at the supplier-reference 14.000 kg/module. The 6 named enclosure, protection, cooling, conversion, charging, and retention allowances contribute 295.000 kg and remain design assumptions. No module or accessory geometry, installed position, complete pack mass, or railway approval is established.

## HVAC reference-package account detail

The five source records are supplier-reference package hardware only. Their source roles leave mounting, ducts, complete equipment mass, geometry, location and railway qualification unresolved.

| Source component group | Quantity | Unit mass (kg) | Source-account mass (kg/car) | Candidate geometry (kg/car) | Residual (kg/car) | Evidence class |
|---|---:|---:|---:|---:|---:|---|
| Supplier-reference HVAC package | 5 source occurrence | 192.000 | 960.000 | 0.000 | 960.000 | supplier-reference |
| **Account total** | 5 source occurrences |  | **960.000** | **0.000** | **960.000** |  |

## Seat and interior account detail

The fixture source classes and other-interior allowance reconcile the existing 800 kg account. Candidate geometry is counted once; the remaining account balance is not inferred to be a measured part or an installed seat mass.

| Source component group | Quantity | Unit mass (kg) | Source-account mass (kg/car) | Candidate geometry (kg/car) | Residual (kg/car) | Evidence class |
|---|---:|---:|---:|---:|---:|---|
| Seat fixture source mass class A | 20 source occurrence | 11.467 | 229.338 | 181.117 | 48.220 | counted-fixture-with-proposed-material-placement |
| Seat fixture source mass class B | 4 source occurrence | 7.239 | 28.956 | 20.738 | 8.218 | counted-fixture-with-proposed-material-placement |
| Other-interior allowance without candidate geometry | 1 source occurrence | 541.706 | 541.706 | 0.000 | 541.706 | unlocated-allocation |
| **Account total** | 25 source occurrences |  | **800.000** | **201.856** | **598.144** |  |

## Door, glazing and frame-joint account details

These source-level groups show the existing counted or supplier-reference components and their mapped CAD mass. An entry with zero candidate geometry remains an accounting item without a demonstrated installed location.

| Account | Source component | Quantity | Unit mass (kg) | Source mass (kg/car) | Candidate geometry (count / kg) | Residual (kg/car) | Evidence class |
|---|---|---:|---:|---:|---:|---:|---|
| retained-comfort/doors | 1300 mm door-operator supplier reference | 2 | 41.000 | 82.000 | 0 / 0.000 | 82.000 | supplier-reference |
| retained-comfort/doors | Proposed door-leaf material | 2 | 22.933 | 45.867 | 48 / 29.100 | 16.767 | counted-component-with-partial-proposed-geometry |
| **retained-comfort/doors total** |  | 4 source occurrences |  | **127.867** |  | **98.767** |  |
| retained-comfort/glazing | Glass panes | 1 | 390.000 | 390.000 | 24 / 390.000 | 0.000 | unlocated-counted-material |
| retained-comfort/glazing | PVB interlayers | 1 | 21.143 | 21.143 | 12 / 21.143 | 0.000 | unlocated-counted-material |
| retained-comfort/glazing | Aluminium glazing retention | 1 | 11.016 | 11.016 | 0 / 0.000 | 11.016 | unlocated-counted-material |
| retained-comfort/glazing | EPDM glazing seals | 1 | 6.528 | 6.528 | 0 / 0.000 | 6.528 | unlocated-counted-material |
| retained-comfort/glazing | Glazing bond allowance | 1 | 2.938 | 2.938 | 0 / 0.000 | 2.938 | unlocated-counted-material |
| **retained-comfort/glazing total** |  | 5 source occurrences |  | **431.625** |  | **20.482** |  |
| retained-comfort/frame-joints | Roof-spreader plates | 24 | 4.277 | 102.643 | 0 / 0.000 | 102.643 | unlocated-counted-material |
| retained-comfort/frame-joints | GFRP hardpoint isolators | 24 | 0.251 | 6.019 | 0 / 0.000 | 6.019 | unlocated-counted-material |
| retained-comfort/frame-joints | Frame-joint gusset plates | 260 | 0.173 | 44.928 | 0 / 0.000 | 44.928 | unlocated-counted-material |
| retained-comfort/frame-joints | GFRP joint-isolation pads | 130 | 0.046 | 5.928 | 0 / 0.000 | 5.928 | unlocated-counted-material |
| retained-comfort/frame-joints | Crush sleeves | 520 | 0.043 | 22.121 | 0 / 0.000 | 22.121 | unlocated-counted-material |
| retained-comfort/frame-joints | M8 bolt shanks | 520 | 0.024 | 12.311 | 0 / 0.000 | 12.311 | unlocated-counted-material |
| retained-comfort/frame-joints | M8 head-and-nut stock envelopes | 520 | 0.015 | 7.541 | 0 / 0.000 | 7.541 | unlocated-counted-material |
| retained-comfort/frame-joints | Joint bond film | 130 | 0.010 | 1.248 | 0 / 0.000 | 1.248 | unlocated-counted-material |
| **retained-comfort/frame-joints total** |  | 2,128 source occurrences |  | **202.739** |  | **202.739** |  |

Door operator figures are 1300 mm product references; the selected 1400 mm openings and deeper leaves are not established compatible installations. The frame-joint component masses are counted stock estimates with no placed candidate geometry. These breakdowns add no mass and do not close installation or qualification.

The located-material centre of gravity is calculated from the represented geometry subset only. It excludes all residual accounts, including the service pack, HVAC, unlocated bogie balance, roof coating takeoff, attachment allowance, and source-account mass without candidate geometry. It is not the installed vehicle CG. Average axle masses are not axle reactions; longitudinal balance and dynamic wheel loads remain unresolved.

Exact retained source-occurrence IDs link 750 candidate geometry occurrences (1,324.307 kg/car) to 750 source occurrences, with each linked mass checked equal. Separately, exact nested source-geometry IDs link 1,516 occurrences (1,162.040 kg/car); those nested links are also mass-checked and have distinct candidate geometry IDs. Together, exact links identify 2,266 of 2,482 candidate geometry occurrences and 2,486.346 kg/car. An additional 44 occurrences (478.763 kg/car) map to 3 source accounts through declared glazing, PVB, and deleted-door-infill groups whose aggregate masses match the source accounts exactly. These are calculated group links, not exact per-part source IDs. The remaining 216 occurrences (6,645.452 kg/car) lack an exact source-occurrence or nested-subgeometry link. None of these mappings proves manufacture or physical installation.
The [mass closure worksheet](mass-closure-worksheet.json.gz) has one row for every retained source-account occurrence, candidate geometry occurrence, and account closure. It keeps source-accounted mass, CAD-derived mass, and account residuals in separate fields. Every row's physically installed mass and installed position remain null; a candidate geometry centroid is not an installed position, and a positive accounting residual is not a physical part.

## Calculated source-component groups

| Group rule | Source account mass | Candidate parts | Calculated group mass | Difference |
|---|---:|---:|---:|---:|
| `comfort-design/deleted-door-infill-v1` | 67.620000 kg | 8 | 67.620000 kg | +0.000000000 kg |
| `comfort-design/glazing-glass-v1` | 390.000000 kg | 24 | 390.000000 kg | +0.000000000 kg |
| `comfort-design/glazing-pvb-v1` | 21.143200 kg | 12 | 21.143200 kg | +0.000000000 kg |

These groups improve source-to-geometry traceability only. Their material was already included in located geometry, so they add no mass and reduce no account residual. The associated occurrence IDs identify component-account groupings, not exact per-part identities.

Source occurrences keep their source IDs and occurrence-definition IDs in [mass-ledger.json.gz](mass-ledger.json.gz). The report is bound by [manifest.json](manifest.json). Regenerate with `python3 -m engineering.mass_ledger_audit build` and verify with `python3 -m engineering.mass_ledger_audit verify`.

No physical acceptance, manufacturing release, or operating release is asserted.
