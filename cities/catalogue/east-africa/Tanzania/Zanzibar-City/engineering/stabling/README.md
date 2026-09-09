# Station and depot overnight allocation

Plan: **42 trainsets at stations + 92 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0434-0670-s021743 | 92 | 5,474.0 | 21 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0178-0650-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0415-0602-s005984 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0602-s005984 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0529-s009005 | station | forward | revenue | 1 |
| line-1 | line-1-0511-0529-s009005 | station | reverse | revenue | 1 |
| line-1 | line-1-0545-0520-s010623 | station | forward | revenue | 1 |
| line-1 | line-1-0545-0520-s010623 | station | reverse | revenue | 1 |
| line-1 | line-1-0615-0556-s013625 | station | forward | revenue | 1 |
| line-1 | line-1-0615-0556-s013625 | station | reverse | revenue | 1 |
| line-1 | line-1-0724-0594-s016358 | station | forward | revenue | 1 |
| line-1 | line-1-0724-0594-s016358 | station | reverse | revenue | 1 |
| line-1 | line-1-0826-0578-s019084 | station | reverse | revenue | 2 |
| line-2 | line-2-0363-0136-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0503-0420-s006840 | station | forward | revenue | 1 |
| line-2 | line-2-0503-0420-s006840 | station | reverse | revenue | 1 |
| line-2 | line-2-0536-0618-s011796 | station | forward | revenue | 1 |
| line-2 | line-2-0536-0618-s011796 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0556-s010187 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0556-s010187 | station | reverse | revenue | 1 |
| line-2 | line-2-0553-0494-s008786 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0494-s008786 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0671-s014802 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0671-s014802 | station | reverse | revenue | 1 |
| line-2 | line-2-0712-0922-s021027 | station | reverse | revenue | 2 |
| line-3 | line-3-0434-0670-s021743 | station | reverse | revenue | 2 |
| line-3 | line-3-0482-0632-s018821 | station | forward | revenue | 1 |
| line-3 | line-3-0482-0632-s018821 | station | reverse | revenue | 1 |
| line-3 | line-3-0551-0556-s015235 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0556-s015235 | station | reverse | revenue | 1 |
| line-3 | line-3-0637-0565-s013060 | station | forward | revenue | 1 |
| line-3 | line-3-0637-0565-s013060 | station | reverse | revenue | 1 |
| line-3 | line-3-0741-0616-s010035 | station | forward | revenue | 1 |
| line-3 | line-3-0741-0616-s010035 | station | reverse | revenue | 1 |
| line-3 | line-3-0832-0703-s007015 | station | forward | revenue | 1 |
| line-3 | line-3-0832-0703-s007015 | station | reverse | revenue | 1 |
| line-3 | line-3-1069-0872-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0434-0670-s021743 | depot | — | revenue | 23 |
| line-1 | line-3-0434-0670-s021743 | depot | — | spare | 3 |
| line-1 | line-3-0434-0670-s021743 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0434-0670-s021743 | depot | — | revenue | 27 |
| line-2 | line-3-0434-0670-s021743 | depot | — | spare | 4 |
| line-2 | line-3-0434-0670-s021743 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0434-0670-s021743 | depot | — | revenue | 28 |
| line-3 | line-3-0434-0670-s021743 | depot | — | spare | 4 |
| line-3 | line-3-0434-0670-s021743 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (27 trains), line-2 (32 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **92 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0178-0650-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0415-0602-s005984 | forward | revenue | 3 | pending |
| line-1 | line-1-0415-0602-s005984 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0529-s009005 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0529-s009005 | reverse | revenue | 3 | pending |
| line-1 | line-1-0545-0520-s010623 | forward | revenue | 3 | pending |
| line-1 | line-1-0545-0520-s010623 | reverse | revenue | 3 | pending |
| line-1 | line-1-0615-0556-s013625 | forward | revenue | 3 | pending |
| line-1 | line-1-0615-0556-s013625 | reverse | revenue | 3 | pending |
| line-1 | line-1-0724-0594-s016358 | forward | revenue | 3 | pending |
| line-1 | line-1-0724-0594-s016358 | reverse | revenue | 3 | pending |
| line-1 | line-1-0826-0578-s019084 | reverse | revenue | 3 | pending |
| line-1 | line-1-0415-0602-s005984 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0602-s005984 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0529-s009005 | forward | spare | 1 | pending |
| line-1 | line-1-0511-0529-s009005 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0363-0136-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0503-0420-s006840 | forward | revenue | 4 | pending |
| line-2 | line-2-0503-0420-s006840 | reverse | revenue | 4 | pending |
| line-2 | line-2-0553-0494-s008786 | forward | revenue | 4 | pending |
| line-2 | line-2-0553-0494-s008786 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0556-s010187 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0556-s010187 | reverse | revenue | 3 | pending |
| line-2 | line-2-0536-0618-s011796 | forward | revenue | 3 | pending |
| line-2 | line-2-0536-0618-s011796 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0671-s014802 | forward | revenue | 3 | pending |
| line-2 | line-2-0611-0671-s014802 | reverse | revenue | 3 | pending |
| line-2 | line-2-0712-0922-s021027 | reverse | revenue | 3 | pending |
| line-2 | line-2-0551-0556-s010187 | forward | spare | 1 | pending |
| line-2 | line-2-0551-0556-s010187 | reverse | spare | 1 | pending |
| line-2 | line-2-0536-0618-s011796 | forward | spare | 1 | pending |
| line-2 | line-2-0536-0618-s011796 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0671-s014802 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0832-0703-s007015 | forward | revenue | 4 | pending |
| line-3 | line-3-0832-0703-s007015 | reverse | revenue | 4 | pending |
| line-3 | line-3-0741-0616-s010035 | forward | revenue | 4 | pending |
| line-3 | line-3-0741-0616-s010035 | reverse | revenue | 4 | pending |
| line-3 | line-3-0637-0565-s013060 | forward | revenue | 4 | pending |
| line-3 | line-3-0637-0565-s013060 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0556-s015235 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0556-s015235 | reverse | revenue | 3 | pending |
| line-3 | line-3-0482-0632-s018821 | forward | revenue | 3 | pending |
| line-3 | line-3-0482-0632-s018821 | reverse | revenue | 3 | pending |
| line-3 | line-3-0434-0670-s021743 | reverse | revenue | 3 | pending |
| line-3 | line-3-0637-0565-s013060 | reverse | spare | 1 | pending |
| line-3 | line-3-0551-0556-s015235 | forward | spare | 1 | pending |
| line-3 | line-3-0551-0556-s015235 | reverse | spare | 1 | pending |
| line-3 | line-3-0482-0632-s018821 | forward | spare | 1 | pending |
| line-3 | line-3-0482-0632-s018821 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**76 trainsets exceed the reference platform envelope**, requiring **4,522.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0178-0650-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0415-0602-s005984 | 8 | 2 | 6 | 357.0 |
| line-1-0511-0529-s009005 | 8 | 2 | 6 | 357.0 |
| line-1-0545-0520-s010623 | 6 | 4 | 2 | 119.0 |
| line-1-0615-0556-s013625 | 6 | 4 | 2 | 119.0 |
| line-1-0724-0594-s016358 | 6 | 4 | 2 | 119.0 |
| line-1-0826-0578-s019084 | 3 | 2 | 1 | 59.5 |
| line-2-0363-0136-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0503-0420-s006840 | 8 | 2 | 6 | 357.0 |
| line-2-0536-0618-s011796 | 8 | 2 | 6 | 357.0 |
| line-2-0551-0556-s010187 | 8 | 4 | 4 | 238.0 |
| line-2-0553-0494-s008786 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0671-s014802 | 7 | 2 | 5 | 297.5 |
| line-2-0712-0922-s021027 | 3 | 2 | 1 | 59.5 |
| line-3-0434-0670-s021743 | 3 | 2 | 1 | 59.5 |
| line-3-0482-0632-s018821 | 8 | 2 | 6 | 357.0 |
| line-3-0551-0556-s015235 | 8 | 4 | 4 | 238.0 |
| line-3-0637-0565-s013060 | 8 | 4 | 4 | 238.0 |
| line-3-0741-0616-s010035 | 8 | 4 | 4 | 238.0 |
| line-3-0832-0703-s007015 | 8 | 2 | 6 | 357.0 |
| line-3-1069-0872-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Zanzibar-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
