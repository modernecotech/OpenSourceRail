# Station and depot overnight allocation

Plan: **40 trainsets at stations + 85 at depots = 125 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0335-0312-s025733 | 85 | 5,057.5 | 19 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0335-0312-s025733 | station | reverse | revenue | 2 |
| line-1 | line-1-0475-0431-s019851 | station | forward | revenue | 1 |
| line-1 | line-1-0475-0431-s019851 | station | reverse | revenue | 1 |
| line-1 | line-1-0492-0498-s017758 | station | forward | revenue | 1 |
| line-1 | line-1-0492-0498-s017758 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0536-s015654 | station | forward | revenue | 1 |
| line-1 | line-1-0566-0536-s015654 | station | reverse | revenue | 1 |
| line-1 | line-1-0618-0605-s013831 | station | forward | revenue | 1 |
| line-1 | line-1-0618-0605-s013831 | station | reverse | revenue | 1 |
| line-1 | line-1-0734-0682-s010826 | station | forward | revenue | 1 |
| line-1 | line-1-0734-0682-s010826 | station | reverse | revenue | 1 |
| line-1 | line-1-0828-0834-s007008 | station | forward | revenue | 1 |
| line-1 | line-1-0828-0834-s007008 | station | reverse | revenue | 1 |
| line-1 | line-1-0939-1100-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0412-0236-s014522 | station | reverse | revenue | 2 |
| line-2 | line-2-0544-0350-s009045 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0350-s009045 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0417-s006026 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0417-s006026 | station | reverse | revenue | 1 |
| line-2 | line-2-0753-0471-s003015 | station | forward | revenue | 1 |
| line-2 | line-2-0753-0471-s003015 | station | reverse | revenue | 1 |
| line-2 | line-2-0876-0538-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0936-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0460-0693-s007010 | station | forward | revenue | 1 |
| line-3 | line-3-0460-0693-s007010 | station | reverse | revenue | 1 |
| line-3 | line-3-0503-0610-s009026 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0610-s009026 | station | reverse | revenue | 1 |
| line-3 | line-3-0566-0536-s011028 | station | forward | revenue | 1 |
| line-3 | line-3-0566-0536-s011028 | station | reverse | revenue | 1 |
| line-3 | line-3-0569-0468-s012462 | station | forward | revenue | 1 |
| line-3 | line-3-0569-0468-s012462 | station | reverse | revenue | 1 |
| line-3 | line-3-0588-0344-s015475 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0344-s015475 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0201-s019239 | station | reverse | revenue | 2 |
| line-1 | line-1-0335-0312-s025733 | depot | — | revenue | 32 |
| line-1 | line-1-0335-0312-s025733 | depot | — | spare | 4 |
| line-1 | line-1-0335-0312-s025733 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0335-0312-s025733 | depot | — | revenue | 17 |
| line-2 | line-1-0335-0312-s025733 | depot | — | spare | 2 |
| line-2 | line-1-0335-0312-s025733 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0335-0312-s025733 | depot | — | revenue | 24 |
| line-3 | line-1-0335-0312-s025733 | depot | — | spare | 3 |
| line-3 | line-1-0335-0312-s025733 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (20 trains), line-3 (28 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **125 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **85 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0939-1100-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0828-0834-s007008 | forward | revenue | 4 | pending |
| line-1 | line-1-0828-0834-s007008 | reverse | revenue | 4 | pending |
| line-1 | line-1-0734-0682-s010826 | forward | revenue | 4 | pending |
| line-1 | line-1-0734-0682-s010826 | reverse | revenue | 4 | pending |
| line-1 | line-1-0618-0605-s013831 | forward | revenue | 4 | pending |
| line-1 | line-1-0618-0605-s013831 | reverse | revenue | 3 | pending |
| line-1 | line-1-0566-0536-s015654 | forward | revenue | 3 | pending |
| line-1 | line-1-0566-0536-s015654 | reverse | revenue | 3 | pending |
| line-1 | line-1-0492-0498-s017758 | forward | revenue | 3 | pending |
| line-1 | line-1-0492-0498-s017758 | reverse | revenue | 3 | pending |
| line-1 | line-1-0475-0431-s019851 | forward | revenue | 3 | pending |
| line-1 | line-1-0475-0431-s019851 | reverse | revenue | 3 | pending |
| line-1 | line-1-0335-0312-s025733 | reverse | revenue | 3 | pending |
| line-1 | line-1-0618-0605-s013831 | reverse | spare | 1 | pending |
| line-1 | line-1-0566-0536-s015654 | forward | spare | 1 | pending |
| line-1 | line-1-0566-0536-s015654 | reverse | spare | 1 | pending |
| line-1 | line-1-0492-0498-s017758 | forward | spare | 1 | pending |
| line-1 | line-1-0492-0498-s017758 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0753-0471-s003015 | forward | revenue | 4 | pending |
| line-2 | line-2-0753-0471-s003015 | reverse | revenue | 4 | pending |
| line-2 | line-2-0626-0417-s006026 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0417-s006026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0544-0350-s009045 | forward | revenue | 3 | pending |
| line-2 | line-2-0544-0350-s009045 | reverse | revenue | 3 | pending |
| line-2 | line-2-0412-0236-s014522 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0417-s006026 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0417-s006026 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0350-s009045 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0460-0693-s007010 | forward | revenue | 4 | pending |
| line-3 | line-3-0460-0693-s007010 | reverse | revenue | 3 | pending |
| line-3 | line-3-0503-0610-s009026 | forward | revenue | 3 | pending |
| line-3 | line-3-0503-0610-s009026 | reverse | revenue | 3 | pending |
| line-3 | line-3-0566-0536-s011028 | forward | revenue | 3 | pending |
| line-3 | line-3-0566-0536-s011028 | reverse | revenue | 3 | pending |
| line-3 | line-3-0569-0468-s012462 | forward | revenue | 3 | pending |
| line-3 | line-3-0569-0468-s012462 | reverse | revenue | 3 | pending |
| line-3 | line-3-0588-0344-s015475 | forward | revenue | 3 | pending |
| line-3 | line-3-0588-0344-s015475 | reverse | revenue | 3 | pending |
| line-3 | line-3-0658-0201-s019239 | reverse | revenue | 3 | pending |
| line-3 | line-3-0460-0693-s007010 | reverse | spare | 1 | pending |
| line-3 | line-3-0503-0610-s009026 | forward | spare | 1 | pending |
| line-3 | line-3-0503-0610-s009026 | reverse | spare | 1 | pending |
| line-3 | line-3-0566-0536-s011028 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**81 trainsets exceed the reference platform envelope**, requiring **4,819.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0335-0312-s025733 | 3 | 2 | 1 | 59.5 |
| line-1-0475-0431-s019851 | 6 | 2 | 4 | 238.0 |
| line-1-0492-0498-s017758 | 8 | 2 | 6 | 357.0 |
| line-1-0566-0536-s015654 | 8 | 4 | 4 | 238.0 |
| line-1-0618-0605-s013831 | 8 | 2 | 6 | 357.0 |
| line-1-0734-0682-s010826 | 8 | 2 | 6 | 357.0 |
| line-1-0828-0834-s007008 | 8 | 2 | 6 | 357.0 |
| line-1-0939-1100-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0412-0236-s014522 | 3 | 2 | 1 | 59.5 |
| line-2-0544-0350-s009045 | 7 | 2 | 5 | 297.5 |
| line-2-0626-0417-s006026 | 8 | 2 | 6 | 357.0 |
| line-2-0753-0471-s003015 | 8 | 2 | 6 | 357.0 |
| line-2-0876-0538-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0354-0936-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0460-0693-s007010 | 8 | 2 | 6 | 357.0 |
| line-3-0503-0610-s009026 | 8 | 2 | 6 | 357.0 |
| line-3-0566-0536-s011028 | 7 | 4 | 3 | 178.5 |
| line-3-0569-0468-s012462 | 6 | 2 | 4 | 238.0 |
| line-3-0588-0344-s015475 | 6 | 2 | 4 | 238.0 |
| line-3-0658-0201-s019239 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Taif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
