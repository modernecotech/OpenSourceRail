# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 82 at depots = 118 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0491-0802-s000000 | line-1 | declared-depot | 29 | 1,725.5 | 6 |
| line-2-0654-0283-s000000 | line-2 | declared-depot | 25 | 1,487.5 | 6 |
| line-3-0421-0641-s013224 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0491-0802-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0500-0655-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0655-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0510-0504-s006117 | station | forward | revenue | 1 |
| line-1 | line-1-0510-0504-s006117 | station | reverse | revenue | 1 |
| line-1 | line-1-0519-0365-s008972 | station | forward | revenue | 1 |
| line-1 | line-1-0519-0365-s008972 | station | reverse | revenue | 1 |
| line-1 | line-1-0527-0190-s012600 | station | reverse | revenue | 2 |
| line-2 | line-2-0361-0731-s011926 | station | reverse | revenue | 2 |
| line-2 | line-2-0421-0640-s009504 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0640-s009504 | station | reverse | revenue | 1 |
| line-2 | line-2-0422-0637-s009435 | station | forward | revenue | 1 |
| line-2 | line-2-0422-0637-s009435 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0504-s005871 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0504-s005871 | station | reverse | revenue | 1 |
| line-2 | line-2-0540-0457-s004624 | station | forward | revenue | 1 |
| line-2 | line-2-0540-0457-s004624 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0396-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0396-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0654-0283-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0421-0641-s013224 | station | reverse | revenue | 2 |
| line-3 | line-3-0422-0637-s013136 | station | forward | revenue | 1 |
| line-3 | line-3-0422-0637-s013136 | station | reverse | revenue | 1 |
| line-3 | line-3-0450-0463-s009412 | station | forward | revenue | 1 |
| line-3 | line-3-0450-0463-s009412 | station | reverse | revenue | 1 |
| line-3 | line-3-0474-0323-s006401 | station | forward | revenue | 1 |
| line-3 | line-3-0474-0323-s006401 | station | reverse | revenue | 1 |
| line-3 | line-3-0476-0055-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0498-0182-s003382 | station | forward | revenue | 1 |
| line-3 | line-3-0498-0182-s003382 | station | reverse | revenue | 1 |
| line-1 | line-1-0491-0802-s000000 | depot | — | revenue | 25 |
| line-1 | line-1-0491-0802-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0491-0802-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0654-0283-s000000 | depot | — | revenue | 21 |
| line-2 | line-2-0654-0283-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0654-0283-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0421-0641-s013224 | depot | — | revenue | 24 |
| line-3 | line-3-0421-0641-s013224 | depot | — | spare | 3 |
| line-3 | line-3-0421-0641-s013224 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ramadi-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **118 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **106 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **82 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0491-0802-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0500-0655-s003015 | forward | revenue | 5 | pending |
| line-1 | line-1-0500-0655-s003015 | reverse | revenue | 5 | pending |
| line-1 | line-1-0510-0504-s006117 | forward | revenue | 4 | pending |
| line-1 | line-1-0510-0504-s006117 | reverse | revenue | 4 | pending |
| line-1 | line-1-0519-0365-s008972 | forward | revenue | 4 | pending |
| line-1 | line-1-0519-0365-s008972 | reverse | revenue | 4 | pending |
| line-1 | line-1-0527-0190-s012600 | reverse | revenue | 4 | pending |
| line-1 | line-1-0510-0504-s006117 | forward | spare | 1 | pending |
| line-1 | line-1-0510-0504-s006117 | reverse | spare | 1 | pending |
| line-1 | line-1-0519-0365-s008972 | forward | spare | 1 | pending |
| line-1 | line-1-0519-0365-s008972 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0654-0283-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0580-0396-s003002 | forward | revenue | 3 | pending |
| line-2 | line-2-0580-0396-s003002 | reverse | revenue | 3 | pending |
| line-2 | line-2-0540-0457-s004624 | forward | revenue | 3 | pending |
| line-2 | line-2-0540-0457-s004624 | reverse | revenue | 3 | pending |
| line-2 | line-2-0510-0504-s005871 | forward | revenue | 3 | pending |
| line-2 | line-2-0510-0504-s005871 | reverse | revenue | 3 | pending |
| line-2 | line-2-0422-0637-s009435 | forward | revenue | 3 | pending |
| line-2 | line-2-0422-0637-s009435 | reverse | revenue | 3 | pending |
| line-2 | line-2-0421-0640-s009504 | forward | revenue | 3 | pending |
| line-2 | line-2-0421-0640-s009504 | reverse | revenue | 3 | pending |
| line-2 | line-2-0361-0731-s011926 | reverse | revenue | 2 | pending |
| line-2 | line-2-0361-0731-s011926 | reverse | spare | 1 | pending |
| line-2 | line-2-0654-0283-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0396-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0396-s003002 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0476-0055-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0498-0182-s003382 | forward | revenue | 4 | pending |
| line-3 | line-3-0498-0182-s003382 | reverse | revenue | 4 | pending |
| line-3 | line-3-0474-0323-s006401 | forward | revenue | 4 | pending |
| line-3 | line-3-0474-0323-s006401 | reverse | revenue | 4 | pending |
| line-3 | line-3-0450-0463-s009412 | forward | revenue | 4 | pending |
| line-3 | line-3-0450-0463-s009412 | reverse | revenue | 3 | pending |
| line-3 | line-3-0422-0637-s013136 | forward | revenue | 3 | pending |
| line-3 | line-3-0422-0637-s013136 | reverse | revenue | 3 | pending |
| line-3 | line-3-0421-0641-s013224 | reverse | revenue | 3 | pending |
| line-3 | line-3-0450-0463-s009412 | reverse | spare | 1 | pending |
| line-3 | line-3-0422-0637-s013136 | forward | spare | 1 | pending |
| line-3 | line-3-0422-0637-s013136 | reverse | spare | 1 | pending |
| line-3 | line-3-0421-0641-s013224 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**70 trainsets exceed the reference platform envelope**, requiring **4,165.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0491-0802-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0500-0655-s003015 | 10 | 2 | 8 | 476.0 |
| line-1-0510-0504-s006117 | 10 | 4 | 6 | 357.0 |
| line-1-0519-0365-s008972 | 10 | 2 | 8 | 476.0 |
| line-1-0527-0190-s012600 | 4 | 2 | 2 | 119.0 |
| line-2-0361-0731-s011926 | 3 | 2 | 1 | 59.5 |
| line-2-0421-0640-s009504 | 6 | 4 | 2 | 119.0 |
| line-2-0422-0637-s009435 | 6 | 4 | 2 | 119.0 |
| line-2-0510-0504-s005871 | 6 | 4 | 2 | 119.0 |
| line-2-0540-0457-s004624 | 6 | 2 | 4 | 238.0 |
| line-2-0580-0396-s003002 | 8 | 2 | 6 | 357.0 |
| line-2-0654-0283-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0421-0641-s013224 | 4 | 2 | 2 | 119.0 |
| line-3-0422-0637-s013136 | 8 | 4 | 4 | 238.0 |
| line-3-0450-0463-s009412 | 8 | 2 | 6 | 357.0 |
| line-3-0474-0323-s006401 | 8 | 2 | 6 | 357.0 |
| line-3-0476-0055-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0498-0182-s003382 | 8 | 4 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Ramadi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
