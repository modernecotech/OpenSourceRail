# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 176 at depots = 220 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0335-0312-s023887 | line-1 | declared-depot | 63 | 3,748.5 | 11 |
| line-2-0876-0538-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 6 |
| line-3-0354-0936-s000000 | line-3 | declared-depot | 46 | 2,737.0 | 9 |
| line-4-0381-0362-s000000 | line-4 | declared-depot | 22 | 1,309.0 | 4 |
| line-5-0589-0264-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0335-0312-s023887 | station | reverse | revenue | 2 |
| line-1 | line-1-0381-0362-s022342 | station | forward | revenue | 1 |
| line-1 | line-1-0381-0362-s022342 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0545-s016686 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0545-s016686 | station | reverse | revenue | 1 |
| line-1 | line-1-0742-0746-s010535 | station | forward | revenue | 1 |
| line-1 | line-1-0742-0746-s010535 | station | reverse | revenue | 1 |
| line-1 | line-1-0939-1100-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0412-0236-s014522 | station | reverse | revenue | 2 |
| line-2 | line-2-0565-0374-s008182 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0374-s008182 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0382-s008022 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0382-s008022 | station | reverse | revenue | 1 |
| line-2 | line-2-0753-0471-s003015 | station | forward | revenue | 1 |
| line-2 | line-2-0753-0471-s003015 | station | reverse | revenue | 1 |
| line-2 | line-2-0876-0538-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0936-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0451-0702-s007001 | station | forward | revenue | 1 |
| line-3 | line-3-0451-0702-s007001 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0547-s010974 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0547-s010974 | station | reverse | revenue | 1 |
| line-3 | line-3-0565-0374-s015113 | station | forward | revenue | 1 |
| line-3 | line-3-0565-0374-s015113 | station | reverse | revenue | 1 |
| line-3 | line-3-0565-0382-s014953 | station | forward | revenue | 1 |
| line-3 | line-3-0565-0382-s014953 | station | reverse | revenue | 1 |
| line-3 | line-3-0569-0468-s012797 | station | forward | revenue | 1 |
| line-3 | line-3-0569-0468-s012797 | station | reverse | revenue | 1 |
| line-3 | line-3-0589-0264-s017592 | station | forward | revenue | 1 |
| line-3 | line-3-0589-0264-s017592 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0201-s019968 | station | reverse | revenue | 2 |
| line-4 | line-4-0114-0388-s007634 | station | reverse | revenue | 2 |
| line-4 | line-4-0381-0362-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0538-0086-s004935 | station | reverse | revenue | 2 |
| line-5 | line-5-0589-0264-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0335-0312-s023887 | depot | — | revenue | 56 |
| line-1 | line-1-0335-0312-s023887 | depot | — | spare | 6 |
| line-1 | line-1-0335-0312-s023887 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0876-0538-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0876-0538-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0876-0538-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0936-s000000 | depot | — | revenue | 40 |
| line-3 | line-3-0354-0936-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0354-0936-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0381-0362-s000000 | depot | — | revenue | 19 |
| line-4 | line-4-0381-0362-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0381-0362-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0589-0264-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0589-0264-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0589-0264-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/taif-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **220 trainsets at 22 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **198 revenue, 17 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **176 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0939-1100-s000000 | forward | revenue | 9 | pending |
| line-1 | line-1-0742-0746-s010535 | forward | revenue | 9 | pending |
| line-1 | line-1-0742-0746-s010535 | reverse | revenue | 8 | pending |
| line-1 | line-1-0554-0545-s016686 | forward | revenue | 8 | pending |
| line-1 | line-1-0554-0545-s016686 | reverse | revenue | 8 | pending |
| line-1 | line-1-0381-0362-s022342 | forward | revenue | 8 | pending |
| line-1 | line-1-0381-0362-s022342 | reverse | revenue | 8 | pending |
| line-1 | line-1-0335-0312-s023887 | reverse | revenue | 8 | pending |
| line-1 | line-1-0742-0746-s010535 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0545-s016686 | forward | spare | 1 | pending |
| line-1 | line-1-0554-0545-s016686 | reverse | spare | 1 | pending |
| line-1 | line-1-0381-0362-s022342 | forward | spare | 1 | pending |
| line-1 | line-1-0381-0362-s022342 | reverse | spare | 1 | pending |
| line-1 | line-1-0335-0312-s023887 | reverse | spare | 1 | pending |
| line-1 | line-1-0939-1100-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0753-0471-s003015 | forward | revenue | 5 | pending |
| line-2 | line-2-0753-0471-s003015 | reverse | revenue | 5 | pending |
| line-2 | line-2-0565-0382-s008022 | forward | revenue | 5 | pending |
| line-2 | line-2-0565-0382-s008022 | reverse | revenue | 5 | pending |
| line-2 | line-2-0565-0374-s008182 | forward | revenue | 5 | pending |
| line-2 | line-2-0565-0374-s008182 | reverse | revenue | 5 | pending |
| line-2 | line-2-0412-0236-s014522 | reverse | revenue | 4 | pending |
| line-2 | line-2-0412-0236-s014522 | reverse | spare | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0753-0471-s003015 | forward | spare | 1 | pending |
| line-2 | line-2-0753-0471-s003015 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0451-0702-s007001 | forward | revenue | 4 | pending |
| line-3 | line-3-0451-0702-s007001 | reverse | revenue | 4 | pending |
| line-3 | line-3-0555-0547-s010974 | forward | revenue | 4 | pending |
| line-3 | line-3-0555-0547-s010974 | reverse | revenue | 4 | pending |
| line-3 | line-3-0569-0468-s012797 | forward | revenue | 4 | pending |
| line-3 | line-3-0569-0468-s012797 | reverse | revenue | 4 | pending |
| line-3 | line-3-0565-0382-s014953 | forward | revenue | 4 | pending |
| line-3 | line-3-0565-0382-s014953 | reverse | revenue | 4 | pending |
| line-3 | line-3-0565-0374-s015113 | forward | revenue | 4 | pending |
| line-3 | line-3-0565-0374-s015113 | reverse | revenue | 4 | pending |
| line-3 | line-3-0589-0264-s017592 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0264-s017592 | reverse | revenue | 4 | pending |
| line-3 | line-3-0658-0201-s019968 | reverse | revenue | 4 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0451-0702-s007001 | forward | spare | 1 | pending |
| line-3 | line-3-0451-0702-s007001 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0547-s010974 | forward | spare | 1 | pending |
| line-3 | line-3-0555-0547-s010974 | reverse | spare | 1 | pending |
| line-3 | line-3-0569-0468-s012797 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0381-0362-s000000 | forward | revenue | 12 | pending |
| line-4 | line-4-0114-0388-s007634 | reverse | revenue | 11 | pending |
| line-4 | line-4-0114-0388-s007634 | reverse | spare | 1 | pending |
| line-4 | line-4-0381-0362-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0114-0388-s007634 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0589-0264-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0538-0086-s004935 | reverse | revenue | 7 | pending |
| line-5 | line-5-0589-0264-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0538-0086-s004935 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**160 trainsets exceed the reference platform envelope**, requiring **9,520.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0335-0312-s023887 | 9 | 2 | 7 | 416.5 |
| line-1-0381-0362-s022342 | 18 | 4 | 14 | 833.0 |
| line-1-0554-0545-s016686 | 18 | 4 | 14 | 833.0 |
| line-1-0742-0746-s010535 | 18 | 2 | 16 | 952.0 |
| line-1-0939-1100-s000000 | 10 | 2 | 8 | 476.0 |
| line-2-0412-0236-s014522 | 5 | 2 | 3 | 178.5 |
| line-2-0565-0374-s008182 | 10 | 4 | 6 | 357.0 |
| line-2-0565-0382-s008022 | 10 | 4 | 6 | 357.0 |
| line-2-0753-0471-s003015 | 12 | 2 | 10 | 595.0 |
| line-2-0876-0538-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0354-0936-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0451-0702-s007001 | 10 | 2 | 8 | 476.0 |
| line-3-0555-0547-s010974 | 10 | 4 | 6 | 357.0 |
| line-3-0565-0374-s015113 | 8 | 4 | 4 | 238.0 |
| line-3-0565-0382-s014953 | 8 | 4 | 4 | 238.0 |
| line-3-0569-0468-s012797 | 9 | 2 | 7 | 416.5 |
| line-3-0589-0264-s017592 | 8 | 4 | 4 | 238.0 |
| line-3-0658-0201-s019968 | 4 | 2 | 2 | 119.0 |
| line-4-0114-0388-s007634 | 13 | 2 | 11 | 654.5 |
| line-4-0381-0362-s000000 | 13 | 2 | 11 | 654.5 |
| line-5-0538-0086-s004935 | 8 | 2 | 6 | 357.0 |
| line-5-0589-0264-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Taif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
