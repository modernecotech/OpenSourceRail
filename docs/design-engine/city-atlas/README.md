# City railway maps and calculated studies

[Open the city Workbench](../../workbench/current/index.html?outlineCity=samawah) to inspect a calculated network. The atlas covers all **266 cities and 1,565 lines**, using each city's exact selected outline, operational stops, service calculations and cost ledger. A new calculation replaces the map and its result tables together. An old response cannot replace a more recently selected city.

The map provides:

- Individually selectable lines, stations and platform/access markers, with pan, zoom, fit, north and a distance scale.
- Source-checked geographic context, attribution and switchable layers; original/revised alignments remain distinguishable.
- Per-line demand assumptions, usable/offered capacity, headway, journey/cycle time, active/reserve fleet and train-km.
- Actual calculated section times, braking/launch requirements, mechanical traction work and nominal auxiliary loads. Mechanical work is labelled separately from delivered electrical energy.
- Joined operational stops, their original access markers, platform envelopes and connector lengths. Accessible walking routes and surveyed clearances remain to be verified.
- Civil quantities, project resources, the complete fourteen-scope ledger, installed capital and 30-year whole-life cost cases.
- A station-to-station journey inspector using calculated leg times and explicit interchange references. Waiting, walking, transfer overhead and symmetric return travel are declared planning assumptions; it is not a protected timetable.
- A fare scenario with explicitly entered annual paid trips and average fare. Discounted fare receipts can be compared with the calculated whole-life costs. Peak per-line demand is never silently converted to annual paying passengers. Debt, tax, financing dates and wider benefits require separate inputs.
- Calculation, configuration, selection and source identities, known failures, evidence gaps and downloadable records.

## Calculations first, maps second

The presentation compiler verifies the complete upstream city publication, then replays each selected geometry, service and cost identity. It refuses mismatched inputs. The maps inherit the calculation's declared assumptions and uncertainty; they do not inherit physical qualification from a different train or earlier railway architecture. No original route file or selected physical railway is changed by generating the atlas.

Original, anchor-preserving straighter alignments and rounded square-ring alternatives remain available through the existing city calculation controls. Close stop markers retain separately priced access paths instead of creating arbitrarily long platforms. Geometry alone does not establish lower noise or route clearance.

Production and civil planning retain two shifts. Operating hours, headways and fleet requirements come from the scenario; extended operation can use three shifts. Surveyed demand/OD, available propulsion and braking maps, adverse thermal duty, detailed structures, actual accessible paths and independent engineering review remain separate evidence requirements.

The atlas's [manifest](manifest.json) and [city index](summary.json) bind the compressed per-city dossiers to the existing calculated publication. The UI has a separate asset receipt so a presentation change need not rerun unchanged engineering calculations. Local completed studies use the same renderer after their immutable artifacts have been verified. Incomplete, failed, stale or changed studies cannot replace the displayed result.

```sh
python -m engineering.outline.city_atlas compile docs/design-engine/city-atlas
python -m engineering.outline.city_atlas verify docs/design-engine/city-atlas
./osr workbench
```

Compilation resumes completed city packets under the same source request. `--maximum-cities N` limits one invocation while retaining the remaining frontier. An explicit `--city slug` defines a separate subset. A source change requires a fresh output directory. No native structural, electromagnetic, CAD or hardware acceptance tests are executed by this presentation compiler.

## Verification

The publication covers 266 city dossiers, 1,565 lines and 13,580 operational station complexes. The independent read-only audit reconciled route lengths, fleet, train-km, all fourteen cost scopes, original markers, platform/access geometry and geographic source hashes, with zero failures. It used 35.4 CPU seconds and 83.4 MiB peak memory under 90-second CPU and 512 MiB address-space limits. Source integrity was checked by hashes; this was not an operating-system source-write sandbox.

```sh
python -m pytest -q tests/test_city_atlas.py tests/test_city_atlas_api.py engineering/development_baseline/tests/test_readme_context.py
node tools/automation/tests/test-city-journeys.mjs
node tools/automation/tests/verify-city-atlas.mjs
```

The browser check exercises Baghdad and Samawah, changed demand and alignment, replaced study identities, map controls, fare calculations, rapid selection and mobile width. The standalone published-data path also checks geographic hashes and rejects altered city bytes. Runtime logs and screenshots remain in ignored `build/city-atlas-browser`; the versioned manifest identifies the reproducible city data. These checks verify software/data consistency, not physical railway performance.

## Scope beyond the map

The current planning workspace remains the route/stop/service/OD proposal editor. From a completed local study, **Edit this outline and recalculate** binds edits to that study's exact base. Complete result, summary, geometry, planning, execution, delivery programme and disabled business-system drafts remain downloadable.

Day-type operating timetables, surveyed OD assignment and congestion/denied-boarding models, debt-service finance and actual simulation playback require their own current candidate-specific models. This atlas supplies the calculated network context for those extensions; an empty OD table is not zero demand, and a calculated journey is not measured train motion.

[Project introduction](../../../README.md) · [Calculation methods](../outline-completion/README.md) · [Planning editor](../../workbench/planning/README.md)
