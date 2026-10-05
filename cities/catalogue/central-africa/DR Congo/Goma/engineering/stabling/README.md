# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 111 at depots = 149 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0681-0770-s019435 | line-1 | declared-depot | 44 | 2,618.0 | 9 |
| line-2-0948-0862-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0430-0815-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0237-0086-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0333-0319-s006688 | station | forward | revenue | 1 |
| line-1 | line-1-0333-0319-s006688 | station | reverse | revenue | 1 |
| line-1 | line-1-0402-0409-s009212 | station | forward | revenue | 1 |
| line-1 | line-1-0402-0409-s009212 | station | reverse | revenue | 1 |
| line-1 | line-1-0484-0515-s012211 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0515-s012211 | station | reverse | revenue | 1 |
| line-1 | line-1-0527-0570-s013772 | station | forward | revenue | 1 |
| line-1 | line-1-0527-0570-s013772 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0621-s015221 | station | forward | revenue | 1 |
| line-1 | line-1-0566-0621-s015221 | station | reverse | revenue | 1 |
| line-1 | line-1-0648-0727-s018231 | station | forward | revenue | 1 |
| line-1 | line-1-0648-0727-s018231 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0770-s019435 | station | reverse | revenue | 2 |
| line-2 | line-2-0319-0639-s016085 | station | reverse | revenue | 2 |
| line-2 | line-2-0421-0682-s013665 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0682-s013665 | station | reverse | revenue | 1 |
| line-2 | line-2-0506-0717-s011628 | station | forward | revenue | 1 |
| line-2 | line-2-0506-0717-s011628 | station | reverse | revenue | 1 |
| line-2 | line-2-0591-0753-s009607 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0753-s009607 | station | reverse | revenue | 1 |
| line-2 | line-2-0717-0806-s006589 | station | forward | revenue | 1 |
| line-2 | line-2-0717-0806-s006589 | station | reverse | revenue | 1 |
| line-2 | line-2-0948-0862-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0392-0261-s011395 | station | reverse | revenue | 2 |
| line-3 | line-3-0402-0409-s008352 | station | forward | revenue | 1 |
| line-3 | line-3-0402-0409-s008352 | station | reverse | revenue | 1 |
| line-3 | line-3-0410-0523-s006006 | station | forward | revenue | 1 |
| line-3 | line-3-0410-0523-s006006 | station | reverse | revenue | 1 |
| line-3 | line-3-0421-0682-s002735 | station | forward | revenue | 1 |
| line-3 | line-3-0421-0682-s002735 | station | reverse | revenue | 1 |
| line-3 | line-3-0430-0815-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0681-0770-s019435 | depot | — | revenue | 38 |
| line-1 | line-1-0681-0770-s019435 | depot | — | spare | 5 |
| line-1 | line-1-0681-0770-s019435 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0948-0862-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0948-0862-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0948-0862-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0430-0815-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0430-0815-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0430-0815-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/goma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **149 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **134 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **111 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0237-0086-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0333-0319-s006688 | forward | revenue | 4 | pending |
| line-1 | line-1-0333-0319-s006688 | reverse | revenue | 4 | pending |
| line-1 | line-1-0402-0409-s009212 | forward | revenue | 4 | pending |
| line-1 | line-1-0402-0409-s009212 | reverse | revenue | 4 | pending |
| line-1 | line-1-0484-0515-s012211 | forward | revenue | 4 | pending |
| line-1 | line-1-0484-0515-s012211 | reverse | revenue | 4 | pending |
| line-1 | line-1-0527-0570-s013772 | forward | revenue | 4 | pending |
| line-1 | line-1-0527-0570-s013772 | reverse | revenue | 4 | pending |
| line-1 | line-1-0566-0621-s015221 | forward | revenue | 4 | pending |
| line-1 | line-1-0566-0621-s015221 | reverse | revenue | 4 | pending |
| line-1 | line-1-0648-0727-s018231 | forward | revenue | 4 | pending |
| line-1 | line-1-0648-0727-s018231 | reverse | revenue | 3 | pending |
| line-1 | line-1-0681-0770-s019435 | reverse | revenue | 3 | pending |
| line-1 | line-1-0648-0727-s018231 | reverse | spare | 1 | pending |
| line-1 | line-1-0681-0770-s019435 | reverse | spare | 1 | pending |
| line-1 | line-1-0237-0086-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0333-0319-s006688 | forward | spare | 1 | pending |
| line-1 | line-1-0333-0319-s006688 | reverse | spare | 1 | pending |
| line-1 | line-1-0402-0409-s009212 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0948-0862-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0717-0806-s006589 | forward | revenue | 5 | pending |
| line-2 | line-2-0717-0806-s006589 | reverse | revenue | 5 | pending |
| line-2 | line-2-0591-0753-s009607 | forward | revenue | 5 | pending |
| line-2 | line-2-0591-0753-s009607 | reverse | revenue | 5 | pending |
| line-2 | line-2-0506-0717-s011628 | forward | revenue | 5 | pending |
| line-2 | line-2-0506-0717-s011628 | reverse | revenue | 4 | pending |
| line-2 | line-2-0421-0682-s013665 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0682-s013665 | reverse | revenue | 4 | pending |
| line-2 | line-2-0319-0639-s016085 | reverse | revenue | 4 | pending |
| line-2 | line-2-0506-0717-s011628 | reverse | spare | 1 | pending |
| line-2 | line-2-0421-0682-s013665 | forward | spare | 1 | pending |
| line-2 | line-2-0421-0682-s013665 | reverse | spare | 1 | pending |
| line-2 | line-2-0319-0639-s016085 | reverse | spare | 1 | pending |
| line-2 | line-2-0948-0862-s000000 | forward | cold_reserve | 1 | pending |
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

**103 trainsets exceed the reference platform envelope**, requiring **6,128.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0237-0086-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0333-0319-s006688 | 10 | 2 | 8 | 476.0 |
| line-1-0402-0409-s009212 | 9 | 4 | 5 | 297.5 |
| line-1-0484-0515-s012211 | 8 | 2 | 6 | 357.0 |
| line-1-0527-0570-s013772 | 8 | 2 | 6 | 357.0 |
| line-1-0566-0621-s015221 | 8 | 2 | 6 | 357.0 |
| line-1-0648-0727-s018231 | 8 | 2 | 6 | 357.0 |
| line-1-0681-0770-s019435 | 4 | 2 | 2 | 119.0 |
| line-2-0319-0639-s016085 | 5 | 2 | 3 | 178.5 |
| line-2-0421-0682-s013665 | 10 | 4 | 6 | 357.0 |
| line-2-0506-0717-s011628 | 10 | 2 | 8 | 476.0 |
| line-2-0591-0753-s009607 | 10 | 2 | 8 | 476.0 |
| line-2-0717-0806-s006589 | 10 | 2 | 8 | 476.0 |
| line-2-0948-0862-s000000 | 6 | 2 | 4 | 238.0 |
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
