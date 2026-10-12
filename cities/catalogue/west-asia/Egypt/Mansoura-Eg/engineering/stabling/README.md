# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 143 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0781-0662-s000000 | line-1 | declared-depot | 23 | 1,368.5 | 5 |
| line-2-0399-0719-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-1100-0131-s027935 | line-3 | declared-depot | 73 | 4,343.5 | 12 |
| line-4-0621-0523-s000000 | line-4 | declared-depot | 25 | 1,487.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0292-0628-s010085 | station | reverse | revenue | 2 |
| line-1 | line-1-0427-0637-s007299 | station | forward | revenue | 1 |
| line-1 | line-1-0427-0637-s007299 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0645-s005133 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0645-s005133 | station | reverse | revenue | 1 |
| line-1 | line-1-0781-0662-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0399-0719-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0427-0637-s001872 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0637-s001872 | station | reverse | revenue | 1 |
| line-2 | line-2-0499-0428-s006742 | station | forward | revenue | 1 |
| line-2 | line-2-0499-0428-s006742 | station | reverse | revenue | 1 |
| line-2 | line-2-0536-0322-s009169 | station | reverse | revenue | 2 |
| line-3 | line-3-0405-0945-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0467-0764-s004755 | station | forward | revenue | 1 |
| line-3 | line-3-0467-0764-s004755 | station | reverse | revenue | 1 |
| line-3 | line-3-0532-0645-s008260 | station | forward | revenue | 1 |
| line-3 | line-3-0532-0645-s008260 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0523-s012489 | station | forward | revenue | 1 |
| line-3 | line-3-0621-0523-s012489 | station | reverse | revenue | 1 |
| line-3 | line-3-0783-0451-s017286 | station | forward | revenue | 1 |
| line-3 | line-3-0783-0451-s017286 | station | reverse | revenue | 1 |
| line-3 | line-3-1100-0131-s027935 | station | reverse | revenue | 2 |
| line-4 | line-4-0621-0523-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0638-0438-s001987 | station | forward | revenue | 1 |
| line-4 | line-4-0638-0438-s001987 | station | reverse | revenue | 1 |
| line-4 | line-4-0765-0138-s009686 | station | reverse | revenue | 2 |
| line-1 | line-1-0781-0662-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0781-0662-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0781-0662-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0399-0719-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0399-0719-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0399-0719-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1100-0131-s027935 | depot | — | revenue | 65 |
| line-3 | line-3-1100-0131-s027935 | depot | — | spare | 7 |
| line-3 | line-3-1100-0131-s027935 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0621-0523-s000000 | depot | — | revenue | 22 |
| line-4 | line-4-0621-0523-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0621-0523-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mansoura-eg-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 17 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **160 revenue, 13 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **143 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0781-0662-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0645-s005133 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0645-s005133 | reverse | revenue | 5 | pending |
| line-1 | line-1-0427-0637-s007299 | forward | revenue | 5 | pending |
| line-1 | line-1-0427-0637-s007299 | reverse | revenue | 4 | pending |
| line-1 | line-1-0292-0628-s010085 | reverse | revenue | 4 | pending |
| line-1 | line-1-0427-0637-s007299 | reverse | spare | 1 | pending |
| line-1 | line-1-0292-0628-s010085 | reverse | spare | 1 | pending |
| line-1 | line-1-0781-0662-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0399-0719-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0427-0637-s001872 | forward | revenue | 5 | pending |
| line-2 | line-2-0427-0637-s001872 | reverse | revenue | 5 | pending |
| line-2 | line-2-0499-0428-s006742 | forward | revenue | 4 | pending |
| line-2 | line-2-0499-0428-s006742 | reverse | revenue | 4 | pending |
| line-2 | line-2-0536-0322-s009169 | reverse | revenue | 4 | pending |
| line-2 | line-2-0499-0428-s006742 | forward | spare | 1 | pending |
| line-2 | line-2-0499-0428-s006742 | reverse | spare | 1 | pending |
| line-2 | line-2-0536-0322-s009169 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0467-0764-s004755 | forward | revenue | 8 | pending |
| line-3 | line-3-0467-0764-s004755 | reverse | revenue | 8 | pending |
| line-3 | line-3-0532-0645-s008260 | forward | revenue | 8 | pending |
| line-3 | line-3-0532-0645-s008260 | reverse | revenue | 8 | pending |
| line-3 | line-3-0621-0523-s012489 | forward | revenue | 8 | pending |
| line-3 | line-3-0621-0523-s012489 | reverse | revenue | 8 | pending |
| line-3 | line-3-0783-0451-s017286 | forward | revenue | 7 | pending |
| line-3 | line-3-0783-0451-s017286 | reverse | revenue | 7 | pending |
| line-3 | line-3-1100-0131-s027935 | reverse | revenue | 7 | pending |
| line-3 | line-3-0783-0451-s017286 | forward | spare | 1 | pending |
| line-3 | line-3-0783-0451-s017286 | reverse | spare | 1 | pending |
| line-3 | line-3-1100-0131-s027935 | reverse | spare | 1 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0764-s004755 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0764-s004755 | reverse | spare | 1 | pending |
| line-3 | line-3-0532-0645-s008260 | forward | spare | 1 | pending |
| line-3 | line-3-0532-0645-s008260 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0621-0523-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0638-0438-s001987 | forward | revenue | 7 | pending |
| line-4 | line-4-0638-0438-s001987 | reverse | revenue | 7 | pending |
| line-4 | line-4-0765-0138-s009686 | reverse | revenue | 7 | pending |
| line-4 | line-4-0621-0523-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0638-0438-s001987 | forward | spare | 1 | pending |
| line-4 | line-4-0638-0438-s001987 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**133 trainsets exceed the reference platform envelope**, requiring **7,913.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0292-0628-s010085 | 5 | 2 | 3 | 178.5 |
| line-1-0427-0637-s007299 | 10 | 4 | 6 | 357.0 |
| line-1-0532-0645-s005133 | 10 | 4 | 6 | 357.0 |
| line-1-0781-0662-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0399-0719-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0427-0637-s001872 | 10 | 4 | 6 | 357.0 |
| line-2-0499-0428-s006742 | 10 | 2 | 8 | 476.0 |
| line-2-0536-0322-s009169 | 5 | 2 | 3 | 178.5 |
| line-3-0405-0945-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0467-0764-s004755 | 18 | 2 | 16 | 952.0 |
| line-3-0532-0645-s008260 | 18 | 4 | 14 | 833.0 |
| line-3-0621-0523-s012489 | 16 | 4 | 12 | 714.0 |
| line-3-0783-0451-s017286 | 16 | 2 | 14 | 833.0 |
| line-3-1100-0131-s027935 | 8 | 2 | 6 | 357.0 |
| line-4-0621-0523-s000000 | 8 | 2 | 6 | 357.0 |
| line-4-0638-0438-s001987 | 16 | 2 | 14 | 833.0 |
| line-4-0765-0138-s009686 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mansoura-Eg/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
