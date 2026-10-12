# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 58 at depots = 98 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0296-0125-s000000 | line-1 | declared-depot | 17 | 833.0 | 4 |
| line-2-0450-0180-s014744 | line-2 | declared-depot | 18 | 882.0 | 5 |
| line-3-0181-0288-s000000 | line-3 | declared-depot | 14 | 686.0 | 4 |
| line-4-0446-0552-s000000 | line-4 | declared-depot | 9 | 441.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0296-0125-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0373-0371-s006062 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0371-s006062 | station | reverse | revenue | 1 |
| line-1 | line-1-0375-0364-s005849 | station | forward | revenue | 1 |
| line-1 | line-1-0375-0364-s005849 | station | reverse | revenue | 1 |
| line-1 | line-1-0382-0268-s003572 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0268-s003572 | station | reverse | revenue | 1 |
| line-1 | line-1-0446-0552-s011906 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0552-s011906 | station | reverse | revenue | 1 |
| line-1 | line-1-0477-0623-s013611 | station | reverse | revenue | 2 |
| line-2 | line-2-0086-0716-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0147-0574-s003616 | station | forward | revenue | 1 |
| line-2 | line-2-0147-0574-s003616 | station | reverse | revenue | 1 |
| line-2 | line-2-0229-0467-s006634 | station | forward | revenue | 1 |
| line-2 | line-2-0229-0467-s006634 | station | reverse | revenue | 1 |
| line-2 | line-2-0311-0360-s009641 | station | forward | revenue | 1 |
| line-2 | line-2-0311-0360-s009641 | station | reverse | revenue | 1 |
| line-2 | line-2-0382-0268-s012245 | station | forward | revenue | 1 |
| line-2 | line-2-0382-0268-s012245 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0180-s014744 | station | reverse | revenue | 2 |
| line-3 | line-3-0181-0288-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0311-0361-s003540 | station | forward | revenue | 1 |
| line-3 | line-3-0311-0361-s003540 | station | reverse | revenue | 1 |
| line-3 | line-3-0373-0371-s005154 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0371-s005154 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0364-s005367 | station | forward | revenue | 1 |
| line-3 | line-3-0375-0364-s005367 | station | reverse | revenue | 1 |
| line-3 | line-3-0475-0362-s007627 | station | forward | revenue | 1 |
| line-3 | line-3-0475-0362-s007627 | station | reverse | revenue | 1 |
| line-3 | line-3-0702-0427-s013177 | station | reverse | revenue | 2 |
| line-4 | line-4-0312-0443-s005941 | station | reverse | revenue | 2 |
| line-4 | line-4-0446-0552-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0296-0125-s000000 | depot | — | revenue | 14 |
| line-1 | line-1-0296-0125-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0296-0125-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0450-0180-s014744 | depot | — | revenue | 15 |
| line-2 | line-2-0450-0180-s014744 | depot | — | spare | 2 |
| line-2 | line-2-0450-0180-s014744 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0181-0288-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0181-0288-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0181-0288-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0446-0552-s000000 | depot | — | revenue | 7 |
| line-4 | line-4-0446-0552-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0446-0552-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kakamega-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **98 trainsets at 20 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **87 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **58 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0296-0125-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0382-0268-s003572 | forward | revenue | 3 | pending |
| line-1 | line-1-0382-0268-s003572 | reverse | revenue | 3 | pending |
| line-1 | line-1-0375-0364-s005849 | forward | revenue | 3 | pending |
| line-1 | line-1-0375-0364-s005849 | reverse | revenue | 3 | pending |
| line-1 | line-1-0373-0371-s006062 | forward | revenue | 3 | pending |
| line-1 | line-1-0373-0371-s006062 | reverse | revenue | 2 | pending |
| line-1 | line-1-0446-0552-s011906 | forward | revenue | 2 | pending |
| line-1 | line-1-0446-0552-s011906 | reverse | revenue | 2 | pending |
| line-1 | line-1-0477-0623-s013611 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0371-s006062 | reverse | spare | 1 | pending |
| line-1 | line-1-0446-0552-s011906 | forward | spare | 1 | pending |
| line-1 | line-1-0446-0552-s011906 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0086-0716-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | forward | revenue | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | reverse | revenue | 3 | pending |
| line-2 | line-2-0229-0467-s006634 | forward | revenue | 3 | pending |
| line-2 | line-2-0229-0467-s006634 | reverse | revenue | 3 | pending |
| line-2 | line-2-0311-0360-s009641 | forward | revenue | 3 | pending |
| line-2 | line-2-0311-0360-s009641 | reverse | revenue | 3 | pending |
| line-2 | line-2-0382-0268-s012245 | forward | revenue | 2 | pending |
| line-2 | line-2-0382-0268-s012245 | reverse | revenue | 2 | pending |
| line-2 | line-2-0450-0180-s014744 | reverse | revenue | 2 | pending |
| line-2 | line-2-0382-0268-s012245 | forward | spare | 1 | pending |
| line-2 | line-2-0382-0268-s012245 | reverse | spare | 1 | pending |
| line-2 | line-2-0450-0180-s014744 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0181-0288-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0311-0361-s003540 | forward | revenue | 3 | pending |
| line-3 | line-3-0311-0361-s003540 | reverse | revenue | 3 | pending |
| line-3 | line-3-0373-0371-s005154 | forward | revenue | 2 | pending |
| line-3 | line-3-0373-0371-s005154 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0364-s005367 | forward | revenue | 2 | pending |
| line-3 | line-3-0375-0364-s005367 | reverse | revenue | 2 | pending |
| line-3 | line-3-0475-0362-s007627 | forward | revenue | 2 | pending |
| line-3 | line-3-0475-0362-s007627 | reverse | revenue | 2 | pending |
| line-3 | line-3-0702-0427-s013177 | reverse | revenue | 2 | pending |
| line-3 | line-3-0373-0371-s005154 | forward | spare | 1 | pending |
| line-3 | line-3-0373-0371-s005154 | reverse | spare | 1 | pending |
| line-3 | line-3-0375-0364-s005367 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0446-0552-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0312-0443-s005941 | reverse | revenue | 5 | pending |
| line-4 | line-4-0312-0443-s005941 | reverse | spare | 1 | pending |
| line-4 | line-4-0446-0552-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **1,960.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0296-0125-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0373-0371-s006062 | 6 | 4 | 2 | 98.0 |
| line-1-0375-0364-s005849 | 6 | 4 | 2 | 98.0 |
| line-1-0382-0268-s003572 | 6 | 4 | 2 | 98.0 |
| line-1-0446-0552-s011906 | 6 | 4 | 2 | 98.0 |
| line-1-0477-0623-s013611 | 2 | 2 | 0 | 0.0 |
| line-2-0086-0716-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0147-0574-s003616 | 6 | 2 | 4 | 196.0 |
| line-2-0229-0467-s006634 | 6 | 2 | 4 | 196.0 |
| line-2-0311-0360-s009641 | 6 | 4 | 2 | 98.0 |
| line-2-0382-0268-s012245 | 6 | 4 | 2 | 98.0 |
| line-2-0450-0180-s014744 | 3 | 2 | 1 | 49.0 |
| line-3-0181-0288-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0311-0361-s003540 | 6 | 4 | 2 | 98.0 |
| line-3-0373-0371-s005154 | 6 | 4 | 2 | 98.0 |
| line-3-0375-0364-s005367 | 5 | 4 | 1 | 49.0 |
| line-3-0475-0362-s007627 | 4 | 2 | 2 | 98.0 |
| line-3-0702-0427-s013177 | 2 | 2 | 0 | 0.0 |
| line-4-0312-0443-s005941 | 6 | 2 | 4 | 196.0 |
| line-4-0446-0552-s000000 | 7 | 2 | 5 | 245.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kakamega/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
