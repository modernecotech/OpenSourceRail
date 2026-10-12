# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 193 at depots = 233 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1066-0823-s026247 | line-1 | declared-depot | 72 | 4,284.0 | 12 |
| line-2-0695-0946-s000000 | line-2 | declared-depot | 40 | 2,380.0 | 7 |
| line-3-0912-0331-s000000 | line-3 | declared-depot | 46 | 2,737.0 | 8 |
| line-4-0682-0519-s000000 | line-4 | declared-depot | 11 | 654.5 | 3 |
| line-5-0379-0747-s000000 | line-5 | declared-depot | 24 | 1,428.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0146-0238-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0428-0486-s009161 | station | forward | revenue | 1 |
| line-1 | line-1-0428-0486-s009161 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0592-s013390 | station | forward | revenue | 1 |
| line-1 | line-1-0585-0592-s013390 | station | reverse | revenue | 1 |
| line-1 | line-1-0970-0805-s023438 | station | forward | revenue | 1 |
| line-1 | line-1-0970-0805-s023438 | station | reverse | revenue | 1 |
| line-1 | line-1-1066-0823-s026247 | station | reverse | revenue | 2 |
| line-2 | line-2-0365-0369-s015242 | station | reverse | revenue | 2 |
| line-2 | line-2-0428-0486-s012263 | station | forward | revenue | 1 |
| line-2 | line-2-0428-0486-s012263 | station | reverse | revenue | 1 |
| line-2 | line-2-0515-0646-s008228 | station | forward | revenue | 1 |
| line-2 | line-2-0515-0646-s008228 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0946-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0244-0849-s018851 | station | reverse | revenue | 2 |
| line-3 | line-3-0379-0747-s015142 | station | forward | revenue | 1 |
| line-3 | line-3-0379-0747-s015142 | station | reverse | revenue | 1 |
| line-3 | line-3-0515-0646-s011275 | station | forward | revenue | 1 |
| line-3 | line-3-0515-0646-s011275 | station | reverse | revenue | 1 |
| line-3 | line-3-0585-0592-s009422 | station | forward | revenue | 1 |
| line-3 | line-3-0585-0592-s009422 | station | reverse | revenue | 1 |
| line-3 | line-3-0682-0519-s006701 | station | forward | revenue | 1 |
| line-3 | line-3-0682-0519-s006701 | station | reverse | revenue | 1 |
| line-3 | line-3-0912-0331-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0488-0463-s005108 | station | reverse | revenue | 2 |
| line-4 | line-4-0562-0487-s003352 | station | forward | revenue | 1 |
| line-4 | line-4-0562-0487-s003352 | station | reverse | revenue | 1 |
| line-4 | line-4-0682-0519-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0036-0689-s008638 | station | reverse | revenue | 2 |
| line-5 | line-5-0379-0747-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1066-0823-s026247 | depot | — | revenue | 64 |
| line-1 | line-1-1066-0823-s026247 | depot | — | spare | 7 |
| line-1 | line-1-1066-0823-s026247 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0946-s000000 | depot | — | revenue | 35 |
| line-2 | line-2-0695-0946-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0695-0946-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0912-0331-s000000 | depot | — | revenue | 40 |
| line-3 | line-3-0912-0331-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0912-0331-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0682-0519-s000000 | depot | — | revenue | 9 |
| line-4 | line-4-0682-0519-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0682-0519-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0379-0747-s000000 | depot | — | revenue | 21 |
| line-5 | line-5-0379-0747-s000000 | depot | — | spare | 2 |
| line-5 | line-5-0379-0747-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fayoum-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **233 trainsets at 20 stations**; largest initial station queue **21**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **209 revenue, 19 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **193 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0146-0238-s000000 | forward | revenue | 10 | pending |
| line-1 | line-1-0428-0486-s009161 | forward | revenue | 10 | pending |
| line-1 | line-1-0428-0486-s009161 | reverse | revenue | 9 | pending |
| line-1 | line-1-0585-0592-s013390 | forward | revenue | 9 | pending |
| line-1 | line-1-0585-0592-s013390 | reverse | revenue | 9 | pending |
| line-1 | line-1-0970-0805-s023438 | forward | revenue | 9 | pending |
| line-1 | line-1-0970-0805-s023438 | reverse | revenue | 9 | pending |
| line-1 | line-1-1066-0823-s026247 | reverse | revenue | 9 | pending |
| line-1 | line-1-0428-0486-s009161 | reverse | spare | 1 | pending |
| line-1 | line-1-0585-0592-s013390 | forward | spare | 1 | pending |
| line-1 | line-1-0585-0592-s013390 | reverse | spare | 1 | pending |
| line-1 | line-1-0970-0805-s023438 | forward | spare | 1 | pending |
| line-1 | line-1-0970-0805-s023438 | reverse | spare | 1 | pending |
| line-1 | line-1-1066-0823-s026247 | reverse | spare | 1 | pending |
| line-1 | line-1-0146-0238-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0428-0486-s009161 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0946-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0515-0646-s008228 | forward | revenue | 7 | pending |
| line-2 | line-2-0515-0646-s008228 | reverse | revenue | 7 | pending |
| line-2 | line-2-0428-0486-s012263 | forward | revenue | 7 | pending |
| line-2 | line-2-0428-0486-s012263 | reverse | revenue | 7 | pending |
| line-2 | line-2-0365-0369-s015242 | reverse | revenue | 7 | pending |
| line-2 | line-2-0515-0646-s008228 | forward | spare | 1 | pending |
| line-2 | line-2-0515-0646-s008228 | reverse | spare | 1 | pending |
| line-2 | line-2-0428-0486-s012263 | forward | spare | 1 | pending |
| line-2 | line-2-0428-0486-s012263 | reverse | spare | 1 | pending |
| line-2 | line-2-0365-0369-s015242 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0912-0331-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0682-0519-s006701 | forward | revenue | 6 | pending |
| line-3 | line-3-0682-0519-s006701 | reverse | revenue | 5 | pending |
| line-3 | line-3-0585-0592-s009422 | forward | revenue | 5 | pending |
| line-3 | line-3-0585-0592-s009422 | reverse | revenue | 5 | pending |
| line-3 | line-3-0515-0646-s011275 | forward | revenue | 5 | pending |
| line-3 | line-3-0515-0646-s011275 | reverse | revenue | 5 | pending |
| line-3 | line-3-0379-0747-s015142 | forward | revenue | 5 | pending |
| line-3 | line-3-0379-0747-s015142 | reverse | revenue | 5 | pending |
| line-3 | line-3-0244-0849-s018851 | reverse | revenue | 5 | pending |
| line-3 | line-3-0682-0519-s006701 | reverse | spare | 1 | pending |
| line-3 | line-3-0585-0592-s009422 | forward | spare | 1 | pending |
| line-3 | line-3-0585-0592-s009422 | reverse | spare | 1 | pending |
| line-3 | line-3-0515-0646-s011275 | forward | spare | 1 | pending |
| line-3 | line-3-0515-0646-s011275 | reverse | spare | 1 | pending |
| line-3 | line-3-0379-0747-s015142 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0682-0519-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0562-0487-s003352 | forward | revenue | 4 | pending |
| line-4 | line-4-0562-0487-s003352 | reverse | revenue | 4 | pending |
| line-4 | line-4-0488-0463-s005108 | reverse | revenue | 3 | pending |
| line-4 | line-4-0488-0463-s005108 | reverse | spare | 1 | pending |
| line-4 | line-4-0682-0519-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0379-0747-s000000 | forward | revenue | 13 | pending |
| line-5 | line-5-0036-0689-s008638 | reverse | revenue | 12 | pending |
| line-5 | line-5-0036-0689-s008638 | reverse | spare | 1 | pending |
| line-5 | line-5-0379-0747-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0036-0689-s008638 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**177 trainsets exceed the reference platform envelope**, requiring **10,531.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0146-0238-s000000 | 11 | 2 | 9 | 535.5 |
| line-1-0428-0486-s009161 | 21 | 4 | 17 | 1,011.5 |
| line-1-0585-0592-s013390 | 20 | 4 | 16 | 952.0 |
| line-1-0970-0805-s023438 | 20 | 2 | 18 | 1,071.0 |
| line-1-1066-0823-s026247 | 10 | 2 | 8 | 476.0 |
| line-2-0365-0369-s015242 | 8 | 2 | 6 | 357.0 |
| line-2-0428-0486-s012263 | 16 | 4 | 12 | 714.0 |
| line-2-0515-0646-s008228 | 16 | 4 | 12 | 714.0 |
| line-2-0695-0946-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0244-0849-s018851 | 5 | 2 | 3 | 178.5 |
| line-3-0379-0747-s015142 | 11 | 4 | 7 | 416.5 |
| line-3-0515-0646-s011275 | 12 | 4 | 8 | 476.0 |
| line-3-0585-0592-s009422 | 12 | 4 | 8 | 476.0 |
| line-3-0682-0519-s006701 | 12 | 4 | 8 | 476.0 |
| line-3-0912-0331-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0488-0463-s005108 | 4 | 2 | 2 | 119.0 |
| line-4-0562-0487-s003352 | 8 | 2 | 6 | 357.0 |
| line-4-0682-0519-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0036-0689-s008638 | 14 | 2 | 12 | 714.0 |
| line-5-0379-0747-s000000 | 14 | 2 | 12 | 714.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Fayoum/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
