# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 157 at depots = 205 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0033-0102-s026142 | line-1 | declared-depot | 60 | 3,570.0 | 11 |
| line-2-0027-0123-s000000 | line-2 | declared-depot | 52 | 3,094.0 | 10 |
| line-3-0976-0350-s000000 | line-3 | declared-depot | 45 | 2,677.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0033-0102-s026142 | station | reverse | revenue | 2 |
| line-1 | line-1-0079-0063-s024085 | station | forward | revenue | 1 |
| line-1 | line-1-0079-0063-s024085 | station | reverse | revenue | 1 |
| line-1 | line-1-0143-0140-s022058 | station | forward | revenue | 1 |
| line-1 | line-1-0143-0140-s022058 | station | reverse | revenue | 1 |
| line-1 | line-1-0401-0324-s015083 | station | forward | revenue | 1 |
| line-1 | line-1-0401-0324-s015083 | station | reverse | revenue | 1 |
| line-1 | line-1-0514-0398-s012081 | station | forward | revenue | 1 |
| line-1 | line-1-0514-0398-s012081 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0473-s009070 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0473-s009070 | station | reverse | revenue | 1 |
| line-1 | line-1-0740-0547-s006057 | station | forward | revenue | 1 |
| line-1 | line-1-0740-0547-s006057 | station | reverse | revenue | 1 |
| line-1 | line-1-0853-0620-s003040 | station | forward | revenue | 1 |
| line-1 | line-1-0853-0620-s003040 | station | reverse | revenue | 1 |
| line-1 | line-1-0937-0722-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0027-0123-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0086-0251-s003007 | station | forward | revenue | 1 |
| line-2 | line-2-0086-0251-s003007 | station | reverse | revenue | 1 |
| line-2 | line-2-0164-0405-s006519 | station | forward | revenue | 1 |
| line-2 | line-2-0164-0405-s006519 | station | reverse | revenue | 1 |
| line-2 | line-2-0248-0527-s010007 | station | forward | revenue | 1 |
| line-2 | line-2-0248-0527-s010007 | station | reverse | revenue | 1 |
| line-2 | line-2-0333-0629-s013009 | station | forward | revenue | 1 |
| line-2 | line-2-0333-0629-s013009 | station | reverse | revenue | 1 |
| line-2 | line-2-0417-0732-s016023 | station | forward | revenue | 1 |
| line-2 | line-2-0417-0732-s016023 | station | reverse | revenue | 1 |
| line-2 | line-2-0495-0826-s018737 | station | forward | revenue | 1 |
| line-2 | line-2-0495-0826-s018737 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0928-s021410 | station | reverse | revenue | 2 |
| line-3 | line-3-0196-0662-s018511 | station | reverse | revenue | 2 |
| line-3 | line-3-0313-0625-s015853 | station | forward | revenue | 1 |
| line-3 | line-3-0313-0625-s015853 | station | reverse | revenue | 1 |
| line-3 | line-3-0430-0588-s013183 | station | forward | revenue | 1 |
| line-3 | line-3-0430-0588-s013183 | station | reverse | revenue | 1 |
| line-3 | line-3-0562-0547-s010168 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0547-s010168 | station | reverse | revenue | 1 |
| line-3 | line-3-0694-0505-s007145 | station | forward | revenue | 1 |
| line-3 | line-3-0694-0505-s007145 | station | reverse | revenue | 1 |
| line-3 | line-3-0827-0463-s004125 | station | forward | revenue | 1 |
| line-3 | line-3-0827-0463-s004125 | station | reverse | revenue | 1 |
| line-3 | line-3-0976-0350-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0033-0102-s026142 | depot | — | revenue | 52 |
| line-1 | line-1-0033-0102-s026142 | depot | — | spare | 7 |
| line-1 | line-1-0033-0102-s026142 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0027-0123-s000000 | depot | — | revenue | 45 |
| line-2 | line-2-0027-0123-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0027-0123-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0976-0350-s000000 | depot | — | revenue | 39 |
| line-3 | line-3-0976-0350-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0976-0350-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/narayanganj-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **205 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **184 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **157 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0937-0722-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0853-0620-s003040 | forward | revenue | 5 | pending |
| line-1 | line-1-0853-0620-s003040 | reverse | revenue | 5 | pending |
| line-1 | line-1-0740-0547-s006057 | forward | revenue | 5 | pending |
| line-1 | line-1-0740-0547-s006057 | reverse | revenue | 5 | pending |
| line-1 | line-1-0627-0473-s009070 | forward | revenue | 5 | pending |
| line-1 | line-1-0627-0473-s009070 | reverse | revenue | 4 | pending |
| line-1 | line-1-0514-0398-s012081 | forward | revenue | 4 | pending |
| line-1 | line-1-0514-0398-s012081 | reverse | revenue | 4 | pending |
| line-1 | line-1-0401-0324-s015083 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0324-s015083 | reverse | revenue | 4 | pending |
| line-1 | line-1-0143-0140-s022058 | forward | revenue | 4 | pending |
| line-1 | line-1-0143-0140-s022058 | reverse | revenue | 4 | pending |
| line-1 | line-1-0079-0063-s024085 | forward | revenue | 4 | pending |
| line-1 | line-1-0079-0063-s024085 | reverse | revenue | 4 | pending |
| line-1 | line-1-0033-0102-s026142 | reverse | revenue | 4 | pending |
| line-1 | line-1-0627-0473-s009070 | reverse | spare | 1 | pending |
| line-1 | line-1-0514-0398-s012081 | forward | spare | 1 | pending |
| line-1 | line-1-0514-0398-s012081 | reverse | spare | 1 | pending |
| line-1 | line-1-0401-0324-s015083 | forward | spare | 1 | pending |
| line-1 | line-1-0401-0324-s015083 | reverse | spare | 1 | pending |
| line-1 | line-1-0143-0140-s022058 | forward | spare | 1 | pending |
| line-1 | line-1-0143-0140-s022058 | reverse | spare | 1 | pending |
| line-1 | line-1-0079-0063-s024085 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0027-0123-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0086-0251-s003007 | forward | revenue | 5 | pending |
| line-2 | line-2-0086-0251-s003007 | reverse | revenue | 5 | pending |
| line-2 | line-2-0164-0405-s006519 | forward | revenue | 5 | pending |
| line-2 | line-2-0164-0405-s006519 | reverse | revenue | 5 | pending |
| line-2 | line-2-0248-0527-s010007 | forward | revenue | 4 | pending |
| line-2 | line-2-0248-0527-s010007 | reverse | revenue | 4 | pending |
| line-2 | line-2-0333-0629-s013009 | forward | revenue | 4 | pending |
| line-2 | line-2-0333-0629-s013009 | reverse | revenue | 4 | pending |
| line-2 | line-2-0417-0732-s016023 | forward | revenue | 4 | pending |
| line-2 | line-2-0417-0732-s016023 | reverse | revenue | 4 | pending |
| line-2 | line-2-0495-0826-s018737 | forward | revenue | 4 | pending |
| line-2 | line-2-0495-0826-s018737 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0928-s021410 | reverse | revenue | 4 | pending |
| line-2 | line-2-0248-0527-s010007 | forward | spare | 1 | pending |
| line-2 | line-2-0248-0527-s010007 | reverse | spare | 1 | pending |
| line-2 | line-2-0333-0629-s013009 | forward | spare | 1 | pending |
| line-2 | line-2-0333-0629-s013009 | reverse | spare | 1 | pending |
| line-2 | line-2-0417-0732-s016023 | forward | spare | 1 | pending |
| line-2 | line-2-0417-0732-s016023 | reverse | spare | 1 | pending |
| line-2 | line-2-0495-0826-s018737 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0976-0350-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0827-0463-s004125 | forward | revenue | 5 | pending |
| line-3 | line-3-0827-0463-s004125 | reverse | revenue | 5 | pending |
| line-3 | line-3-0694-0505-s007145 | forward | revenue | 5 | pending |
| line-3 | line-3-0694-0505-s007145 | reverse | revenue | 5 | pending |
| line-3 | line-3-0562-0547-s010168 | forward | revenue | 4 | pending |
| line-3 | line-3-0562-0547-s010168 | reverse | revenue | 4 | pending |
| line-3 | line-3-0430-0588-s013183 | forward | revenue | 4 | pending |
| line-3 | line-3-0430-0588-s013183 | reverse | revenue | 4 | pending |
| line-3 | line-3-0313-0625-s015853 | forward | revenue | 4 | pending |
| line-3 | line-3-0313-0625-s015853 | reverse | revenue | 4 | pending |
| line-3 | line-3-0196-0662-s018511 | reverse | revenue | 4 | pending |
| line-3 | line-3-0562-0547-s010168 | forward | spare | 1 | pending |
| line-3 | line-3-0562-0547-s010168 | reverse | spare | 1 | pending |
| line-3 | line-3-0430-0588-s013183 | forward | spare | 1 | pending |
| line-3 | line-3-0430-0588-s013183 | reverse | spare | 1 | pending |
| line-3 | line-3-0313-0625-s015853 | forward | spare | 1 | pending |
| line-3 | line-3-0313-0625-s015853 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**153 trainsets exceed the reference platform envelope**, requiring **9,103.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0033-0102-s026142 | 4 | 2 | 2 | 119.0 |
| line-1-0079-0063-s024085 | 9 | 2 | 7 | 416.5 |
| line-1-0143-0140-s022058 | 10 | 2 | 8 | 476.0 |
| line-1-0401-0324-s015083 | 10 | 2 | 8 | 476.0 |
| line-1-0514-0398-s012081 | 10 | 2 | 8 | 476.0 |
| line-1-0627-0473-s009070 | 10 | 2 | 8 | 476.0 |
| line-1-0740-0547-s006057 | 10 | 2 | 8 | 476.0 |
| line-1-0853-0620-s003040 | 10 | 2 | 8 | 476.0 |
| line-1-0937-0722-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0027-0123-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0086-0251-s003007 | 10 | 2 | 8 | 476.0 |
| line-2-0164-0405-s006519 | 10 | 2 | 8 | 476.0 |
| line-2-0248-0527-s010007 | 10 | 2 | 8 | 476.0 |
| line-2-0333-0629-s013009 | 10 | 4 | 6 | 357.0 |
| line-2-0417-0732-s016023 | 10 | 2 | 8 | 476.0 |
| line-2-0495-0826-s018737 | 9 | 2 | 7 | 416.5 |
| line-2-0551-0928-s021410 | 4 | 2 | 2 | 119.0 |
| line-3-0196-0662-s018511 | 4 | 2 | 2 | 119.0 |
| line-3-0313-0625-s015853 | 10 | 4 | 6 | 357.0 |
| line-3-0430-0588-s013183 | 10 | 2 | 8 | 476.0 |
| line-3-0562-0547-s010168 | 10 | 2 | 8 | 476.0 |
| line-3-0694-0505-s007145 | 10 | 2 | 8 | 476.0 |
| line-3-0827-0463-s004125 | 10 | 2 | 8 | 476.0 |
| line-3-0976-0350-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Narayanganj/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
