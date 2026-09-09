# Station and depot overnight allocation

Plan: **34 trainsets at stations + 53 at depots = 87 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0485-0820-s016810 | line-1 | declared-depot | 22 | 1,309.0 | 14 |
| line-2-0815-0443-s013638 | line-2 | storage-at-existing-powered-service-point | 18 | 1,071.0 | 0 |
| line-3-0667-0751-s009502 | line-3 | storage-at-existing-powered-service-point | 13 | 773.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0485-0820-s016810 | station | reverse | revenue | 2 |
| line-1 | line-1-0535-0739-s014436 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0739-s014436 | station | reverse | revenue | 1 |
| line-1 | line-1-0563-0557-s009370 | station | forward | revenue | 1 |
| line-1 | line-1-0563-0557-s009370 | station | reverse | revenue | 1 |
| line-1 | line-1-0572-0645-s012039 | station | forward | revenue | 1 |
| line-1 | line-1-0572-0645-s012039 | station | reverse | revenue | 1 |
| line-1 | line-1-0677-0589-s006011 | station | forward | revenue | 1 |
| line-1 | line-1-0677-0589-s006011 | station | reverse | revenue | 1 |
| line-1 | line-1-0763-0503-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0763-0503-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0863-0492-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0365-0585-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0456-0571-s002175 | station | forward | revenue | 1 |
| line-2 | line-2-0456-0571-s002175 | station | reverse | revenue | 1 |
| line-2 | line-2-0563-0557-s005110 | station | forward | revenue | 1 |
| line-2 | line-2-0563-0557-s005110 | station | reverse | revenue | 1 |
| line-2 | line-2-0617-0523-s008192 | station | forward | revenue | 1 |
| line-2 | line-2-0617-0523-s008192 | station | reverse | revenue | 1 |
| line-2 | line-2-0741-0466-s011194 | station | forward | revenue | 1 |
| line-2 | line-2-0741-0466-s011194 | station | reverse | revenue | 1 |
| line-2 | line-2-0815-0443-s013638 | station | reverse | revenue | 2 |
| line-3 | line-3-0514-0433-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0563-0557-s003724 | station | forward | revenue | 1 |
| line-3 | line-3-0563-0557-s003724 | station | reverse | revenue | 1 |
| line-3 | line-3-0639-0620-s006034 | station | forward | revenue | 1 |
| line-3 | line-3-0639-0620-s006034 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0751-s009502 | station | reverse | revenue | 2 |
| line-1 | line-1-0485-0820-s016810 | depot | — | revenue | 18 |
| line-1 | line-1-0485-0820-s016810 | depot | — | spare | 3 |
| line-1 | line-1-0485-0820-s016810 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0815-0443-s013638 | depot | — | revenue | 15 |
| line-2 | line-2-0815-0443-s013638 | depot | — | spare | 2 |
| line-2 | line-2-0815-0443-s013638 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0667-0751-s009502 | depot | — | revenue | 11 |
| line-3 | line-3-0667-0751-s009502 | depot | — | spare | 1 |
| line-3 | line-3-0667-0751-s009502 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/beni-suef-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **87 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **78 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **53 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0863-0492-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0763-0503-s003005 | forward | revenue | 3 | pending |
| line-1 | line-1-0763-0503-s003005 | reverse | revenue | 3 | pending |
| line-1 | line-1-0677-0589-s006011 | forward | revenue | 3 | pending |
| line-1 | line-1-0677-0589-s006011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0563-0557-s009370 | forward | revenue | 3 | pending |
| line-1 | line-1-0563-0557-s009370 | reverse | revenue | 3 | pending |
| line-1 | line-1-0572-0645-s012039 | forward | revenue | 3 | pending |
| line-1 | line-1-0572-0645-s012039 | reverse | revenue | 2 | pending |
| line-1 | line-1-0535-0739-s014436 | forward | revenue | 2 | pending |
| line-1 | line-1-0535-0739-s014436 | reverse | revenue | 2 | pending |
| line-1 | line-1-0485-0820-s016810 | reverse | revenue | 2 | pending |
| line-1 | line-1-0572-0645-s012039 | reverse | spare | 1 | pending |
| line-1 | line-1-0535-0739-s014436 | forward | spare | 1 | pending |
| line-1 | line-1-0535-0739-s014436 | reverse | spare | 1 | pending |
| line-1 | line-1-0485-0820-s016810 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0365-0585-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0571-s002175 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0571-s002175 | reverse | revenue | 3 | pending |
| line-2 | line-2-0563-0557-s005110 | forward | revenue | 3 | pending |
| line-2 | line-2-0563-0557-s005110 | reverse | revenue | 3 | pending |
| line-2 | line-2-0617-0523-s008192 | forward | revenue | 3 | pending |
| line-2 | line-2-0617-0523-s008192 | reverse | revenue | 3 | pending |
| line-2 | line-2-0741-0466-s011194 | forward | revenue | 2 | pending |
| line-2 | line-2-0741-0466-s011194 | reverse | revenue | 2 | pending |
| line-2 | line-2-0815-0443-s013638 | reverse | revenue | 2 | pending |
| line-2 | line-2-0741-0466-s011194 | forward | spare | 1 | pending |
| line-2 | line-2-0741-0466-s011194 | reverse | spare | 1 | pending |
| line-2 | line-2-0815-0443-s013638 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0514-0433-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0563-0557-s003724 | forward | revenue | 3 | pending |
| line-3 | line-3-0563-0557-s003724 | reverse | revenue | 3 | pending |
| line-3 | line-3-0639-0620-s006034 | forward | revenue | 3 | pending |
| line-3 | line-3-0639-0620-s006034 | reverse | revenue | 3 | pending |
| line-3 | line-3-0667-0751-s009502 | reverse | revenue | 3 | pending |
| line-3 | line-3-0563-0557-s003724 | forward | spare | 1 | pending |
| line-3 | line-3-0563-0557-s003724 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**47 trainsets exceed the reference platform envelope**, requiring **2,796.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0485-0820-s016810 | 3 | 2 | 1 | 59.5 |
| line-1-0535-0739-s014436 | 6 | 2 | 4 | 238.0 |
| line-1-0563-0557-s009370 | 6 | 4 | 2 | 119.0 |
| line-1-0572-0645-s012039 | 6 | 2 | 4 | 238.0 |
| line-1-0677-0589-s006011 | 6 | 2 | 4 | 238.0 |
| line-1-0763-0503-s003005 | 6 | 2 | 4 | 238.0 |
| line-1-0863-0492-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0365-0585-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0456-0571-s002175 | 6 | 2 | 4 | 238.0 |
| line-2-0563-0557-s005110 | 6 | 4 | 2 | 119.0 |
| line-2-0617-0523-s008192 | 6 | 2 | 4 | 238.0 |
| line-2-0741-0466-s011194 | 6 | 2 | 4 | 238.0 |
| line-2-0815-0443-s013638 | 3 | 2 | 1 | 59.5 |
| line-3-0514-0433-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0563-0557-s003724 | 8 | 4 | 4 | 238.0 |
| line-3-0639-0620-s006034 | 6 | 2 | 4 | 238.0 |
| line-3-0667-0751-s009502 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Beni-Suef/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
