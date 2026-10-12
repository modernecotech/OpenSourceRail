# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 59 at depots = 103 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0535-0039-s000000 | line-1 | declared-depot | 16 | 784.0 | 4 |
| line-2-0105-0497-s000000 | line-2 | declared-depot | 13 | 637.0 | 4 |
| line-3-0484-0136-s013485 | line-3 | declared-depot | 15 | 735.0 | 4 |
| line-4-0452-0278-s000000 | line-4 | declared-depot | 8 | 392.0 | 2 |
| line-5-0105-0497-s000000 | line-5 | declared-depot | 7 | 343.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0392-0605-s012752 | station | reverse | revenue | 2 |
| line-1 | line-1-0405-0365-s007672 | station | forward | revenue | 1 |
| line-1 | line-1-0405-0365-s007672 | station | reverse | revenue | 1 |
| line-1 | line-1-0406-0350-s007364 | station | forward | revenue | 1 |
| line-1 | line-1-0406-0350-s007364 | station | reverse | revenue | 1 |
| line-1 | line-1-0429-0142-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0429-0142-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0039-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0105-0497-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0233-0453-s003251 | station | forward | revenue | 1 |
| line-2 | line-2-0233-0453-s003251 | station | reverse | revenue | 1 |
| line-2 | line-2-0384-0364-s007438 | station | forward | revenue | 1 |
| line-2 | line-2-0384-0364-s007438 | station | reverse | revenue | 1 |
| line-2 | line-2-0392-0360-s007647 | station | forward | revenue | 1 |
| line-2 | line-2-0392-0360-s007647 | station | reverse | revenue | 1 |
| line-2 | line-2-0405-0365-s008102 | station | forward | revenue | 1 |
| line-2 | line-2-0405-0365-s008102 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0386-s012022 | station | reverse | revenue | 2 |
| line-3 | line-3-0133-0467-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0241-0382-s003450 | station | forward | revenue | 1 |
| line-3 | line-3-0241-0382-s003450 | station | reverse | revenue | 1 |
| line-3 | line-3-0384-0364-s007570 | station | forward | revenue | 1 |
| line-3 | line-3-0384-0364-s007570 | station | reverse | revenue | 1 |
| line-3 | line-3-0392-0360-s007779 | station | forward | revenue | 1 |
| line-3 | line-3-0392-0360-s007779 | station | reverse | revenue | 1 |
| line-3 | line-3-0406-0350-s008187 | station | forward | revenue | 1 |
| line-3 | line-3-0406-0350-s008187 | station | reverse | revenue | 1 |
| line-3 | line-3-0452-0278-s010307 | station | forward | revenue | 1 |
| line-3 | line-3-0452-0278-s010307 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0136-s013485 | station | reverse | revenue | 2 |
| line-4 | line-4-0452-0278-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0563-0188-s004727 | station | reverse | revenue | 2 |
| line-5 | line-5-0037-0388-s004803 | station | reverse | revenue | 2 |
| line-5 | line-5-0105-0497-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0535-0039-s000000 | depot | — | revenue | 13 |
| line-1 | line-1-0535-0039-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0535-0039-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0105-0497-s000000 | depot | — | revenue | 10 |
| line-2 | line-2-0105-0497-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0105-0497-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0484-0136-s013485 | depot | — | revenue | 12 |
| line-3 | line-3-0484-0136-s013485 | depot | — | spare | 2 |
| line-3 | line-3-0484-0136-s013485 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0452-0278-s000000 | depot | — | revenue | 6 |
| line-4 | line-4-0452-0278-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0452-0278-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0105-0497-s000000 | depot | — | revenue | 5 |
| line-5 | line-5-0105-0497-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0105-0497-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/namibe-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **103 trainsets at 22 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **90 revenue, 8 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **59 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0535-0039-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | forward | revenue | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | reverse | revenue | 3 | pending |
| line-1 | line-1-0406-0350-s007364 | forward | revenue | 3 | pending |
| line-1 | line-1-0406-0350-s007364 | reverse | revenue | 3 | pending |
| line-1 | line-1-0405-0365-s007672 | forward | revenue | 3 | pending |
| line-1 | line-1-0405-0365-s007672 | reverse | revenue | 3 | pending |
| line-1 | line-1-0392-0605-s012752 | reverse | revenue | 2 | pending |
| line-1 | line-1-0392-0605-s012752 | reverse | spare | 1 | pending |
| line-1 | line-1-0535-0039-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0429-0142-s003002 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0105-0497-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | forward | revenue | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | reverse | revenue | 2 | pending |
| line-2 | line-2-0384-0364-s007438 | forward | revenue | 2 | pending |
| line-2 | line-2-0384-0364-s007438 | reverse | revenue | 2 | pending |
| line-2 | line-2-0392-0360-s007647 | forward | revenue | 2 | pending |
| line-2 | line-2-0392-0360-s007647 | reverse | revenue | 2 | pending |
| line-2 | line-2-0405-0365-s008102 | forward | revenue | 2 | pending |
| line-2 | line-2-0405-0365-s008102 | reverse | revenue | 2 | pending |
| line-2 | line-2-0545-0386-s012022 | reverse | revenue | 2 | pending |
| line-2 | line-2-0233-0453-s003251 | reverse | spare | 1 | pending |
| line-2 | line-2-0384-0364-s007438 | forward | spare | 1 | pending |
| line-2 | line-2-0384-0364-s007438 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0133-0467-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | forward | revenue | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | reverse | revenue | 2 | pending |
| line-3 | line-3-0384-0364-s007570 | forward | revenue | 2 | pending |
| line-3 | line-3-0384-0364-s007570 | reverse | revenue | 2 | pending |
| line-3 | line-3-0392-0360-s007779 | forward | revenue | 2 | pending |
| line-3 | line-3-0392-0360-s007779 | reverse | revenue | 2 | pending |
| line-3 | line-3-0406-0350-s008187 | forward | revenue | 2 | pending |
| line-3 | line-3-0406-0350-s008187 | reverse | revenue | 2 | pending |
| line-3 | line-3-0452-0278-s010307 | forward | revenue | 2 | pending |
| line-3 | line-3-0452-0278-s010307 | reverse | revenue | 2 | pending |
| line-3 | line-3-0484-0136-s013485 | reverse | revenue | 2 | pending |
| line-3 | line-3-0241-0382-s003450 | reverse | spare | 1 | pending |
| line-3 | line-3-0384-0364-s007570 | forward | spare | 1 | pending |
| line-3 | line-3-0384-0364-s007570 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0452-0278-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0563-0188-s004727 | reverse | revenue | 5 | pending |
| line-4 | line-4-0452-0278-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0563-0188-s004727 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0105-0497-s000000 | forward | revenue | 5 | pending |
| line-5 | line-5-0037-0388-s004803 | reverse | revenue | 4 | pending |
| line-5 | line-5-0037-0388-s004803 | reverse | spare | 1 | pending |
| line-5 | line-5-0105-0497-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,009.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0392-0605-s012752 | 3 | 2 | 1 | 49.0 |
| line-1-0405-0365-s007672 | 6 | 4 | 2 | 98.0 |
| line-1-0406-0350-s007364 | 6 | 4 | 2 | 98.0 |
| line-1-0429-0142-s003002 | 7 | 2 | 5 | 245.0 |
| line-1-0535-0039-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0105-0497-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0233-0453-s003251 | 6 | 2 | 4 | 196.0 |
| line-2-0384-0364-s007438 | 6 | 4 | 2 | 98.0 |
| line-2-0392-0360-s007647 | 4 | 4 | 0 | 0.0 |
| line-2-0405-0365-s008102 | 4 | 4 | 0 | 0.0 |
| line-2-0545-0386-s012022 | 2 | 2 | 0 | 0.0 |
| line-3-0133-0467-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0241-0382-s003450 | 6 | 2 | 4 | 196.0 |
| line-3-0384-0364-s007570 | 6 | 4 | 2 | 98.0 |
| line-3-0392-0360-s007779 | 4 | 4 | 0 | 0.0 |
| line-3-0406-0350-s008187 | 4 | 4 | 0 | 0.0 |
| line-3-0452-0278-s010307 | 4 | 4 | 0 | 0.0 |
| line-3-0484-0136-s013485 | 2 | 2 | 0 | 0.0 |
| line-4-0452-0278-s000000 | 6 | 2 | 4 | 196.0 |
| line-4-0563-0188-s004727 | 6 | 2 | 4 | 196.0 |
| line-5-0037-0388-s004803 | 5 | 2 | 3 | 147.0 |
| line-5-0105-0497-s000000 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Namibe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
