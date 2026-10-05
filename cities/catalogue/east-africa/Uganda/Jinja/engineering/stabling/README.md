# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 48 at depots = 90 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0143-0732-s000000 | line-1 | declared-depot | 14 | 686.0 | 4 |
| line-2-0277-0213-s017376 | line-2 | declared-depot | 19 | 931.0 | 5 |
| line-3-0732-0095-s000000 | line-3 | declared-depot | 15 | 735.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0143-0732-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0274-0592-s004769 | station | forward | revenue | 1 |
| line-1 | line-1-0274-0592-s004769 | station | reverse | revenue | 1 |
| line-1 | line-1-0374-0503-s007787 | station | forward | revenue | 1 |
| line-1 | line-1-0374-0503-s007787 | station | reverse | revenue | 1 |
| line-1 | line-1-0463-0424-s010456 | station | forward | revenue | 1 |
| line-1 | line-1-0463-0424-s010456 | station | reverse | revenue | 1 |
| line-1 | line-1-0508-0384-s011828 | station | forward | revenue | 1 |
| line-1 | line-1-0508-0384-s011828 | station | reverse | revenue | 1 |
| line-1 | line-1-0512-0380-s011941 | station | forward | revenue | 1 |
| line-1 | line-1-0512-0380-s011941 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0349-s012992 | station | reverse | revenue | 2 |
| line-2 | line-2-0277-0213-s017376 | station | reverse | revenue | 2 |
| line-2 | line-2-0372-0281-s014807 | station | forward | revenue | 1 |
| line-2 | line-2-0372-0281-s014807 | station | reverse | revenue | 1 |
| line-2 | line-2-0467-0348-s012261 | station | forward | revenue | 1 |
| line-2 | line-2-0467-0348-s012261 | station | reverse | revenue | 1 |
| line-2 | line-2-0469-0345-s007508 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0345-s007508 | station | reverse | revenue | 1 |
| line-2 | line-2-0508-0384-s008611 | station | forward | revenue | 1 |
| line-2 | line-2-0508-0384-s008611 | station | reverse | revenue | 1 |
| line-2 | line-2-0512-0380-s011023 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0380-s011023 | station | reverse | revenue | 1 |
| line-2 | line-2-0513-0313-s005634 | station | forward | revenue | 1 |
| line-2 | line-2-0513-0313-s005634 | station | reverse | revenue | 1 |
| line-2 | line-2-0648-0466-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0315-0459-s012787 | station | reverse | revenue | 2 |
| line-3 | line-3-0413-0387-s010043 | station | forward | revenue | 1 |
| line-3 | line-3-0413-0387-s010043 | station | reverse | revenue | 1 |
| line-3 | line-3-0467-0348-s008588 | station | forward | revenue | 1 |
| line-3 | line-3-0467-0348-s008588 | station | reverse | revenue | 1 |
| line-3 | line-3-0469-0345-s008517 | station | forward | revenue | 1 |
| line-3 | line-3-0469-0345-s008517 | station | reverse | revenue | 1 |
| line-3 | line-3-0513-0313-s007313 | station | forward | revenue | 1 |
| line-3 | line-3-0513-0313-s007313 | station | reverse | revenue | 1 |
| line-3 | line-3-0732-0095-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0143-0732-s000000 | depot | — | revenue | 11 |
| line-1 | line-1-0143-0732-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0143-0732-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0277-0213-s017376 | depot | — | revenue | 15 |
| line-2 | line-2-0277-0213-s017376 | depot | — | spare | 3 |
| line-2 | line-2-0277-0213-s017376 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0732-0095-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0732-0095-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0732-0095-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jinja-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **90 trainsets at 21 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **80 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **48 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0143-0732-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0274-0592-s004769 | forward | revenue | 2 | pending |
| line-1 | line-1-0274-0592-s004769 | reverse | revenue | 2 | pending |
| line-1 | line-1-0374-0503-s007787 | forward | revenue | 2 | pending |
| line-1 | line-1-0374-0503-s007787 | reverse | revenue | 2 | pending |
| line-1 | line-1-0463-0424-s010456 | forward | revenue | 2 | pending |
| line-1 | line-1-0463-0424-s010456 | reverse | revenue | 2 | pending |
| line-1 | line-1-0508-0384-s011828 | forward | revenue | 2 | pending |
| line-1 | line-1-0508-0384-s011828 | reverse | revenue | 2 | pending |
| line-1 | line-1-0512-0380-s011941 | forward | revenue | 2 | pending |
| line-1 | line-1-0512-0380-s011941 | reverse | revenue | 2 | pending |
| line-1 | line-1-0547-0349-s012992 | reverse | revenue | 2 | pending |
| line-1 | line-1-0274-0592-s004769 | forward | spare | 1 | pending |
| line-1 | line-1-0274-0592-s004769 | reverse | spare | 1 | pending |
| line-1 | line-1-0374-0503-s007787 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0648-0466-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0313-s005634 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0313-s005634 | reverse | revenue | 3 | pending |
| line-2 | line-2-0469-0345-s007508 | forward | revenue | 2 | pending |
| line-2 | line-2-0469-0345-s007508 | reverse | revenue | 2 | pending |
| line-2 | line-2-0508-0384-s008611 | forward | revenue | 2 | pending |
| line-2 | line-2-0508-0384-s008611 | reverse | revenue | 2 | pending |
| line-2 | line-2-0512-0380-s011023 | forward | revenue | 2 | pending |
| line-2 | line-2-0512-0380-s011023 | reverse | revenue | 2 | pending |
| line-2 | line-2-0467-0348-s012261 | forward | revenue | 2 | pending |
| line-2 | line-2-0467-0348-s012261 | reverse | revenue | 2 | pending |
| line-2 | line-2-0372-0281-s014807 | forward | revenue | 2 | pending |
| line-2 | line-2-0372-0281-s014807 | reverse | revenue | 2 | pending |
| line-2 | line-2-0277-0213-s017376 | reverse | revenue | 2 | pending |
| line-2 | line-2-0469-0345-s007508 | forward | spare | 1 | pending |
| line-2 | line-2-0469-0345-s007508 | reverse | spare | 1 | pending |
| line-2 | line-2-0508-0384-s008611 | forward | spare | 1 | pending |
| line-2 | line-2-0508-0384-s008611 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0732-0095-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0513-0313-s007313 | forward | revenue | 3 | pending |
| line-3 | line-3-0513-0313-s007313 | reverse | revenue | 3 | pending |
| line-3 | line-3-0469-0345-s008517 | forward | revenue | 3 | pending |
| line-3 | line-3-0469-0345-s008517 | reverse | revenue | 2 | pending |
| line-3 | line-3-0467-0348-s008588 | forward | revenue | 2 | pending |
| line-3 | line-3-0467-0348-s008588 | reverse | revenue | 2 | pending |
| line-3 | line-3-0413-0387-s010043 | forward | revenue | 2 | pending |
| line-3 | line-3-0413-0387-s010043 | reverse | revenue | 2 | pending |
| line-3 | line-3-0315-0459-s012787 | reverse | revenue | 2 | pending |
| line-3 | line-3-0469-0345-s008517 | reverse | spare | 1 | pending |
| line-3 | line-3-0467-0348-s008588 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0348-s008588 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,372.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0143-0732-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0274-0592-s004769 | 6 | 2 | 4 | 196.0 |
| line-1-0374-0503-s007787 | 5 | 2 | 3 | 147.0 |
| line-1-0463-0424-s010456 | 4 | 2 | 2 | 98.0 |
| line-1-0508-0384-s011828 | 4 | 4 | 0 | 0.0 |
| line-1-0512-0380-s011941 | 4 | 4 | 0 | 0.0 |
| line-1-0547-0349-s012992 | 2 | 2 | 0 | 0.0 |
| line-2-0277-0213-s017376 | 2 | 2 | 0 | 0.0 |
| line-2-0372-0281-s014807 | 4 | 2 | 2 | 98.0 |
| line-2-0467-0348-s012261 | 4 | 4 | 0 | 0.0 |
| line-2-0469-0345-s007508 | 6 | 4 | 2 | 98.0 |
| line-2-0508-0384-s008611 | 6 | 4 | 2 | 98.0 |
| line-2-0512-0380-s011023 | 4 | 4 | 0 | 0.0 |
| line-2-0513-0313-s005634 | 6 | 4 | 2 | 98.0 |
| line-2-0648-0466-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0315-0459-s012787 | 2 | 2 | 0 | 0.0 |
| line-3-0413-0387-s010043 | 4 | 2 | 2 | 98.0 |
| line-3-0467-0348-s008588 | 6 | 4 | 2 | 98.0 |
| line-3-0469-0345-s008517 | 6 | 4 | 2 | 98.0 |
| line-3-0513-0313-s007313 | 6 | 4 | 2 | 98.0 |
| line-3-0732-0095-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Jinja/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
