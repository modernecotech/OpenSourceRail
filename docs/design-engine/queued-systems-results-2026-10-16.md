# Queued civil, mechanical and factory design work — 16 October 2026

All **63 allocated packages received executed preliminary investigations** in this
continuation. The [review packet](queued-systems/index.html) contains **68 distinct
investigations and 2,178 retained candidate/reference records**, including failures.
Six native geometry checks passed. These are bounded engineering studies; complete
manufacturable railway designs have not been established. Mandatory acceptance and
actual production/inspection records remain open.

| Workstream | Packages | Executed work |
|---|---:|---|
| Mechanical | 34 | 25 distinct research submodels, 694 unique finite variants; source-product audits, preliminary manufacturing definitions and cut/drill schedules |
| Civil, station and site | 18 | 86 bounded alternatives plus selected beam reassessment; drainage, canopies, platforms, approaches, pier/bearing/jack demands, factory structures and mould/strongback geometry |
| Factory, energy, safety and assurance | 7 | Electrical/air/fluid demands, British equipment cases, hook/headroom feedback, eight finite production calendars, output resource bounds and commissioning requirements |
| Basis, route and integration | 3 | 18 provisional six-car load cases; 864 inherited beam geometries reassessed against their response envelope; seven platform-length studies; actual assembly graph and 12 interface audits |
| Connection tooling | 1 | 376 feedback candidates, two retained local alternatives and regenerated native fixture checks |

Counts identify local models and retained records, not the number of completed
components. Reused investigation families are counted once. Fixed-reference
coverage/demand calculations count as one record. Full component physics, process
qualification and accepted interface designs remain necessary beyond these models.

## Coupled civil feedback

The previous 96-strand proposals were selected under the retained LM3 three-car,
12-axle trace. The separate Baghdad planning basis specifies six cars, 111 m and
24 axles. Its supplier axle pattern is still absent. The new sensitivity cases
therefore state assumed equal-length/equal-mass cars, two bogies/car, a 3.5 m
bogie-centre inset, 2 m wheelbase, longitudinal car CG offsets of −0.5/0/+0.5 m,
and axle multipliers of 1/1.25. Mass cases are 258/276/384 t. Force and first-moment
equilibrium are checked explicitly. No assumed pattern becomes an approved load.

Under the larger provisional envelope the old proposals develop sampled minimum
service compression of **−9.357 and −8.369 MPa**. They are retained as failed
planning screens. New selection across the same 864 geometries yields:

| Candidate | Geometry / lift position | Sampled service minimum | Initial bed force | Known hook equivalent |
|---|---|---:|---:|---:|
| `civil-74d3ee021424` | 1.4 m depth, 0.30 m stems, 112 strands, 75% lower strands, lift fraction 0.22 | +0.0568 MPa | 17.248 MN | 119.607 t |
| `civil-8afcf9832578` | Same section/strands; lift fraction 0.20 | +0.0568 MPa | 17.248 MN | 119.607 t |

The positive minimum is a small sampled numerical result, **not an accepted
structural reserve**. Maximum sampled compression demand is 22.663 MPa, with no
accepted material limit. The 125 t hook value remains a planning ceiling;
complete rig mass and an offered crane rating have not been established.
Shear, end zones, reinforcement, losses, deflection, fatigue, dynamics and
complete load-path qualification remain open.

The governing provisional live support reaction, **746.670 kN per beam end**,
now propagates to pier, cap, bearing and replacement-jack demand studies. Extra
permanent actions and accepted loading remain unresolved. The new stressing
demand propagates into return-rail sensitivities and a 112-hole head. At 60 mm
strand pitch, adjacent 90 mm jack envelopes clash; a four-tier axial arrangement
is a geometry proposal only. Its 154 kN seats and 17.248 MN total return path
still require structural design and qualification.

A 6 mm mould skin over 750 mm supports fails the wet-concrete deflection screen.
A 10 mm skin over 300 mm supports gives approximately 0.207 mm in the declared
strip model; welds, plate action, material resistance and demouldability remain
unqualified. The bearing-maintenance model physically raises the proposed
pedestals 280 mm to provide a 300 mm maintenance gap. The resulting rail-datum
change is an unresolved route interface, not a free clearance improvement.

The LM3 catalogue platforms are 55.5–59.5 m long. The six-car length study selects
a **116 m provisional platform** against a 111 m train plus two 2 m research
allowances. Site fit, egress, access and actual platform modules remain open.
The original three-car catalogue and its baseline geometry are unchanged.

## Mechanical proposals and manufacturing details

Known conflicts now fail their actual source-compatibility checks:

| Interface | Existing conflict | Explicit research branch |
|---|---|---|
| Front glazing carrier | 1,780 mm reference height versus 2,010 mm CAD carrier | 2,100 mm carrier envelope; source adoption and detailed joins open |
| Side glazing | 1,650 mm reference frame width versus 2,900/3,600 mm panes | 3,750 mm frame envelope and preliminary cut/seal/drain definitions |
| Bogie | 3,500 mm CAD frame versus 3,400 mm reference envelope | Compact frame branch; full running-dynamics/load/supplier validation open |
| Battery tray | Four 1,450 × 250 × 370 mm modules exceed a 5,400 × 320 mm tray | 5,900 × 400 mm tray branch; retention, isolation, thermal/fire qualification open |
| Gangway/services | Zero source car-end gap cannot accommodate articulation | 1.8 m proposed gaps, 53.1 m three-car train, revised centres and service routing |
| Chassis | Local stiffness alternatives exceed the existing 260 mm sill height | A 750 mm-deep, 25 mm-wall proposal passes only its local EI diagnostic |

The chassis branch adds about 14.464 t of conservatively included member mass per
car and models 49.714 t total car load. Its 10.33 mm research deflection does not
justify adoption: the source envelope fails, and mass, floor, bogie, clearance,
traction and civil demands would need a further coordinated architecture revision.
It cannot inherit the current six-car mass assumptions.

Gangway motion uses a continuous conservative bound across signed yaw/pitch/roll
ranges. The proposed service loop includes the actual 1.8 m straight gap, bend
geometry and a 0.683 m motion bound; the first local passing route has about
2.920 m developed length. Full collision, fatigue, cable/hose specifications and
supplier travel acceptance remain open. Source-changing alternatives are
`proposed_candidate_ids`, never source-compatible selected configurations.

The [mechanical report](queued-systems/mechanical/report.json) links actual product
and PDR audits, preliminary manufacturing definitions, lamp plate hole drawings,
service-rail drill schedules and glazing cut/drain details. Those drafts do not
populate issued production artifacts or claim measured process capability.

## British equipment and factory cases

Existing 14 factory equipment cases remain available. Four additional utility
cases retain manufacturer sources, origin distinctions and configuration questions:

| Supplier / model | Published basis used | Remaining configuration evidence |
|---|---|---|
| [Avelair evo 11 / Integra](https://avelair.co.uk/wp-content/uploads/2023/01/Avelair-11_15kw-datasheet.pdf) | Manufacturer states UK design/manufacture; 87 m³/h at 10 bar, 11 kW motor | Delivered dry flow, connected input, pressure losses, Baghdad ambient derating, offered origin and service |
| [Bambi VTS200D](https://bambi-air.co.uk/product/vts200d/) | 126 L/min at 8 bar and maximum 50% duty; [UK manufacture statement](https://bambi-air.co.uk/about-us/our-usps/) | One/two duty units fail the continuous CMM demand after allowances; three duty plus one standby is only a demand hypothesis |
| [AirBench FN126784](https://www.airbench.com/products/airbench-downdraught-benches/airbench-fn/) | 1.27 × 0.675 × 0.84 m bench, 50 kg standard surface load; manufacturer states UK assembly | Dust/fume duty, capture, filter/fire strategy and exact component origin; cannot support a 500 kg fixture |
| [Bowers distribution transformers](https://www.bowerselec.co.uk/transformers/distribution-transformers/) | Published 315–3,150 kVA stock range, standard 11 kV/415 V | Utility voltage/fault duty, exact factory/origin, ambient losses, protection, commissioning and offered configuration |

UK manufacture has priority; UK assembly and unconfirmed offered origin remain
separate. No supplier has been contacted, qualified or contracted through this
work. Published models establish investigation inputs, not a purchase selection.

The electrical hypotheses produce 445/574/702 kVA peaks with candidate
630/800/1,000 kVA transformers. Only 59.13 kVA of connected demand is tied to
published equipment values; substantial allowances remain unaccepted. Air,
cooling, extraction and firewater studies retain their actual scope limits.
Finite schedules preserve maintenance and process hold points. Aggregate output
bounds for the 54-beams/day target require at least 134 beds and more than two
cranes; these necessary bounds do not constitute a feasible commissioned factory.

## Actual requirements still preventing completion

The audit reads source records rather than assuming generated files are approvals:

| Evidence | Actual current state |
|---|---|
| Vehicle product partition | 120 rows = 62 local production + 58 supplier/configuration products |
| Required production artifacts | **472 missing or unissued** |
| First-article characteristics | **416 planned; zero actual result records** |
| Vehicle/station factory drawing definitions | **47 definitions; zero issued drawing references** |
| Baghdad deployment qualification | Ten missing controlled input groups retained in the audit |

Every package retains its original mandatory gates, source IDs, dependencies and
owner. The [production requests](queued-systems/manufacturing/production-artifact-requests.csv),
[inspection register](queued-systems/manufacturing/inspection-execution-register.csv)
and [58 supplier configuration requests](queued-systems/manufacturing/supplier-configuration-requests.csv)
give concrete next records. Supplier requests remain unsent. Populated approval
names and matching bytes alone would not authenticate an engineering authority.

Further closure requires controlled loads/material limits/site and ground records,
accepted configuration changes, complete discipline models and interfaces,
issued production information, physical first articles/tests and competent design
review. These cannot be replaced by repeating unchanged searches. No package is
marked engineering-complete or released for manufacture.

## Reproduction and verification

```sh
./osr design campaign queue --output build/queued-design/new-run --native
./osr design campaign verify-queue --output build/queued-design/new-run
./osr design campaign verify-queue-snapshot \
  --destination docs/design-engine/queued-systems
```

The completed local run is `build/queued-design/final-native-2`. The published
snapshot binds its exact files and source state. Six native checks cover the
proposed mould/strongback assembly, bearing-maintenance geometry, two connection
fixtures and two 112-strand beam alternatives. FCStd and STEP were reopened with
part identity, bounds and volume checks. Only the tooling steel subset receives
an interference check; beam strand/concrete overlap is intentional. Geometry
checks do not prove structural resistance or process qualification.

Publication retains FCStd and compact input/result files. Full STEP and native
execution logs remain in the sealed local run. Verification checks integrity,
source applicability and receipt semantics; it does not recompute the studies.
Earlier immutable snapshots remain historical evidence, with their original load
bases and unresolved gates. There is no unbounded/background agent loop.

Verification also covers exact package IDs, removed gates, stale sources, artifact
tampering, incomplete native reopen claims, force/CG equilibrium and disjoint
source-compatible selections/source-changing proposals. The wider factory/design
regression suite passed before the final selection classification correction;
the affected queue and mechanical tests were rerun after it. Desktop (1,440 px)
and mobile (390 px) review checks cover all 108 local links and page overflow.
