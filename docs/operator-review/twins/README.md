# Train, platform and viaduct inspection

For current Airport quantities, use the [corrected budgetary enquiry](../../../cities/Baghdad/engineering/simulation/audited-enquiry.zip). The [prototype twin](../../../cities/Baghdad/engineering/prototype/review.html) and [first-article drawings](../../../cities/Baghdad/engineering/prototype/README.md) describe the earlier 12 km study. Check the geometry and loading against the revised issue before pricing a part. The straight-station views below retain their own reference designs.

Open the station viewer locally, or serve the repository root with `python3 -m http.server 8000` and visit `/docs/operator-review/twins/`. Choose an assembly, orbit with the mouse or arrow keys and select a part to read its dimensions in metres. Each model also opens in an IFC4 viewer. The IFC coordinates use the island midpoint as the origin, track direction as x and rail-head elevation as z. [Station viewer](index.html)

| Operator review | Core v0.7 powered-wheel study | Baghdad first programme |
|---|---|---|
| Formation and service | Six 17 m cars, 104.5 m coupled, 276 normal places | Six 17 m cars, 104.5 m coupled, 700 normal places |
| Boarding | Two 1.4 m doors per car on the island side, 12 total | Four 1.3 m doors on each side of each car, 48 total |
| Station | 125 × 8 m island, tracks 10.80 m apart | 125 × 8 m island, tracks 10.85 m apart |
| Supply | Six stowed roof-collector envelopes and overhead contact datum | Outboard protected conductor, four shoe sets allocated per train |
| Design scope | 30 km study, 12 stations and 51 trainsets | 148.2 km planning allowance, 64 stations and 242 trainsets |
| Interchange | [Core IFC4](core.ifc) | [Baghdad IFC4](baghdad.ifc) |

Review the core running gear for motor and brake access. Its wheels, hubs, disc annuli, axle shafts, box-member walls and bolsters come from the inherited vehicle geometry. The 60 bogie pieces per car yield 4,965.818 kg at the model density. The 24 motor, 24 brake-shoe and six stowed collector envelopes come from the powered prototype, placed on the joined train’s 17.5 m car pitch. Equipment envelopes carry no inferred installed mass. [Core bogie screenshot](core-bogie.png) · [Vehicle calculation](../../reference-v07/digital/vehicle/README.md)

At the Baghdad island, check the platform-side doors, the unused openings on the opposite side and the outboard supply. Use the controls view to review car-node ownership and the linked wiring schedule. Cabinet envelopes are location markers. The operator needs supplier access, isolation and fault-test evidence before accepting their installation. The station model represents a typical straight site. The independent 605.652 km metropolitan concept has its own alignment, cost and quantities. [Station screenshot](baghdad-station.png) · [Boarding screenshot](baghdad-boarding.png) · [Electrical interfaces](../../../cities/Baghdad/engineering/controls/README.md)

Choose **Frame quotation** in the Baghdad viewer to inspect the actual 128-piece OBJ of one braced body and its two bogie frames. Every piece retains its original stock identifier. The quantity for this quotation revision is 5,196.181 kg of cut stock per car. Connections, drives, wheelsets, suspension and fitout require further take-off. The mesh retains its own revision and evaluation. [Frame screenshot](baghdad-steel-frame.png) · [Stock quotation and checks](../../../cities/Baghdad/engineering/mechanical/vehicle/README.md)

## Quantities and delivery records

The two station models each show 28 running beams and 30 support positions in a 140 m display window. These are drawing-window quantities. The 30 km study carries 6,000 running beams. The 148.2 km first programme carries 29,640. The core 13-strand bare beam has a digital mass of 29.964382 t. Baghdad’s trial box section and pad interfaces have a separate design record. Beam solids show outer envelopes, so mass take-off must use the referenced section schedules. The deck, body panels, windows and controller markers use schematic sections. A 75 mm static gap and 10.25 m centred end margins require checking against measured vehicle and platform movement. Station access, pier caps, separate platform foundations and construction-stage stability remain open. [Core production schedule](../../reference-v07/digital/production/README.md) · [Baghdad trial sections](../../../cities/Baghdad/engineering/mechanical/civil/README.md)

The register records the physical candidate, evaluation, selection, design revision, source hashes, export hashes and occurrence counts. IFC objects carry stable design GUIDs derived from the physical candidate and named occurrence. The project property set contains the identities and source hashes. The manufacturing and construction records retain their respective quotation or planning purposes. Physical serials, installed mass and release evidence remain open. [Model register](model-register.json) · [Core manufacturing routes](../../reference-v07/manufacturing/routing.csv) · [Baghdad quotation interfaces](../../../cities/Baghdad/engineering/mechanical/README.md)

## Reproduce and check

From the repository root, use the project environment with IfcOpenShell 0.9.0.post1, then the repository Playwright installation and Chrome. `CHROME_PATH` can point to a different Chromium executable.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python docs/operator-review/twins/build_models.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python docs/operator-review/twins/build_models.py --check
node docs/operator-review/twins/capture.cjs
```

The check compares regenerated files, validates the IFC schema, reopens each design GUID and checks its placement, then tessellates every distinct represented solid with OpenCascade. The Chrome check exercises all six assembly views for each station, changes selected components, checks the engineering links and captures the separate frame quotation. The drawings and tests support digital review. Full swept geometry, as-installed measurements, accessibility trials and independent safety acceptance remain outstanding.
