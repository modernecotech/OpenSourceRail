# Station and depot overnight allocation

Plan: **22 trainsets at stations + 25 at depots = 47 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0351-0573-s009443 | 25 | 1,225.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0351-0573-s009443 | station | reverse | revenue | 2 |
| line-1 | line-1-0382-0394-s004936 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0394-s004936 | station | reverse | revenue | 1 |
| line-1 | line-1-0398-0485-s007186 | station | forward | revenue | 1 |
| line-1 | line-1-0398-0485-s007186 | station | reverse | revenue | 1 |
| line-1 | line-1-0449-0448-s003010 | station | forward | revenue | 1 |
| line-1 | line-1-0449-0448-s003010 | station | reverse | revenue | 1 |
| line-1 | line-1-0580-0436-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0325-0372-s008413 | station | reverse | revenue | 2 |
| line-2 | line-2-0382-0394-s006805 | station | forward | revenue | 1 |
| line-2 | line-2-0382-0394-s006805 | station | reverse | revenue | 1 |
| line-2 | line-2-0400-0518-s003212 | station | forward | revenue | 1 |
| line-2 | line-2-0400-0518-s003212 | station | reverse | revenue | 1 |
| line-2 | line-2-0455-0642-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0348-0616-s004370 | station | reverse | revenue | 2 |
| line-3 | line-3-0508-0509-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0351-0573-s009443 | depot | — | revenue | 8 |
| line-1 | line-1-0351-0573-s009443 | depot | — | spare | 1 |
| line-1 | line-1-0351-0573-s009443 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0351-0573-s009443 | depot | — | revenue | 7 |
| line-2 | line-1-0351-0573-s009443 | depot | — | spare | 1 |
| line-2 | line-1-0351-0573-s009443 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0351-0573-s009443 | depot | — | revenue | 4 |
| line-3 | line-1-0351-0573-s009443 | depot | — | spare | 1 |
| line-3 | line-1-0351-0573-s009443 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (9 trains), line-3 (6 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **47 trainsets at 11 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **41 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **25 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **9 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0580-0436-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0449-0448-s003010 | forward | revenue | 3 | pending |
| line-1 | line-1-0449-0448-s003010 | reverse | revenue | 2 | pending |
| line-1 | line-1-0382-0394-s004936 | forward | revenue | 2 | pending |
| line-1 | line-1-0382-0394-s004936 | reverse | revenue | 2 | pending |
| line-1 | line-1-0398-0485-s007186 | forward | revenue | 2 | pending |
| line-1 | line-1-0398-0485-s007186 | reverse | revenue | 2 | pending |
| line-1 | line-1-0351-0573-s009443 | reverse | revenue | 2 | pending |
| line-1 | line-1-0449-0448-s003010 | reverse | spare | 1 | pending |
| line-1 | line-1-0382-0394-s004936 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0455-0642-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0400-0518-s003212 | forward | revenue | 3 | pending |
| line-2 | line-2-0400-0518-s003212 | reverse | revenue | 3 | pending |
| line-2 | line-2-0382-0394-s006805 | forward | revenue | 2 | pending |
| line-2 | line-2-0382-0394-s006805 | reverse | revenue | 2 | pending |
| line-2 | line-2-0325-0372-s008413 | reverse | revenue | 2 | pending |
| line-2 | line-2-0382-0394-s006805 | forward | spare | 1 | pending |
| line-2 | line-2-0382-0394-s006805 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0508-0509-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0348-0616-s004370 | reverse | revenue | 4 | pending |
| line-3 | line-3-0508-0509-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0348-0616-s004370 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**21 trainsets exceed the reference platform envelope**, requiring **1,029.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0351-0573-s009443 | 2 | 2 | 0 | 0.0 |
| line-1-0382-0394-s004936 | 5 | 4 | 1 | 49.0 |
| line-1-0398-0485-s007186 | 4 | 2 | 2 | 98.0 |
| line-1-0449-0448-s003010 | 6 | 2 | 4 | 196.0 |
| line-1-0580-0436-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0325-0372-s008413 | 2 | 2 | 0 | 0.0 |
| line-2-0382-0394-s006805 | 6 | 4 | 2 | 98.0 |
| line-2-0400-0518-s003212 | 6 | 2 | 4 | 196.0 |
| line-2-0455-0642-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0348-0616-s004370 | 5 | 2 | 3 | 147.0 |
| line-3-0508-0509-s000000 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Xai-Xai/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
