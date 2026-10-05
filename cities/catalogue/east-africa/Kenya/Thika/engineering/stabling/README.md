# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 181 at depots = 215 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0016-0869-s026109 | line-1 | declared-depot | 69 | 4,105.5 | 12 |
| line-2-0665-0928-s000000 | line-2 | declared-depot | 45 | 2,677.5 | 8 |
| line-3-1020-0216-s000000 | line-3 | declared-depot | 67 | 3,986.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0016-0869-s026109 | station | reverse | revenue | 2 |
| line-1 | line-1-0394-0608-s015215 | station | forward | revenue | 1 |
| line-1 | line-1-0394-0608-s015215 | station | reverse | revenue | 1 |
| line-1 | line-1-0471-0565-s013225 | station | forward | revenue | 1 |
| line-1 | line-1-0471-0565-s013225 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0521-s011245 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0521-s011245 | station | reverse | revenue | 1 |
| line-1 | line-1-0613-0485-s009617 | station | forward | revenue | 1 |
| line-1 | line-1-0613-0485-s009617 | station | reverse | revenue | 1 |
| line-1 | line-1-0748-0409-s006170 | station | forward | revenue | 1 |
| line-1 | line-1-0748-0409-s006170 | station | reverse | revenue | 1 |
| line-1 | line-1-0901-0237-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0574-0297-s014246 | station | forward | revenue | 1 |
| line-2 | line-2-0574-0297-s014246 | station | reverse | revenue | 1 |
| line-2 | line-2-0586-0120-s018324 | station | reverse | revenue | 2 |
| line-2 | line-2-0613-0485-s010151 | station | forward | revenue | 1 |
| line-2 | line-2-0613-0485-s010151 | station | reverse | revenue | 1 |
| line-2 | line-2-0646-0639-s006798 | station | forward | revenue | 1 |
| line-2 | line-2-0646-0639-s006798 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0928-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0675-0777-s003786 | station | forward | revenue | 1 |
| line-2 | line-2-0675-0777-s003786 | station | reverse | revenue | 1 |
| line-3 | line-3-0341-0923-s023755 | station | reverse | revenue | 2 |
| line-3 | line-3-0585-0705-s015492 | station | forward | revenue | 1 |
| line-3 | line-3-0585-0705-s015492 | station | reverse | revenue | 1 |
| line-3 | line-3-0646-0640-s013511 | station | forward | revenue | 1 |
| line-3 | line-3-0646-0640-s013511 | station | reverse | revenue | 1 |
| line-3 | line-3-1020-0216-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0016-0869-s026109 | depot | — | revenue | 61 |
| line-1 | line-1-0016-0869-s026109 | depot | — | spare | 7 |
| line-1 | line-1-0016-0869-s026109 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0665-0928-s000000 | depot | — | revenue | 39 |
| line-2 | line-2-0665-0928-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0665-0928-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1020-0216-s000000 | depot | — | revenue | 60 |
| line-3 | line-3-1020-0216-s000000 | depot | — | spare | 6 |
| line-3 | line-3-1020-0216-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/thika-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **215 trainsets at 17 stations**; largest initial station queue **26**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **194 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **181 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0901-0237-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0748-0409-s006170 | forward | revenue | 7 | pending |
| line-1 | line-1-0748-0409-s006170 | reverse | revenue | 7 | pending |
| line-1 | line-1-0613-0485-s009617 | forward | revenue | 6 | pending |
| line-1 | line-1-0613-0485-s009617 | reverse | revenue | 6 | pending |
| line-1 | line-1-0550-0521-s011245 | forward | revenue | 6 | pending |
| line-1 | line-1-0550-0521-s011245 | reverse | revenue | 6 | pending |
| line-1 | line-1-0471-0565-s013225 | forward | revenue | 6 | pending |
| line-1 | line-1-0471-0565-s013225 | reverse | revenue | 6 | pending |
| line-1 | line-1-0394-0608-s015215 | forward | revenue | 6 | pending |
| line-1 | line-1-0394-0608-s015215 | reverse | revenue | 6 | pending |
| line-1 | line-1-0016-0869-s026109 | reverse | revenue | 6 | pending |
| line-1 | line-1-0613-0485-s009617 | forward | spare | 1 | pending |
| line-1 | line-1-0613-0485-s009617 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0521-s011245 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0521-s011245 | reverse | spare | 1 | pending |
| line-1 | line-1-0471-0565-s013225 | forward | spare | 1 | pending |
| line-1 | line-1-0471-0565-s013225 | reverse | spare | 1 | pending |
| line-1 | line-1-0394-0608-s015215 | forward | spare | 1 | pending |
| line-1 | line-1-0394-0608-s015215 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0665-0928-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0675-0777-s003786 | forward | revenue | 5 | pending |
| line-2 | line-2-0675-0777-s003786 | reverse | revenue | 5 | pending |
| line-2 | line-2-0646-0639-s006798 | forward | revenue | 5 | pending |
| line-2 | line-2-0646-0639-s006798 | reverse | revenue | 5 | pending |
| line-2 | line-2-0613-0485-s010151 | forward | revenue | 5 | pending |
| line-2 | line-2-0613-0485-s010151 | reverse | revenue | 5 | pending |
| line-2 | line-2-0574-0297-s014246 | forward | revenue | 5 | pending |
| line-2 | line-2-0574-0297-s014246 | reverse | revenue | 5 | pending |
| line-2 | line-2-0586-0120-s018324 | reverse | revenue | 5 | pending |
| line-2 | line-2-0675-0777-s003786 | forward | spare | 1 | pending |
| line-2 | line-2-0675-0777-s003786 | reverse | spare | 1 | pending |
| line-2 | line-2-0646-0639-s006798 | forward | spare | 1 | pending |
| line-2 | line-2-0646-0639-s006798 | reverse | spare | 1 | pending |
| line-2 | line-2-0613-0485-s010151 | forward | spare | 1 | pending |
| line-2 | line-2-0613-0485-s010151 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | revenue | 12 | pending |
| line-3 | line-3-0646-0640-s013511 | forward | revenue | 12 | pending |
| line-3 | line-3-0646-0640-s013511 | reverse | revenue | 11 | pending |
| line-3 | line-3-0585-0705-s015492 | forward | revenue | 11 | pending |
| line-3 | line-3-0585-0705-s015492 | reverse | revenue | 11 | pending |
| line-3 | line-3-0341-0923-s023755 | reverse | revenue | 11 | pending |
| line-3 | line-3-0646-0640-s013511 | reverse | spare | 1 | pending |
| line-3 | line-3-0585-0705-s015492 | forward | spare | 1 | pending |
| line-3 | line-3-0585-0705-s015492 | reverse | spare | 1 | pending |
| line-3 | line-3-0341-0923-s023755 | reverse | spare | 1 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0646-0640-s013511 | forward | spare | 1 | pending |
| line-3 | line-3-0646-0640-s013511 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**173 trainsets exceed the reference platform envelope**, requiring **10,293.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0016-0869-s026109 | 6 | 2 | 4 | 238.0 |
| line-1-0394-0608-s015215 | 14 | 2 | 12 | 714.0 |
| line-1-0471-0565-s013225 | 14 | 2 | 12 | 714.0 |
| line-1-0550-0521-s011245 | 14 | 2 | 12 | 714.0 |
| line-1-0613-0485-s009617 | 14 | 4 | 10 | 595.0 |
| line-1-0748-0409-s006170 | 14 | 2 | 12 | 714.0 |
| line-1-0901-0237-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0574-0297-s014246 | 10 | 2 | 8 | 476.0 |
| line-2-0586-0120-s018324 | 5 | 2 | 3 | 178.5 |
| line-2-0613-0485-s010151 | 12 | 4 | 8 | 476.0 |
| line-2-0646-0639-s006798 | 12 | 4 | 8 | 476.0 |
| line-2-0665-0928-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0675-0777-s003786 | 12 | 2 | 10 | 595.0 |
| line-3-0341-0923-s023755 | 12 | 2 | 10 | 595.0 |
| line-3-0585-0705-s015492 | 24 | 2 | 22 | 1,309.0 |
| line-3-0646-0640-s013511 | 26 | 4 | 22 | 1,309.0 |
| line-3-1020-0216-s000000 | 13 | 2 | 11 | 654.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Thika/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
