# Station and depot overnight allocation

Plan: **42 trainsets at stations + 77 at depots = 119 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0145-0992-s024048 | 77 | 4,581.5 | 18 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0445-0353-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0460-0463-s003013 | station | forward | revenue | 1 |
| line-1 | line-1-0460-0463-s003013 | station | reverse | revenue | 1 |
| line-1 | line-1-0545-0560-s006308 | station | forward | revenue | 1 |
| line-1 | line-1-0545-0560-s006308 | station | reverse | revenue | 1 |
| line-1 | line-1-0592-0728-s011164 | station | forward | revenue | 1 |
| line-1 | line-1-0592-0728-s011164 | station | reverse | revenue | 1 |
| line-1 | line-1-0593-0842-s013502 | station | forward | revenue | 1 |
| line-1 | line-1-0593-0842-s013502 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0623-s008849 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0623-s008849 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0895-s015818 | station | reverse | revenue | 2 |
| line-2 | line-2-0145-0992-s024048 | station | reverse | revenue | 2 |
| line-2 | line-2-0396-0679-s014764 | station | forward | revenue | 1 |
| line-2 | line-2-0396-0679-s014764 | station | reverse | revenue | 1 |
| line-2 | line-2-0486-0597-s011764 | station | forward | revenue | 1 |
| line-2 | line-2-0486-0597-s011764 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0560-s010016 | station | forward | revenue | 1 |
| line-2 | line-2-0545-0560-s010016 | station | reverse | revenue | 1 |
| line-2 | line-2-0581-0543-s008757 | station | forward | revenue | 1 |
| line-2 | line-2-0581-0543-s008757 | station | reverse | revenue | 1 |
| line-2 | line-2-0623-0464-s006292 | station | forward | revenue | 1 |
| line-2 | line-2-0623-0464-s006292 | station | reverse | revenue | 1 |
| line-2 | line-2-0713-0491-s003267 | station | forward | revenue | 1 |
| line-2 | line-2-0713-0491-s003267 | station | reverse | revenue | 1 |
| line-2 | line-2-0818-0385-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0533-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0545-0560-s005830 | station | forward | revenue | 1 |
| line-3 | line-3-0545-0560-s005830 | station | reverse | revenue | 1 |
| line-3 | line-3-0574-0441-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0574-0441-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0633-0604-s008528 | station | forward | revenue | 1 |
| line-3 | line-3-0633-0604-s008528 | station | reverse | revenue | 1 |
| line-3 | line-3-0654-0714-s011212 | station | forward | revenue | 1 |
| line-3 | line-3-0654-0714-s011212 | station | reverse | revenue | 1 |
| line-3 | line-3-0725-0794-s013896 | station | reverse | revenue | 2 |
| line-1 | line-2-0145-0992-s024048 | depot | — | revenue | 18 |
| line-1 | line-2-0145-0992-s024048 | depot | — | spare | 3 |
| line-1 | line-2-0145-0992-s024048 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0145-0992-s024048 | depot | — | revenue | 31 |
| line-2 | line-2-0145-0992-s024048 | depot | — | spare | 4 |
| line-2 | line-2-0145-0992-s024048 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0145-0992-s024048 | depot | — | revenue | 16 |
| line-3 | line-2-0145-0992-s024048 | depot | — | spare | 2 |
| line-3 | line-2-0145-0992-s024048 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (22 trains), line-3 (19 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **119 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **107 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **77 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0445-0353-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | forward | revenue | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | reverse | revenue | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | forward | revenue | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | reverse | revenue | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | reverse | revenue | 2 | pending |
| line-1 | line-1-0593-0842-s013502 | forward | revenue | 2 | pending |
| line-1 | line-1-0593-0842-s013502 | reverse | revenue | 2 | pending |
| line-1 | line-1-0647-0895-s015818 | reverse | revenue | 2 | pending |
| line-1 | line-1-0592-0728-s011164 | reverse | spare | 1 | pending |
| line-1 | line-1-0593-0842-s013502 | forward | spare | 1 | pending |
| line-1 | line-1-0593-0842-s013502 | reverse | spare | 1 | pending |
| line-1 | line-1-0647-0895-s015818 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | forward | revenue | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | reverse | revenue | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | forward | revenue | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | reverse | revenue | 4 | pending |
| line-2 | line-2-0581-0543-s008757 | forward | revenue | 3 | pending |
| line-2 | line-2-0581-0543-s008757 | reverse | revenue | 3 | pending |
| line-2 | line-2-0545-0560-s010016 | forward | revenue | 3 | pending |
| line-2 | line-2-0545-0560-s010016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0597-s011764 | forward | revenue | 3 | pending |
| line-2 | line-2-0486-0597-s011764 | reverse | revenue | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | forward | revenue | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | reverse | revenue | 3 | pending |
| line-2 | line-2-0145-0992-s024048 | reverse | revenue | 3 | pending |
| line-2 | line-2-0581-0543-s008757 | forward | spare | 1 | pending |
| line-2 | line-2-0581-0543-s008757 | reverse | spare | 1 | pending |
| line-2 | line-2-0545-0560-s010016 | forward | spare | 1 | pending |
| line-2 | line-2-0545-0560-s010016 | reverse | spare | 1 | pending |
| line-2 | line-2-0486-0597-s011764 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0574-0441-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0574-0441-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | forward | revenue | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | reverse | revenue | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | forward | revenue | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | reverse | revenue | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | forward | revenue | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | reverse | revenue | 2 | pending |
| line-3 | line-3-0725-0794-s013896 | reverse | revenue | 2 | pending |
| line-3 | line-3-0654-0714-s011212 | reverse | spare | 1 | pending |
| line-3 | line-3-0725-0794-s013896 | reverse | spare | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0445-0353-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0460-0463-s003013 | 6 | 2 | 4 | 238.0 |
| line-1-0545-0560-s006308 | 6 | 4 | 2 | 119.0 |
| line-1-0592-0728-s011164 | 6 | 2 | 4 | 238.0 |
| line-1-0593-0842-s013502 | 6 | 2 | 4 | 238.0 |
| line-1-0612-0623-s008849 | 6 | 4 | 2 | 119.0 |
| line-1-0647-0895-s015818 | 3 | 2 | 1 | 59.5 |
| line-2-0145-0992-s024048 | 3 | 2 | 1 | 59.5 |
| line-2-0396-0679-s014764 | 6 | 2 | 4 | 238.0 |
| line-2-0486-0597-s011764 | 7 | 2 | 5 | 297.5 |
| line-2-0545-0560-s010016 | 8 | 4 | 4 | 238.0 |
| line-2-0581-0543-s008757 | 8 | 2 | 6 | 357.0 |
| line-2-0623-0464-s006292 | 8 | 2 | 6 | 357.0 |
| line-2-0713-0491-s003267 | 8 | 2 | 6 | 357.0 |
| line-2-0818-0385-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0533-0317-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0545-0560-s005830 | 6 | 4 | 2 | 119.0 |
| line-3-0574-0441-s003009 | 6 | 2 | 4 | 238.0 |
| line-3-0633-0604-s008528 | 6 | 4 | 2 | 119.0 |
| line-3-0654-0714-s011212 | 6 | 2 | 4 | 238.0 |
| line-3-0725-0794-s013896 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lubango/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
