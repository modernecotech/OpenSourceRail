# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 151 at depots = 191 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0784-0410-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0449-0306-s027717 | line-2 | declared-depot | 71 | 4,224.5 | 12 |
| line-3-0393-0347-s000000 | line-3 | declared-depot | 20 | 1,190.0 | 4 |
| line-4-0589-0610-s000000 | line-4 | declared-depot | 10 | 595.0 | 2 |
| line-5-0656-0652-s000000 | line-5 | declared-depot | 10 | 595.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0232-0603-s016910 | station | reverse | revenue | 2 |
| line-1 | line-1-0403-0556-s011927 | station | forward | revenue | 1 |
| line-1 | line-1-0403-0556-s011927 | station | reverse | revenue | 1 |
| line-1 | line-1-0479-0595-s008860 | station | forward | revenue | 1 |
| line-1 | line-1-0479-0595-s008860 | station | reverse | revenue | 1 |
| line-1 | line-1-0540-0554-s007154 | station | forward | revenue | 1 |
| line-1 | line-1-0540-0554-s007154 | station | reverse | revenue | 1 |
| line-1 | line-1-0655-0460-s003378 | station | forward | revenue | 1 |
| line-1 | line-1-0655-0460-s003378 | station | reverse | revenue | 1 |
| line-1 | line-1-0784-0410-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0449-0306-s027717 | station | reverse | revenue | 2 |
| line-2 | line-2-0468-0495-s022359 | station | forward | revenue | 1 |
| line-2 | line-2-0468-0495-s022359 | station | reverse | revenue | 1 |
| line-2 | line-2-0485-0520-s019349 | station | forward | revenue | 1 |
| line-2 | line-2-0485-0520-s019349 | station | reverse | revenue | 1 |
| line-2 | line-2-0539-0552-s016908 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0552-s016908 | station | reverse | revenue | 1 |
| line-2 | line-2-0589-0610-s014569 | station | forward | revenue | 1 |
| line-2 | line-2-0589-0610-s014569 | station | reverse | revenue | 1 |
| line-2 | line-2-0656-0652-s012818 | station | forward | revenue | 1 |
| line-2 | line-2-0656-0652-s012818 | station | reverse | revenue | 1 |
| line-2 | line-2-0906-1035-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0393-0347-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0556-s004263 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0556-s004263 | station | reverse | revenue | 1 |
| line-3 | line-3-0411-0736-s007929 | station | reverse | revenue | 2 |
| line-4 | line-4-0468-0735-s004135 | station | reverse | revenue | 2 |
| line-4 | line-4-0589-0610-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0656-0652-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0735-0485-s004063 | station | reverse | revenue | 2 |
| line-1 | line-1-0784-0410-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-0784-0410-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0784-0410-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0449-0306-s027717 | depot | — | revenue | 63 |
| line-2 | line-2-0449-0306-s027717 | depot | — | spare | 7 |
| line-2 | line-2-0449-0306-s027717 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0393-0347-s000000 | depot | — | revenue | 17 |
| line-3 | line-3-0393-0347-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0393-0347-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0589-0610-s000000 | depot | — | revenue | 8 |
| line-4 | line-4-0589-0610-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0589-0610-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0656-0652-s000000 | depot | — | revenue | 8 |
| line-5 | line-5-0656-0652-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0656-0652-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kisumu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **191 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **171 revenue, 15 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **151 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0784-0410-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0655-0460-s003378 | forward | revenue | 5 | pending |
| line-1 | line-1-0655-0460-s003378 | reverse | revenue | 5 | pending |
| line-1 | line-1-0540-0554-s007154 | forward | revenue | 5 | pending |
| line-1 | line-1-0540-0554-s007154 | reverse | revenue | 5 | pending |
| line-1 | line-1-0479-0595-s008860 | forward | revenue | 5 | pending |
| line-1 | line-1-0479-0595-s008860 | reverse | revenue | 5 | pending |
| line-1 | line-1-0403-0556-s011927 | forward | revenue | 4 | pending |
| line-1 | line-1-0403-0556-s011927 | reverse | revenue | 4 | pending |
| line-1 | line-1-0232-0603-s016910 | reverse | revenue | 4 | pending |
| line-1 | line-1-0403-0556-s011927 | forward | spare | 1 | pending |
| line-1 | line-1-0403-0556-s011927 | reverse | spare | 1 | pending |
| line-1 | line-1-0232-0603-s016910 | reverse | spare | 1 | pending |
| line-1 | line-1-0784-0410-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0655-0460-s003378 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0656-0652-s012818 | forward | revenue | 7 | pending |
| line-2 | line-2-0656-0652-s012818 | reverse | revenue | 7 | pending |
| line-2 | line-2-0589-0610-s014569 | forward | revenue | 7 | pending |
| line-2 | line-2-0589-0610-s014569 | reverse | revenue | 7 | pending |
| line-2 | line-2-0539-0552-s016908 | forward | revenue | 6 | pending |
| line-2 | line-2-0539-0552-s016908 | reverse | revenue | 6 | pending |
| line-2 | line-2-0485-0520-s019349 | forward | revenue | 6 | pending |
| line-2 | line-2-0485-0520-s019349 | reverse | revenue | 6 | pending |
| line-2 | line-2-0468-0495-s022359 | forward | revenue | 6 | pending |
| line-2 | line-2-0468-0495-s022359 | reverse | revenue | 6 | pending |
| line-2 | line-2-0449-0306-s027717 | reverse | revenue | 6 | pending |
| line-2 | line-2-0539-0552-s016908 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0552-s016908 | reverse | spare | 1 | pending |
| line-2 | line-2-0485-0520-s019349 | forward | spare | 1 | pending |
| line-2 | line-2-0485-0520-s019349 | reverse | spare | 1 | pending |
| line-2 | line-2-0468-0495-s022359 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0495-s022359 | reverse | spare | 1 | pending |
| line-2 | line-2-0449-0306-s027717 | reverse | spare | 1 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0393-0347-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0403-0556-s004263 | forward | revenue | 6 | pending |
| line-3 | line-3-0403-0556-s004263 | reverse | revenue | 6 | pending |
| line-3 | line-3-0411-0736-s007929 | reverse | revenue | 5 | pending |
| line-3 | line-3-0411-0736-s007929 | reverse | spare | 1 | pending |
| line-3 | line-3-0393-0347-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0556-s004263 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0589-0610-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0468-0735-s004135 | reverse | revenue | 6 | pending |
| line-4 | line-4-0589-0610-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0468-0735-s004135 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0656-0652-s000000 | forward | revenue | 6 | pending |
| line-5 | line-5-0735-0485-s004063 | reverse | revenue | 6 | pending |
| line-5 | line-5-0656-0652-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0735-0485-s004063 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**139 trainsets exceed the reference platform envelope**, requiring **8,270.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0232-0603-s016910 | 5 | 2 | 3 | 178.5 |
| line-1-0403-0556-s011927 | 10 | 4 | 6 | 357.0 |
| line-1-0479-0595-s008860 | 10 | 2 | 8 | 476.0 |
| line-1-0540-0554-s007154 | 10 | 4 | 6 | 357.0 |
| line-1-0655-0460-s003378 | 11 | 2 | 9 | 535.5 |
| line-1-0784-0410-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0449-0306-s027717 | 7 | 2 | 5 | 297.5 |
| line-2-0468-0495-s022359 | 14 | 2 | 12 | 714.0 |
| line-2-0485-0520-s019349 | 14 | 2 | 12 | 714.0 |
| line-2-0539-0552-s016908 | 14 | 4 | 10 | 595.0 |
| line-2-0589-0610-s014569 | 14 | 4 | 10 | 595.0 |
| line-2-0656-0652-s012818 | 14 | 4 | 10 | 595.0 |
| line-2-0906-1035-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0393-0347-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0403-0556-s004263 | 13 | 4 | 9 | 535.5 |
| line-3-0411-0736-s007929 | 6 | 2 | 4 | 238.0 |
| line-4-0468-0735-s004135 | 7 | 2 | 5 | 297.5 |
| line-4-0589-0610-s000000 | 7 | 2 | 5 | 297.5 |
| line-5-0656-0652-s000000 | 7 | 2 | 5 | 297.5 |
| line-5-0735-0485-s004063 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisumu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
