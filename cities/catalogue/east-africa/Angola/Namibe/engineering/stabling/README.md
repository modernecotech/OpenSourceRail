# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 42 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0535-0039-s000000 | line-1 | declared-depot | 14 | 686.0 | 4 |
| line-2-0105-0497-s000000 | line-2 | declared-depot | 11 | 539.0 | 3 |
| line-3-0484-0136-s013914 | line-3 | declared-depot | 17 | 833.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0391-0512-s010740 | station | forward | revenue | 1 |
| line-1 | line-1-0391-0512-s010740 | station | reverse | revenue | 1 |
| line-1 | line-1-0392-0605-s012752 | station | reverse | revenue | 2 |
| line-1 | line-1-0400-0416-s008745 | station | forward | revenue | 1 |
| line-1 | line-1-0400-0416-s008745 | station | reverse | revenue | 1 |
| line-1 | line-1-0413-0285-s006006 | station | forward | revenue | 1 |
| line-1 | line-1-0413-0285-s006006 | station | reverse | revenue | 1 |
| line-1 | line-1-0421-0196-s004160 | station | forward | revenue | 1 |
| line-1 | line-1-0421-0196-s004160 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0039-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0105-0497-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0232-0451-s003125 | station | forward | revenue | 1 |
| line-2 | line-2-0232-0451-s003125 | station | reverse | revenue | 1 |
| line-2 | line-2-0306-0436-s004741 | station | forward | revenue | 1 |
| line-2 | line-2-0306-0436-s004741 | station | reverse | revenue | 1 |
| line-2 | line-2-0400-0416-s006822 | station | forward | revenue | 1 |
| line-2 | line-2-0400-0416-s006822 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0386-s010006 | station | reverse | revenue | 2 |
| line-3 | line-3-0133-0467-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0228-0414-s004002 | station | forward | revenue | 1 |
| line-3 | line-3-0228-0414-s004002 | station | reverse | revenue | 1 |
| line-3 | line-3-0352-0350-s007012 | station | forward | revenue | 1 |
| line-3 | line-3-0352-0350-s007012 | station | reverse | revenue | 1 |
| line-3 | line-3-0357-0250-s010021 | station | forward | revenue | 1 |
| line-3 | line-3-0357-0250-s010021 | station | reverse | revenue | 1 |
| line-3 | line-3-0421-0196-s011901 | station | forward | revenue | 1 |
| line-3 | line-3-0421-0196-s011901 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0136-s013914 | station | reverse | revenue | 2 |
| line-1 | line-1-0535-0039-s000000 | depot | — | revenue | 11 |
| line-1 | line-1-0535-0039-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0535-0039-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0105-0497-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0105-0497-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0105-0497-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0484-0136-s013914 | depot | — | revenue | 14 |
| line-3 | line-3-0484-0136-s013914 | depot | — | spare | 2 |
| line-3 | line-3-0484-0136-s013914 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/namibe-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **42 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0535-0039-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0421-0196-s004160 | forward | revenue | 3 | pending |
| line-1 | line-1-0421-0196-s004160 | reverse | revenue | 3 | pending |
| line-1 | line-1-0413-0285-s006006 | forward | revenue | 2 | pending |
| line-1 | line-1-0413-0285-s006006 | reverse | revenue | 2 | pending |
| line-1 | line-1-0400-0416-s008745 | forward | revenue | 2 | pending |
| line-1 | line-1-0400-0416-s008745 | reverse | revenue | 2 | pending |
| line-1 | line-1-0391-0512-s010740 | forward | revenue | 2 | pending |
| line-1 | line-1-0391-0512-s010740 | reverse | revenue | 2 | pending |
| line-1 | line-1-0392-0605-s012752 | reverse | revenue | 2 | pending |
| line-1 | line-1-0413-0285-s006006 | forward | spare | 1 | pending |
| line-1 | line-1-0413-0285-s006006 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-0416-s008745 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0105-0497-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0232-0451-s003125 | forward | revenue | 3 | pending |
| line-2 | line-2-0232-0451-s003125 | reverse | revenue | 3 | pending |
| line-2 | line-2-0306-0436-s004741 | forward | revenue | 2 | pending |
| line-2 | line-2-0306-0436-s004741 | reverse | revenue | 2 | pending |
| line-2 | line-2-0400-0416-s006822 | forward | revenue | 2 | pending |
| line-2 | line-2-0400-0416-s006822 | reverse | revenue | 2 | pending |
| line-2 | line-2-0545-0386-s010006 | reverse | revenue | 2 | pending |
| line-2 | line-2-0306-0436-s004741 | forward | spare | 1 | pending |
| line-2 | line-2-0306-0436-s004741 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0133-0467-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0228-0414-s004002 | forward | revenue | 3 | pending |
| line-3 | line-3-0228-0414-s004002 | reverse | revenue | 3 | pending |
| line-3 | line-3-0352-0350-s007012 | forward | revenue | 3 | pending |
| line-3 | line-3-0352-0350-s007012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0357-0250-s010021 | forward | revenue | 3 | pending |
| line-3 | line-3-0357-0250-s010021 | reverse | revenue | 2 | pending |
| line-3 | line-3-0421-0196-s011901 | forward | revenue | 2 | pending |
| line-3 | line-3-0421-0196-s011901 | reverse | revenue | 2 | pending |
| line-3 | line-3-0484-0136-s013914 | reverse | revenue | 2 | pending |
| line-3 | line-3-0357-0250-s010021 | reverse | spare | 1 | pending |
| line-3 | line-3-0421-0196-s011901 | forward | spare | 1 | pending |
| line-3 | line-3-0421-0196-s011901 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**34 trainsets exceed the reference platform envelope**, requiring **1,666.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0391-0512-s010740 | 4 | 2 | 2 | 98.0 |
| line-1-0392-0605-s012752 | 2 | 2 | 0 | 0.0 |
| line-1-0400-0416-s008745 | 5 | 4 | 1 | 49.0 |
| line-1-0413-0285-s006006 | 6 | 2 | 4 | 196.0 |
| line-1-0421-0196-s004160 | 6 | 4 | 2 | 98.0 |
| line-1-0535-0039-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0105-0497-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0232-0451-s003125 | 6 | 2 | 4 | 196.0 |
| line-2-0306-0436-s004741 | 6 | 2 | 4 | 196.0 |
| line-2-0400-0416-s006822 | 4 | 4 | 0 | 0.0 |
| line-2-0545-0386-s010006 | 2 | 2 | 0 | 0.0 |
| line-3-0133-0467-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0228-0414-s004002 | 6 | 2 | 4 | 196.0 |
| line-3-0352-0350-s007012 | 6 | 2 | 4 | 196.0 |
| line-3-0357-0250-s010021 | 6 | 2 | 4 | 196.0 |
| line-3-0421-0196-s011901 | 6 | 4 | 2 | 98.0 |
| line-3-0484-0136-s013914 | 2 | 2 | 0 | 0.0 |

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
