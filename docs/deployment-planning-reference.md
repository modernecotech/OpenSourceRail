# Deployment Planning Reference

This page defines the common interpretation of every generated OpenSourceRail
city README and national brief. Location folders contain only local inputs,
calculated results, exceptions and evidence links. Shared assumptions belong
here or in the linked machine-readable templates—not in hundreds of generated
copies.

## Generation And Review Boundary

The city catalogue is deterministic:

```text
city catalogue + OSM/raster evidence + shared templates
  → routed network + stations + service + fleet
  → energy, civil, CAPEX and finance calculations
  → engineering and simulation evidence
  → concise city README and national aggregation
```

Generated READMEs are indexes and decision summaries. The authoritative local
inputs and results remain `design.toml`, the expanded scenario TOML, and the
JSON/GeoJSON evidence inside each city folder. Git records changes to inputs,
generators and outputs together. Do not hand-edit a generated city or country
README; change its source or a shared template and regenerate it.

## Network And Station Planning

`osr_geo` rasterises source-locked OpenStreetMap roads, buildings, water,
protected areas and demand anchors onto the planning grid. `osr-design` uses a
demand-rewarded least-cost route, places stations against the demand surface,
and classifies each segment as at-grade, elevated or bridge. Tunnels are not in
the upstream catalogue.

The standard spacing policy is 1.6 km in central areas, 3 km in ordinary urban
areas, and up to 7 km on low-demand outer approaches. Cross-line platforms
inside the 600 m station-complex envelope are consolidated as one interchange.
Coverage, transfer reachability, civil mix and source hits are reported in each
city's `*.design-quality.yaml`; they are planning indicators rather than survey
acceptance.

## Service, Fleet And Capacity

The default service is GoA 4 battery-electric operation with line-specific
time windows and headways. Fleet sizing covers peak revenue service, planned
maintenance spares and cold reserve. Off-peak surplus performs terminal or
depot inspections without creating a second service-rotation fleet unless a
local schedule proves one is required.

Healthy trainsets may stable overnight at protected powered stations near their
first departure. Red defects, overdue heavy maintenance, isolation failures or
security failures return a set to the main depot. Station stabling requires
charging, CCTV, remote traction isolation, emergency access and an OCC-assigned
track slot.

Capacity uses the selected trainset family's AW2 planning capacity, the actual
generated timetable and a controlled practical load factor. The annual paid-trip
range is a capacity-use scenario, not a ridership forecast. Replace it with a
surveyed demand model before an investment decision.

## Energy Method

Each city calculation combines:

- trainset energy per car-km and the generated timetable;
- climate and non-revenue movement factors;
- opportunity charging at powered stations;
- station/depot PV and stationary LFP storage;
- a dedicated solar plant or equivalent PPA asset for the remaining annual
  traction-energy requirement; and
- residual grid import after those assets.

The generator checks every line's powered-stop gap, traversal energy, delivered
charge, protected onboard reserve and operating margin. These are feasibility
screens; grid connection, protection, harmonics, thermal, fire and local solar
yield studies remain deployment work.

## Civil And Cost Method

Civil geometry is generated from the parametric source and exported to IFC4.3
for Bonsai coordination. Checked quantities feed the generated
[`civil-cost-model.toml`](../lib/templates/civil-cost-model.toml), which is then
consumed by city CAPEX, finance, IFC properties and documentation. Current
design targets are 2.584 M USD/route-km at-grade, 9.748 M USD/route-km elevated
and 18 M USD/route-km for bridges. The retained 3/12/18 M benchmarks remain
visible for audit.

These figures are unquoted planning targets. Land, utilities, tax and duty,
site geotechnics, project risk, programme, independent checking and local
supplier rates must be added or validated before procurement. The complete
shared cost basis is in the [generated cost model](cost-model.md).

## Capital And Finance Method

City CAPEX includes civil works, stations, depots, rolling stock, residual train
control, charging interfaces, timetable-sized dedicated solar and EPC/project
services. The national trainset factory is excluded from cities and counted
once in each national brief, sized to the largest single-city fleet programme.

The procurement-origin model separates imported value—the minimum foreign
currency or international-capital requirement—from locally supplied labour,
materials, fabrication and services that can use domestic funding. Country
finance parameters define construction period, debt rates, tenor and the local
bond/equity split.

The foreign-turnkey comparison is an editable like-for-like sensitivity, not a
vendor quotation. Both cases use the same network, fleet, service, energy scope
and financing schedule. Replace the multiplier, external share and all funding
terms with scope-normalised bids and signed lender terms before approval.

OPEX, revenue, NPV, IRR and DSCR outputs are planning screens. Capacity-use
scenarios are not demand forecasts, and no grant, tax treatment, land-value
capture or lender commitment exists unless explicit controlled evidence says
otherwise.

## QA, Maintenance And Assurance

Shared construction QA gates, manufacturing travellers and maintenance
intervals are generated from the controlled templates. City-specific asset
counts and schedules are materialised in the local operations bundle. The
common system covers civil works, trackform, stations, rolling stock, passenger
systems, energy, signalling/comms, depots and integrated trial running.

Generated evidence proves internal consistency and reproducibility—not railway
certification. Survey, geotechnical release, structural design, fire/egress,
product acceptance, calibrated operations modelling, independent safety
assessment and authority approval remain deployment responsibilities.

## Local Evidence Contract

Each city README links the current status of these local artifacts:

| Artifact | Purpose |
|---|---|
| `design.toml` | Authoritative generated network, fleet and CAPEX design |
| `<slug>.toml` | Expanded simulator scenario |
| `<slug>.design-quality.yaml` | Coverage, routing and civil-quality gates |
| `engineering/finance/summary.json` | Reconciled CAPEX, OPEX and finance cases |
| `engineering/simulation/validation-summary.json` | Nominal and degraded simulation acceptance |
| `engineering/gis/summary.json` | GIS package provenance and layer counts |
| `engineering/sumo/summary.json` | Executed timetable screening |
| `engineering/energy/summary.json` | Grid, charging and solar screening |
| `operations/` | Asset, QA, manufacturing and maintenance evidence |

The README generator verifies source hashes and passing status before publishing
these evidence links. Repository health also regenerates city and country pages
and rejects drift.

## Regeneration

```bash
# One city
tools/automation/regenerate-city.sh samawah

# Complete catalogue, using current caches
tools/automation/regenerate-all.sh

# Documentation, links and generated drift
python3 tools/automation/check-readmes.py
python3 tools/automation/check-markdown-links.py
python3 tools/automation/repo-health.py --quiet
```

Changes to common assumptions should normally touch one template or this page,
then regenerate affected outputs. Location folders should change only when
their local input, calculated result, evidence or explicit exception changes.
