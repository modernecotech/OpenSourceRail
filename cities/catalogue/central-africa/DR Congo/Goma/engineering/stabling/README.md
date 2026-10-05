# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 110 at depots = 148 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0681-0770-s018793 | line-1 | declared-depot | 44 | 2,618.0 | 9 |
| line-2-0948-0862-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0430-0815-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0237-0086-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0333-0319-s006047 | station | forward | revenue | 1 |
| line-1 | line-1-0333-0319-s006047 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0409-s008571 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0409-s008571 | station | reverse | revenue | 1 |
| line-1 | line-1-0484-0515-s011569 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0515-s011569 | station | reverse | revenue | 1 |
| line-1 | line-1-0527-0570-s013131 | station | forward | revenue | 1 |
| line-1 | line-1-0527-0570-s013131 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0621-s014579 | station | forward | revenue | 1 |
| line-1 | line-1-0566-0621-s014579 | station | reverse | revenue | 1 |
| line-1 | line-1-0648-0727-s017590 | station | forward | revenue | 1 |
| line-1 | line-1-0648-0727-s017590 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0770-s018793 | station | reverse | revenue | 2 |
| line-2 | line-2-0319-0639-s015718 | station | reverse | revenue | 2 |
| line-2 | line-2-0421-0682-s013298 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0682-s013298 | station | reverse | revenue | 1 |
| line-2 | line-2-0506-0717-s011262 | station | forward | revenue | 1 |
| line-2 | line-2-0506-0717-s011262 | station | reverse | revenue | 1 |
| line-2 | line-2-0591-0753-s009240 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0753-s009240 | station | reverse | revenue | 1 |
| line-2 | line-2-0717-0806-s006222 | station | forward | revenue | 1 |
| line-2 | line-2-0717-0806-s006222 | station | reverse | revenue | 1 |
| line-2 | line-2-0948-0862-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0392-0261-s011395 | station | reverse | revenue | 2 |
| line-3 | line-3-0402-0409-s008352 | station | forward | revenue | 1 |
| line-3 | line-3-0402-0409-s008352 | station | reverse | revenue | 1 |
| line-3 | line-3-0410-0523-s006006 | station | forward | revenue | 1 |
| line-3 | line-3-0410-0523-s006006 | station | reverse | revenue | 1 |
| line-3 | line-3-0421-0682-s002735 | station | forward | revenue | 1 |
| line-3 | line-3-0421-0682-s002735 | station | reverse | revenue | 1 |
| line-3 | line-3-0430-0815-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0681-0770-s018793 | depot | — | revenue | 38 |
| line-1 | line-1-0681-0770-s018793 | depot | — | spare | 5 |
| line-1 | line-1-0681-0770-s018793 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0948-0862-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0948-0862-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0948-0862-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0430-0815-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0430-0815-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0430-0815-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/goma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **148 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **133 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **110 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0237-0086-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0333-0319-s006047 | forward | revenue | 4 | pending |
| line-1 | line-1-0333-0319-s006047 | reverse | revenue | 4 | pending |
| line-1 | line-1-0402-0409-s008571 | forward | revenue | 4 | pending |
| line-1 | line-1-0402-0409-s008571 | reverse | revenue | 4 | pending |
| line-1 | line-1-0484-0515-s011569 | forward | revenue | 4 | pending |
| line-1 | line-1-0484-0515-s011569 | reverse | revenue | 4 | pending |
| line-1 | line-1-0527-0570-s013131 | forward | revenue | 4 | pending |
| line-1 | line-1-0527-0570-s013131 | reverse | revenue | 4 | pending |
| line-1 | line-1-0566-0621-s014579 | forward | revenue | 4 | pending |
| line-1 | line-1-0566-0621-s014579 | reverse | revenue | 4 | pending |
| line-1 | line-1-0648-0727-s017590 | forward | revenue | 4 | pending |
| line-1 | line-1-0648-0727-s017590 | reverse | revenue | 3 | pending |
| line-1 | line-1-0681-0770-s018793 | reverse | revenue | 3 | pending |
| line-1 | line-1-0648-0727-s017590 | reverse | spare | 1 | pending |
| line-1 | line-1-0681-0770-s018793 | reverse | spare | 1 | pending |
| line-1 | line-1-0237-0086-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0333-0319-s006047 | forward | spare | 1 | pending |
| line-1 | line-1-0333-0319-s006047 | reverse | spare | 1 | pending |
| line-1 | line-1-0402-0409-s008571 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0948-0862-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0717-0806-s006222 | forward | revenue | 5 | pending |
| line-2 | line-2-0717-0806-s006222 | reverse | revenue | 5 | pending |
| line-2 | line-2-0591-0753-s009240 | forward | revenue | 5 | pending |
| line-2 | line-2-0591-0753-s009240 | reverse | revenue | 5 | pending |
| line-2 | line-2-0506-0717-s011262 | forward | revenue | 4 | pending |
| line-2 | line-2-0506-0717-s011262 | reverse | revenue | 4 | pending |
| line-2 | line-2-0421-0682-s013298 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0682-s013298 | reverse | revenue | 4 | pending |
| line-2 | line-2-0319-0639-s015718 | reverse | revenue | 4 | pending |
| line-2 | line-2-0506-0717-s011262 | forward | spare | 1 | pending |
| line-2 | line-2-0506-0717-s011262 | reverse | spare | 1 | pending |
| line-2 | line-2-0421-0682-s013298 | forward | spare | 1 | pending |
| line-2 | line-2-0421-0682-s013298 | reverse | spare | 1 | pending |
| line-2 | line-2-0319-0639-s015718 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0430-0815-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0421-0682-s002735 | forward | revenue | 5 | pending |
| line-3 | line-3-0421-0682-s002735 | reverse | revenue | 4 | pending |
| line-3 | line-3-0410-0523-s006006 | forward | revenue | 4 | pending |
| line-3 | line-3-0410-0523-s006006 | reverse | revenue | 4 | pending |
| line-3 | line-3-0402-0409-s008352 | forward | revenue | 4 | pending |
| line-3 | line-3-0402-0409-s008352 | reverse | revenue | 4 | pending |
| line-3 | line-3-0392-0261-s011395 | reverse | revenue | 4 | pending |
| line-3 | line-3-0421-0682-s002735 | reverse | spare | 1 | pending |
| line-3 | line-3-0410-0523-s006006 | forward | spare | 1 | pending |
| line-3 | line-3-0410-0523-s006006 | reverse | spare | 1 | pending |
| line-3 | line-3-0402-0409-s008352 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**102 trainsets exceed the reference platform envelope**, requiring **6,069.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0237-0086-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0333-0319-s006047 | 10 | 2 | 8 | 476.0 |
| line-1-0402-0409-s008571 | 9 | 4 | 5 | 297.5 |
| line-1-0484-0515-s011569 | 8 | 2 | 6 | 357.0 |
| line-1-0527-0570-s013131 | 8 | 2 | 6 | 357.0 |
| line-1-0566-0621-s014579 | 8 | 2 | 6 | 357.0 |
| line-1-0648-0727-s017590 | 8 | 2 | 6 | 357.0 |
| line-1-0681-0770-s018793 | 4 | 2 | 2 | 119.0 |
| line-2-0319-0639-s015718 | 5 | 2 | 3 | 178.5 |
| line-2-0421-0682-s013298 | 10 | 4 | 6 | 357.0 |
| line-2-0506-0717-s011262 | 10 | 2 | 8 | 476.0 |
| line-2-0591-0753-s009240 | 10 | 2 | 8 | 476.0 |
| line-2-0717-0806-s006222 | 10 | 2 | 8 | 476.0 |
| line-2-0948-0862-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0392-0261-s011395 | 4 | 2 | 2 | 119.0 |
| line-3-0402-0409-s008352 | 9 | 4 | 5 | 297.5 |
| line-3-0410-0523-s006006 | 10 | 2 | 8 | 476.0 |
| line-3-0421-0682-s002735 | 10 | 4 | 6 | 357.0 |
| line-3-0430-0815-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Goma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
