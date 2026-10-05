# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 92 at depots = 124 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0669-0351-s000000 | line-1 | declared-depot | 26 | 1,547.0 | 6 |
| line-2-0332-0976-s015494 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0384-0457-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0627-0880-s010928 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0880-s010928 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0925-s012819 | station | reverse | revenue | 2 |
| line-1 | line-1-0634-0789-s009050 | station | forward | revenue | 1 |
| line-1 | line-1-0634-0789-s009050 | station | reverse | revenue | 1 |
| line-1 | line-1-0646-0643-s006031 | station | forward | revenue | 1 |
| line-1 | line-1-0646-0643-s006031 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0497-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0497-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0667-0371-s000417 | station | forward | revenue | 1 |
| line-1 | line-1-0667-0371-s000417 | station | reverse | revenue | 1 |
| line-1 | line-1-0669-0351-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0332-0976-s015494 | station | reverse | revenue | 2 |
| line-2 | line-2-0398-0771-s010759 | station | forward | revenue | 1 |
| line-2 | line-2-0398-0771-s010759 | station | reverse | revenue | 1 |
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
| line-1 | line-1-0669-0351-s000000 | depot | — | revenue | 22 |
| line-1 | line-1-0669-0351-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0669-0351-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0976-s015494 | depot | — | revenue | 33 |
| line-2 | line-2-0332-0976-s015494 | depot | — | spare | 4 |
| line-2 | line-2-0332-0976-s015494 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0384-0457-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0384-0457-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0384-0457-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ilorin-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **124 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **92 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0669-0351-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0667-0371-s000417 | forward | revenue | 3 | pending |
| line-1 | line-1-0667-0371-s000417 | reverse | revenue | 3 | pending |
| line-1 | line-1-0657-0497-s003019 | forward | revenue | 3 | pending |
| line-1 | line-1-0657-0497-s003019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0646-0643-s006031 | forward | revenue | 3 | pending |
| line-1 | line-1-0646-0643-s006031 | reverse | revenue | 3 | pending |
| line-1 | line-1-0634-0789-s009050 | forward | revenue | 3 | pending |
| line-1 | line-1-0634-0789-s009050 | reverse | revenue | 3 | pending |
| line-1 | line-1-0627-0880-s010928 | forward | revenue | 3 | pending |
| line-1 | line-1-0627-0880-s010928 | reverse | revenue | 3 | pending |
| line-1 | line-1-0628-0925-s012819 | reverse | revenue | 3 | pending |
| line-1 | line-1-0669-0351-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0667-0371-s000417 | forward | spare | 1 | pending |
| line-1 | line-1-0667-0371-s000417 | reverse | spare | 1 | pending |
| line-1 | line-1-0657-0497-s003019 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0559-0305-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0520-0416-s002578 | forward | revenue | 6 | pending |
| line-2 | line-2-0520-0416-s002578 | reverse | revenue | 6 | pending |
| line-2 | line-2-0469-0566-s006036 | forward | revenue | 5 | pending |
| line-2 | line-2-0469-0566-s006036 | reverse | revenue | 5 | pending |
| line-2 | line-2-0398-0771-s010759 | forward | revenue | 5 | pending |
| line-2 | line-2-0398-0771-s010759 | reverse | revenue | 5 | pending |
| line-2 | line-2-0332-0976-s015494 | reverse | revenue | 5 | pending |
| line-2 | line-2-0469-0566-s006036 | forward | spare | 1 | pending |
| line-2 | line-2-0469-0566-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0398-0771-s010759 | forward | spare | 1 | pending |
| line-2 | line-2-0398-0771-s010759 | reverse | spare | 1 | pending |
| line-2 | line-2-0332-0976-s015494 | reverse | cold_reserve | 1 | pending |
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

**84 trainsets exceed the reference platform envelope**, requiring **4,998.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0627-0880-s010928 | 6 | 2 | 4 | 238.0 |
| line-1-0628-0925-s012819 | 3 | 2 | 1 | 59.5 |
| line-1-0634-0789-s009050 | 6 | 2 | 4 | 238.0 |
| line-1-0646-0643-s006031 | 6 | 2 | 4 | 238.0 |
| line-1-0657-0497-s003019 | 7 | 2 | 5 | 297.5 |
| line-1-0667-0371-s000417 | 8 | 4 | 4 | 238.0 |
| line-1-0669-0351-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0332-0976-s015494 | 6 | 2 | 4 | 238.0 |
| line-2-0398-0771-s010759 | 12 | 2 | 10 | 595.0 |
| line-2-0469-0566-s006036 | 12 | 2 | 10 | 595.0 |
| line-2-0520-0416-s002578 | 12 | 4 | 8 | 476.0 |
| line-2-0559-0305-s000000 | 6 | 2 | 4 | 238.0 |
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
