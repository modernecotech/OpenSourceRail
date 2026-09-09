# Station and depot overnight allocation

Plan: **40 trainsets at stations + 59 at depots = 99 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0512-0958-s019447 | 59 | 3,510.5 | 15 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0512-0958-s019447 | station | reverse | revenue | 2 |
| line-1 | line-1-0551-0854-s017044 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0854-s017044 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0554-s009562 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0554-s009562 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0755-s014633 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0755-s014633 | station | reverse | revenue | 1 |
| line-1 | line-1-0600-0648-s012213 | station | forward | revenue | 1 |
| line-1 | line-1-0600-0648-s012213 | station | reverse | revenue | 1 |
| line-1 | line-1-0682-0504-s006182 | station | forward | revenue | 1 |
| line-1 | line-1-0682-0504-s006182 | station | reverse | revenue | 1 |
| line-1 | line-1-0737-0368-s003007 | station | forward | revenue | 1 |
| line-1 | line-1-0737-0368-s003007 | station | reverse | revenue | 1 |
| line-1 | line-1-0809-0277-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0344-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0462-0584-s003019 | station | forward | revenue | 1 |
| line-2 | line-2-0462-0584-s003019 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0554-s006128 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0554-s006128 | station | reverse | revenue | 1 |
| line-2 | line-2-0691-0553-s009033 | station | forward | revenue | 1 |
| line-2 | line-2-0691-0553-s009033 | station | reverse | revenue | 1 |
| line-2 | line-2-0727-0613-s011123 | station | forward | revenue | 1 |
| line-2 | line-2-0727-0613-s011123 | station | reverse | revenue | 1 |
| line-2 | line-2-0799-0649-s013211 | station | forward | revenue | 1 |
| line-2 | line-2-0799-0649-s013211 | station | reverse | revenue | 1 |
| line-2 | line-2-0890-0681-s015312 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0321-s011922 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0466-s009022 | station | forward | revenue | 1 |
| line-3 | line-3-0483-0466-s009022 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0554-s006618 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0554-s006618 | station | reverse | revenue | 1 |
| line-3 | line-3-0645-0665-s003015 | station | forward | revenue | 1 |
| line-3 | line-3-0645-0665-s003015 | station | reverse | revenue | 1 |
| line-3 | line-3-0738-0736-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0512-0958-s019447 | depot | — | revenue | 21 |
| line-1 | line-1-0512-0958-s019447 | depot | — | spare | 3 |
| line-1 | line-1-0512-0958-s019447 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0512-0958-s019447 | depot | — | revenue | 15 |
| line-2 | line-1-0512-0958-s019447 | depot | — | spare | 2 |
| line-2 | line-1-0512-0958-s019447 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0512-0958-s019447 | depot | — | revenue | 13 |
| line-3 | line-1-0512-0958-s019447 | depot | — | spare | 2 |
| line-3 | line-1-0512-0958-s019447 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (18 trains), line-3 (16 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **99 trainsets at 20 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **89 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **59 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0809-0277-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0737-0368-s003007 | forward | revenue | 3 | pending |
| line-1 | line-1-0737-0368-s003007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0682-0504-s006182 | forward | revenue | 3 | pending |
| line-1 | line-1-0682-0504-s006182 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0554-s009562 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0554-s009562 | reverse | revenue | 3 | pending |
| line-1 | line-1-0600-0648-s012213 | forward | revenue | 3 | pending |
| line-1 | line-1-0600-0648-s012213 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0755-s014633 | forward | revenue | 2 | pending |
| line-1 | line-1-0571-0755-s014633 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-0854-s017044 | forward | revenue | 2 | pending |
| line-1 | line-1-0551-0854-s017044 | reverse | revenue | 2 | pending |
| line-1 | line-1-0512-0958-s019447 | reverse | revenue | 2 | pending |
| line-1 | line-1-0571-0755-s014633 | forward | spare | 1 | pending |
| line-1 | line-1-0571-0755-s014633 | reverse | spare | 1 | pending |
| line-1 | line-1-0551-0854-s017044 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0854-s017044 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0344-0606-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0462-0584-s003019 | forward | revenue | 3 | pending |
| line-2 | line-2-0462-0584-s003019 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0554-s006128 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0554-s006128 | reverse | revenue | 3 | pending |
| line-2 | line-2-0691-0553-s009033 | forward | revenue | 2 | pending |
| line-2 | line-2-0691-0553-s009033 | reverse | revenue | 2 | pending |
| line-2 | line-2-0727-0613-s011123 | forward | revenue | 2 | pending |
| line-2 | line-2-0727-0613-s011123 | reverse | revenue | 2 | pending |
| line-2 | line-2-0799-0649-s013211 | forward | revenue | 2 | pending |
| line-2 | line-2-0799-0649-s013211 | reverse | revenue | 2 | pending |
| line-2 | line-2-0890-0681-s015312 | reverse | revenue | 2 | pending |
| line-2 | line-2-0691-0553-s009033 | forward | spare | 1 | pending |
| line-2 | line-2-0691-0553-s009033 | reverse | spare | 1 | pending |
| line-2 | line-2-0727-0613-s011123 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0738-0736-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0645-0665-s003015 | forward | revenue | 3 | pending |
| line-3 | line-3-0645-0665-s003015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0554-s006618 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0554-s006618 | reverse | revenue | 3 | pending |
| line-3 | line-3-0483-0466-s009022 | forward | revenue | 3 | pending |
| line-3 | line-3-0483-0466-s009022 | reverse | revenue | 3 | pending |
| line-3 | line-3-0483-0321-s011922 | reverse | revenue | 2 | pending |
| line-3 | line-3-0483-0321-s011922 | reverse | spare | 1 | pending |
| line-3 | line-3-0738-0736-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0645-0665-s003015 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**53 trainsets exceed the reference platform envelope**, requiring **3,153.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0512-0958-s019447 | 2 | 2 | 0 | 0.0 |
| line-1-0551-0854-s017044 | 6 | 2 | 4 | 238.0 |
| line-1-0555-0554-s009562 | 6 | 4 | 2 | 119.0 |
| line-1-0571-0755-s014633 | 6 | 2 | 4 | 238.0 |
| line-1-0600-0648-s012213 | 6 | 2 | 4 | 238.0 |
| line-1-0682-0504-s006182 | 6 | 2 | 4 | 238.0 |
| line-1-0737-0368-s003007 | 6 | 2 | 4 | 238.0 |
| line-1-0809-0277-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0344-0606-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0462-0584-s003019 | 6 | 2 | 4 | 238.0 |
| line-2-0555-0554-s006128 | 6 | 4 | 2 | 119.0 |
| line-2-0691-0553-s009033 | 6 | 2 | 4 | 238.0 |
| line-2-0727-0613-s011123 | 5 | 2 | 3 | 178.5 |
| line-2-0799-0649-s013211 | 4 | 2 | 2 | 119.0 |
| line-2-0890-0681-s015312 | 2 | 2 | 0 | 0.0 |
| line-3-0483-0321-s011922 | 3 | 2 | 1 | 59.5 |
| line-3-0483-0466-s009022 | 6 | 2 | 4 | 238.0 |
| line-3-0555-0554-s006618 | 6 | 4 | 2 | 119.0 |
| line-3-0645-0665-s003015 | 7 | 2 | 5 | 297.5 |
| line-3-0738-0736-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Nyala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
