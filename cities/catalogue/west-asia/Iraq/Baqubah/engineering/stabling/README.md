# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 134 at depots = 164 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0811-0508-s000000 | line-1 | declared-depot | 27 | 1,606.5 | 5 |
| line-2-0185-1002-s020796 | line-2 | declared-depot | 54 | 3,213.0 | 9 |
| line-3-0123-0580-s000000 | line-3 | declared-depot | 53 | 3,153.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0395-0236-s011136 | station | reverse | revenue | 2 |
| line-1 | line-1-0587-0362-s005982 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0362-s005982 | station | reverse | revenue | 1 |
| line-1 | line-1-0698-0434-s003025 | station | forward | revenue | 1 |
| line-1 | line-1-0698-0434-s003025 | station | reverse | revenue | 1 |
| line-1 | line-1-0811-0508-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0185-1002-s020796 | station | reverse | revenue | 2 |
| line-2 | line-2-0516-0584-s009043 | station | forward | revenue | 1 |
| line-2 | line-2-0516-0584-s009043 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0466-s006036 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0466-s006036 | station | reverse | revenue | 1 |
| line-2 | line-2-0645-0348-s003020 | station | forward | revenue | 1 |
| line-2 | line-2-0645-0348-s003020 | station | reverse | revenue | 1 |
| line-2 | line-2-0711-0229-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0123-0580-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0383-0515-s007003 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0515-s007003 | station | reverse | revenue | 1 |
| line-3 | line-3-0503-0454-s010014 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0454-s010014 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0392-s013023 | station | forward | revenue | 1 |
| line-3 | line-3-0626-0392-s013023 | station | reverse | revenue | 1 |
| line-3 | line-3-0779-0314-s016869 | station | forward | revenue | 1 |
| line-3 | line-3-0779-0314-s016869 | station | reverse | revenue | 1 |
| line-3 | line-3-0927-0228-s020718 | station | reverse | revenue | 2 |
| line-1 | line-1-0811-0508-s000000 | depot | — | revenue | 23 |
| line-1 | line-1-0811-0508-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0811-0508-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0185-1002-s020796 | depot | — | revenue | 48 |
| line-2 | line-2-0185-1002-s020796 | depot | — | spare | 5 |
| line-2 | line-2-0185-1002-s020796 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0123-0580-s000000 | depot | — | revenue | 47 |
| line-3 | line-3-0123-0580-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0123-0580-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/baqubah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **164 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **148 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **134 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0811-0508-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0698-0434-s003025 | forward | revenue | 5 | pending |
| line-1 | line-1-0698-0434-s003025 | reverse | revenue | 5 | pending |
| line-1 | line-1-0587-0362-s005982 | forward | revenue | 5 | pending |
| line-1 | line-1-0587-0362-s005982 | reverse | revenue | 5 | pending |
| line-1 | line-1-0395-0236-s011136 | reverse | revenue | 5 | pending |
| line-1 | line-1-0698-0434-s003025 | forward | spare | 1 | pending |
| line-1 | line-1-0698-0434-s003025 | reverse | spare | 1 | pending |
| line-1 | line-1-0587-0362-s005982 | forward | spare | 1 | pending |
| line-1 | line-1-0587-0362-s005982 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0711-0229-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0645-0348-s003020 | forward | revenue | 8 | pending |
| line-2 | line-2-0645-0348-s003020 | reverse | revenue | 7 | pending |
| line-2 | line-2-0580-0466-s006036 | forward | revenue | 7 | pending |
| line-2 | line-2-0580-0466-s006036 | reverse | revenue | 7 | pending |
| line-2 | line-2-0516-0584-s009043 | forward | revenue | 7 | pending |
| line-2 | line-2-0516-0584-s009043 | reverse | revenue | 7 | pending |
| line-2 | line-2-0185-1002-s020796 | reverse | revenue | 7 | pending |
| line-2 | line-2-0645-0348-s003020 | reverse | spare | 1 | pending |
| line-2 | line-2-0580-0466-s006036 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0466-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0516-0584-s009043 | forward | spare | 1 | pending |
| line-2 | line-2-0516-0584-s009043 | reverse | spare | 1 | pending |
| line-2 | line-2-0185-1002-s020796 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0123-0580-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0383-0515-s007003 | forward | revenue | 6 | pending |
| line-3 | line-3-0383-0515-s007003 | reverse | revenue | 6 | pending |
| line-3 | line-3-0503-0454-s010014 | forward | revenue | 6 | pending |
| line-3 | line-3-0503-0454-s010014 | reverse | revenue | 6 | pending |
| line-3 | line-3-0626-0392-s013023 | forward | revenue | 6 | pending |
| line-3 | line-3-0626-0392-s013023 | reverse | revenue | 6 | pending |
| line-3 | line-3-0779-0314-s016869 | forward | revenue | 6 | pending |
| line-3 | line-3-0779-0314-s016869 | reverse | revenue | 6 | pending |
| line-3 | line-3-0927-0228-s020718 | reverse | revenue | 5 | pending |
| line-3 | line-3-0927-0228-s020718 | reverse | spare | 1 | pending |
| line-3 | line-3-0123-0580-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0383-0515-s007003 | forward | spare | 1 | pending |
| line-3 | line-3-0383-0515-s007003 | reverse | spare | 1 | pending |
| line-3 | line-3-0503-0454-s010014 | forward | spare | 1 | pending |
| line-3 | line-3-0503-0454-s010014 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**134 trainsets exceed the reference platform envelope**, requiring **7,973.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0395-0236-s011136 | 5 | 2 | 3 | 178.5 |
| line-1-0587-0362-s005982 | 12 | 2 | 10 | 595.0 |
| line-1-0698-0434-s003025 | 12 | 2 | 10 | 595.0 |
| line-1-0811-0508-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0185-1002-s020796 | 8 | 2 | 6 | 357.0 |
| line-2-0516-0584-s009043 | 16 | 2 | 14 | 833.0 |
| line-2-0580-0466-s006036 | 16 | 2 | 14 | 833.0 |
| line-2-0645-0348-s003020 | 16 | 2 | 14 | 833.0 |
| line-2-0711-0229-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0123-0580-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0383-0515-s007003 | 14 | 2 | 12 | 714.0 |
| line-3-0503-0454-s010014 | 14 | 2 | 12 | 714.0 |
| line-3-0626-0392-s013023 | 12 | 2 | 10 | 595.0 |
| line-3-0779-0314-s016869 | 12 | 2 | 10 | 595.0 |
| line-3-0927-0228-s020718 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Baqubah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
