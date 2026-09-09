# Station and depot overnight allocation

Plan: **32 trainsets at stations + 37 at depots = 69 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0121-0078-s012094 | 37 | 1,813.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0288-0520-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0349-0451-s002024 | station | forward | revenue | 1 |
| line-1 | line-1-0349-0451-s002024 | station | reverse | revenue | 1 |
| line-1 | line-1-0371-0112-s010141 | station | reverse | revenue | 2 |
| line-1 | line-1-0379-0373-s004059 | station | forward | revenue | 1 |
| line-1 | line-1-0379-0373-s004059 | station | reverse | revenue | 1 |
| line-1 | line-1-0391-0287-s006034 | station | forward | revenue | 1 |
| line-1 | line-1-0391-0287-s006034 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0196-s008078 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0196-s008078 | station | reverse | revenue | 1 |
| line-2 | line-2-0379-0373-s006263 | station | forward | revenue | 1 |
| line-2 | line-2-0379-0373-s006263 | station | reverse | revenue | 1 |
| line-2 | line-2-0431-0513-s009823 | station | reverse | revenue | 2 |
| line-2 | line-2-0468-0325-s003622 | station | forward | revenue | 1 |
| line-2 | line-2-0468-0325-s003622 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0266-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0121-0078-s012094 | station | reverse | revenue | 2 |
| line-3 | line-3-0249-0212-s008353 | station | forward | revenue | 1 |
| line-3 | line-3-0249-0212-s008353 | station | reverse | revenue | 1 |
| line-3 | line-3-0334-0349-s004611 | station | forward | revenue | 1 |
| line-3 | line-3-0334-0349-s004611 | station | reverse | revenue | 1 |
| line-3 | line-3-0379-0373-s003284 | station | forward | revenue | 1 |
| line-3 | line-3-0379-0373-s003284 | station | reverse | revenue | 1 |
| line-3 | line-3-0450-0397-s001604 | station | forward | revenue | 1 |
| line-3 | line-3-0450-0397-s001604 | station | reverse | revenue | 1 |
| line-3 | line-3-0506-0435-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0121-0078-s012094 | depot | — | revenue | 9 |
| line-1 | line-3-0121-0078-s012094 | depot | — | spare | 2 |
| line-1 | line-3-0121-0078-s012094 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0121-0078-s012094 | depot | — | revenue | 10 |
| line-2 | line-3-0121-0078-s012094 | depot | — | spare | 1 |
| line-2 | line-3-0121-0078-s012094 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0121-0078-s012094 | depot | — | revenue | 10 |
| line-3 | line-3-0121-0078-s012094 | depot | — | spare | 2 |
| line-3 | line-3-0121-0078-s012094 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (12 trains), line-2 (12 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **69 trainsets at 16 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **61 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **37 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0288-0520-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0349-0451-s002024 | forward | revenue | 2 | pending |
| line-1 | line-1-0349-0451-s002024 | reverse | revenue | 2 | pending |
| line-1 | line-1-0379-0373-s004059 | forward | revenue | 2 | pending |
| line-1 | line-1-0379-0373-s004059 | reverse | revenue | 2 | pending |
| line-1 | line-1-0391-0287-s006034 | forward | revenue | 2 | pending |
| line-1 | line-1-0391-0287-s006034 | reverse | revenue | 2 | pending |
| line-1 | line-1-0402-0196-s008078 | forward | revenue | 2 | pending |
| line-1 | line-1-0402-0196-s008078 | reverse | revenue | 2 | pending |
| line-1 | line-1-0371-0112-s010141 | reverse | revenue | 2 | pending |
| line-1 | line-1-0349-0451-s002024 | forward | spare | 1 | pending |
| line-1 | line-1-0349-0451-s002024 | reverse | spare | 1 | pending |
| line-1 | line-1-0379-0373-s004059 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0603-0266-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0468-0325-s003622 | forward | revenue | 3 | pending |
| line-2 | line-2-0468-0325-s003622 | reverse | revenue | 3 | pending |
| line-2 | line-2-0379-0373-s006263 | forward | revenue | 3 | pending |
| line-2 | line-2-0379-0373-s006263 | reverse | revenue | 3 | pending |
| line-2 | line-2-0431-0513-s009823 | reverse | revenue | 3 | pending |
| line-2 | line-2-0603-0266-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0325-s003622 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0506-0435-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0450-0397-s001604 | forward | revenue | 3 | pending |
| line-3 | line-3-0450-0397-s001604 | reverse | revenue | 2 | pending |
| line-3 | line-3-0379-0373-s003284 | forward | revenue | 2 | pending |
| line-3 | line-3-0379-0373-s003284 | reverse | revenue | 2 | pending |
| line-3 | line-3-0334-0349-s004611 | forward | revenue | 2 | pending |
| line-3 | line-3-0334-0349-s004611 | reverse | revenue | 2 | pending |
| line-3 | line-3-0249-0212-s008353 | forward | revenue | 2 | pending |
| line-3 | line-3-0249-0212-s008353 | reverse | revenue | 2 | pending |
| line-3 | line-3-0121-0078-s012094 | reverse | revenue | 2 | pending |
| line-3 | line-3-0450-0397-s001604 | reverse | spare | 1 | pending |
| line-3 | line-3-0379-0373-s003284 | forward | spare | 1 | pending |
| line-3 | line-3-0379-0373-s003284 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**31 trainsets exceed the reference platform envelope**, requiring **1,519.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0288-0520-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0349-0451-s002024 | 6 | 2 | 4 | 196.0 |
| line-1-0371-0112-s010141 | 2 | 2 | 0 | 0.0 |
| line-1-0379-0373-s004059 | 5 | 4 | 1 | 49.0 |
| line-1-0391-0287-s006034 | 4 | 2 | 2 | 98.0 |
| line-1-0402-0196-s008078 | 4 | 2 | 2 | 98.0 |
| line-2-0379-0373-s006263 | 6 | 4 | 2 | 98.0 |
| line-2-0431-0513-s009823 | 3 | 2 | 1 | 49.0 |
| line-2-0468-0325-s003622 | 7 | 2 | 5 | 245.0 |
| line-2-0603-0266-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0121-0078-s012094 | 2 | 2 | 0 | 0.0 |
| line-3-0249-0212-s008353 | 4 | 2 | 2 | 98.0 |
| line-3-0334-0349-s004611 | 4 | 2 | 2 | 98.0 |
| line-3-0379-0373-s003284 | 6 | 4 | 2 | 98.0 |
| line-3-0450-0397-s001604 | 6 | 2 | 4 | 196.0 |
| line-3-0506-0435-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Masaka/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
