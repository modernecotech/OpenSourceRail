# Station and depot overnight allocation

Plan: **42 trainsets at stations + 71 at depots = 113 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0646-0668-s018121 | 71 | 4,224.5 | 17 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0224-0492-s016470 | station | reverse | revenue | 2 |
| line-1 | line-1-0301-0526-s014162 | station | forward | revenue | 1 |
| line-1 | line-1-0301-0526-s014162 | station | reverse | revenue | 1 |
| line-1 | line-1-0414-0524-s011852 | station | forward | revenue | 1 |
| line-1 | line-1-0414-0524-s011852 | station | reverse | revenue | 1 |
| line-1 | line-1-0500-0575-s009552 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0575-s009552 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0560-s008153 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0560-s008153 | station | reverse | revenue | 1 |
| line-1 | line-1-0624-0567-s006531 | station | forward | revenue | 1 |
| line-1 | line-1-0624-0567-s006531 | station | reverse | revenue | 1 |
| line-1 | line-1-0701-0622-s003512 | station | forward | revenue | 1 |
| line-1 | line-1-0701-0622-s003512 | station | reverse | revenue | 1 |
| line-1 | line-1-0835-0580-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0439-0983-s017586 | station | reverse | revenue | 2 |
| line-2 | line-2-0535-0639-s008775 | station | forward | revenue | 1 |
| line-2 | line-2-0535-0639-s008775 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0560-s006897 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0560-s006897 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0700-s010647 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0700-s010647 | station | reverse | revenue | 1 |
| line-2 | line-2-0627-0525-s004621 | station | forward | revenue | 1 |
| line-2 | line-2-0627-0525-s004621 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0505-s003005 | station | forward | revenue | 1 |
| line-2 | line-2-0687-0505-s003005 | station | reverse | revenue | 1 |
| line-2 | line-2-0769-0425-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0288-0012-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0464-0279-s007025 | station | forward | revenue | 1 |
| line-3 | line-3-0464-0279-s007025 | station | reverse | revenue | 1 |
| line-3 | line-3-0530-0415-s010468 | station | forward | revenue | 1 |
| line-3 | line-3-0530-0415-s010468 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0560-s014107 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0560-s014107 | station | reverse | revenue | 1 |
| line-3 | line-3-0611-0626-s016128 | station | forward | revenue | 1 |
| line-3 | line-3-0611-0626-s016128 | station | reverse | revenue | 1 |
| line-3 | line-3-0646-0668-s018121 | station | reverse | revenue | 2 |
| line-1 | line-3-0646-0668-s018121 | depot | — | revenue | 16 |
| line-1 | line-3-0646-0668-s018121 | depot | — | spare | 3 |
| line-1 | line-3-0646-0668-s018121 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0646-0668-s018121 | depot | — | revenue | 19 |
| line-2 | line-3-0646-0668-s018121 | depot | — | spare | 3 |
| line-2 | line-3-0646-0668-s018121 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0646-0668-s018121 | depot | — | revenue | 24 |
| line-3 | line-3-0646-0668-s018121 | depot | — | spare | 3 |
| line-3 | line-3-0646-0668-s018121 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (20 trains), line-2 (23 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **113 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **101 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **71 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0835-0580-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0701-0622-s003512 | forward | revenue | 3 | pending |
| line-1 | line-1-0701-0622-s003512 | reverse | revenue | 3 | pending |
| line-1 | line-1-0624-0567-s006531 | forward | revenue | 3 | pending |
| line-1 | line-1-0624-0567-s006531 | reverse | revenue | 2 | pending |
| line-1 | line-1-0555-0560-s008153 | forward | revenue | 2 | pending |
| line-1 | line-1-0555-0560-s008153 | reverse | revenue | 2 | pending |
| line-1 | line-1-0500-0575-s009552 | forward | revenue | 2 | pending |
| line-1 | line-1-0500-0575-s009552 | reverse | revenue | 2 | pending |
| line-1 | line-1-0414-0524-s011852 | forward | revenue | 2 | pending |
| line-1 | line-1-0414-0524-s011852 | reverse | revenue | 2 | pending |
| line-1 | line-1-0301-0526-s014162 | forward | revenue | 2 | pending |
| line-1 | line-1-0301-0526-s014162 | reverse | revenue | 2 | pending |
| line-1 | line-1-0224-0492-s016470 | reverse | revenue | 2 | pending |
| line-1 | line-1-0624-0567-s006531 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0560-s008153 | forward | spare | 1 | pending |
| line-1 | line-1-0555-0560-s008153 | reverse | spare | 1 | pending |
| line-1 | line-1-0500-0575-s009552 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0769-0425-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0687-0505-s003005 | forward | revenue | 3 | pending |
| line-2 | line-2-0687-0505-s003005 | reverse | revenue | 3 | pending |
| line-2 | line-2-0627-0525-s004621 | forward | revenue | 3 | pending |
| line-2 | line-2-0627-0525-s004621 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0560-s006897 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0560-s006897 | reverse | revenue | 3 | pending |
| line-2 | line-2-0535-0639-s008775 | forward | revenue | 3 | pending |
| line-2 | line-2-0535-0639-s008775 | reverse | revenue | 3 | pending |
| line-2 | line-2-0580-0700-s010647 | forward | revenue | 2 | pending |
| line-2 | line-2-0580-0700-s010647 | reverse | revenue | 2 | pending |
| line-2 | line-2-0439-0983-s017586 | reverse | revenue | 2 | pending |
| line-2 | line-2-0580-0700-s010647 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0700-s010647 | reverse | spare | 1 | pending |
| line-2 | line-2-0439-0983-s017586 | reverse | spare | 1 | pending |
| line-2 | line-2-0769-0425-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0288-0012-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0464-0279-s007025 | forward | revenue | 4 | pending |
| line-3 | line-3-0464-0279-s007025 | reverse | revenue | 4 | pending |
| line-3 | line-3-0530-0415-s010468 | forward | revenue | 4 | pending |
| line-3 | line-3-0530-0415-s010468 | reverse | revenue | 4 | pending |
| line-3 | line-3-0555-0560-s014107 | forward | revenue | 4 | pending |
| line-3 | line-3-0555-0560-s014107 | reverse | revenue | 3 | pending |
| line-3 | line-3-0611-0626-s016128 | forward | revenue | 3 | pending |
| line-3 | line-3-0611-0626-s016128 | reverse | revenue | 3 | pending |
| line-3 | line-3-0646-0668-s018121 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0560-s014107 | reverse | spare | 1 | pending |
| line-3 | line-3-0611-0626-s016128 | forward | spare | 1 | pending |
| line-3 | line-3-0611-0626-s016128 | reverse | spare | 1 | pending |
| line-3 | line-3-0646-0668-s018121 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**65 trainsets exceed the reference platform envelope**, requiring **3,867.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0224-0492-s016470 | 2 | 2 | 0 | 0.0 |
| line-1-0301-0526-s014162 | 4 | 2 | 2 | 119.0 |
| line-1-0414-0524-s011852 | 4 | 2 | 2 | 119.0 |
| line-1-0500-0575-s009552 | 5 | 2 | 3 | 178.5 |
| line-1-0555-0560-s008153 | 6 | 4 | 2 | 119.0 |
| line-1-0624-0567-s006531 | 6 | 2 | 4 | 238.0 |
| line-1-0701-0622-s003512 | 6 | 2 | 4 | 238.0 |
| line-1-0835-0580-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0439-0983-s017586 | 3 | 2 | 1 | 59.5 |
| line-2-0535-0639-s008775 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0560-s006897 | 6 | 4 | 2 | 119.0 |
| line-2-0580-0700-s010647 | 6 | 2 | 4 | 238.0 |
| line-2-0627-0525-s004621 | 6 | 2 | 4 | 238.0 |
| line-2-0687-0505-s003005 | 6 | 2 | 4 | 238.0 |
| line-2-0769-0425-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0288-0012-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0464-0279-s007025 | 8 | 2 | 6 | 357.0 |
| line-3-0530-0415-s010468 | 8 | 2 | 6 | 357.0 |
| line-3-0555-0560-s014107 | 8 | 4 | 4 | 238.0 |
| line-3-0611-0626-s016128 | 8 | 2 | 6 | 357.0 |
| line-3-0646-0668-s018121 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Dodoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
