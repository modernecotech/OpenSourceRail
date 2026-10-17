# Baghdad engineering twin development and specification coverage

The coordinated design campaign joins the complete controlled inventory to executable mechanical, civil, software and factory studies. It provides a searchable specification and variant browser, source-bound model packets, actual failure-directed repairs, and explicit requests for unfinished detail. The deliverable is a federated engineering design twin. A complete manufacturable railway specification and a physically correlated operating twin remain open.

Open the [component and variant browser](baghdad-digital-twin-2026-10-17/index.html). The [execution summary](baghdad-digital-twin-2026-10-17/summary.json), [component register](baghdad-digital-twin-2026-10-17/components.csv), [source and output manifest](baghdad-digital-twin-2026-10-17/manifest.json), and [outstanding specification and evidence requests](baghdad-digital-twin-2026-10-17/open-requests.json.gz) accompany it. The existing [reference geometry and electrical/thermal viewer](../../engineering/models/digital-twins/best-practice/index.html) remains a separate, explicitly provisional configuration.

## Actual team and execution

Four AI agents developed the implementation together, with completed roles rotating into independent criticism. Their reviews found and corrected weakened load-context acceptance, inconsistent software clocks, dangling specification relationships, overwritten source revisions, missing observation endpoint timing, and lost provenance. The retained command executes three deterministic numerical adapters concurrently; it does not launch fresh LLM conversations or conduct autonomous internet research.

| Role | Delivered work | Independent challenge |
| --- | --- | --- |
| Configuration integrator | Complete inventory joins, source and revision control, parent coupling, observation replay, component browser and CLI | Civil agent checked coupling; mechanical agent challenged graph, software and observation handling |
| Mechanical designer | Connected-frame repairs, open-I and closed-box hypotheses, plates, fasteners, welds, splices and fixtures | Software/factory agent checked load-context integrity, mass and reaction conservation |
| Civil designer | Four vehicle/span contexts, beam/cage/support alternatives, individual strand locations and both support envelopes | Software/factory agent checked independent beam and footing equations |
| Software and manufacturing designer | Controller replay alternatives, precharge and thermal studies, equipment/process interfaces and supplier evidence requests | Mechanical agent exercised stale-clock, backwards-time and provenance counterexamples |

## Retained scope

| Measure | Retained scope |
| --- | ---: |
| Work packages | 63 |
| Source-qualified controlled items | 345 |
| Terminal source attributes | 20,799 |
| Existing reference model instances | 414 |
| Existing reference model interfaces | 545 |
| New discipline systems | 28 |
| Evaluated discipline alternatives | 80 |
| Part records across alternative configurations | 6,863 |
| Mechanical revision to civil-parent sensitivity cases | 8 |
| Civil evaluations in those sensitivity cases | 24 |

Source attributes include stored requirements and metadata as well as engineering values. All 345 controlled identities resolve to actual source records, including the scalar family identifier in the trainset manifest. Part counts cover competing configurations and must not be summed into a single train or factory BOM. Inventory coverage and detailed design completion are tracked separately; completed full specifications remain zero.

Each controlled item retains its source records, JSON pointers, source hash, candidate equipment default where present, actual production-data requirements, and required detail sections. Package records preserve the original completion conditions, drawings, inspection characteristics, supplier requests and acceptance gates. Every generated variant has a configuration hash; part instances are uniquely named across systems and alternatives, while retaining the producer's local labels.

## Mechanical and civil iterations

Mechanical work contains 14 alternatives across the independent LM3 and six-car hypotheses. Connected-frame variants retain plate/tube geometry and mass, bolt/nut/washer instances, load-path weld groups, proposed splices, fixture requirements, manufacturing sequence and inspection needs. Failure-directed descendants retain actual parent identities, repair reasons and newly introduced failures. Separate open-I and closed-box models compare longitudinal concepts within a declared elastic beam approximation; transverse load paths, stability, fatigue and crashworthiness remain unresolved.

Civil work contains 36 alternatives across LM3/six-car and 20/25 m contexts. It recalculates geometry, selfweight, moving-load demands, reinforcement-fit screens, prestress response, bearings and foundation pressure. Individual strands have locations; reinforcement groups retain their spacing and quantity rules. Both outer support assemblies retain their own seat, bearing, anchor, cap, column and footing definitions. Thirty alternatives retain known failed checks and six pass the available local screens while remaining conditional on missing evidence. Full foundation reinforcement, temporary works and supplier anchorage/lifting configurations remain open.

The integration study transfers the steel mass of two actual mechanical generations into their matching 20/25 m civil contexts. Each case recomputes civil demand and performs up to three failure-directed evaluations. This is an explicit gross-added-mass sensitivity: removed structure, unmodelled accessories and actual CG redistribution remain unknown. Failed mechanical proposals remain diagnostic and are never adopted as accepted loading. These calculations demonstrate one-way static transfer consistency; complete train–structure dynamics remain open.

The original 414-instance reference model preserves its own configuration, mass allocation, interfaces, physical-contact and dynamic-passage gates. Its 1,157 unresolved reference allocations remain visible. The new frame and civil hypotheses do not silently replace it.

## Software and factory studies

Software alternatives share the same adverse fixtures. The guarded replay binds elapsed time to a controller-owned cycle epoch and checks stale, future, reordered and backwards-receipt observations. Faults latch into lockout. The output represents a closure request in a simulator; target-controller implementation, hardware interlocks, transport qualification and operational acceptance remain open.

The lane also evaluates RC precharge tolerance corners, nominal/degraded HVAC performance, and compressed-air capacity alternatives. Rejected policies and undersized options remain in the packet. Factory equipment records preserve published envelopes and the distinction between British manufacture, UK supply/integration and unconfirmed offered origin. Configured machine drawings, utility/foundation actions, tooling trials, supplier internal BOMs, production capacity and actual commissioning evidence remain requests. No supplier has been contacted.

## Observations and physical correlation

The [observation contract](baghdad-digital-twin-2026-10-17/telemetry-contract.json) defines two initial read-only channels: nominal HVAC endpoint temperature and static surrogate track gauge. It binds asset identity, configuration hash, units, operating scenario, UTC timestamp, sensor identity, source digest and calibration reference. Time-specific predictions additionally require the exact model endpoint time. Incompatible units/revisions, invalid numbers, duplicate observations and backwards sensor chronology are rejected.

Replay retains the original observation provenance alongside predicted values, residuals, bias and RMSE. Its residual thresholds are declared illustrative study assumptions. Sensor names, calibration references and field-source digests remain unverified claims until authenticated independently. Matching synthetic observations cannot establish physical validation. Asset serial-number association, synchronized installed measurements, accepted uncertainty limits and independent hold-out validation are outstanding requirements.

## Reproduce and inspect

```sh
./osr design twin plan
./osr design twin run --output build/design-twin/new-campaign --concurrency 3
./osr design twin verify --output build/design-twin/new-campaign --replay
./osr design twin verify --output docs/design-engine/baghdad-digital-twin-2026-10-17 --replay
```

Use a fresh output directory. Source/input bytes are captured before execution and checked afterwards, numerical caches reset between campaigns, and executable-code changes require a new Python process. Exact replay requires the recorded Python/NumPy environment. Historical integrity checking uses `--historical` and grants no current-source applicability. The compressed JSON files contain complete retained packets and can be read with Python's `gzip.open` and `json.load`.

Observation replay writes a separate result file and does not change the sealed design packet:

```sh
./osr design twin observe \
  --packet docs/design-engine/baghdad-digital-twin-2026-10-17 \
  --observations /path/to/revision-bound-observations.json \
  --output build/design-twin/observation-review.json
```

## What remains before complete specifications

The executable models expose unfinished engineering rather than generating approvals. Missing detail includes configuration-specific fastener lengths/preloads, qualified weld and fatigue details, complete reinforcement/anchorage and temporary works, issued dimensional tolerances, purchased equipment internals and controlled software/hardware builds. The register assigns the actual production artifacts, inspection characteristics and supplier configurations to their packages; each missing value needs its own controlled design or supplier evidence.

Accepted six-car actions, Baghdad survey/geotechnical/utility records, adopted material/process limits and configured equipment data remain the controlling external inputs. Issued manufacturing drawings, representative production trials, measurements and independent project acceptance remain the route to manufacture. The development continues provisionally under the user's earlier instruction to keep these acceptance gates open.

## Verification

The focused and existing regression suite passed **146 tests**, including separately authored mechanical, software and integration counterexamples. A fresh three-worker execution and full numerical replay passed source, exact-member and output-hash verification. Browser checks exercised all 381 displayed records, source/component coverage, civil and mechanical filtering, parent-coupling views, empty searches and detailed part/revision rendering without page errors.

A synthetic two-channel observation batch also passed the CLI intake and retained its full provenance and residuals. Its physical-validation and calibration-authentication fields remained false. The [verification receipt](baghdad-twin-verification-2026-10-17.json) binds these checks to the retained manifest.
