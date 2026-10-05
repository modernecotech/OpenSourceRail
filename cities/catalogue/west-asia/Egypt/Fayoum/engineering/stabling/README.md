# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 144 at depots = 184 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1066-0823-s025597 | line-1 | declared-depot | 65 | 3,867.5 | 11 |
| line-2-0695-0946-s000000 | line-2 | declared-depot | 34 | 2,023.0 | 7 |
| line-3-0912-0331-s000000 | line-3 | declared-depot | 45 | 2,677.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0146-0238-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0360-0440-s007016 | station | forward | revenue | 1 |
| line-1 | line-1-0360-0440-s007016 | station | reverse | revenue | 1 |
| line-1 | line-1-0428-0486-s008851 | station | forward | revenue | 1 |
| line-1 | line-1-0428-0486-s008851 | station | reverse | revenue | 1 |
| line-1 | line-1-0506-0539-s010979 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0539-s010979 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0592-s013080 | station | forward | revenue | 1 |
| line-1 | line-1-0585-0592-s013080 | station | reverse | revenue | 1 |
| line-1 | line-1-0972-0804-s023063 | station | forward | revenue | 1 |
| line-1 | line-1-0972-0804-s023063 | station | reverse | revenue | 1 |
| line-1 | line-1-1066-0823-s025597 | station | reverse | revenue | 2 |
| line-2 | line-2-0365-0369-s014921 | station | reverse | revenue | 2 |
| line-2 | line-2-0428-0486-s011942 | station | forward | revenue | 1 |
| line-2 | line-2-0428-0486-s011942 | station | reverse | revenue | 1 |
| line-2 | line-2-0472-0567-s009923 | station | forward | revenue | 1 |
| line-2 | line-2-0472-0567-s009923 | station | reverse | revenue | 1 |
| line-2 | line-2-0515-0646-s007907 | station | forward | revenue | 1 |
| line-2 | line-2-0515-0646-s007907 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0802-s003960 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0802-s003960 | station | reverse | revenue | 1 |
| line-2 | line-2-0695-0946-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0244-0849-s018744 | station | reverse | revenue | 2 |
| line-3 | line-3-0382-0745-s014959 | station | forward | revenue | 1 |
| line-3 | line-3-0382-0745-s014959 | station | reverse | revenue | 1 |
| line-3 | line-3-0515-0646-s011168 | station | forward | revenue | 1 |
| line-3 | line-3-0515-0646-s011168 | station | reverse | revenue | 1 |
| line-3 | line-3-0585-0592-s009315 | station | forward | revenue | 1 |
| line-3 | line-3-0585-0592-s009315 | station | reverse | revenue | 1 |
| line-3 | line-3-0668-0530-s007012 | station | forward | revenue | 1 |
| line-3 | line-3-0668-0530-s007012 | station | reverse | revenue | 1 |
| line-3 | line-3-0794-0435-s003518 | station | forward | revenue | 1 |
| line-3 | line-3-0794-0435-s003518 | station | reverse | revenue | 1 |
| line-3 | line-3-0912-0331-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1066-0823-s025597 | depot | — | revenue | 57 |
| line-1 | line-1-1066-0823-s025597 | depot | — | spare | 7 |
| line-1 | line-1-1066-0823-s025597 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0946-s000000 | depot | — | revenue | 29 |
| line-2 | line-2-0695-0946-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0695-0946-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0912-0331-s000000 | depot | — | revenue | 39 |
| line-3 | line-3-0912-0331-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0912-0331-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fayoum-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **184 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **165 revenue, 16 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **144 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0146-0238-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0360-0440-s007016 | forward | revenue | 6 | pending |
| line-1 | line-1-0360-0440-s007016 | reverse | revenue | 6 | pending |
| line-1 | line-1-0428-0486-s008851 | forward | revenue | 6 | pending |
| line-1 | line-1-0428-0486-s008851 | reverse | revenue | 6 | pending |
| line-1 | line-1-0506-0539-s010979 | forward | revenue | 6 | pending |
| line-1 | line-1-0506-0539-s010979 | reverse | revenue | 6 | pending |
| line-1 | line-1-0585-0592-s013080 | forward | revenue | 6 | pending |
| line-1 | line-1-0585-0592-s013080 | reverse | revenue | 6 | pending |
| line-1 | line-1-0972-0804-s023063 | forward | revenue | 6 | pending |
| line-1 | line-1-0972-0804-s023063 | reverse | revenue | 6 | pending |
| line-1 | line-1-1066-0823-s025597 | reverse | revenue | 5 | pending |
| line-1 | line-1-1066-0823-s025597 | reverse | spare | 1 | pending |
| line-1 | line-1-0146-0238-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0360-0440-s007016 | forward | spare | 1 | pending |
| line-1 | line-1-0360-0440-s007016 | reverse | spare | 1 | pending |
| line-1 | line-1-0428-0486-s008851 | forward | spare | 1 | pending |
| line-1 | line-1-0428-0486-s008851 | reverse | spare | 1 | pending |
| line-1 | line-1-0506-0539-s010979 | forward | spare | 1 | pending |
| line-1 | line-1-0506-0539-s010979 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0946-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0599-0802-s003960 | forward | revenue | 4 | pending |
| line-2 | line-2-0599-0802-s003960 | reverse | revenue | 4 | pending |
| line-2 | line-2-0515-0646-s007907 | forward | revenue | 4 | pending |
| line-2 | line-2-0515-0646-s007907 | reverse | revenue | 4 | pending |
| line-2 | line-2-0472-0567-s009923 | forward | revenue | 4 | pending |
| line-2 | line-2-0472-0567-s009923 | reverse | revenue | 4 | pending |
| line-2 | line-2-0428-0486-s011942 | forward | revenue | 4 | pending |
| line-2 | line-2-0428-0486-s011942 | reverse | revenue | 4 | pending |
| line-2 | line-2-0365-0369-s014921 | reverse | revenue | 4 | pending |
| line-2 | line-2-0599-0802-s003960 | forward | spare | 1 | pending |
| line-2 | line-2-0599-0802-s003960 | reverse | spare | 1 | pending |
| line-2 | line-2-0515-0646-s007907 | forward | spare | 1 | pending |
| line-2 | line-2-0515-0646-s007907 | reverse | spare | 1 | pending |
| line-2 | line-2-0472-0567-s009923 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0912-0331-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0794-0435-s003518 | forward | revenue | 5 | pending |
| line-3 | line-3-0794-0435-s003518 | reverse | revenue | 5 | pending |
| line-3 | line-3-0668-0530-s007012 | forward | revenue | 5 | pending |
| line-3 | line-3-0668-0530-s007012 | reverse | revenue | 5 | pending |
| line-3 | line-3-0585-0592-s009315 | forward | revenue | 4 | pending |
| line-3 | line-3-0585-0592-s009315 | reverse | revenue | 4 | pending |
| line-3 | line-3-0515-0646-s011168 | forward | revenue | 4 | pending |
| line-3 | line-3-0515-0646-s011168 | reverse | revenue | 4 | pending |
| line-3 | line-3-0382-0745-s014959 | forward | revenue | 4 | pending |
| line-3 | line-3-0382-0745-s014959 | reverse | revenue | 4 | pending |
| line-3 | line-3-0244-0849-s018744 | reverse | revenue | 4 | pending |
| line-3 | line-3-0585-0592-s009315 | forward | spare | 1 | pending |
| line-3 | line-3-0585-0592-s009315 | reverse | spare | 1 | pending |
| line-3 | line-3-0515-0646-s011168 | forward | spare | 1 | pending |
| line-3 | line-3-0515-0646-s011168 | reverse | spare | 1 | pending |
| line-3 | line-3-0382-0745-s014959 | forward | spare | 1 | pending |
| line-3 | line-3-0382-0745-s014959 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**132 trainsets exceed the reference platform envelope**, requiring **7,854.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0146-0238-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0360-0440-s007016 | 14 | 2 | 12 | 714.0 |
| line-1-0428-0486-s008851 | 14 | 4 | 10 | 595.0 |
| line-1-0506-0539-s010979 | 14 | 2 | 12 | 714.0 |
| line-1-0585-0592-s013080 | 12 | 4 | 8 | 476.0 |
| line-1-0972-0804-s023063 | 12 | 2 | 10 | 595.0 |
| line-1-1066-0823-s025597 | 6 | 2 | 4 | 238.0 |
| line-2-0365-0369-s014921 | 4 | 2 | 2 | 119.0 |
| line-2-0428-0486-s011942 | 8 | 4 | 4 | 238.0 |
| line-2-0472-0567-s009923 | 9 | 2 | 7 | 416.5 |
| line-2-0515-0646-s007907 | 10 | 4 | 6 | 357.0 |
| line-2-0599-0802-s003960 | 10 | 2 | 8 | 476.0 |
| line-2-0695-0946-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0244-0849-s018744 | 4 | 2 | 2 | 119.0 |
| line-3-0382-0745-s014959 | 10 | 2 | 8 | 476.0 |
| line-3-0515-0646-s011168 | 10 | 4 | 6 | 357.0 |
| line-3-0585-0592-s009315 | 10 | 4 | 6 | 357.0 |
| line-3-0668-0530-s007012 | 10 | 2 | 8 | 476.0 |
| line-3-0794-0435-s003518 | 10 | 2 | 8 | 476.0 |
| line-3-0912-0331-s000000 | 5 | 2 | 3 | 178.5 |

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
