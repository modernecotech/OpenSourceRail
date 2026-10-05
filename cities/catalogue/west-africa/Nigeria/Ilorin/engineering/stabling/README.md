# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 98 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0669-0351-s000000 | line-1 | declared-depot | 31 | 1,844.5 | 7 |
| line-2-0332-0976-s015815 | line-2 | declared-depot | 39 | 2,320.5 | 7 |
| line-3-0384-0457-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0626-0887-s011076 | station | forward | revenue | 1 |
| line-1 | line-1-0626-0887-s011076 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0925-s013109 | station | reverse | revenue | 2 |
| line-1 | line-1-0634-0789-s009050 | station | forward | revenue | 1 |
| line-1 | line-1-0634-0789-s009050 | station | reverse | revenue | 1 |
| line-1 | line-1-0646-0643-s006031 | station | forward | revenue | 1 |
| line-1 | line-1-0646-0643-s006031 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0497-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0497-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0667-0371-s000417 | station | forward | revenue | 1 |
| line-1 | line-1-0667-0371-s000417 | station | reverse | revenue | 1 |
| line-1 | line-1-0669-0351-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0332-0976-s015815 | station | reverse | revenue | 2 |
| line-2 | line-2-0395-0778-s010924 | station | forward | revenue | 1 |
| line-2 | line-2-0395-0778-s010924 | station | reverse | revenue | 1 |
| line-2 | line-2-0469-0566-s006036 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0566-s006036 | station | reverse | revenue | 1 |
| line-2 | line-2-0520-0416-s002578 | station | forward | revenue | 1 |
| line-2 | line-2-0520-0416-s002578 | station | reverse | revenue | 1 |
| line-2 | line-2-0559-0305-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0384-0457-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0518-0416-s003020 | station | forward | revenue | 1 |
| line-3 | line-3-0518-0416-s003020 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0371-s006396 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0371-s006396 | station | reverse | revenue | 1 |
| line-3 | line-3-0890-0291-s011845 | station | reverse | revenue | 2 |
| line-1 | line-1-0669-0351-s000000 | depot | — | revenue | 26 |
| line-1 | line-1-0669-0351-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0669-0351-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0976-s015815 | depot | — | revenue | 34 |
| line-2 | line-2-0332-0976-s015815 | depot | — | spare | 4 |
| line-2 | line-2-0332-0976-s015815 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0384-0457-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0384-0457-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0384-0457-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ilorin-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0669-0351-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0667-0371-s000417 | forward | revenue | 4 | pending |
| line-1 | line-1-0667-0371-s000417 | reverse | revenue | 4 | pending |
| line-1 | line-1-0657-0497-s003019 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0497-s003019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0646-0643-s006031 | forward | revenue | 3 | pending |
| line-1 | line-1-0646-0643-s006031 | reverse | revenue | 3 | pending |
| line-1 | line-1-0634-0789-s009050 | forward | revenue | 3 | pending |
| line-1 | line-1-0634-0789-s009050 | reverse | revenue | 3 | pending |
| line-1 | line-1-0626-0887-s011076 | forward | revenue | 3 | pending |
| line-1 | line-1-0626-0887-s011076 | reverse | revenue | 3 | pending |
| line-1 | line-1-0628-0925-s013109 | reverse | revenue | 3 | pending |
| line-1 | line-1-0657-0497-s003019 | reverse | spare | 1 | pending |
| line-1 | line-1-0646-0643-s006031 | forward | spare | 1 | pending |
| line-1 | line-1-0646-0643-s006031 | reverse | spare | 1 | pending |
| line-1 | line-1-0634-0789-s009050 | forward | spare | 1 | pending |
| line-1 | line-1-0634-0789-s009050 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0559-0305-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0520-0416-s002578 | forward | revenue | 6 | pending |
| line-2 | line-2-0520-0416-s002578 | reverse | revenue | 6 | pending |
| line-2 | line-2-0469-0566-s006036 | forward | revenue | 6 | pending |
| line-2 | line-2-0469-0566-s006036 | reverse | revenue | 5 | pending |
| line-2 | line-2-0395-0778-s010924 | forward | revenue | 5 | pending |
| line-2 | line-2-0395-0778-s010924 | reverse | revenue | 5 | pending |
| line-2 | line-2-0332-0976-s015815 | reverse | revenue | 5 | pending |
| line-2 | line-2-0469-0566-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0395-0778-s010924 | forward | spare | 1 | pending |
| line-2 | line-2-0395-0778-s010924 | reverse | spare | 1 | pending |
| line-2 | line-2-0332-0976-s015815 | reverse | spare | 1 | pending |
| line-2 | line-2-0559-0305-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0384-0457-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0518-0416-s003020 | forward | revenue | 6 | pending |
| line-3 | line-3-0518-0416-s003020 | reverse | revenue | 5 | pending |
| line-3 | line-3-0667-0371-s006396 | forward | revenue | 5 | pending |
| line-3 | line-3-0667-0371-s006396 | reverse | revenue | 5 | pending |
| line-3 | line-3-0890-0291-s011845 | reverse | revenue | 5 | pending |
| line-3 | line-3-0518-0416-s003020 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0371-s006396 | forward | spare | 1 | pending |
| line-3 | line-3-0667-0371-s006396 | reverse | spare | 1 | pending |
| line-3 | line-3-0890-0291-s011845 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**90 trainsets exceed the reference platform envelope**, requiring **5,355.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0626-0887-s011076 | 6 | 2 | 4 | 238.0 |
| line-1-0628-0925-s013109 | 3 | 2 | 1 | 59.5 |
| line-1-0634-0789-s009050 | 8 | 2 | 6 | 357.0 |
| line-1-0646-0643-s006031 | 8 | 2 | 6 | 357.0 |
| line-1-0657-0497-s003019 | 8 | 2 | 6 | 357.0 |
| line-1-0667-0371-s000417 | 8 | 4 | 4 | 238.0 |
| line-1-0669-0351-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0332-0976-s015815 | 6 | 2 | 4 | 238.0 |
| line-2-0395-0778-s010924 | 12 | 2 | 10 | 595.0 |
| line-2-0469-0566-s006036 | 12 | 2 | 10 | 595.0 |
| line-2-0520-0416-s002578 | 12 | 4 | 8 | 476.0 |
| line-2-0559-0305-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0384-0457-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0518-0416-s003020 | 12 | 4 | 8 | 476.0 |
| line-3-0667-0371-s006396 | 12 | 4 | 8 | 476.0 |
| line-3-0890-0291-s011845 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Ilorin/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
