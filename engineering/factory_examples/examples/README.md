# Baghdad mechanical, civil and factory development examples

Generated from versioned SI inputs and official supplier information checked on 16 October 2026. These are review models; all physical release gates remain open.

Open [the offline visual review](index.html), [the engineering report](report.json), [the equipment/RFQ register](equipment-rfq.csv), [utility gaps](utilities.json) or [process/inspection routes](process-routes.csv).

## What is built

The [second development iteration](development.md) adds three native models and full-span prestress alternatives, explicit bed-restraint stiffness/imperfection cases, fixture workholding and crane-runway interface demands. The original four models below remain baseline examples.

The fixture has a nominal model mass of 149.01 kg, a 500 kg payload hypothesis and a 1.5 load multiplier. Its six locators have independent kinematic rank. The payload-only elastic deflection bound is 0.742 mm against a provisional 1 mm review limit. This does not establish weld, pin, clamp, wall or anchor resistance.

[Fixture drawing](fixture/drawing.svg), [native FreeCAD](fixture/model.FCStd), [cut list/BOM](fixture-bom.csv), [stock cutting plan](fixture-cutting-plan.json). Datum plates are welded mounts with bored locator interfaces; locator retention, shims and clamps need detailed design. Inspect the assembled fixture by a separate survey: it does not fit the Axiom CMM.

The canonical pi section is 1.1990 m², centroid 0.7748 m above soffit and gross inertia 0.142999 m⁴. New solid end-diaphragm fill is a separate hypothesis with nonoverlapping solids, not a canonical accepted detail.

| Span | Bare mass | With hypothetical solid end diaphragms | Lifting demand incl 2 t rigging and 1.25 multiplier | Bare dead-load deflection |
| --- | ---: | ---: | ---: | ---: |
| 20 m | 59.95 t | 65.86 t | 84.83 t | 12.24 mm |
| 25 m | 74.94 t | 80.85 t | 103.56 t | 29.87 mm |

The bare-section Pi20 transfer hypothesis gives top-fibre stress -0.202 MPa with compression positive, so it predicts slight top tension. Concrete tensile/transfer limits are unknown. This needs a revised or qualified prestress/transfer design; a numerical stress result supplies no acceptance.

[Pi25 mould/bed drawing](pi25-mould-bed/drawing.svg) and [native FreeCAD](pi25-mould-bed/model.FCStd) show concrete, conceptual mould faces, side boxes, ties, strongback reservations and 40 tendon axes. These overlap across manufacturing states by design; this is not a finished mould or stressing-bed fabrication package.

The proposed 40-strand research scenario starts at 6.16 MN. Ideal pinned Euler screening of two 500 × 300 × 16 mm bed boxes gives demand/Euler = 2.48 over an unbraced 25 m, so that unsupported configuration fails even the ideal screen. The alternative 3 m brace assumption needs real brace/connection/foundation design. No railway live-load result or resistance acceptance is supplied.

## Factory examples

[Vehicle hall plan](vehicle-factory/plan.svg) and [native model](vehicle-factory/model.FCStd): 144 × 60 m; one canonical 135 × 6.5 m six-car assembly lane, component machining/welding, conditioned metrology and separated pilot composites reservations. Roof grid 12 × 30 m, 10 m concept columns and a 250 mm slab are coordination hypotheses. Roof-only gravity takeoff does not include wind, seismic or crane loads. Ground bearing capacity and foundation sizes remain unknown. Crane runways require separate supports/design. The two canonical 2 km test tracks require additional land and alignment.

[Pilot precast yard plan](precast-yard/plan.svg) and [native model](precast-yard/model.FCStd): 160 × 100 m with four casting positions, reinforcing/stressing, batching/washwater reservations, heavy transport routes and four storage positions. A complete concrete batching plant, rebar/strand preparation line, heavy trailers and laboratory remain unselected; the named mixer/grips do not supply those systems.

At 2 working days per full bed cycle, 85% availability and 95% accepted yield, four positions give 1.615 accepted beams/working day. The earlier 54/day programme target needs at least 134 positions at the same assumptions, before other bottlenecks. This pilot has no qualified production rate.

## Named equipment candidates

| Supplier/model | Origin basis | Specification source |
| --- | --- | --- |
| Brauer — H350/2BLC flanged-base positive-locking clamp | Designed/manufactured at Milton Keynes, England, supplier statement; offered unit confirmation pending | [Official source](https://www.brauer.co.uk/product/horizontal-positive-locking-clamps/) |
| Prosaw (UK supplier), BOMAR (Czech OEM) — Workline 510.350 DG manual bandsaw | Imported alternative via UK supplier; Czech OEM, no British-manufacture credit; offered unit origin certificate pending | [Official source](https://www.prosaw.co.uk/machine/bomar-workline-510350dg/) |
| Esprit Automation — Photon 5G, 3 x 1.5 m, 4 kW option | Britain manufacture published; offered configuration certificate pending | [Official source](https://espritautomation.com/photon-5g/) |
| Yamazaki Mazak — CV5-500 | Built in Worcester, Britain, explicitly published for CV5 family | [Official source](https://www.mazak.com/uk-en/products/cv5/) |
| Aberlink — Axiom 900, honeycomb table | British manufacture published; model-specific origin declaration pending | [Official source](https://www.aberlink.com/) |
| Oxford Welders — MULTIMIG 333 2Pulse Synergic wheeled power unit | Manufactured in York, Britain, supplier statement | [Official source](https://oxfordwelders.co.uk/pulse-mig-multimig-2pulse-synergic/) |
| Composite Integration — CIJECT 1, resin-specific variant to select | UK design/integration at Saltash; offered unit manufacturing origin to confirm | [Official source](https://www.composite-integration.co.uk/products/ciject-one-injection-machine/) |
| Airflow Group — Bespoke composite curing oven enquiry | UK manufactured ovens published, Sheffield; offered unit origin pending | [Official source](https://www.airflow-group.com/composite-curing-ovens) |
| Street Crane — ZX8 10 t variable-gauge trolley, bespoke bridge | UK hoist manufacture published; bridge fabrication and exact origin to confirm | [Official source](https://streetcrane.com/hoists/wire-rope-hoists/) |
| Rapid International — Planetary precast mixer; 1 m3 output enquiry | Northern Ireland, United Kingdom, design/manufacture published; prioritised UK alternative | [Official source](https://rapidinternational.com/planetary-concrete-mixer/) |
| Matravers Engineering — Bespoke OSR Pi20/Pi25 steel mould enquiry | British steel mould manufacture published; bespoke offer pending | [Official source](https://www.matravers.co.uk/) |
| CCL Precast — SLA 15 mm spring-loaded grip 604073 | CCL core prestress products UK manufactured, Ossett; exact offered grip origin to confirm | [Official source](https://www.cclprecast.com/about) |
| Street Crane — Configured 125 t open-winch crane enquiry | UK manufacturer family; offered hoist/bridge fabrication origin to confirm | [Official source](https://streetcrane.com/hoists/wire-rope-hoists/) |
| Tata Steel UK — Celsius hot-finished RHS, nominal 100 x 50 x 5 mm candidate | UK producer lead; offered size, mill and origin certificate to confirm | [Official source](https://www.tatasteeluk.com/en-US/construction/products/tube/structural-hollow-sections/celsius) |

Supplier dimensions and numerical fields are in [the versioned register](../data/equipment.json), with document/page pointers. Published dimensions, historical specifications and OSR reservations are separate. Machine solids are external envelope proxies, not manufacturer CAD. UK supply/integration does not prove British manufacture. Rapid's Northern Ireland manufacture is identified separately.

The laser's 4 kW output is not its electrical input: the historical 4 kW-option sheet lists 40.2–58.9 kVA. The Mazak's 18.5 kW figure is spindle output at 10% ED. Total site power remains unknown. Axiom plus CIJECT publish 700 L/min combined air demand at their respective conditions; reference-flow bases and diversity are unconfirmed, so no compressor rating is adopted. Baghdad heat, dust, process cooling, extraction, fire and metrology HVAC require design.

The 80 t crane screen fails for the developed Pi25 lifting scenario. A 125 t Street open-winch configuration is an enquiry within its published 80–250 t family, not a quoted catalogue model or accepted lifting design. The 10 t ZX8 is for component handling. Bridge span is distinct from trolley gauge.

Installed CAPEX is **unknown**. The £2,640 ex-VAT Oxford UK retail reference is dated and excludes an agreed Iraq package; it is not a factory estimate. No supplier has been contacted and no delivery, service, performance or origin has been accepted.

## Build and inspect

```sh
.venv/bin/python -m engineering.factory_examples.build --native
.venv/bin/python -m engineering.factory_examples.build --check
.venv/bin/python -m pytest engineering/analysis/tests/test_factory_examples.py -q
```

FCStd documents are retained in Git; neutral STEP exports are generated beside them and remain ignored under repository policy. Each native receipt records toolchain, exact input/exporter hashes, per-part volumes/bounds, file hashes and actual FCStd/STEP reopen checks. `--check` verifies tracked CAD and reproducible text; it verifies STEP hashes when local exports exist. Deleted STEP files can be regenerated with `--native`.

Follow the [staged plan](../../../docs/design-engine/mechanical-civil-factory-plan-2026-10-16.md). Next gates are supplier technical returns, site/ground design, detailed fabrication/structural checks, measured first articles and accepted factory trials; all remain open.
