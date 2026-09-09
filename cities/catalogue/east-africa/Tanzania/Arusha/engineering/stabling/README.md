# Station and depot overnight allocation

Plan: **40 trainsets at stations + 113 at depots = 153 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0085-0118-s025108 | 113 | 6,723.5 | 23 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0216-0447-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0365-0547-s003867 | station | forward | revenue | 1 |
| line-1 | line-1-0365-0547-s003867 | station | reverse | revenue | 1 |
| line-1 | line-1-0463-0507-s006869 | station | forward | revenue | 1 |
| line-1 | line-1-0463-0507-s006869 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0557-s010230 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0557-s010230 | station | reverse | revenue | 1 |
| line-1 | line-1-0575-0629-s012881 | station | forward | revenue | 1 |
| line-1 | line-1-0575-0629-s012881 | station | reverse | revenue | 1 |
| line-1 | line-1-0690-0685-s015888 | station | forward | revenue | 1 |
| line-1 | line-1-0690-0685-s015888 | station | reverse | revenue | 1 |
| line-1 | line-1-0799-0721-s018734 | station | reverse | revenue | 2 |
| line-2 | line-2-0418-1069-s020043 | station | reverse | revenue | 2 |
| line-2 | line-2-0458-0842-s014542 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0842-s014542 | station | reverse | revenue | 1 |
| line-2 | line-2-0480-0610-s007128 | station | forward | revenue | 1 |
| line-2 | line-2-0480-0610-s007128 | station | reverse | revenue | 1 |
| line-2 | line-2-0514-0687-s009044 | station | forward | revenue | 1 |
| line-2 | line-2-0514-0687-s009044 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0557-s005202 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0557-s005202 | station | reverse | revenue | 1 |
| line-2 | line-2-0571-0465-s003009 | station | forward | revenue | 1 |
| line-2 | line-2-0571-0465-s003009 | station | reverse | revenue | 1 |
| line-2 | line-2-0674-0383-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0085-0118-s025108 | station | reverse | revenue | 2 |
| line-3 | line-3-0397-0394-s016032 | station | forward | revenue | 1 |
| line-3 | line-3-0397-0394-s016032 | station | reverse | revenue | 1 |
| line-3 | line-3-0494-0476-s012532 | station | forward | revenue | 1 |
| line-3 | line-3-0494-0476-s012532 | station | reverse | revenue | 1 |
| line-3 | line-3-0544-0557-s010056 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0557-s010056 | station | reverse | revenue | 1 |
| line-3 | line-3-0665-0604-s006517 | station | forward | revenue | 1 |
| line-3 | line-3-0665-0604-s006517 | station | reverse | revenue | 1 |
| line-3 | line-3-0919-0713-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0085-0118-s025108 | depot | — | revenue | 27 |
| line-1 | line-3-0085-0118-s025108 | depot | — | spare | 4 |
| line-1 | line-3-0085-0118-s025108 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0085-0118-s025108 | depot | — | revenue | 28 |
| line-2 | line-3-0085-0118-s025108 | depot | — | spare | 4 |
| line-2 | line-3-0085-0118-s025108 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0085-0118-s025108 | depot | — | revenue | 42 |
| line-3 | line-3-0085-0118-s025108 | depot | — | spare | 5 |
| line-3 | line-3-0085-0118-s025108 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (32 trains), line-2 (33 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **153 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **137 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **113 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0216-0447-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0365-0547-s003867 | forward | revenue | 4 | pending |
| line-1 | line-1-0365-0547-s003867 | reverse | revenue | 4 | pending |
| line-1 | line-1-0463-0507-s006869 | forward | revenue | 4 | pending |
| line-1 | line-1-0463-0507-s006869 | reverse | revenue | 4 | pending |
| line-1 | line-1-0544-0557-s010230 | forward | revenue | 3 | pending |
| line-1 | line-1-0544-0557-s010230 | reverse | revenue | 3 | pending |
| line-1 | line-1-0575-0629-s012881 | forward | revenue | 3 | pending |
| line-1 | line-1-0575-0629-s012881 | reverse | revenue | 3 | pending |
| line-1 | line-1-0690-0685-s015888 | forward | revenue | 3 | pending |
| line-1 | line-1-0690-0685-s015888 | reverse | revenue | 3 | pending |
| line-1 | line-1-0799-0721-s018734 | reverse | revenue | 3 | pending |
| line-1 | line-1-0544-0557-s010230 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0557-s010230 | reverse | spare | 1 | pending |
| line-1 | line-1-0575-0629-s012881 | forward | spare | 1 | pending |
| line-1 | line-1-0575-0629-s012881 | reverse | spare | 1 | pending |
| line-1 | line-1-0690-0685-s015888 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0571-0465-s003009 | forward | revenue | 4 | pending |
| line-2 | line-2-0571-0465-s003009 | reverse | revenue | 4 | pending |
| line-2 | line-2-0544-0557-s005202 | forward | revenue | 4 | pending |
| line-2 | line-2-0544-0557-s005202 | reverse | revenue | 4 | pending |
| line-2 | line-2-0480-0610-s007128 | forward | revenue | 4 | pending |
| line-2 | line-2-0480-0610-s007128 | reverse | revenue | 3 | pending |
| line-2 | line-2-0514-0687-s009044 | forward | revenue | 3 | pending |
| line-2 | line-2-0514-0687-s009044 | reverse | revenue | 3 | pending |
| line-2 | line-2-0458-0842-s014542 | forward | revenue | 3 | pending |
| line-2 | line-2-0458-0842-s014542 | reverse | revenue | 3 | pending |
| line-2 | line-2-0418-1069-s020043 | reverse | revenue | 3 | pending |
| line-2 | line-2-0480-0610-s007128 | reverse | spare | 1 | pending |
| line-2 | line-2-0514-0687-s009044 | forward | spare | 1 | pending |
| line-2 | line-2-0514-0687-s009044 | reverse | spare | 1 | pending |
| line-2 | line-2-0458-0842-s014542 | forward | spare | 1 | pending |
| line-2 | line-2-0458-0842-s014542 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0665-0604-s006517 | forward | revenue | 6 | pending |
| line-3 | line-3-0665-0604-s006517 | reverse | revenue | 6 | pending |
| line-3 | line-3-0544-0557-s010056 | forward | revenue | 6 | pending |
| line-3 | line-3-0544-0557-s010056 | reverse | revenue | 5 | pending |
| line-3 | line-3-0494-0476-s012532 | forward | revenue | 5 | pending |
| line-3 | line-3-0494-0476-s012532 | reverse | revenue | 5 | pending |
| line-3 | line-3-0397-0394-s016032 | forward | revenue | 5 | pending |
| line-3 | line-3-0397-0394-s016032 | reverse | revenue | 5 | pending |
| line-3 | line-3-0085-0118-s025108 | reverse | revenue | 5 | pending |
| line-3 | line-3-0544-0557-s010056 | reverse | spare | 1 | pending |
| line-3 | line-3-0494-0476-s012532 | forward | spare | 1 | pending |
| line-3 | line-3-0494-0476-s012532 | reverse | spare | 1 | pending |
| line-3 | line-3-0397-0394-s016032 | forward | spare | 1 | pending |
| line-3 | line-3-0397-0394-s016032 | reverse | spare | 1 | pending |
| line-3 | line-3-0085-0118-s025108 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0216-0447-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0365-0547-s003867 | 8 | 2 | 6 | 357.0 |
| line-1-0463-0507-s006869 | 8 | 2 | 6 | 357.0 |
| line-1-0544-0557-s010230 | 8 | 4 | 4 | 238.0 |
| line-1-0575-0629-s012881 | 8 | 2 | 6 | 357.0 |
| line-1-0690-0685-s015888 | 7 | 2 | 5 | 297.5 |
| line-1-0799-0721-s018734 | 3 | 2 | 1 | 59.5 |
| line-2-0418-1069-s020043 | 3 | 2 | 1 | 59.5 |
| line-2-0458-0842-s014542 | 8 | 2 | 6 | 357.0 |
| line-2-0480-0610-s007128 | 8 | 2 | 6 | 357.0 |
| line-2-0514-0687-s009044 | 8 | 2 | 6 | 357.0 |
| line-2-0544-0557-s005202 | 8 | 4 | 4 | 238.0 |
| line-2-0571-0465-s003009 | 8 | 2 | 6 | 357.0 |
| line-2-0674-0383-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0085-0118-s025108 | 6 | 2 | 4 | 238.0 |
| line-3-0397-0394-s016032 | 12 | 2 | 10 | 595.0 |
| line-3-0494-0476-s012532 | 12 | 2 | 10 | 595.0 |
| line-3-0544-0557-s010056 | 12 | 4 | 8 | 476.0 |
| line-3-0665-0604-s006517 | 12 | 2 | 10 | 595.0 |
| line-3-0919-0713-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Arusha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
