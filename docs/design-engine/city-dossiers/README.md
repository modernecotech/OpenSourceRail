# City railway design dossiers

[Browse all cities](../../../cities/catalogue/README.md) · [Baghdad](../../../cities/catalogue/west-asia/Iraq/Baghdad/README.md) · [Samawah](../../../cities/catalogue/west-asia/Iraq/Samawah/README.md) · [Project introduction](../../../README.md)

Every city has a readable design dossier at its original city README address. The page includes a visible geographic network map, current line/station/service/fleet tables, energy accounting, civil and depot quantities, manufacturing and workforce cases, capital and whole-life budgets, explicit passenger/funding sensitivities, site requirements and downloads. National briefs aggregate standalone city outlines without assuming shared-factory savings.

The interactive [Workbench atlas](../../workbench/current/index.html?outlineCity=baghdad) remains available for map inspection and recalculation. A new local calculation carries its own identities; a city page describes its published calculated outline until regenerated.

## Data and scope

The dossiers consume the authenticated [city atlas](../city-atlas/README.md) and [complete calculated outlines](../outline-completion/README.md). The selected route, operational platform groups, original access markers, explicit interchange references, service, fleet, mass allowances and cost ledger belong to the same candidate configuration. A city research configuration can include onboard traction with its own added mass and cost; it does not change the selected passive reference vehicle.

Maps use source-checked geographic context, current selected coordinates and operational stations. A local geographic projection, rounded display coordinates and background simplification support legible maps; GIS exports preserve source coordinates. Collision-limited labels use line/station reference numbers rather than inventing official station names. Depot and energy requirements without locations have null GIS geometry and explicit planning status. Geographic context is not surveyed clearance or land availability.

Service calculations are conditional outline results. Mechanical traction work, nominal auxiliaries and priced supply-efficiency scenarios are distinguished from physically supported total grid demand. Complete installed equipment, actual propulsion/thermal/braking maps, detailed civil interfaces and protected operating timetables remain separate evidence work.

## Prices, resources and finance

Installed capital and thirty-year whole-life low/base/high cases come from the unchanged fourteen-scope ledger. Annual operating provision includes the source annual electricity, operations, maintenance, recovery and reliability accounts; scheduled renewal and disposal capital remain separate. The cases are sensitivity assumptions, not statistical confidence intervals or firm bids.

Factory and civil production use two eight-hour shifts with declared utilisation. Operations retain their service-hour and shift hypotheses. Covered posts, distinct shift positions, productive capacity, paid hours and paid FTE are separate measures. The existing cost already includes payroll/relief and factory capital; displaying workforce does not add those costs again. The civil workforce envelope uses declared labour-budget fractions and a planning delivery window. It is an aggregate resource hypothesis, not a detailed site schedule or an approved employment roster.

The calculated operating posts cover control room and access sites. They are not the whole operating organisation: vehicle/civil/power maintenance, cleaning, security/emergencies, management, HR/procurement, training and independent assurance retain explicit function/competence/authority requirements and unknown staffing where not sized. Unknown allocation is not zero cost or zero people.

The versioned [planning policy](../../../engineering/city_reports/planning-policy.json) makes otherwise missing outline assumptions executable. Illustrative paid-trip estimates combine peak-section flow with a daily profile, counter-direction loading, average section/peak loading, average trip length, transfers, collection and demand multipliers. They are not surveyed ridership forecasts. Fare and cost-covering-fare cases preserve adverse results. The separate debt overlay declares loan share, real interest, term and capitalised grace; it neither establishes imported content nor adds finance charges to canonical engineering cost. A real financing case requires local fares, dated capital draws, actual revenue, tax and funding terms.

## Files and source ownership

Each city contains `engineering/outline/summary.json`, a static network SVG, line/station/cost/workforce/finance/make-buy CSVs, GIS layers, disabled delivery/business drafts and an output manifest. Each CSV identifies its atlas packet and outline evaluation. The [publication manifest](manifest.json) binds all city front doors, reports, country briefs, input publications and producer sources.

Physical evidence remains in the unchanged geographic hold summaries under `engineering/current/summary.json`. The `/3` city presentation receipt explicitly owns the enhanced front door and links to its separate outline dossier. The geographic evaluator and register retain their source epoch; presentation changes do not invalidate unchanged cost calculations or relabel them as physical acceptance. The current coordinated publisher uses this presentation owner and verifier. The low-level geographic producer remains usable on its own for hold-only fixtures.

```sh
python -m engineering.city_reports.publication publish
python -m engineering.city_reports.publication verify
python tools/automation/generate-city-geography-index.py
```

Publication checks the complete upstream catalogue before rendering. A source/payload-consistent previous publication is reused. The single-writer lock is in ignored `build/`; maps are bounded to authenticated geographic input packets (64 MiB maximum decompressed context). Failed/interrupted generation is preserved as a failed invocation and does not become a completed publication. No CAD, structural, motor or hardware test is executed by the dossier renderer.

## Verification

```sh
python -m pytest -q tests/test_city_dossier_analysis.py tests/test_city_dossier_maps.py tests/test_city_report_publication.py
python tools/automation/generate-city-geography-index.py --check
python tools/automation/check-readmes.py
```

The analysis tests independently control demand, annuity/debt arithmetic, workforce/source bindings and cost reconciliation. Map controls cover projection, scale, preserved selected geometry, civil segment clipping, source identities and unlocated requirements. Publication tests cover ownership, current-page content, map/CSV source identity, candidate separation, catalogue link resolution and tampered payload rejection. These verify calculated-data consistency; physical release requires the independent engineering workflow.

## Source comparison

The restoration was checked against the actual [v0.4 city dossiers](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue), including the [Samawah native/animated study](https://github.com/modernecotech/OpenSourceRail/blob/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Samawah/engineering/digital-twin/README.md). Those files retain their own battery, formation, energy, costing and evidence assumptions. They provide a feature/content reference and source history; their numbers are not inputs to the current dossiers.
