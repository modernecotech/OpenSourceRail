# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **50 trainsets at stations + 184 at depots = 234 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0118-s026730 | line-1 | declared-depot | 67 | 3,986.5 | 12 |
| line-2-0265-0473-s000000 | line-2 | declared-depot | 49 | 2,915.5 | 10 |
| line-3-0383-0212-s000000 | line-3 | declared-depot | 68 | 4,046.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0118-s026730 | station | reverse | revenue | 2 |
| line-1 | line-1-0448-0475-s016711 | station | forward | revenue | 1 |
| line-1 | line-1-0448-0475-s016711 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0584-s013543 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0584-s013543 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0672-s010979 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0672-s010979 | station | reverse | revenue | 1 |
| line-1 | line-1-0698-0776-s007976 | station | forward | revenue | 1 |
| line-1 | line-1-0698-0776-s007976 | station | reverse | revenue | 1 |
| line-1 | line-1-0783-0877-s005017 | station | forward | revenue | 1 |
| line-1 | line-1-0783-0877-s005017 | station | reverse | revenue | 1 |
| line-1 | line-1-0785-0879-s004949 | station | forward | revenue | 1 |
| line-1 | line-1-0785-0879-s004949 | station | reverse | revenue | 1 |
| line-1 | line-1-0811-0902-s004156 | station | forward | revenue | 1 |
| line-1 | line-1-0811-0902-s004156 | station | reverse | revenue | 1 |
| line-1 | line-1-0914-1037-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0265-0473-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0371-0556-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0371-0556-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0478-0639-s006045 | station | forward | revenue | 1 |
| line-2 | line-2-0478-0639-s006045 | station | reverse | revenue | 1 |
| line-2 | line-2-0584-0722-s009052 | station | forward | revenue | 1 |
| line-2 | line-2-0584-0722-s009052 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0805-s012059 | station | forward | revenue | 1 |
| line-2 | line-2-0690-0805-s012059 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0876-s014674 | station | forward | revenue | 1 |
| line-2 | line-2-0782-0876-s014674 | station | reverse | revenue | 1 |
| line-2 | line-2-0785-0879-s014759 | station | forward | revenue | 1 |
| line-2 | line-2-0785-0879-s014759 | station | reverse | revenue | 1 |
| line-2 | line-2-0811-0902-s015592 | station | forward | revenue | 1 |
| line-2 | line-2-0811-0902-s015592 | station | reverse | revenue | 1 |
| line-2 | line-2-0894-1095-s020938 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0482-0385-s004664 | station | forward | revenue | 1 |
| line-3 | line-3-0482-0385-s004664 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0460-s007683 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0460-s007683 | station | reverse | revenue | 1 |
| line-3 | line-3-0645-0571-s010689 | station | forward | revenue | 1 |
| line-3 | line-3-0645-0571-s010689 | station | reverse | revenue | 1 |
| line-3 | line-3-0736-0700-s014199 | station | forward | revenue | 1 |
| line-3 | line-3-0736-0700-s014199 | station | reverse | revenue | 1 |
| line-3 | line-3-0827-0829-s017709 | station | forward | revenue | 1 |
| line-3 | line-3-0827-0829-s017709 | station | reverse | revenue | 1 |
| line-3 | line-3-1082-1083-s026528 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0118-s026730 | depot | — | revenue | 59 |
| line-1 | line-1-0215-0118-s026730 | depot | — | spare | 7 |
| line-1 | line-1-0215-0118-s026730 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0265-0473-s000000 | depot | — | revenue | 42 |
| line-2 | line-2-0265-0473-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0265-0473-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0383-0212-s000000 | depot | — | revenue | 60 |
| line-3 | line-3-0383-0212-s000000 | depot | — | spare | 7 |
| line-3 | line-3-0383-0212-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/pokhara-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **234 trainsets at 25 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **211 revenue, 20 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **184 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **25 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0914-1037-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0811-0902-s004156 | forward | revenue | 5 | pending |
| line-1 | line-1-0811-0902-s004156 | reverse | revenue | 5 | pending |
| line-1 | line-1-0785-0879-s004949 | forward | revenue | 5 | pending |
| line-1 | line-1-0785-0879-s004949 | reverse | revenue | 5 | pending |
| line-1 | line-1-0783-0877-s005017 | forward | revenue | 5 | pending |
| line-1 | line-1-0783-0877-s005017 | reverse | revenue | 5 | pending |
| line-1 | line-1-0698-0776-s007976 | forward | revenue | 5 | pending |
| line-1 | line-1-0698-0776-s007976 | reverse | revenue | 5 | pending |
| line-1 | line-1-0612-0672-s010979 | forward | revenue | 5 | pending |
| line-1 | line-1-0612-0672-s010979 | reverse | revenue | 5 | pending |
| line-1 | line-1-0539-0584-s013543 | forward | revenue | 5 | pending |
| line-1 | line-1-0539-0584-s013543 | reverse | revenue | 5 | pending |
| line-1 | line-1-0448-0475-s016711 | forward | revenue | 4 | pending |
| line-1 | line-1-0448-0475-s016711 | reverse | revenue | 4 | pending |
| line-1 | line-1-0215-0118-s026730 | reverse | revenue | 4 | pending |
| line-1 | line-1-0448-0475-s016711 | forward | spare | 1 | pending |
| line-1 | line-1-0448-0475-s016711 | reverse | spare | 1 | pending |
| line-1 | line-1-0215-0118-s026730 | reverse | spare | 1 | pending |
| line-1 | line-1-0914-1037-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0811-0902-s004156 | forward | spare | 1 | pending |
| line-1 | line-1-0811-0902-s004156 | reverse | spare | 1 | pending |
| line-1 | line-1-0785-0879-s004949 | forward | spare | 1 | pending |
| line-1 | line-1-0785-0879-s004949 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0371-0556-s003018 | forward | revenue | 4 | pending |
| line-2 | line-2-0371-0556-s003018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0478-0639-s006045 | forward | revenue | 4 | pending |
| line-2 | line-2-0478-0639-s006045 | reverse | revenue | 4 | pending |
| line-2 | line-2-0584-0722-s009052 | forward | revenue | 4 | pending |
| line-2 | line-2-0584-0722-s009052 | reverse | revenue | 4 | pending |
| line-2 | line-2-0690-0805-s012059 | forward | revenue | 4 | pending |
| line-2 | line-2-0690-0805-s012059 | reverse | revenue | 4 | pending |
| line-2 | line-2-0782-0876-s014674 | forward | revenue | 4 | pending |
| line-2 | line-2-0782-0876-s014674 | reverse | revenue | 4 | pending |
| line-2 | line-2-0785-0879-s014759 | forward | revenue | 4 | pending |
| line-2 | line-2-0785-0879-s014759 | reverse | revenue | 3 | pending |
| line-2 | line-2-0811-0902-s015592 | forward | revenue | 3 | pending |
| line-2 | line-2-0811-0902-s015592 | reverse | revenue | 3 | pending |
| line-2 | line-2-0894-1095-s020938 | reverse | revenue | 3 | pending |
| line-2 | line-2-0785-0879-s014759 | reverse | spare | 1 | pending |
| line-2 | line-2-0811-0902-s015592 | forward | spare | 1 | pending |
| line-2 | line-2-0811-0902-s015592 | reverse | spare | 1 | pending |
| line-2 | line-2-0894-1095-s020938 | reverse | spare | 1 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0371-0556-s003018 | forward | spare | 1 | pending |
| line-2 | line-2-0371-0556-s003018 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0482-0385-s004664 | forward | revenue | 7 | pending |
| line-3 | line-3-0482-0385-s004664 | reverse | revenue | 6 | pending |
| line-3 | line-3-0567-0460-s007683 | forward | revenue | 6 | pending |
| line-3 | line-3-0567-0460-s007683 | reverse | revenue | 6 | pending |
| line-3 | line-3-0645-0571-s010689 | forward | revenue | 6 | pending |
| line-3 | line-3-0645-0571-s010689 | reverse | revenue | 6 | pending |
| line-3 | line-3-0736-0700-s014199 | forward | revenue | 6 | pending |
| line-3 | line-3-0736-0700-s014199 | reverse | revenue | 6 | pending |
| line-3 | line-3-0827-0829-s017709 | forward | revenue | 6 | pending |
| line-3 | line-3-0827-0829-s017709 | reverse | revenue | 6 | pending |
| line-3 | line-3-1082-1083-s026528 | reverse | revenue | 6 | pending |
| line-3 | line-3-0482-0385-s004664 | reverse | spare | 1 | pending |
| line-3 | line-3-0567-0460-s007683 | forward | spare | 1 | pending |
| line-3 | line-3-0567-0460-s007683 | reverse | spare | 1 | pending |
| line-3 | line-3-0645-0571-s010689 | forward | spare | 1 | pending |
| line-3 | line-3-0645-0571-s010689 | reverse | spare | 1 | pending |
| line-3 | line-3-0736-0700-s014199 | forward | spare | 1 | pending |
| line-3 | line-3-0736-0700-s014199 | reverse | spare | 1 | pending |
| line-3 | line-3-0827-0829-s017709 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**168 trainsets exceed the reference platform envelope**, requiring **9,996.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0118-s026730 | 5 | 2 | 3 | 178.5 |
| line-1-0448-0475-s016711 | 10 | 2 | 8 | 476.0 |
| line-1-0539-0584-s013543 | 10 | 2 | 8 | 476.0 |
| line-1-0612-0672-s010979 | 10 | 2 | 8 | 476.0 |
| line-1-0698-0776-s007976 | 10 | 4 | 6 | 357.0 |
| line-1-0783-0877-s005017 | 10 | 4 | 6 | 357.0 |
| line-1-0785-0879-s004949 | 12 | 4 | 8 | 476.0 |
| line-1-0811-0902-s004156 | 12 | 4 | 8 | 476.0 |
| line-1-0914-1037-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0265-0473-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0371-0556-s003018 | 10 | 2 | 8 | 476.0 |
| line-2-0478-0639-s006045 | 8 | 2 | 6 | 357.0 |
| line-2-0584-0722-s009052 | 8 | 2 | 6 | 357.0 |
| line-2-0690-0805-s012059 | 8 | 4 | 4 | 238.0 |
| line-2-0782-0876-s014674 | 8 | 4 | 4 | 238.0 |
| line-2-0785-0879-s014759 | 8 | 4 | 4 | 238.0 |
| line-2-0811-0902-s015592 | 8 | 4 | 4 | 238.0 |
| line-2-0894-1095-s020938 | 4 | 2 | 2 | 119.0 |
| line-3-0383-0212-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0482-0385-s004664 | 14 | 2 | 12 | 714.0 |
| line-3-0567-0460-s007683 | 14 | 2 | 12 | 714.0 |
| line-3-0645-0571-s010689 | 14 | 2 | 12 | 714.0 |
| line-3-0736-0700-s014199 | 14 | 2 | 12 | 714.0 |
| line-3-0827-0829-s017709 | 13 | 2 | 11 | 654.5 |
| line-3-1082-1083-s026528 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Pokhara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
