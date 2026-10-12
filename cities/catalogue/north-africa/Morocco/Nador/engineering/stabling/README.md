# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 50 at depots = 92 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0328-0422-s000000 | line-1 | declared-depot | 11 | 539.0 | 4 |
| line-2-0479-0445-s015368 | line-2 | declared-depot | 21 | 1,029.0 | 5 |
| line-3-0619-0416-s000000 | line-3 | declared-depot | 9 | 441.0 | 3 |
| line-4-0459-0131-s000000 | line-4 | declared-depot | 9 | 441.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0328-0422-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0367-0344-s002834 | station | forward | revenue | 1 |
| line-1 | line-1-0367-0344-s002834 | station | reverse | revenue | 1 |
| line-1 | line-1-0376-0368-s001997 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0368-s001997 | station | reverse | revenue | 1 |
| line-1 | line-1-0379-0365-s002122 | station | forward | revenue | 1 |
| line-1 | line-1-0379-0365-s002122 | station | reverse | revenue | 1 |
| line-1 | line-1-0384-0361-s002307 | station | forward | revenue | 1 |
| line-1 | line-1-0384-0361-s002307 | station | reverse | revenue | 1 |
| line-1 | line-1-0440-0045-s010064 | station | reverse | revenue | 2 |
| line-1 | line-1-0457-0143-s007814 | station | forward | revenue | 1 |
| line-1 | line-1-0457-0143-s007814 | station | reverse | revenue | 1 |
| line-1 | line-1-0459-0131-s008071 | station | forward | revenue | 1 |
| line-1 | line-1-0459-0131-s008071 | station | reverse | revenue | 1 |
| line-2 | line-2-0034-0117-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0243-0279-s007024 | station | forward | revenue | 1 |
| line-2 | line-2-0243-0279-s007024 | station | reverse | revenue | 1 |
| line-2 | line-2-0376-0367-s011599 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0367-s011599 | station | reverse | revenue | 1 |
| line-2 | line-2-0379-0365-s011676 | station | forward | revenue | 1 |
| line-2 | line-2-0379-0365-s011676 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0445-s015368 | station | reverse | revenue | 2 |
| line-3 | line-3-0313-0282-s008540 | station | reverse | revenue | 2 |
| line-3 | line-3-0367-0344-s006853 | station | forward | revenue | 1 |
| line-3 | line-3-0367-0344-s006853 | station | reverse | revenue | 1 |
| line-3 | line-3-0384-0361-s006325 | station | forward | revenue | 1 |
| line-3 | line-3-0384-0361-s006325 | station | reverse | revenue | 1 |
| line-3 | line-3-0493-0392-s003016 | station | forward | revenue | 1 |
| line-3 | line-3-0493-0392-s003016 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0416-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0457-0143-s000563 | station | forward | revenue | 1 |
| line-4 | line-4-0457-0143-s000563 | station | reverse | revenue | 1 |
| line-4 | line-4-0459-0131-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0663-0137-s006874 | station | reverse | revenue | 2 |
| line-1 | line-1-0328-0422-s000000 | depot | — | revenue | 8 |
| line-1 | line-1-0328-0422-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0328-0422-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0479-0445-s015368 | depot | — | revenue | 18 |
| line-2 | line-2-0479-0445-s015368 | depot | — | spare | 2 |
| line-2 | line-2-0479-0445-s015368 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0619-0416-s000000 | depot | — | revenue | 7 |
| line-3 | line-3-0619-0416-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0619-0416-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0459-0131-s000000 | depot | — | revenue | 7 |
| line-4 | line-4-0459-0131-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0459-0131-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nador-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **92 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 6 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **50 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0328-0422-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0376-0368-s001997 | forward | revenue | 2 | pending |
| line-1 | line-1-0376-0368-s001997 | reverse | revenue | 2 | pending |
| line-1 | line-1-0379-0365-s002122 | forward | revenue | 2 | pending |
| line-1 | line-1-0379-0365-s002122 | reverse | revenue | 2 | pending |
| line-1 | line-1-0384-0361-s002307 | forward | revenue | 2 | pending |
| line-1 | line-1-0384-0361-s002307 | reverse | revenue | 2 | pending |
| line-1 | line-1-0367-0344-s002834 | forward | revenue | 2 | pending |
| line-1 | line-1-0367-0344-s002834 | reverse | revenue | 2 | pending |
| line-1 | line-1-0457-0143-s007814 | forward | revenue | 2 | pending |
| line-1 | line-1-0457-0143-s007814 | reverse | revenue | 1 | pending |
| line-1 | line-1-0459-0131-s008071 | forward | revenue | 1 | pending |
| line-1 | line-1-0459-0131-s008071 | reverse | revenue | 1 | pending |
| line-1 | line-1-0440-0045-s010064 | reverse | revenue | 1 | pending |
| line-1 | line-1-0457-0143-s007814 | reverse | spare | 1 | pending |
| line-1 | line-1-0459-0131-s008071 | forward | spare | 1 | pending |
| line-1 | line-1-0459-0131-s008071 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0243-0279-s007024 | forward | revenue | 4 | pending |
| line-2 | line-2-0243-0279-s007024 | reverse | revenue | 4 | pending |
| line-2 | line-2-0376-0367-s011599 | forward | revenue | 4 | pending |
| line-2 | line-2-0376-0367-s011599 | reverse | revenue | 3 | pending |
| line-2 | line-2-0379-0365-s011676 | forward | revenue | 3 | pending |
| line-2 | line-2-0379-0365-s011676 | reverse | revenue | 3 | pending |
| line-2 | line-2-0479-0445-s015368 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0367-s011599 | reverse | spare | 1 | pending |
| line-2 | line-2-0379-0365-s011676 | forward | spare | 1 | pending |
| line-2 | line-2-0379-0365-s011676 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0619-0416-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0493-0392-s003016 | forward | revenue | 2 | pending |
| line-3 | line-3-0493-0392-s003016 | reverse | revenue | 2 | pending |
| line-3 | line-3-0384-0361-s006325 | forward | revenue | 2 | pending |
| line-3 | line-3-0384-0361-s006325 | reverse | revenue | 2 | pending |
| line-3 | line-3-0367-0344-s006853 | forward | revenue | 2 | pending |
| line-3 | line-3-0367-0344-s006853 | reverse | revenue | 2 | pending |
| line-3 | line-3-0313-0282-s008540 | reverse | revenue | 2 | pending |
| line-3 | line-3-0493-0392-s003016 | forward | spare | 1 | pending |
| line-3 | line-3-0493-0392-s003016 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0459-0131-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0457-0143-s000563 | forward | revenue | 3 | pending |
| line-4 | line-4-0457-0143-s000563 | reverse | revenue | 3 | pending |
| line-4 | line-4-0663-0137-s006874 | reverse | revenue | 3 | pending |
| line-4 | line-4-0457-0143-s000563 | forward | spare | 1 | pending |
| line-4 | line-4-0457-0143-s000563 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0328-0422-s000000 | 2 | 2 | 0 | 0.0 |
| line-1-0367-0344-s002834 | 4 | 4 | 0 | 0.0 |
| line-1-0376-0368-s001997 | 4 | 4 | 0 | 0.0 |
| line-1-0379-0365-s002122 | 4 | 4 | 0 | 0.0 |
| line-1-0384-0361-s002307 | 4 | 4 | 0 | 0.0 |
| line-1-0440-0045-s010064 | 1 | 2 | 0 | 0.0 |
| line-1-0457-0143-s007814 | 4 | 4 | 0 | 0.0 |
| line-1-0459-0131-s008071 | 4 | 4 | 0 | 0.0 |
| line-2-0034-0117-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0243-0279-s007024 | 8 | 2 | 6 | 294.0 |
| line-2-0376-0367-s011599 | 8 | 4 | 4 | 196.0 |
| line-2-0379-0365-s011676 | 8 | 4 | 4 | 196.0 |
| line-2-0479-0445-s015368 | 3 | 2 | 1 | 49.0 |
| line-3-0313-0282-s008540 | 2 | 2 | 0 | 0.0 |
| line-3-0367-0344-s006853 | 4 | 4 | 0 | 0.0 |
| line-3-0384-0361-s006325 | 4 | 4 | 0 | 0.0 |
| line-3-0493-0392-s003016 | 6 | 2 | 4 | 196.0 |
| line-3-0619-0416-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0457-0143-s000563 | 8 | 4 | 4 | 196.0 |
| line-4-0459-0131-s000000 | 4 | 2 | 2 | 98.0 |
| line-4-0663-0137-s006874 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Nador/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
