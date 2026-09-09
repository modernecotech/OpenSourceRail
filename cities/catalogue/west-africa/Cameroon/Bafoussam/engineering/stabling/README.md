# Station and depot overnight allocation

Plan: **46 trainsets at stations + 112 at depots = 158 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-1046-0061-s026438 | 112 | 6,664.0 | 24 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0332-0510-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0421-0541-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0421-0541-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0496-0503-s005094 | station | forward | revenue | 1 |
| line-1 | line-1-0496-0503-s005094 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0548-s007179 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0548-s007179 | station | reverse | revenue | 1 |
| line-1 | line-1-0617-0572-s009059 | station | forward | revenue | 1 |
| line-1 | line-1-0617-0572-s009059 | station | reverse | revenue | 1 |
| line-1 | line-1-0678-0485-s012080 | station | forward | revenue | 1 |
| line-1 | line-1-0678-0485-s012080 | station | reverse | revenue | 1 |
| line-1 | line-1-0790-0520-s015107 | station | forward | revenue | 1 |
| line-1 | line-1-0790-0520-s015107 | station | reverse | revenue | 1 |
| line-1 | line-1-1086-0483-s023031 | station | reverse | revenue | 2 |
| line-2 | line-2-0248-0064-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0393-0335-s007025 | station | forward | revenue | 1 |
| line-2 | line-2-0393-0335-s007025 | station | reverse | revenue | 1 |
| line-2 | line-2-0469-0412-s010046 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0412-s010046 | station | reverse | revenue | 1 |
| line-2 | line-2-0513-0661-s018531 | station | forward | revenue | 1 |
| line-2 | line-2-0513-0661-s018531 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0766-s021289 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0766-s021289 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0548-s015770 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0548-s015770 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0468-s013059 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0468-s013059 | station | reverse | revenue | 1 |
| line-2 | line-2-0581-0875-s024042 | station | reverse | revenue | 2 |
| line-3 | line-3-0465-0671-s004019 | station | forward | revenue | 1 |
| line-3 | line-3-0465-0671-s004019 | station | reverse | revenue | 1 |
| line-3 | line-3-0486-0828-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0508-0597-s006017 | station | forward | revenue | 1 |
| line-3 | line-3-0508-0597-s006017 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0548-s008022 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0548-s008022 | station | reverse | revenue | 1 |
| line-3 | line-3-0602-0482-s010025 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0482-s010025 | station | reverse | revenue | 1 |
| line-3 | line-3-0721-0400-s013527 | station | forward | revenue | 1 |
| line-3 | line-3-0721-0400-s013527 | station | reverse | revenue | 1 |
| line-3 | line-3-1046-0061-s026438 | station | reverse | revenue | 2 |
| line-1 | line-3-1046-0061-s026438 | depot | — | revenue | 28 |
| line-1 | line-3-1046-0061-s026438 | depot | — | spare | 4 |
| line-1 | line-3-1046-0061-s026438 | depot | — | cold_reserve | 1 |
| line-2 | line-3-1046-0061-s026438 | depot | — | revenue | 31 |
| line-2 | line-3-1046-0061-s026438 | depot | — | spare | 4 |
| line-2 | line-3-1046-0061-s026438 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1046-0061-s026438 | depot | — | revenue | 37 |
| line-3 | line-3-1046-0061-s026438 | depot | — | spare | 5 |
| line-3 | line-3-1046-0061-s026438 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (33 trains), line-2 (36 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **158 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **142 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **112 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0332-0510-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0421-0541-s003019 | forward | revenue | 4 | pending |
| line-1 | line-1-0421-0541-s003019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0496-0503-s005094 | forward | revenue | 3 | pending |
| line-1 | line-1-0496-0503-s005094 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0548-s007179 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0548-s007179 | reverse | revenue | 3 | pending |
| line-1 | line-1-0617-0572-s009059 | forward | revenue | 3 | pending |
| line-1 | line-1-0617-0572-s009059 | reverse | revenue | 3 | pending |
| line-1 | line-1-0678-0485-s012080 | forward | revenue | 3 | pending |
| line-1 | line-1-0678-0485-s012080 | reverse | revenue | 3 | pending |
| line-1 | line-1-0790-0520-s015107 | forward | revenue | 3 | pending |
| line-1 | line-1-0790-0520-s015107 | reverse | revenue | 3 | pending |
| line-1 | line-1-1086-0483-s023031 | reverse | revenue | 3 | pending |
| line-1 | line-1-0421-0541-s003019 | reverse | spare | 1 | pending |
| line-1 | line-1-0496-0503-s005094 | forward | spare | 1 | pending |
| line-1 | line-1-0496-0503-s005094 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0548-s007179 | forward | spare | 1 | pending |
| line-1 | line-1-0555-0548-s007179 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0248-0064-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0393-0335-s007025 | forward | revenue | 4 | pending |
| line-2 | line-2-0393-0335-s007025 | reverse | revenue | 4 | pending |
| line-2 | line-2-0469-0412-s010046 | forward | revenue | 4 | pending |
| line-2 | line-2-0469-0412-s010046 | reverse | revenue | 4 | pending |
| line-2 | line-2-0567-0468-s013059 | forward | revenue | 3 | pending |
| line-2 | line-2-0567-0468-s013059 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0548-s015770 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0548-s015770 | reverse | revenue | 3 | pending |
| line-2 | line-2-0513-0661-s018531 | forward | revenue | 3 | pending |
| line-2 | line-2-0513-0661-s018531 | reverse | revenue | 3 | pending |
| line-2 | line-2-0552-0766-s021289 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0766-s021289 | reverse | revenue | 3 | pending |
| line-2 | line-2-0581-0875-s024042 | reverse | revenue | 3 | pending |
| line-2 | line-2-0567-0468-s013059 | forward | spare | 1 | pending |
| line-2 | line-2-0567-0468-s013059 | reverse | spare | 1 | pending |
| line-2 | line-2-0555-0548-s015770 | forward | spare | 1 | pending |
| line-2 | line-2-0555-0548-s015770 | reverse | spare | 1 | pending |
| line-2 | line-2-0513-0661-s018531 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0486-0828-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0465-0671-s004019 | forward | revenue | 5 | pending |
| line-3 | line-3-0465-0671-s004019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0508-0597-s006017 | forward | revenue | 4 | pending |
| line-3 | line-3-0508-0597-s006017 | reverse | revenue | 4 | pending |
| line-3 | line-3-0555-0548-s008022 | forward | revenue | 4 | pending |
| line-3 | line-3-0555-0548-s008022 | reverse | revenue | 4 | pending |
| line-3 | line-3-0602-0482-s010025 | forward | revenue | 4 | pending |
| line-3 | line-3-0602-0482-s010025 | reverse | revenue | 4 | pending |
| line-3 | line-3-0721-0400-s013527 | forward | revenue | 4 | pending |
| line-3 | line-3-0721-0400-s013527 | reverse | revenue | 4 | pending |
| line-3 | line-3-1046-0061-s026438 | reverse | revenue | 4 | pending |
| line-3 | line-3-0508-0597-s006017 | forward | spare | 1 | pending |
| line-3 | line-3-0508-0597-s006017 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0548-s008022 | forward | spare | 1 | pending |
| line-3 | line-3-0555-0548-s008022 | reverse | spare | 1 | pending |
| line-3 | line-3-0602-0482-s010025 | forward | spare | 1 | pending |
| line-3 | line-3-0602-0482-s010025 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**106 trainsets exceed the reference platform envelope**, requiring **6,307.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0332-0510-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0421-0541-s003019 | 8 | 2 | 6 | 357.0 |
| line-1-0496-0503-s005094 | 8 | 2 | 6 | 357.0 |
| line-1-0555-0548-s007179 | 8 | 4 | 4 | 238.0 |
| line-1-0617-0572-s009059 | 6 | 2 | 4 | 238.0 |
| line-1-0678-0485-s012080 | 6 | 2 | 4 | 238.0 |
| line-1-0790-0520-s015107 | 6 | 2 | 4 | 238.0 |
| line-1-1086-0483-s023031 | 3 | 2 | 1 | 59.5 |
| line-2-0248-0064-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0393-0335-s007025 | 8 | 2 | 6 | 357.0 |
| line-2-0469-0412-s010046 | 8 | 2 | 6 | 357.0 |
| line-2-0513-0661-s018531 | 7 | 2 | 5 | 297.5 |
| line-2-0552-0766-s021289 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0548-s015770 | 8 | 4 | 4 | 238.0 |
| line-2-0567-0468-s013059 | 8 | 2 | 6 | 357.0 |
| line-2-0581-0875-s024042 | 3 | 2 | 1 | 59.5 |
| line-3-0465-0671-s004019 | 10 | 2 | 8 | 476.0 |
| line-3-0486-0828-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0508-0597-s006017 | 10 | 2 | 8 | 476.0 |
| line-3-0555-0548-s008022 | 10 | 4 | 6 | 357.0 |
| line-3-0602-0482-s010025 | 10 | 2 | 8 | 476.0 |
| line-3-0721-0400-s013527 | 8 | 2 | 6 | 357.0 |
| line-3-1046-0061-s026438 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bafoussam/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
