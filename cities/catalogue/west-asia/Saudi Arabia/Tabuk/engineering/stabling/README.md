# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 133 at depots = 181 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0283-0726-s000000 | line-1 | declared-depot | 37 | 2,201.5 | 8 |
| line-2-0000-0301-s000000 | line-2 | declared-depot | 43 | 2,558.5 | 9 |
| line-3-0729-0230-s022857 | line-3 | declared-depot | 53 | 3,153.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0283-0726-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0350-0609-s003024 | station | forward | revenue | 1 |
| line-1 | line-1-0350-0609-s003024 | station | reverse | revenue | 1 |
| line-1 | line-1-0416-0492-s006028 | station | forward | revenue | 1 |
| line-1 | line-1-0416-0492-s006028 | station | reverse | revenue | 1 |
| line-1 | line-1-0473-0392-s008570 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0392-s008570 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0120-s015818 | station | reverse | revenue | 2 |
| line-1 | line-1-0560-0239-s012527 | station | forward | revenue | 1 |
| line-1 | line-1-0560-0239-s012527 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0176-s014185 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0176-s014185 | station | reverse | revenue | 1 |
| line-2 | line-2-0000-0301-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0134-0317-s003499 | station | forward | revenue | 1 |
| line-2 | line-2-0134-0317-s003499 | station | reverse | revenue | 1 |
| line-2 | line-2-0237-0362-s006225 | station | forward | revenue | 1 |
| line-2 | line-2-0237-0362-s006225 | station | reverse | revenue | 1 |
| line-2 | line-2-0367-0379-s008966 | station | forward | revenue | 1 |
| line-2 | line-2-0367-0379-s008966 | station | reverse | revenue | 1 |
| line-2 | line-2-0473-0392-s011194 | station | forward | revenue | 1 |
| line-2 | line-2-0473-0392-s011194 | station | reverse | revenue | 1 |
| line-2 | line-2-0605-0409-s013974 | station | forward | revenue | 1 |
| line-2 | line-2-0605-0409-s013974 | station | reverse | revenue | 1 |
| line-2 | line-2-0705-0422-s016082 | station | forward | revenue | 1 |
| line-2 | line-2-0705-0422-s016082 | station | reverse | revenue | 1 |
| line-2 | line-2-0804-0434-s018162 | station | reverse | revenue | 2 |
| line-3 | line-3-0259-1031-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0324-0812-s007007 | station | forward | revenue | 1 |
| line-3 | line-3-0324-0812-s007007 | station | reverse | revenue | 1 |
| line-3 | line-3-0400-0702-s010024 | station | forward | revenue | 1 |
| line-3 | line-3-0400-0702-s010024 | station | reverse | revenue | 1 |
| line-3 | line-3-0478-0591-s013030 | station | forward | revenue | 1 |
| line-3 | line-3-0478-0591-s013030 | station | reverse | revenue | 1 |
| line-3 | line-3-0522-0528-s014772 | station | forward | revenue | 1 |
| line-3 | line-3-0522-0528-s014772 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0481-s016036 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0481-s016036 | station | reverse | revenue | 1 |
| line-3 | line-3-0605-0409-s017992 | station | forward | revenue | 1 |
| line-3 | line-3-0605-0409-s017992 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0319-s020434 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0319-s020434 | station | reverse | revenue | 1 |
| line-3 | line-3-0729-0230-s022857 | station | reverse | revenue | 2 |
| line-1 | line-1-0283-0726-s000000 | depot | — | revenue | 32 |
| line-1 | line-1-0283-0726-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0283-0726-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0000-0301-s000000 | depot | — | revenue | 37 |
| line-2 | line-2-0000-0301-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0000-0301-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0729-0230-s022857 | depot | — | revenue | 46 |
| line-3 | line-3-0729-0230-s022857 | depot | — | spare | 6 |
| line-3 | line-3-0729-0230-s022857 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tabuk-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **181 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **133 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0283-0726-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0609-s003024 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0609-s003024 | reverse | revenue | 4 | pending |
| line-1 | line-1-0416-0492-s006028 | forward | revenue | 4 | pending |
| line-1 | line-1-0416-0492-s006028 | reverse | revenue | 4 | pending |
| line-1 | line-1-0473-0392-s008570 | forward | revenue | 4 | pending |
| line-1 | line-1-0473-0392-s008570 | reverse | revenue | 4 | pending |
| line-1 | line-1-0560-0239-s012527 | forward | revenue | 4 | pending |
| line-1 | line-1-0560-0239-s012527 | reverse | revenue | 4 | pending |
| line-1 | line-1-0583-0176-s014185 | forward | revenue | 4 | pending |
| line-1 | line-1-0583-0176-s014185 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0120-s015818 | reverse | revenue | 3 | pending |
| line-1 | line-1-0583-0176-s014185 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0120-s015818 | reverse | spare | 1 | pending |
| line-1 | line-1-0283-0726-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0350-0609-s003024 | forward | spare | 1 | pending |
| line-1 | line-1-0350-0609-s003024 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0134-0317-s003499 | forward | revenue | 4 | pending |
| line-2 | line-2-0134-0317-s003499 | reverse | revenue | 4 | pending |
| line-2 | line-2-0237-0362-s006225 | forward | revenue | 4 | pending |
| line-2 | line-2-0237-0362-s006225 | reverse | revenue | 4 | pending |
| line-2 | line-2-0367-0379-s008966 | forward | revenue | 4 | pending |
| line-2 | line-2-0367-0379-s008966 | reverse | revenue | 4 | pending |
| line-2 | line-2-0473-0392-s011194 | forward | revenue | 4 | pending |
| line-2 | line-2-0473-0392-s011194 | reverse | revenue | 4 | pending |
| line-2 | line-2-0605-0409-s013974 | forward | revenue | 4 | pending |
| line-2 | line-2-0605-0409-s013974 | reverse | revenue | 4 | pending |
| line-2 | line-2-0705-0422-s016082 | forward | revenue | 3 | pending |
| line-2 | line-2-0705-0422-s016082 | reverse | revenue | 3 | pending |
| line-2 | line-2-0804-0434-s018162 | reverse | revenue | 3 | pending |
| line-2 | line-2-0705-0422-s016082 | forward | spare | 1 | pending |
| line-2 | line-2-0705-0422-s016082 | reverse | spare | 1 | pending |
| line-2 | line-2-0804-0434-s018162 | reverse | spare | 1 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003499 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003499 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0259-1031-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0324-0812-s007007 | forward | revenue | 4 | pending |
| line-3 | line-3-0324-0812-s007007 | reverse | revenue | 4 | pending |
| line-3 | line-3-0400-0702-s010024 | forward | revenue | 4 | pending |
| line-3 | line-3-0400-0702-s010024 | reverse | revenue | 4 | pending |
| line-3 | line-3-0478-0591-s013030 | forward | revenue | 4 | pending |
| line-3 | line-3-0478-0591-s013030 | reverse | revenue | 4 | pending |
| line-3 | line-3-0522-0528-s014772 | forward | revenue | 4 | pending |
| line-3 | line-3-0522-0528-s014772 | reverse | revenue | 4 | pending |
| line-3 | line-3-0554-0481-s016036 | forward | revenue | 4 | pending |
| line-3 | line-3-0554-0481-s016036 | reverse | revenue | 4 | pending |
| line-3 | line-3-0605-0409-s017992 | forward | revenue | 4 | pending |
| line-3 | line-3-0605-0409-s017992 | reverse | revenue | 4 | pending |
| line-3 | line-3-0667-0319-s020434 | forward | revenue | 4 | pending |
| line-3 | line-3-0667-0319-s020434 | reverse | revenue | 4 | pending |
| line-3 | line-3-0729-0230-s022857 | reverse | revenue | 4 | pending |
| line-3 | line-3-0259-1031-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0324-0812-s007007 | forward | spare | 1 | pending |
| line-3 | line-3-0324-0812-s007007 | reverse | spare | 1 | pending |
| line-3 | line-3-0400-0702-s010024 | forward | spare | 1 | pending |
| line-3 | line-3-0400-0702-s010024 | reverse | spare | 1 | pending |
| line-3 | line-3-0478-0591-s013030 | forward | spare | 1 | pending |
| line-3 | line-3-0478-0591-s013030 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**125 trainsets exceed the reference platform envelope**, requiring **7,437.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0283-0726-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0350-0609-s003024 | 10 | 2 | 8 | 476.0 |
| line-1-0416-0492-s006028 | 8 | 2 | 6 | 357.0 |
| line-1-0473-0392-s008570 | 8 | 4 | 4 | 238.0 |
| line-1-0548-0120-s015818 | 4 | 2 | 2 | 119.0 |
| line-1-0560-0239-s012527 | 8 | 2 | 6 | 357.0 |
| line-1-0583-0176-s014185 | 8 | 2 | 6 | 357.0 |
| line-2-0000-0301-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0134-0317-s003499 | 10 | 2 | 8 | 476.0 |
| line-2-0237-0362-s006225 | 8 | 2 | 6 | 357.0 |
| line-2-0367-0379-s008966 | 8 | 2 | 6 | 357.0 |
| line-2-0473-0392-s011194 | 8 | 4 | 4 | 238.0 |
| line-2-0605-0409-s013974 | 8 | 4 | 4 | 238.0 |
| line-2-0705-0422-s016082 | 8 | 2 | 6 | 357.0 |
| line-2-0804-0434-s018162 | 4 | 2 | 2 | 119.0 |
| line-3-0259-1031-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0324-0812-s007007 | 10 | 2 | 8 | 476.0 |
| line-3-0400-0702-s010024 | 10 | 2 | 8 | 476.0 |
| line-3-0478-0591-s013030 | 10 | 2 | 8 | 476.0 |
| line-3-0522-0528-s014772 | 8 | 2 | 6 | 357.0 |
| line-3-0554-0481-s016036 | 8 | 2 | 6 | 357.0 |
| line-3-0605-0409-s017992 | 8 | 4 | 4 | 238.0 |
| line-3-0667-0319-s020434 | 8 | 2 | 6 | 357.0 |
| line-3-0729-0230-s022857 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Tabuk/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
