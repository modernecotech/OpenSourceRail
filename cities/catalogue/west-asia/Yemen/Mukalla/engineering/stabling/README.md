# Station and depot overnight allocation

Plan: **36 trainsets at stations + 116 at depots = 152 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0888-0083-s025965 | 116 | 6,902.0 | 23 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0462-0618-s019192 | station | reverse | revenue | 2 |
| line-1 | line-1-0503-0562-s017210 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0562-s017210 | station | reverse | revenue | 1 |
| line-1 | line-1-0562-0538-s015240 | station | forward | revenue | 1 |
| line-1 | line-1-0562-0538-s015240 | station | reverse | revenue | 1 |
| line-1 | line-1-0611-0547-s012429 | station | forward | revenue | 1 |
| line-1 | line-1-0611-0547-s012429 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0446-s010218 | station | forward | revenue | 1 |
| line-1 | line-1-0628-0446-s010218 | station | reverse | revenue | 1 |
| line-1 | line-1-0834-0200-s003510 | station | forward | revenue | 1 |
| line-1 | line-1-0834-0200-s003510 | station | reverse | revenue | 1 |
| line-1 | line-1-0857-0110-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0656-0592-s003014 | station | forward | revenue | 1 |
| line-2 | line-2-0656-0592-s003014 | station | reverse | revenue | 1 |
| line-2 | line-2-0668-0713-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0720-0444-s006504 | station | forward | revenue | 1 |
| line-2 | line-2-0720-0444-s006504 | station | reverse | revenue | 1 |
| line-2 | line-2-0946-0071-s016453 | station | reverse | revenue | 2 |
| line-3 | line-3-0414-1035-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0543-0614-s010019 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0614-s010019 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0764-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0764-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0562-0538-s012389 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0538-s012389 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0463-s014306 | station | forward | revenue | 1 |
| line-3 | line-3-0591-0463-s014306 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0382-s016216 | station | forward | revenue | 1 |
| line-3 | line-3-0626-0382-s016216 | station | reverse | revenue | 1 |
| line-3 | line-3-0888-0083-s025965 | station | reverse | revenue | 2 |
| line-1 | line-3-0888-0083-s025965 | depot | — | revenue | 29 |
| line-1 | line-3-0888-0083-s025965 | depot | — | spare | 4 |
| line-1 | line-3-0888-0083-s025965 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0888-0083-s025965 | depot | — | revenue | 28 |
| line-2 | line-3-0888-0083-s025965 | depot | — | spare | 3 |
| line-2 | line-3-0888-0083-s025965 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0888-0083-s025965 | depot | — | revenue | 44 |
| line-3 | line-3-0888-0083-s025965 | depot | — | spare | 5 |
| line-3 | line-3-0888-0083-s025965 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (34 trains), line-2 (32 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **152 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **137 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **116 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0857-0110-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0834-0200-s003510 | forward | revenue | 4 | pending |
| line-1 | line-1-0834-0200-s003510 | reverse | revenue | 4 | pending |
| line-1 | line-1-0628-0446-s010218 | forward | revenue | 4 | pending |
| line-1 | line-1-0628-0446-s010218 | reverse | revenue | 4 | pending |
| line-1 | line-1-0611-0547-s012429 | forward | revenue | 4 | pending |
| line-1 | line-1-0611-0547-s012429 | reverse | revenue | 4 | pending |
| line-1 | line-1-0562-0538-s015240 | forward | revenue | 3 | pending |
| line-1 | line-1-0562-0538-s015240 | reverse | revenue | 3 | pending |
| line-1 | line-1-0503-0562-s017210 | forward | revenue | 3 | pending |
| line-1 | line-1-0503-0562-s017210 | reverse | revenue | 3 | pending |
| line-1 | line-1-0462-0618-s019192 | reverse | revenue | 3 | pending |
| line-1 | line-1-0562-0538-s015240 | forward | spare | 1 | pending |
| line-1 | line-1-0562-0538-s015240 | reverse | spare | 1 | pending |
| line-1 | line-1-0503-0562-s017210 | forward | spare | 1 | pending |
| line-1 | line-1-0503-0562-s017210 | reverse | spare | 1 | pending |
| line-1 | line-1-0462-0618-s019192 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0668-0713-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0656-0592-s003014 | forward | revenue | 6 | pending |
| line-2 | line-2-0656-0592-s003014 | reverse | revenue | 6 | pending |
| line-2 | line-2-0720-0444-s006504 | forward | revenue | 6 | pending |
| line-2 | line-2-0720-0444-s006504 | reverse | revenue | 6 | pending |
| line-2 | line-2-0946-0071-s016453 | reverse | revenue | 6 | pending |
| line-2 | line-2-0668-0713-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0656-0592-s003014 | forward | spare | 1 | pending |
| line-2 | line-2-0656-0592-s003014 | reverse | spare | 1 | pending |
| line-2 | line-2-0720-0444-s006504 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0414-1035-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0543-0764-s007019 | forward | revenue | 5 | pending |
| line-3 | line-3-0543-0764-s007019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0543-0614-s010019 | forward | revenue | 5 | pending |
| line-3 | line-3-0543-0614-s010019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0562-0538-s012389 | forward | revenue | 5 | pending |
| line-3 | line-3-0562-0538-s012389 | reverse | revenue | 5 | pending |
| line-3 | line-3-0591-0463-s014306 | forward | revenue | 5 | pending |
| line-3 | line-3-0591-0463-s014306 | reverse | revenue | 5 | pending |
| line-3 | line-3-0626-0382-s016216 | forward | revenue | 5 | pending |
| line-3 | line-3-0626-0382-s016216 | reverse | revenue | 4 | pending |
| line-3 | line-3-0888-0083-s025965 | reverse | revenue | 4 | pending |
| line-3 | line-3-0626-0382-s016216 | reverse | spare | 1 | pending |
| line-3 | line-3-0888-0083-s025965 | reverse | spare | 1 | pending |
| line-3 | line-3-0414-1035-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0543-0764-s007019 | forward | spare | 1 | pending |
| line-3 | line-3-0543-0764-s007019 | reverse | spare | 1 | pending |
| line-3 | line-3-0543-0614-s010019 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**112 trainsets exceed the reference platform envelope**, requiring **6,664.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0462-0618-s019192 | 4 | 2 | 2 | 119.0 |
| line-1-0503-0562-s017210 | 8 | 2 | 6 | 357.0 |
| line-1-0562-0538-s015240 | 8 | 4 | 4 | 238.0 |
| line-1-0611-0547-s012429 | 8 | 2 | 6 | 357.0 |
| line-1-0628-0446-s010218 | 8 | 2 | 6 | 357.0 |
| line-1-0834-0200-s003510 | 8 | 2 | 6 | 357.0 |
| line-1-0857-0110-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0656-0592-s003014 | 14 | 2 | 12 | 714.0 |
| line-2-0668-0713-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0720-0444-s006504 | 13 | 2 | 11 | 654.5 |
| line-2-0946-0071-s016453 | 6 | 2 | 4 | 238.0 |
| line-3-0414-1035-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0543-0614-s010019 | 11 | 2 | 9 | 535.5 |
| line-3-0543-0764-s007019 | 12 | 2 | 10 | 595.0 |
| line-3-0562-0538-s012389 | 10 | 4 | 6 | 357.0 |
| line-3-0591-0463-s014306 | 10 | 2 | 8 | 476.0 |
| line-3-0626-0382-s016216 | 10 | 2 | 8 | 476.0 |
| line-3-0888-0083-s025965 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Mukalla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
