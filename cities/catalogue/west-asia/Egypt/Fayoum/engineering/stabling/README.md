# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 148 at depots = 186 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1066-0823-s025597 | line-1 | declared-depot | 64 | 3,808.0 | 11 |
| line-2-0695-0946-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0912-0331-s000000 | line-3 | declared-depot | 46 | 2,737.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0146-0238-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0360-0440-s007016 | station | forward | revenue | 1 |
| line-1 | line-1-0360-0440-s007016 | station | reverse | revenue | 1 |
| line-1 | line-1-0466-0512-s009897 | station | forward | revenue | 1 |
| line-1 | line-1-0466-0512-s009897 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0571-s012259 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0571-s012259 | station | reverse | revenue | 1 |
| line-1 | line-1-0626-0619-s014159 | station | forward | revenue | 1 |
| line-1 | line-1-0626-0619-s014159 | station | reverse | revenue | 1 |
| line-1 | line-1-0697-0667-s016082 | station | forward | revenue | 1 |
| line-1 | line-1-0697-0667-s016082 | station | reverse | revenue | 1 |
| line-1 | line-1-0972-0804-s023063 | station | forward | revenue | 1 |
| line-1 | line-1-0972-0804-s023063 | station | reverse | revenue | 1 |
| line-1 | line-1-1066-0823-s025597 | station | reverse | revenue | 2 |
| line-2 | line-2-0365-0369-s014921 | station | reverse | revenue | 2 |
| line-2 | line-2-0421-0473-s012272 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0473-s012272 | station | reverse | revenue | 1 |
| line-2 | line-2-0478-0578-s009641 | station | forward | revenue | 1 |
| line-2 | line-2-0478-0578-s009641 | station | reverse | revenue | 1 |
| line-2 | line-2-0534-0681-s006988 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0681-s006988 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0946-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0244-0849-s018744 | station | reverse | revenue | 2 |
| line-3 | line-3-0404-0729-s014386 | station | forward | revenue | 1 |
| line-3 | line-3-0404-0729-s014386 | station | reverse | revenue | 1 |
| line-3 | line-3-0558-0613-s010029 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0613-s010029 | station | reverse | revenue | 1 |
| line-3 | line-3-0668-0530-s007012 | station | forward | revenue | 1 |
| line-3 | line-3-0668-0530-s007012 | station | reverse | revenue | 1 |
| line-3 | line-3-0794-0435-s003518 | station | forward | revenue | 1 |
| line-3 | line-3-0794-0435-s003518 | station | reverse | revenue | 1 |
| line-3 | line-3-0912-0331-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1066-0823-s025597 | depot | — | revenue | 56 |
| line-1 | line-1-1066-0823-s025597 | depot | — | spare | 7 |
| line-1 | line-1-1066-0823-s025597 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0946-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0695-0946-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0695-0946-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0912-0331-s000000 | depot | — | revenue | 40 |
| line-3 | line-3-0912-0331-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0912-0331-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fayoum-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **186 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **167 revenue, 16 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **148 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0146-0238-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0360-0440-s007016 | forward | revenue | 6 | pending |
| line-1 | line-1-0360-0440-s007016 | reverse | revenue | 5 | pending |
| line-1 | line-1-0466-0512-s009897 | forward | revenue | 5 | pending |
| line-1 | line-1-0466-0512-s009897 | reverse | revenue | 5 | pending |
| line-1 | line-1-0555-0571-s012259 | forward | revenue | 5 | pending |
| line-1 | line-1-0555-0571-s012259 | reverse | revenue | 5 | pending |
| line-1 | line-1-0626-0619-s014159 | forward | revenue | 5 | pending |
| line-1 | line-1-0626-0619-s014159 | reverse | revenue | 5 | pending |
| line-1 | line-1-0697-0667-s016082 | forward | revenue | 5 | pending |
| line-1 | line-1-0697-0667-s016082 | reverse | revenue | 5 | pending |
| line-1 | line-1-0972-0804-s023063 | forward | revenue | 5 | pending |
| line-1 | line-1-0972-0804-s023063 | reverse | revenue | 5 | pending |
| line-1 | line-1-1066-0823-s025597 | reverse | revenue | 5 | pending |
| line-1 | line-1-0360-0440-s007016 | reverse | spare | 1 | pending |
| line-1 | line-1-0466-0512-s009897 | forward | spare | 1 | pending |
| line-1 | line-1-0466-0512-s009897 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0571-s012259 | forward | spare | 1 | pending |
| line-1 | line-1-0555-0571-s012259 | reverse | spare | 1 | pending |
| line-1 | line-1-0626-0619-s014159 | forward | spare | 1 | pending |
| line-1 | line-1-0626-0619-s014159 | reverse | spare | 1 | pending |
| line-1 | line-1-0697-0667-s016082 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0946-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0534-0681-s006988 | forward | revenue | 6 | pending |
| line-2 | line-2-0534-0681-s006988 | reverse | revenue | 6 | pending |
| line-2 | line-2-0478-0578-s009641 | forward | revenue | 5 | pending |
| line-2 | line-2-0478-0578-s009641 | reverse | revenue | 5 | pending |
| line-2 | line-2-0421-0473-s012272 | forward | revenue | 5 | pending |
| line-2 | line-2-0421-0473-s012272 | reverse | revenue | 5 | pending |
| line-2 | line-2-0365-0369-s014921 | reverse | revenue | 5 | pending |
| line-2 | line-2-0478-0578-s009641 | forward | spare | 1 | pending |
| line-2 | line-2-0478-0578-s009641 | reverse | spare | 1 | pending |
| line-2 | line-2-0421-0473-s012272 | forward | spare | 1 | pending |
| line-2 | line-2-0421-0473-s012272 | reverse | spare | 1 | pending |
| line-2 | line-2-0365-0369-s014921 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0912-0331-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0794-0435-s003518 | forward | revenue | 6 | pending |
| line-3 | line-3-0794-0435-s003518 | reverse | revenue | 5 | pending |
| line-3 | line-3-0668-0530-s007012 | forward | revenue | 5 | pending |
| line-3 | line-3-0668-0530-s007012 | reverse | revenue | 5 | pending |
| line-3 | line-3-0558-0613-s010029 | forward | revenue | 5 | pending |
| line-3 | line-3-0558-0613-s010029 | reverse | revenue | 5 | pending |
| line-3 | line-3-0404-0729-s014386 | forward | revenue | 5 | pending |
| line-3 | line-3-0404-0729-s014386 | reverse | revenue | 5 | pending |
| line-3 | line-3-0244-0849-s018744 | reverse | revenue | 5 | pending |
| line-3 | line-3-0794-0435-s003518 | reverse | spare | 1 | pending |
| line-3 | line-3-0668-0530-s007012 | forward | spare | 1 | pending |
| line-3 | line-3-0668-0530-s007012 | reverse | spare | 1 | pending |
| line-3 | line-3-0558-0613-s010029 | forward | spare | 1 | pending |
| line-3 | line-3-0558-0613-s010029 | reverse | spare | 1 | pending |
| line-3 | line-3-0404-0729-s014386 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**148 trainsets exceed the reference platform envelope**, requiring **8,806.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0146-0238-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0360-0440-s007016 | 12 | 2 | 10 | 595.0 |
| line-1-0466-0512-s009897 | 12 | 2 | 10 | 595.0 |
| line-1-0555-0571-s012259 | 12 | 2 | 10 | 595.0 |
| line-1-0626-0619-s014159 | 12 | 2 | 10 | 595.0 |
| line-1-0697-0667-s016082 | 11 | 2 | 9 | 535.5 |
| line-1-0972-0804-s023063 | 10 | 2 | 8 | 476.0 |
| line-1-1066-0823-s025597 | 5 | 2 | 3 | 178.5 |
| line-2-0365-0369-s014921 | 6 | 2 | 4 | 238.0 |
| line-2-0421-0473-s012272 | 12 | 2 | 10 | 595.0 |
| line-2-0478-0578-s009641 | 12 | 2 | 10 | 595.0 |
| line-2-0534-0681-s006988 | 12 | 2 | 10 | 595.0 |
| line-2-0695-0946-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0244-0849-s018744 | 5 | 2 | 3 | 178.5 |
| line-3-0404-0729-s014386 | 11 | 2 | 9 | 535.5 |
| line-3-0558-0613-s010029 | 12 | 2 | 10 | 595.0 |
| line-3-0668-0530-s007012 | 12 | 2 | 10 | 595.0 |
| line-3-0794-0435-s003518 | 12 | 2 | 10 | 595.0 |
| line-3-0912-0331-s000000 | 6 | 2 | 4 | 238.0 |

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
