# Station and depot overnight allocation

Plan: **38 trainsets at stations + 101 at depots = 139 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0809-0030-s026309 | 101 | 6,009.5 | 21 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0426-0909-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0454-0266-s015954 | station | reverse | revenue | 2 |
| line-1 | line-1-0489-0763-s003536 | station | forward | revenue | 1 |
| line-1 | line-1-0489-0763-s003536 | station | reverse | revenue | 1 |
| line-1 | line-1-0498-0369-s013414 | station | forward | revenue | 1 |
| line-1 | line-1-0498-0369-s013414 | station | reverse | revenue | 1 |
| line-1 | line-1-0517-0481-s010851 | station | forward | revenue | 1 |
| line-1 | line-1-0517-0481-s010851 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0635-s006542 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0635-s006542 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0555-s008302 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0555-s008302 | station | reverse | revenue | 1 |
| line-2 | line-2-0528-0892-s003233 | station | forward | revenue | 1 |
| line-2 | line-2-0528-0892-s003233 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0555-s012327 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0555-s012327 | station | reverse | revenue | 1 |
| line-2 | line-2-0563-0485-s014346 | station | forward | revenue | 1 |
| line-2 | line-2-0563-0485-s014346 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0988-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0574-0672-s008312 | station | forward | revenue | 1 |
| line-2 | line-2-0574-0672-s008312 | station | reverse | revenue | 1 |
| line-2 | line-2-0605-0586-s010317 | station | forward | revenue | 1 |
| line-2 | line-2-0605-0586-s010317 | station | reverse | revenue | 1 |
| line-2 | line-2-0809-0030-s026309 | station | reverse | revenue | 2 |
| line-3 | line-3-0461-0845-s021874 | station | reverse | revenue | 2 |
| line-3 | line-3-0491-0617-s016656 | station | forward | revenue | 1 |
| line-3 | line-3-0491-0617-s016656 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0555-s013834 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0555-s013834 | station | reverse | revenue | 1 |
| line-3 | line-3-0622-0500-s011591 | station | forward | revenue | 1 |
| line-3 | line-3-0622-0500-s011591 | station | reverse | revenue | 1 |
| line-3 | line-3-0801-0064-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0809-0030-s026309 | depot | — | revenue | 18 |
| line-1 | line-2-0809-0030-s026309 | depot | — | spare | 3 |
| line-1 | line-2-0809-0030-s026309 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0809-0030-s026309 | depot | — | revenue | 36 |
| line-2 | line-2-0809-0030-s026309 | depot | — | spare | 5 |
| line-2 | line-2-0809-0030-s026309 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0809-0030-s026309 | depot | — | revenue | 32 |
| line-3 | line-2-0809-0030-s026309 | depot | — | spare | 4 |
| line-3 | line-2-0809-0030-s026309 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (22 trains), line-3 (37 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **139 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **124 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **101 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0426-0909-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0489-0763-s003536 | forward | revenue | 3 | pending |
| line-1 | line-1-0489-0763-s003536 | reverse | revenue | 3 | pending |
| line-1 | line-1-0532-0635-s006542 | forward | revenue | 3 | pending |
| line-1 | line-1-0532-0635-s006542 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0555-s008302 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0555-s008302 | reverse | revenue | 3 | pending |
| line-1 | line-1-0517-0481-s010851 | forward | revenue | 3 | pending |
| line-1 | line-1-0517-0481-s010851 | reverse | revenue | 2 | pending |
| line-1 | line-1-0498-0369-s013414 | forward | revenue | 2 | pending |
| line-1 | line-1-0498-0369-s013414 | reverse | revenue | 2 | pending |
| line-1 | line-1-0454-0266-s015954 | reverse | revenue | 2 | pending |
| line-1 | line-1-0517-0481-s010851 | reverse | spare | 1 | pending |
| line-1 | line-1-0498-0369-s013414 | forward | spare | 1 | pending |
| line-1 | line-1-0498-0369-s013414 | reverse | spare | 1 | pending |
| line-1 | line-1-0454-0266-s015954 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0528-0892-s003233 | forward | revenue | 5 | pending |
| line-2 | line-2-0528-0892-s003233 | reverse | revenue | 4 | pending |
| line-2 | line-2-0574-0672-s008312 | forward | revenue | 4 | pending |
| line-2 | line-2-0574-0672-s008312 | reverse | revenue | 4 | pending |
| line-2 | line-2-0605-0586-s010317 | forward | revenue | 4 | pending |
| line-2 | line-2-0605-0586-s010317 | reverse | revenue | 4 | pending |
| line-2 | line-2-0550-0555-s012327 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0555-s012327 | reverse | revenue | 4 | pending |
| line-2 | line-2-0563-0485-s014346 | forward | revenue | 4 | pending |
| line-2 | line-2-0563-0485-s014346 | reverse | revenue | 4 | pending |
| line-2 | line-2-0809-0030-s026309 | reverse | revenue | 4 | pending |
| line-2 | line-2-0528-0892-s003233 | reverse | spare | 1 | pending |
| line-2 | line-2-0574-0672-s008312 | forward | spare | 1 | pending |
| line-2 | line-2-0574-0672-s008312 | reverse | spare | 1 | pending |
| line-2 | line-2-0605-0586-s010317 | forward | spare | 1 | pending |
| line-2 | line-2-0605-0586-s010317 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0555-s012327 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0801-0064-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0622-0500-s011591 | forward | revenue | 6 | pending |
| line-3 | line-3-0622-0500-s011591 | reverse | revenue | 5 | pending |
| line-3 | line-3-0550-0555-s013834 | forward | revenue | 5 | pending |
| line-3 | line-3-0550-0555-s013834 | reverse | revenue | 5 | pending |
| line-3 | line-3-0491-0617-s016656 | forward | revenue | 5 | pending |
| line-3 | line-3-0491-0617-s016656 | reverse | revenue | 5 | pending |
| line-3 | line-3-0461-0845-s021874 | reverse | revenue | 5 | pending |
| line-3 | line-3-0622-0500-s011591 | reverse | spare | 1 | pending |
| line-3 | line-3-0550-0555-s013834 | forward | spare | 1 | pending |
| line-3 | line-3-0550-0555-s013834 | reverse | spare | 1 | pending |
| line-3 | line-3-0491-0617-s016656 | forward | spare | 1 | pending |
| line-3 | line-3-0491-0617-s016656 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0426-0909-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0454-0266-s015954 | 3 | 2 | 1 | 59.5 |
| line-1-0489-0763-s003536 | 6 | 2 | 4 | 238.0 |
| line-1-0498-0369-s013414 | 6 | 2 | 4 | 238.0 |
| line-1-0517-0481-s010851 | 6 | 2 | 4 | 238.0 |
| line-1-0532-0635-s006542 | 6 | 2 | 4 | 238.0 |
| line-1-0550-0555-s008302 | 6 | 4 | 2 | 119.0 |
| line-2-0528-0892-s003233 | 10 | 2 | 8 | 476.0 |
| line-2-0550-0555-s012327 | 9 | 4 | 5 | 297.5 |
| line-2-0563-0485-s014346 | 8 | 2 | 6 | 357.0 |
| line-2-0569-0988-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0574-0672-s008312 | 10 | 2 | 8 | 476.0 |
| line-2-0605-0586-s010317 | 10 | 2 | 8 | 476.0 |
| line-2-0809-0030-s026309 | 4 | 2 | 2 | 119.0 |
| line-3-0461-0845-s021874 | 5 | 2 | 3 | 178.5 |
| line-3-0491-0617-s016656 | 12 | 2 | 10 | 595.0 |
| line-3-0550-0555-s013834 | 12 | 4 | 8 | 476.0 |
| line-3-0622-0500-s011591 | 12 | 2 | 10 | 595.0 |
| line-3-0801-0064-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Mazar-E-Sharif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
