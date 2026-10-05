# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 114 at depots = 148 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0737-0167-s023818 | line-1 | declared-depot | 58 | 3,451.0 | 11 |
| line-2-0375-0601-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0487-0404-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0198-1067-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0382-0826-s007012 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0826-s007012 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0694-s010424 | station | forward | revenue | 1 |
| line-1 | line-1-0461-0694-s010424 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0622-s012259 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0622-s012259 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0547-s014213 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0547-s014213 | station | reverse | revenue | 1 |
| line-1 | line-1-0602-0454-s016603 | station | forward | revenue | 1 |
| line-1 | line-1-0602-0454-s016603 | station | reverse | revenue | 1 |
| line-1 | line-1-0659-0358-s019065 | station | forward | revenue | 1 |
| line-1 | line-1-0659-0358-s019065 | station | reverse | revenue | 1 |
| line-1 | line-1-0716-0262-s021539 | station | forward | revenue | 1 |
| line-1 | line-1-0716-0262-s021539 | station | reverse | revenue | 1 |
| line-1 | line-1-0737-0167-s023818 | station | reverse | revenue | 2 |
| line-2 | line-2-0375-0601-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0475-0536-s002667 | station | forward | revenue | 1 |
| line-2 | line-2-0475-0536-s002667 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0454-s006031 | station | forward | revenue | 1 |
| line-2 | line-2-0601-0454-s006031 | station | reverse | revenue | 1 |
| line-2 | line-2-0928-0268-s014541 | station | reverse | revenue | 2 |
| line-3 | line-3-0455-0763-s007445 | station | reverse | revenue | 2 |
| line-3 | line-3-0461-0694-s006015 | station | forward | revenue | 1 |
| line-3 | line-3-0461-0694-s006015 | station | reverse | revenue | 1 |
| line-3 | line-3-0475-0536-s002739 | station | forward | revenue | 1 |
| line-3 | line-3-0475-0536-s002739 | station | reverse | revenue | 1 |
| line-3 | line-3-0487-0404-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0737-0167-s023818 | depot | — | revenue | 51 |
| line-1 | line-1-0737-0167-s023818 | depot | — | spare | 6 |
| line-1 | line-1-0737-0167-s023818 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0375-0601-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0375-0601-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0375-0601-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0487-0404-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0487-0404-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0487-0404-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/maroua-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **148 trainsets at 17 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **133 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **114 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0198-1067-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0382-0826-s007012 | forward | revenue | 5 | pending |
| line-1 | line-1-0382-0826-s007012 | reverse | revenue | 5 | pending |
| line-1 | line-1-0461-0694-s010424 | forward | revenue | 5 | pending |
| line-1 | line-1-0461-0694-s010424 | reverse | revenue | 5 | pending |
| line-1 | line-1-0503-0622-s012259 | forward | revenue | 4 | pending |
| line-1 | line-1-0503-0622-s012259 | reverse | revenue | 4 | pending |
| line-1 | line-1-0548-0547-s014213 | forward | revenue | 4 | pending |
| line-1 | line-1-0548-0547-s014213 | reverse | revenue | 4 | pending |
| line-1 | line-1-0602-0454-s016603 | forward | revenue | 4 | pending |
| line-1 | line-1-0602-0454-s016603 | reverse | revenue | 4 | pending |
| line-1 | line-1-0659-0358-s019065 | forward | revenue | 4 | pending |
| line-1 | line-1-0659-0358-s019065 | reverse | revenue | 4 | pending |
| line-1 | line-1-0716-0262-s021539 | forward | revenue | 4 | pending |
| line-1 | line-1-0716-0262-s021539 | reverse | revenue | 4 | pending |
| line-1 | line-1-0737-0167-s023818 | reverse | revenue | 4 | pending |
| line-1 | line-1-0503-0622-s012259 | forward | spare | 1 | pending |
| line-1 | line-1-0503-0622-s012259 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0547-s014213 | forward | spare | 1 | pending |
| line-1 | line-1-0548-0547-s014213 | reverse | spare | 1 | pending |
| line-1 | line-1-0602-0454-s016603 | forward | spare | 1 | pending |
| line-1 | line-1-0602-0454-s016603 | reverse | spare | 1 | pending |
| line-1 | line-1-0659-0358-s019065 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0375-0601-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0475-0536-s002667 | forward | revenue | 7 | pending |
| line-2 | line-2-0475-0536-s002667 | reverse | revenue | 7 | pending |
| line-2 | line-2-0601-0454-s006031 | forward | revenue | 7 | pending |
| line-2 | line-2-0601-0454-s006031 | reverse | revenue | 7 | pending |
| line-2 | line-2-0928-0268-s014541 | reverse | revenue | 6 | pending |
| line-2 | line-2-0928-0268-s014541 | reverse | spare | 1 | pending |
| line-2 | line-2-0375-0601-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0536-s002667 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0536-s002667 | reverse | spare | 1 | pending |
| line-2 | line-2-0601-0454-s006031 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0487-0404-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0475-0536-s002739 | forward | revenue | 4 | pending |
| line-3 | line-3-0475-0536-s002739 | reverse | revenue | 4 | pending |
| line-3 | line-3-0461-0694-s006015 | forward | revenue | 4 | pending |
| line-3 | line-3-0461-0694-s006015 | reverse | revenue | 4 | pending |
| line-3 | line-3-0455-0763-s007445 | reverse | revenue | 3 | pending |
| line-3 | line-3-0455-0763-s007445 | reverse | spare | 1 | pending |
| line-3 | line-3-0487-0404-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0475-0536-s002739 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**102 trainsets exceed the reference platform envelope**, requiring **6,069.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0198-1067-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0382-0826-s007012 | 10 | 2 | 8 | 476.0 |
| line-1-0461-0694-s010424 | 10 | 4 | 6 | 357.0 |
| line-1-0503-0622-s012259 | 10 | 2 | 8 | 476.0 |
| line-1-0548-0547-s014213 | 10 | 2 | 8 | 476.0 |
| line-1-0602-0454-s016603 | 10 | 4 | 6 | 357.0 |
| line-1-0659-0358-s019065 | 9 | 2 | 7 | 416.5 |
| line-1-0716-0262-s021539 | 8 | 2 | 6 | 357.0 |
| line-1-0737-0167-s023818 | 4 | 2 | 2 | 119.0 |
| line-2-0375-0601-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0475-0536-s002667 | 16 | 4 | 12 | 714.0 |
| line-2-0601-0454-s006031 | 15 | 4 | 11 | 654.5 |
| line-2-0928-0268-s014541 | 7 | 2 | 5 | 297.5 |
| line-3-0455-0763-s007445 | 4 | 2 | 2 | 119.0 |
| line-3-0461-0694-s006015 | 8 | 4 | 4 | 238.0 |
| line-3-0475-0536-s002739 | 9 | 4 | 5 | 297.5 |
| line-3-0487-0404-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Maroua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
