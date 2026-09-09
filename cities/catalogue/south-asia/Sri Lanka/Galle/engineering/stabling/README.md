# Station and depot overnight allocation

Plan: **40 trainsets at stations + 137 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0784-1025-s022688 | 137 | 8,151.5 | 27 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0437-0220-s022407 | station | reverse | revenue | 2 |
| line-1 | line-1-0492-0302-s020271 | station | forward | revenue | 1 |
| line-1 | line-1-0492-0302-s020271 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0379-s018129 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0379-s018129 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0551-s013918 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0551-s013918 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0474-s015988 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0474-s015988 | station | reverse | revenue | 1 |
| line-1 | line-1-0615-0588-s011951 | station | forward | revenue | 1 |
| line-1 | line-1-0615-0588-s011951 | station | reverse | revenue | 1 |
| line-1 | line-1-0653-0648-s009968 | station | forward | revenue | 1 |
| line-1 | line-1-0653-0648-s009968 | station | reverse | revenue | 1 |
| line-1 | line-1-0746-0737-s006967 | station | forward | revenue | 1 |
| line-1 | line-1-0746-0737-s006967 | station | reverse | revenue | 1 |
| line-1 | line-1-0880-1029-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0346-0285-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0443-0489-s006193 | station | forward | revenue | 1 |
| line-2 | line-2-0443-0489-s006193 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0551-s009303 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0551-s009303 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0666-s012223 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0666-s012223 | station | reverse | revenue | 1 |
| line-2 | line-2-0784-1025-s022688 | station | reverse | revenue | 2 |
| line-3 | line-3-0306-1057-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0431-0674-s010019 | station | forward | revenue | 1 |
| line-3 | line-3-0431-0674-s010019 | station | reverse | revenue | 1 |
| line-3 | line-3-0466-0604-s011931 | station | forward | revenue | 1 |
| line-3 | line-3-0466-0604-s011931 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0551-s014679 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0551-s014679 | station | reverse | revenue | 1 |
| line-3 | line-3-0592-0495-s016640 | station | forward | revenue | 1 |
| line-3 | line-3-0592-0495-s016640 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0427-s018590 | station | reverse | revenue | 2 |
| line-1 | line-2-0784-1025-s022688 | depot | — | revenue | 37 |
| line-1 | line-2-0784-1025-s022688 | depot | — | spare | 5 |
| line-1 | line-2-0784-1025-s022688 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0784-1025-s022688 | depot | — | revenue | 46 |
| line-2 | line-2-0784-1025-s022688 | depot | — | spare | 5 |
| line-2 | line-2-0784-1025-s022688 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0784-1025-s022688 | depot | — | revenue | 37 |
| line-3 | line-2-0784-1025-s022688 | depot | — | spare | 4 |
| line-3 | line-2-0784-1025-s022688 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (43 trains), line-3 (42 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 20 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **160 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **137 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0880-1029-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0746-0737-s006967 | forward | revenue | 4 | pending |
| line-1 | line-1-0746-0737-s006967 | reverse | revenue | 4 | pending |
| line-1 | line-1-0653-0648-s009968 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0648-s009968 | reverse | revenue | 4 | pending |
| line-1 | line-1-0615-0588-s011951 | forward | revenue | 4 | pending |
| line-1 | line-1-0615-0588-s011951 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0551-s013918 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0551-s013918 | reverse | revenue | 3 | pending |
| line-1 | line-1-0553-0474-s015988 | forward | revenue | 3 | pending |
| line-1 | line-1-0553-0474-s015988 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0379-s018129 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0379-s018129 | reverse | revenue | 3 | pending |
| line-1 | line-1-0492-0302-s020271 | forward | revenue | 3 | pending |
| line-1 | line-1-0492-0302-s020271 | reverse | revenue | 3 | pending |
| line-1 | line-1-0437-0220-s022407 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0551-s013918 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0551-s013918 | reverse | spare | 1 | pending |
| line-1 | line-1-0553-0474-s015988 | forward | spare | 1 | pending |
| line-1 | line-1-0553-0474-s015988 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0379-s018129 | forward | spare | 1 | pending |
| line-1 | line-1-0548-0379-s018129 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0443-0489-s006193 | forward | revenue | 7 | pending |
| line-2 | line-2-0443-0489-s006193 | reverse | revenue | 7 | pending |
| line-2 | line-2-0550-0551-s009303 | forward | revenue | 7 | pending |
| line-2 | line-2-0550-0551-s009303 | reverse | revenue | 7 | pending |
| line-2 | line-2-0567-0666-s012223 | forward | revenue | 7 | pending |
| line-2 | line-2-0567-0666-s012223 | reverse | revenue | 7 | pending |
| line-2 | line-2-0784-1025-s022688 | reverse | revenue | 7 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0443-0489-s006193 | forward | spare | 1 | pending |
| line-2 | line-2-0443-0489-s006193 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0551-s009303 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0551-s009303 | reverse | spare | 1 | pending |
| line-2 | line-2-0567-0666-s012223 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0431-0674-s010019 | forward | revenue | 5 | pending |
| line-3 | line-3-0431-0674-s010019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0466-0604-s011931 | forward | revenue | 5 | pending |
| line-3 | line-3-0466-0604-s011931 | reverse | revenue | 5 | pending |
| line-3 | line-3-0550-0551-s014679 | forward | revenue | 5 | pending |
| line-3 | line-3-0550-0551-s014679 | reverse | revenue | 5 | pending |
| line-3 | line-3-0592-0495-s016640 | forward | revenue | 5 | pending |
| line-3 | line-3-0592-0495-s016640 | reverse | revenue | 5 | pending |
| line-3 | line-3-0621-0427-s018590 | reverse | revenue | 4 | pending |
| line-3 | line-3-0621-0427-s018590 | reverse | spare | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0431-0674-s010019 | forward | spare | 1 | pending |
| line-3 | line-3-0431-0674-s010019 | reverse | spare | 1 | pending |
| line-3 | line-3-0466-0604-s011931 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**131 trainsets exceed the reference platform envelope**, requiring **7,794.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0437-0220-s022407 | 3 | 2 | 1 | 59.5 |
| line-1-0492-0302-s020271 | 6 | 2 | 4 | 238.0 |
| line-1-0548-0379-s018129 | 8 | 2 | 6 | 357.0 |
| line-1-0550-0551-s013918 | 8 | 4 | 4 | 238.0 |
| line-1-0553-0474-s015988 | 8 | 2 | 6 | 357.0 |
| line-1-0615-0588-s011951 | 8 | 2 | 6 | 357.0 |
| line-1-0653-0648-s009968 | 8 | 2 | 6 | 357.0 |
| line-1-0746-0737-s006967 | 8 | 2 | 6 | 357.0 |
| line-1-0880-1029-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0346-0285-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0443-0489-s006193 | 16 | 2 | 14 | 833.0 |
| line-2-0550-0551-s009303 | 16 | 4 | 12 | 714.0 |
| line-2-0567-0666-s012223 | 15 | 2 | 13 | 773.5 |
| line-2-0784-1025-s022688 | 7 | 2 | 5 | 297.5 |
| line-3-0306-1057-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0431-0674-s010019 | 12 | 2 | 10 | 595.0 |
| line-3-0466-0604-s011931 | 11 | 2 | 9 | 535.5 |
| line-3-0550-0551-s014679 | 10 | 4 | 6 | 357.0 |
| line-3-0592-0495-s016640 | 10 | 2 | 8 | 476.0 |
| line-3-0621-0427-s018590 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Galle/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
