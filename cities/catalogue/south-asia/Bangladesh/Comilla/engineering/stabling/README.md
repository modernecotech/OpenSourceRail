# Station and depot overnight allocation

Plan: **42 trainsets at stations + 72 at depots = 114 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0647-0900-s020123 | line-1 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |
| line-2-0513-0710-s020342 | line-2 | declared-depot | 27 | 1,606.5 | 18 |
| line-3-0708-0301-s015054 | line-3 | storage-at-existing-powered-service-point | 18 | 1,071.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0430-0223-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0507-0407-s005071 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0407-s005071 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0538-s008090 | station | forward | revenue | 1 |
| line-1 | line-1-0511-0538-s008090 | station | reverse | revenue | 1 |
| line-1 | line-1-0558-0542-s009652 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0542-s009652 | station | reverse | revenue | 1 |
| line-1 | line-1-0618-0753-s016405 | station | forward | revenue | 1 |
| line-1 | line-1-0618-0753-s016405 | station | reverse | revenue | 1 |
| line-1 | line-1-0620-0607-s012703 | station | forward | revenue | 1 |
| line-1 | line-1-0620-0607-s012703 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0900-s020123 | station | reverse | revenue | 2 |
| line-2 | line-2-0513-0710-s020342 | station | reverse | revenue | 2 |
| line-2 | line-2-0558-0542-s015541 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0542-s015541 | station | reverse | revenue | 1 |
| line-2 | line-2-0560-0637-s017942 | station | forward | revenue | 1 |
| line-2 | line-2-0560-0637-s017942 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0480-s012867 | station | forward | revenue | 1 |
| line-2 | line-2-0616-0480-s012867 | station | reverse | revenue | 1 |
| line-2 | line-2-0714-0444-s009853 | station | forward | revenue | 1 |
| line-2 | line-2-0714-0444-s009853 | station | reverse | revenue | 1 |
| line-2 | line-2-0756-0332-s006850 | station | forward | revenue | 1 |
| line-2 | line-2-0756-0332-s006850 | station | reverse | revenue | 1 |
| line-2 | line-2-0923-0150-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0358-0684-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0651-s003001 | station | forward | revenue | 1 |
| line-3 | line-3-0480-0651-s003001 | station | reverse | revenue | 1 |
| line-3 | line-3-0508-0558-s006011 | station | forward | revenue | 1 |
| line-3 | line-3-0508-0558-s006011 | station | reverse | revenue | 1 |
| line-3 | line-3-0558-0542-s007212 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0542-s007212 | station | reverse | revenue | 1 |
| line-3 | line-3-0582-0432-s010643 | station | forward | revenue | 1 |
| line-3 | line-3-0582-0432-s010643 | station | reverse | revenue | 1 |
| line-3 | line-3-0639-0359-s012848 | station | forward | revenue | 1 |
| line-3 | line-3-0639-0359-s012848 | station | reverse | revenue | 1 |
| line-3 | line-3-0708-0301-s015054 | station | reverse | revenue | 2 |
| line-1 | line-1-0647-0900-s020123 | depot | — | revenue | 23 |
| line-1 | line-1-0647-0900-s020123 | depot | — | spare | 3 |
| line-1 | line-1-0647-0900-s020123 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0513-0710-s020342 | depot | — | revenue | 23 |
| line-2 | line-2-0513-0710-s020342 | depot | — | spare | 3 |
| line-2 | line-2-0513-0710-s020342 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0708-0301-s015054 | depot | — | revenue | 15 |
| line-3 | line-3-0708-0301-s015054 | depot | — | spare | 2 |
| line-3 | line-3-0708-0301-s015054 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/comilla-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **114 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **103 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **72 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0430-0223-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0507-0407-s005071 | forward | revenue | 3 | pending |
| line-1 | line-1-0507-0407-s005071 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0538-s008090 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0538-s008090 | reverse | revenue | 3 | pending |
| line-1 | line-1-0558-0542-s009652 | forward | revenue | 3 | pending |
| line-1 | line-1-0558-0542-s009652 | reverse | revenue | 3 | pending |
| line-1 | line-1-0620-0607-s012703 | forward | revenue | 3 | pending |
| line-1 | line-1-0620-0607-s012703 | reverse | revenue | 3 | pending |
| line-1 | line-1-0618-0753-s016405 | forward | revenue | 3 | pending |
| line-1 | line-1-0618-0753-s016405 | reverse | revenue | 3 | pending |
| line-1 | line-1-0647-0900-s020123 | reverse | revenue | 3 | pending |
| line-1 | line-1-0507-0407-s005071 | forward | spare | 1 | pending |
| line-1 | line-1-0507-0407-s005071 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0538-s008090 | forward | spare | 1 | pending |
| line-1 | line-1-0511-0538-s008090 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0923-0150-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0756-0332-s006850 | forward | revenue | 3 | pending |
| line-2 | line-2-0756-0332-s006850 | reverse | revenue | 3 | pending |
| line-2 | line-2-0714-0444-s009853 | forward | revenue | 3 | pending |
| line-2 | line-2-0714-0444-s009853 | reverse | revenue | 3 | pending |
| line-2 | line-2-0616-0480-s012867 | forward | revenue | 3 | pending |
| line-2 | line-2-0616-0480-s012867 | reverse | revenue | 3 | pending |
| line-2 | line-2-0558-0542-s015541 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0542-s015541 | reverse | revenue | 3 | pending |
| line-2 | line-2-0560-0637-s017942 | forward | revenue | 3 | pending |
| line-2 | line-2-0560-0637-s017942 | reverse | revenue | 3 | pending |
| line-2 | line-2-0513-0710-s020342 | reverse | revenue | 3 | pending |
| line-2 | line-2-0756-0332-s006850 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0332-s006850 | reverse | spare | 1 | pending |
| line-2 | line-2-0714-0444-s009853 | forward | spare | 1 | pending |
| line-2 | line-2-0714-0444-s009853 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0358-0684-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0480-0651-s003001 | forward | revenue | 3 | pending |
| line-3 | line-3-0480-0651-s003001 | reverse | revenue | 3 | pending |
| line-3 | line-3-0508-0558-s006011 | forward | revenue | 3 | pending |
| line-3 | line-3-0508-0558-s006011 | reverse | revenue | 3 | pending |
| line-3 | line-3-0558-0542-s007212 | forward | revenue | 2 | pending |
| line-3 | line-3-0558-0542-s007212 | reverse | revenue | 2 | pending |
| line-3 | line-3-0582-0432-s010643 | forward | revenue | 2 | pending |
| line-3 | line-3-0582-0432-s010643 | reverse | revenue | 2 | pending |
| line-3 | line-3-0639-0359-s012848 | forward | revenue | 2 | pending |
| line-3 | line-3-0639-0359-s012848 | reverse | revenue | 2 | pending |
| line-3 | line-3-0708-0301-s015054 | reverse | revenue | 2 | pending |
| line-3 | line-3-0558-0542-s007212 | forward | spare | 1 | pending |
| line-3 | line-3-0558-0542-s007212 | reverse | spare | 1 | pending |
| line-3 | line-3-0582-0432-s010643 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**62 trainsets exceed the reference platform envelope**, requiring **3,689.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0430-0223-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0507-0407-s005071 | 8 | 2 | 6 | 357.0 |
| line-1-0511-0538-s008090 | 8 | 4 | 4 | 238.0 |
| line-1-0558-0542-s009652 | 6 | 4 | 2 | 119.0 |
| line-1-0618-0753-s016405 | 6 | 2 | 4 | 238.0 |
| line-1-0620-0607-s012703 | 6 | 2 | 4 | 238.0 |
| line-1-0647-0900-s020123 | 3 | 2 | 1 | 59.5 |
| line-2-0513-0710-s020342 | 3 | 2 | 1 | 59.5 |
| line-2-0558-0542-s015541 | 6 | 4 | 2 | 119.0 |
| line-2-0560-0637-s017942 | 6 | 2 | 4 | 238.0 |
| line-2-0616-0480-s012867 | 6 | 2 | 4 | 238.0 |
| line-2-0714-0444-s009853 | 8 | 2 | 6 | 357.0 |
| line-2-0756-0332-s006850 | 8 | 2 | 6 | 357.0 |
| line-2-0923-0150-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0358-0684-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0480-0651-s003001 | 6 | 2 | 4 | 238.0 |
| line-3-0508-0558-s006011 | 6 | 4 | 2 | 119.0 |
| line-3-0558-0542-s007212 | 6 | 4 | 2 | 119.0 |
| line-3-0582-0432-s010643 | 5 | 2 | 3 | 178.5 |
| line-3-0639-0359-s012848 | 4 | 2 | 2 | 119.0 |
| line-3-0708-0301-s015054 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Comilla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
