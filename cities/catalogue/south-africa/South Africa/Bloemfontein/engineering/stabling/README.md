# Station and depot overnight allocation

Plan: **52 trainsets at stations + 99 at depots = 151 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0279-0546-s027348 | 99 | 5,890.5 | 23 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0279-0546-s027348 | station | reverse | revenue | 2 |
| line-1 | line-1-0521-0642-s021277 | station | forward | revenue | 1 |
| line-1 | line-1-0521-0642-s021277 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0608-s019200 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0608-s019200 | station | reverse | revenue | 1 |
| line-1 | line-1-0650-0679-s017230 | station | forward | revenue | 1 |
| line-1 | line-1-0650-0679-s017230 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0758-s015238 | station | forward | revenue | 1 |
| line-1 | line-1-0694-0758-s015238 | station | reverse | revenue | 1 |
| line-1 | line-1-0755-0765-s013621 | station | forward | revenue | 1 |
| line-1 | line-1-0755-0765-s013621 | station | reverse | revenue | 1 |
| line-1 | line-1-0859-0814-s010631 | station | forward | revenue | 1 |
| line-1 | line-1-0859-0814-s010631 | station | reverse | revenue | 1 |
| line-1 | line-1-0877-0886-s007616 | station | forward | revenue | 1 |
| line-1 | line-1-0877-0886-s007616 | station | reverse | revenue | 1 |
| line-1 | line-1-0959-1016-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0959-1016-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-1080-1059-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0231-0235-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0447-0441-s006681 | station | forward | revenue | 1 |
| line-2 | line-2-0447-0441-s006681 | station | reverse | revenue | 1 |
| line-2 | line-2-0537-0554-s009698 | station | forward | revenue | 1 |
| line-2 | line-2-0537-0554-s009698 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0608-s011956 | station | forward | revenue | 1 |
| line-2 | line-2-0601-0608-s011956 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0575-s013843 | station | forward | revenue | 1 |
| line-2 | line-2-0671-0575-s013843 | station | reverse | revenue | 1 |
| line-2 | line-2-0697-0638-s015721 | station | forward | revenue | 1 |
| line-2 | line-2-0697-0638-s015721 | station | reverse | revenue | 1 |
| line-2 | line-2-0786-0640-s018724 | station | forward | revenue | 1 |
| line-2 | line-2-0786-0640-s018724 | station | reverse | revenue | 1 |
| line-2 | line-2-0887-0707-s021725 | station | forward | revenue | 1 |
| line-2 | line-2-0887-0707-s021725 | station | reverse | revenue | 1 |
| line-2 | line-2-0977-0745-s025897 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0904-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0515-0724-s006028 | station | forward | revenue | 1 |
| line-3 | line-3-0515-0724-s006028 | station | reverse | revenue | 1 |
| line-3 | line-3-0521-0643-s008032 | station | forward | revenue | 1 |
| line-3 | line-3-0521-0643-s008032 | station | reverse | revenue | 1 |
| line-3 | line-3-0541-0855-s003016 | station | forward | revenue | 1 |
| line-3 | line-3-0541-0855-s003016 | station | reverse | revenue | 1 |
| line-3 | line-3-0601-0608-s010044 | station | forward | revenue | 1 |
| line-3 | line-3-0601-0608-s010044 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0536-s012048 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0536-s012048 | station | reverse | revenue | 1 |
| line-3 | line-3-0871-0509-s018854 | station | reverse | revenue | 2 |
| line-1 | line-1-0279-0546-s027348 | depot | — | revenue | 32 |
| line-1 | line-1-0279-0546-s027348 | depot | — | spare | 5 |
| line-1 | line-1-0279-0546-s027348 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0279-0546-s027348 | depot | — | revenue | 30 |
| line-2 | line-1-0279-0546-s027348 | depot | — | spare | 4 |
| line-2 | line-1-0279-0546-s027348 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0279-0546-s027348 | depot | — | revenue | 22 |
| line-3 | line-1-0279-0546-s027348 | depot | — | spare | 3 |
| line-3 | line-1-0279-0546-s027348 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (35 trains), line-3 (26 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **151 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **136 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **52 positions**; **99 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **26 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1080-1059-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0959-1016-s003005 | forward | revenue | 3 | pending |
| line-1 | line-1-0959-1016-s003005 | reverse | revenue | 3 | pending |
| line-1 | line-1-0877-0886-s007616 | forward | revenue | 3 | pending |
| line-1 | line-1-0877-0886-s007616 | reverse | revenue | 3 | pending |
| line-1 | line-1-0859-0814-s010631 | forward | revenue | 3 | pending |
| line-1 | line-1-0859-0814-s010631 | reverse | revenue | 3 | pending |
| line-1 | line-1-0755-0765-s013621 | forward | revenue | 3 | pending |
| line-1 | line-1-0755-0765-s013621 | reverse | revenue | 3 | pending |
| line-1 | line-1-0694-0758-s015238 | forward | revenue | 3 | pending |
| line-1 | line-1-0694-0758-s015238 | reverse | revenue | 3 | pending |
| line-1 | line-1-0650-0679-s017230 | forward | revenue | 3 | pending |
| line-1 | line-1-0650-0679-s017230 | reverse | revenue | 3 | pending |
| line-1 | line-1-0601-0608-s019200 | forward | revenue | 3 | pending |
| line-1 | line-1-0601-0608-s019200 | reverse | revenue | 3 | pending |
| line-1 | line-1-0521-0642-s021277 | forward | revenue | 3 | pending |
| line-1 | line-1-0521-0642-s021277 | reverse | revenue | 2 | pending |
| line-1 | line-1-0279-0546-s027348 | reverse | revenue | 2 | pending |
| line-1 | line-1-0521-0642-s021277 | reverse | spare | 1 | pending |
| line-1 | line-1-0279-0546-s027348 | reverse | spare | 1 | pending |
| line-1 | line-1-1080-1059-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0959-1016-s003005 | forward | spare | 1 | pending |
| line-1 | line-1-0959-1016-s003005 | reverse | spare | 1 | pending |
| line-1 | line-1-0877-0886-s007616 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0231-0235-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0447-0441-s006681 | forward | revenue | 3 | pending |
| line-2 | line-2-0447-0441-s006681 | reverse | revenue | 3 | pending |
| line-2 | line-2-0537-0554-s009698 | forward | revenue | 3 | pending |
| line-2 | line-2-0537-0554-s009698 | reverse | revenue | 3 | pending |
| line-2 | line-2-0601-0608-s011956 | forward | revenue | 3 | pending |
| line-2 | line-2-0601-0608-s011956 | reverse | revenue | 3 | pending |
| line-2 | line-2-0671-0575-s013843 | forward | revenue | 3 | pending |
| line-2 | line-2-0671-0575-s013843 | reverse | revenue | 3 | pending |
| line-2 | line-2-0697-0638-s015721 | forward | revenue | 3 | pending |
| line-2 | line-2-0697-0638-s015721 | reverse | revenue | 3 | pending |
| line-2 | line-2-0786-0640-s018724 | forward | revenue | 3 | pending |
| line-2 | line-2-0786-0640-s018724 | reverse | revenue | 3 | pending |
| line-2 | line-2-0887-0707-s021725 | forward | revenue | 3 | pending |
| line-2 | line-2-0887-0707-s021725 | reverse | revenue | 3 | pending |
| line-2 | line-2-0977-0745-s025897 | reverse | revenue | 3 | pending |
| line-2 | line-2-0231-0235-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0447-0441-s006681 | forward | spare | 1 | pending |
| line-2 | line-2-0447-0441-s006681 | reverse | spare | 1 | pending |
| line-2 | line-2-0537-0554-s009698 | forward | spare | 1 | pending |
| line-2 | line-2-0537-0554-s009698 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0483-0904-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0541-0855-s003016 | forward | revenue | 3 | pending |
| line-3 | line-3-0541-0855-s003016 | reverse | revenue | 3 | pending |
| line-3 | line-3-0515-0724-s006028 | forward | revenue | 3 | pending |
| line-3 | line-3-0515-0724-s006028 | reverse | revenue | 3 | pending |
| line-3 | line-3-0521-0643-s008032 | forward | revenue | 3 | pending |
| line-3 | line-3-0521-0643-s008032 | reverse | revenue | 3 | pending |
| line-3 | line-3-0601-0608-s010044 | forward | revenue | 3 | pending |
| line-3 | line-3-0601-0608-s010044 | reverse | revenue | 3 | pending |
| line-3 | line-3-0641-0536-s012048 | forward | revenue | 3 | pending |
| line-3 | line-3-0641-0536-s012048 | reverse | revenue | 3 | pending |
| line-3 | line-3-0871-0509-s018854 | reverse | revenue | 3 | pending |
| line-3 | line-3-0483-0904-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0541-0855-s003016 | forward | spare | 1 | pending |
| line-3 | line-3-0541-0855-s003016 | reverse | spare | 1 | pending |
| line-3 | line-3-0515-0724-s006028 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**89 trainsets exceed the reference platform envelope**, requiring **5,295.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0279-0546-s027348 | 3 | 2 | 1 | 59.5 |
| line-1-0521-0642-s021277 | 6 | 4 | 2 | 119.0 |
| line-1-0601-0608-s019200 | 6 | 4 | 2 | 119.0 |
| line-1-0650-0679-s017230 | 6 | 2 | 4 | 238.0 |
| line-1-0694-0758-s015238 | 6 | 2 | 4 | 238.0 |
| line-1-0755-0765-s013621 | 6 | 2 | 4 | 238.0 |
| line-1-0859-0814-s010631 | 6 | 2 | 4 | 238.0 |
| line-1-0877-0886-s007616 | 7 | 2 | 5 | 297.5 |
| line-1-0959-1016-s003005 | 8 | 2 | 6 | 357.0 |
| line-1-1080-1059-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0231-0235-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0447-0441-s006681 | 8 | 2 | 6 | 357.0 |
| line-2-0537-0554-s009698 | 8 | 2 | 6 | 357.0 |
| line-2-0601-0608-s011956 | 6 | 4 | 2 | 119.0 |
| line-2-0671-0575-s013843 | 6 | 2 | 4 | 238.0 |
| line-2-0697-0638-s015721 | 6 | 2 | 4 | 238.0 |
| line-2-0786-0640-s018724 | 6 | 2 | 4 | 238.0 |
| line-2-0887-0707-s021725 | 6 | 2 | 4 | 238.0 |
| line-2-0977-0745-s025897 | 3 | 2 | 1 | 59.5 |
| line-3-0483-0904-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0515-0724-s006028 | 7 | 2 | 5 | 297.5 |
| line-3-0521-0643-s008032 | 6 | 4 | 2 | 119.0 |
| line-3-0541-0855-s003016 | 8 | 2 | 6 | 357.0 |
| line-3-0601-0608-s010044 | 6 | 4 | 2 | 119.0 |
| line-3-0641-0536-s012048 | 6 | 2 | 4 | 238.0 |
| line-3-0871-0509-s018854 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Bloemfontein/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
