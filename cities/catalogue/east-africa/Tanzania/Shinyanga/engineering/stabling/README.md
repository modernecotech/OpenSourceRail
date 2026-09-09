# Station and depot overnight allocation

Plan: **26 trainsets at stations + 50 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0494-0328-s015942 | 50 | 2,450.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0031-0708-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0244-0502-s007009 | station | forward | revenue | 1 |
| line-1 | line-1-0244-0502-s007009 | station | reverse | revenue | 1 |
| line-1 | line-1-0371-0457-s010027 | station | forward | revenue | 1 |
| line-1 | line-1-0371-0457-s010027 | station | reverse | revenue | 1 |
| line-1 | line-1-0380-0374-s012522 | station | forward | revenue | 1 |
| line-1 | line-1-0380-0374-s012522 | station | reverse | revenue | 1 |
| line-1 | line-1-0494-0328-s015942 | station | reverse | revenue | 2 |
| line-2 | line-2-0254-0114-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0316-0339-s005201 | station | forward | revenue | 1 |
| line-2 | line-2-0316-0339-s005201 | station | reverse | revenue | 1 |
| line-2 | line-2-0380-0374-s006876 | station | forward | revenue | 1 |
| line-2 | line-2-0380-0374-s006876 | station | reverse | revenue | 1 |
| line-2 | line-2-0468-0382-s009583 | station | reverse | revenue | 2 |
| line-3 | line-3-0380-0374-s002061 | station | forward | revenue | 1 |
| line-3 | line-3-0380-0374-s002061 | station | reverse | revenue | 1 |
| line-3 | line-3-0422-0428-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0459-0299-s005315 | station | forward | revenue | 1 |
| line-3 | line-3-0459-0299-s005315 | station | reverse | revenue | 1 |
| line-3 | line-3-0661-0272-s011259 | station | reverse | revenue | 2 |
| line-1 | line-1-0494-0328-s015942 | depot | — | revenue | 19 |
| line-1 | line-1-0494-0328-s015942 | depot | — | spare | 2 |
| line-1 | line-1-0494-0328-s015942 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0494-0328-s015942 | depot | — | revenue | 10 |
| line-2 | line-1-0494-0328-s015942 | depot | — | spare | 1 |
| line-2 | line-1-0494-0328-s015942 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0494-0328-s015942 | depot | — | revenue | 13 |
| line-3 | line-1-0494-0328-s015942 | depot | — | spare | 2 |
| line-3 | line-1-0494-0328-s015942 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (12 trains), line-3 (16 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **50 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0031-0708-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0244-0502-s007009 | forward | revenue | 4 | pending |
| line-1 | line-1-0244-0502-s007009 | reverse | revenue | 4 | pending |
| line-1 | line-1-0371-0457-s010027 | forward | revenue | 4 | pending |
| line-1 | line-1-0371-0457-s010027 | reverse | revenue | 4 | pending |
| line-1 | line-1-0380-0374-s012522 | forward | revenue | 3 | pending |
| line-1 | line-1-0380-0374-s012522 | reverse | revenue | 3 | pending |
| line-1 | line-1-0494-0328-s015942 | reverse | revenue | 3 | pending |
| line-1 | line-1-0380-0374-s012522 | forward | spare | 1 | pending |
| line-1 | line-1-0380-0374-s012522 | reverse | spare | 1 | pending |
| line-1 | line-1-0494-0328-s015942 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0254-0114-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0316-0339-s005201 | forward | revenue | 3 | pending |
| line-2 | line-2-0316-0339-s005201 | reverse | revenue | 3 | pending |
| line-2 | line-2-0380-0374-s006876 | forward | revenue | 3 | pending |
| line-2 | line-2-0380-0374-s006876 | reverse | revenue | 3 | pending |
| line-2 | line-2-0468-0382-s009583 | reverse | revenue | 3 | pending |
| line-2 | line-2-0254-0114-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0316-0339-s005201 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0422-0428-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0380-0374-s002061 | forward | revenue | 4 | pending |
| line-3 | line-3-0380-0374-s002061 | reverse | revenue | 4 | pending |
| line-3 | line-3-0459-0299-s005315 | forward | revenue | 3 | pending |
| line-3 | line-3-0459-0299-s005315 | reverse | revenue | 3 | pending |
| line-3 | line-3-0661-0272-s011259 | reverse | revenue | 3 | pending |
| line-3 | line-3-0459-0299-s005315 | forward | spare | 1 | pending |
| line-3 | line-3-0459-0299-s005315 | reverse | spare | 1 | pending |
| line-3 | line-3-0661-0272-s011259 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**44 trainsets exceed the reference platform envelope**, requiring **2,156.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0031-0708-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0244-0502-s007009 | 8 | 2 | 6 | 294.0 |
| line-1-0371-0457-s010027 | 8 | 2 | 6 | 294.0 |
| line-1-0380-0374-s012522 | 8 | 4 | 4 | 196.0 |
| line-1-0494-0328-s015942 | 4 | 2 | 2 | 98.0 |
| line-2-0254-0114-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0316-0339-s005201 | 7 | 2 | 5 | 245.0 |
| line-2-0380-0374-s006876 | 6 | 4 | 2 | 98.0 |
| line-2-0468-0382-s009583 | 3 | 2 | 1 | 49.0 |
| line-3-0380-0374-s002061 | 8 | 4 | 4 | 196.0 |
| line-3-0422-0428-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0459-0299-s005315 | 8 | 2 | 6 | 294.0 |
| line-3-0661-0272-s011259 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Shinyanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
