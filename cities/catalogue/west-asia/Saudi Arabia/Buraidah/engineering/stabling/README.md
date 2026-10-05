# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 129 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0230-0021-s026440 | line-1 | declared-depot | 61 | 3,629.5 | 11 |
| line-2-0301-0299-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 7 |
| line-3-0938-0427-s000000 | line-3 | declared-depot | 35 | 2,082.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0230-0021-s026440 | station | reverse | revenue | 2 |
| line-1 | line-1-0419-0253-s019636 | station | forward | revenue | 1 |
| line-1 | line-1-0419-0253-s019636 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0351-s016621 | station | forward | revenue | 1 |
| line-1 | line-1-0511-0351-s016621 | station | reverse | revenue | 1 |
| line-1 | line-1-0569-0413-s014725 | station | forward | revenue | 1 |
| line-1 | line-1-0569-0413-s014725 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0474-s012825 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0474-s012825 | station | reverse | revenue | 1 |
| line-1 | line-1-0692-0543-s010673 | station | forward | revenue | 1 |
| line-1 | line-1-0692-0543-s010673 | station | reverse | revenue | 1 |
| line-1 | line-1-0785-0641-s007661 | station | forward | revenue | 1 |
| line-1 | line-1-0785-0641-s007661 | station | reverse | revenue | 1 |
| line-1 | line-1-0877-0739-s004646 | station | forward | revenue | 1 |
| line-1 | line-1-0877-0739-s004646 | station | reverse | revenue | 1 |
| line-1 | line-1-1016-0841-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0301-0299-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0384-0407-s003023 | station | forward | revenue | 1 |
| line-2 | line-2-0384-0407-s003023 | station | reverse | revenue | 1 |
| line-2 | line-2-0470-0518-s006155 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0518-s006155 | station | reverse | revenue | 1 |
| line-2 | line-2-0549-0621-s009057 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0621-s009057 | station | reverse | revenue | 1 |
| line-2 | line-2-0606-0695-s011114 | station | forward | revenue | 1 |
| line-2 | line-2-0606-0695-s011114 | station | reverse | revenue | 1 |
| line-2 | line-2-0662-0767-s013159 | station | forward | revenue | 1 |
| line-2 | line-2-0662-0767-s013159 | station | reverse | revenue | 1 |
| line-2 | line-2-0718-0840-s015212 | station | reverse | revenue | 2 |
| line-3 | line-3-0250-0578-s015512 | station | reverse | revenue | 2 |
| line-3 | line-3-0404-0536-s012061 | station | forward | revenue | 1 |
| line-3 | line-3-0404-0536-s012061 | station | reverse | revenue | 1 |
| line-3 | line-3-0470-0518-s010592 | station | forward | revenue | 1 |
| line-3 | line-3-0470-0518-s010592 | station | reverse | revenue | 1 |
| line-3 | line-3-0557-0494-s008641 | station | forward | revenue | 1 |
| line-3 | line-3-0557-0494-s008641 | station | reverse | revenue | 1 |
| line-3 | line-3-0627-0474-s007064 | station | forward | revenue | 1 |
| line-3 | line-3-0627-0474-s007064 | station | reverse | revenue | 1 |
| line-3 | line-3-0718-0449-s005036 | station | forward | revenue | 1 |
| line-3 | line-3-0718-0449-s005036 | station | reverse | revenue | 1 |
| line-3 | line-3-0809-0424-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0809-0424-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0938-0427-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0230-0021-s026440 | depot | — | revenue | 53 |
| line-1 | line-1-0230-0021-s026440 | depot | — | spare | 7 |
| line-1 | line-1-0230-0021-s026440 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0301-0299-s000000 | depot | — | revenue | 28 |
| line-2 | line-2-0301-0299-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0301-0299-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0938-0427-s000000 | depot | — | revenue | 30 |
| line-3 | line-3-0938-0427-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0938-0427-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/buraidah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **129 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1016-0841-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0877-0739-s004646 | forward | revenue | 5 | pending |
| line-1 | line-1-0877-0739-s004646 | reverse | revenue | 5 | pending |
| line-1 | line-1-0785-0641-s007661 | forward | revenue | 5 | pending |
| line-1 | line-1-0785-0641-s007661 | reverse | revenue | 5 | pending |
| line-1 | line-1-0692-0543-s010673 | forward | revenue | 5 | pending |
| line-1 | line-1-0692-0543-s010673 | reverse | revenue | 5 | pending |
| line-1 | line-1-0627-0474-s012825 | forward | revenue | 4 | pending |
| line-1 | line-1-0627-0474-s012825 | reverse | revenue | 4 | pending |
| line-1 | line-1-0569-0413-s014725 | forward | revenue | 4 | pending |
| line-1 | line-1-0569-0413-s014725 | reverse | revenue | 4 | pending |
| line-1 | line-1-0511-0351-s016621 | forward | revenue | 4 | pending |
| line-1 | line-1-0511-0351-s016621 | reverse | revenue | 4 | pending |
| line-1 | line-1-0419-0253-s019636 | forward | revenue | 4 | pending |
| line-1 | line-1-0419-0253-s019636 | reverse | revenue | 4 | pending |
| line-1 | line-1-0230-0021-s026440 | reverse | revenue | 4 | pending |
| line-1 | line-1-0627-0474-s012825 | forward | spare | 1 | pending |
| line-1 | line-1-0627-0474-s012825 | reverse | spare | 1 | pending |
| line-1 | line-1-0569-0413-s014725 | forward | spare | 1 | pending |
| line-1 | line-1-0569-0413-s014725 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0351-s016621 | forward | spare | 1 | pending |
| line-1 | line-1-0511-0351-s016621 | reverse | spare | 1 | pending |
| line-1 | line-1-0419-0253-s019636 | forward | spare | 1 | pending |
| line-1 | line-1-0419-0253-s019636 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0301-0299-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0384-0407-s003023 | forward | revenue | 4 | pending |
| line-2 | line-2-0384-0407-s003023 | reverse | revenue | 4 | pending |
| line-2 | line-2-0470-0518-s006155 | forward | revenue | 4 | pending |
| line-2 | line-2-0470-0518-s006155 | reverse | revenue | 4 | pending |
| line-2 | line-2-0549-0621-s009057 | forward | revenue | 4 | pending |
| line-2 | line-2-0549-0621-s009057 | reverse | revenue | 3 | pending |
| line-2 | line-2-0606-0695-s011114 | forward | revenue | 3 | pending |
| line-2 | line-2-0606-0695-s011114 | reverse | revenue | 3 | pending |
| line-2 | line-2-0662-0767-s013159 | forward | revenue | 3 | pending |
| line-2 | line-2-0662-0767-s013159 | reverse | revenue | 3 | pending |
| line-2 | line-2-0718-0840-s015212 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0621-s009057 | reverse | spare | 1 | pending |
| line-2 | line-2-0606-0695-s011114 | forward | spare | 1 | pending |
| line-2 | line-2-0606-0695-s011114 | reverse | spare | 1 | pending |
| line-2 | line-2-0662-0767-s013159 | forward | spare | 1 | pending |
| line-2 | line-2-0662-0767-s013159 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0938-0427-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0809-0424-s003009 | forward | revenue | 4 | pending |
| line-3 | line-3-0809-0424-s003009 | reverse | revenue | 4 | pending |
| line-3 | line-3-0718-0449-s005036 | forward | revenue | 4 | pending |
| line-3 | line-3-0718-0449-s005036 | reverse | revenue | 3 | pending |
| line-3 | line-3-0627-0474-s007064 | forward | revenue | 3 | pending |
| line-3 | line-3-0627-0474-s007064 | reverse | revenue | 3 | pending |
| line-3 | line-3-0557-0494-s008641 | forward | revenue | 3 | pending |
| line-3 | line-3-0557-0494-s008641 | reverse | revenue | 3 | pending |
| line-3 | line-3-0470-0518-s010592 | forward | revenue | 3 | pending |
| line-3 | line-3-0470-0518-s010592 | reverse | revenue | 3 | pending |
| line-3 | line-3-0404-0536-s012061 | forward | revenue | 3 | pending |
| line-3 | line-3-0404-0536-s012061 | reverse | revenue | 3 | pending |
| line-3 | line-3-0250-0578-s015512 | reverse | revenue | 3 | pending |
| line-3 | line-3-0718-0449-s005036 | reverse | spare | 1 | pending |
| line-3 | line-3-0627-0474-s007064 | forward | spare | 1 | pending |
| line-3 | line-3-0627-0474-s007064 | reverse | spare | 1 | pending |
| line-3 | line-3-0557-0494-s008641 | forward | spare | 1 | pending |
| line-3 | line-3-0557-0494-s008641 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**121 trainsets exceed the reference platform envelope**, requiring **7,199.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0230-0021-s026440 | 4 | 2 | 2 | 119.0 |
| line-1-0419-0253-s019636 | 10 | 2 | 8 | 476.0 |
| line-1-0511-0351-s016621 | 10 | 2 | 8 | 476.0 |
| line-1-0569-0413-s014725 | 10 | 2 | 8 | 476.0 |
| line-1-0627-0474-s012825 | 10 | 4 | 6 | 357.0 |
| line-1-0692-0543-s010673 | 10 | 2 | 8 | 476.0 |
| line-1-0785-0641-s007661 | 10 | 2 | 8 | 476.0 |
| line-1-0877-0739-s004646 | 10 | 2 | 8 | 476.0 |
| line-1-1016-0841-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0301-0299-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0384-0407-s003023 | 8 | 2 | 6 | 357.0 |
| line-2-0470-0518-s006155 | 8 | 4 | 4 | 238.0 |
| line-2-0549-0621-s009057 | 8 | 2 | 6 | 357.0 |
| line-2-0606-0695-s011114 | 8 | 2 | 6 | 357.0 |
| line-2-0662-0767-s013159 | 8 | 2 | 6 | 357.0 |
| line-2-0718-0840-s015212 | 3 | 2 | 1 | 59.5 |
| line-3-0250-0578-s015512 | 3 | 2 | 1 | 59.5 |
| line-3-0404-0536-s012061 | 6 | 2 | 4 | 238.0 |
| line-3-0470-0518-s010592 | 6 | 4 | 2 | 119.0 |
| line-3-0557-0494-s008641 | 8 | 2 | 6 | 357.0 |
| line-3-0627-0474-s007064 | 8 | 4 | 4 | 238.0 |
| line-3-0718-0449-s005036 | 8 | 2 | 6 | 357.0 |
| line-3-0809-0424-s003009 | 8 | 2 | 6 | 357.0 |
| line-3-0938-0427-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Buraidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
