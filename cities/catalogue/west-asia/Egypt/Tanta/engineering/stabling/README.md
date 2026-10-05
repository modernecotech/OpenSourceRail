# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 176 at depots = 212 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0334-0571-s000000 | line-1 | declared-depot | 38 | 2,261.0 | 7 |
| line-2-0222-0124-s000000 | line-2 | declared-depot | 65 | 3,867.5 | 11 |
| line-3-0068-0951-s027547 | line-3 | declared-depot | 73 | 4,343.5 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0334-0571-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0458-0515-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0458-0515-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0458-s006013 | station | forward | revenue | 1 |
| line-1 | line-1-0582-0458-s006013 | station | reverse | revenue | 1 |
| line-1 | line-1-0773-0371-s010636 | station | forward | revenue | 1 |
| line-1 | line-1-0773-0371-s010636 | station | reverse | revenue | 1 |
| line-1 | line-1-0950-0251-s015264 | station | reverse | revenue | 2 |
| line-2 | line-2-0222-0124-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0415-0366-s007009 | station | forward | revenue | 1 |
| line-2 | line-2-0415-0366-s007009 | station | reverse | revenue | 1 |
| line-2 | line-2-0494-0474-s010035 | station | forward | revenue | 1 |
| line-2 | line-2-0494-0474-s010035 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0548-s012056 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0548-s012056 | station | reverse | revenue | 1 |
| line-2 | line-2-0602-0621-s014057 | station | forward | revenue | 1 |
| line-2 | line-2-0602-0621-s014057 | station | reverse | revenue | 1 |
| line-2 | line-2-0654-0692-s016072 | station | forward | revenue | 1 |
| line-2 | line-2-0654-0692-s016072 | station | reverse | revenue | 1 |
| line-2 | line-2-0853-1088-s025819 | station | reverse | revenue | 2 |
| line-3 | line-3-0068-0951-s027547 | station | reverse | revenue | 2 |
| line-3 | line-3-0448-0633-s016834 | station | forward | revenue | 1 |
| line-3 | line-3-0448-0633-s016834 | station | reverse | revenue | 1 |
| line-3 | line-3-0546-0546-s013896 | station | forward | revenue | 1 |
| line-3 | line-3-0546-0546-s013896 | station | reverse | revenue | 1 |
| line-3 | line-3-0648-0454-s010812 | station | forward | revenue | 1 |
| line-3 | line-3-0648-0454-s010812 | station | reverse | revenue | 1 |
| line-3 | line-3-0774-0341-s007028 | station | forward | revenue | 1 |
| line-3 | line-3-0774-0341-s007028 | station | reverse | revenue | 1 |
| line-3 | line-3-1031-0151-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0334-0571-s000000 | depot | — | revenue | 33 |
| line-1 | line-1-0334-0571-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0334-0571-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0222-0124-s000000 | depot | — | revenue | 57 |
| line-2 | line-2-0222-0124-s000000 | depot | — | spare | 7 |
| line-2 | line-2-0222-0124-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0068-0951-s027547 | depot | — | revenue | 65 |
| line-3 | line-3-0068-0951-s027547 | depot | — | spare | 7 |
| line-3 | line-3-0068-0951-s027547 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tanta-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **212 trainsets at 18 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **191 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **176 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0334-0571-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0458-0515-s003002 | forward | revenue | 6 | pending |
| line-1 | line-1-0458-0515-s003002 | reverse | revenue | 6 | pending |
| line-1 | line-1-0582-0458-s006013 | forward | revenue | 5 | pending |
| line-1 | line-1-0582-0458-s006013 | reverse | revenue | 5 | pending |
| line-1 | line-1-0773-0371-s010636 | forward | revenue | 5 | pending |
| line-1 | line-1-0773-0371-s010636 | reverse | revenue | 5 | pending |
| line-1 | line-1-0950-0251-s015264 | reverse | revenue | 5 | pending |
| line-1 | line-1-0582-0458-s006013 | forward | spare | 1 | pending |
| line-1 | line-1-0582-0458-s006013 | reverse | spare | 1 | pending |
| line-1 | line-1-0773-0371-s010636 | forward | spare | 1 | pending |
| line-1 | line-1-0773-0371-s010636 | reverse | spare | 1 | pending |
| line-1 | line-1-0950-0251-s015264 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0415-0366-s007009 | forward | revenue | 6 | pending |
| line-2 | line-2-0415-0366-s007009 | reverse | revenue | 6 | pending |
| line-2 | line-2-0494-0474-s010035 | forward | revenue | 6 | pending |
| line-2 | line-2-0494-0474-s010035 | reverse | revenue | 6 | pending |
| line-2 | line-2-0548-0548-s012056 | forward | revenue | 6 | pending |
| line-2 | line-2-0548-0548-s012056 | reverse | revenue | 6 | pending |
| line-2 | line-2-0602-0621-s014057 | forward | revenue | 6 | pending |
| line-2 | line-2-0602-0621-s014057 | reverse | revenue | 6 | pending |
| line-2 | line-2-0654-0692-s016072 | forward | revenue | 6 | pending |
| line-2 | line-2-0654-0692-s016072 | reverse | revenue | 6 | pending |
| line-2 | line-2-0853-1088-s025819 | reverse | revenue | 5 | pending |
| line-2 | line-2-0853-1088-s025819 | reverse | spare | 1 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0415-0366-s007009 | forward | spare | 1 | pending |
| line-2 | line-2-0415-0366-s007009 | reverse | spare | 1 | pending |
| line-2 | line-2-0494-0474-s010035 | forward | spare | 1 | pending |
| line-2 | line-2-0494-0474-s010035 | reverse | spare | 1 | pending |
| line-2 | line-2-0548-0548-s012056 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0548-s012056 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0774-0341-s007028 | forward | revenue | 8 | pending |
| line-3 | line-3-0774-0341-s007028 | reverse | revenue | 8 | pending |
| line-3 | line-3-0648-0454-s010812 | forward | revenue | 8 | pending |
| line-3 | line-3-0648-0454-s010812 | reverse | revenue | 8 | pending |
| line-3 | line-3-0546-0546-s013896 | forward | revenue | 8 | pending |
| line-3 | line-3-0546-0546-s013896 | reverse | revenue | 8 | pending |
| line-3 | line-3-0448-0633-s016834 | forward | revenue | 7 | pending |
| line-3 | line-3-0448-0633-s016834 | reverse | revenue | 7 | pending |
| line-3 | line-3-0068-0951-s027547 | reverse | revenue | 7 | pending |
| line-3 | line-3-0448-0633-s016834 | forward | spare | 1 | pending |
| line-3 | line-3-0448-0633-s016834 | reverse | spare | 1 | pending |
| line-3 | line-3-0068-0951-s027547 | reverse | spare | 1 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0774-0341-s007028 | forward | spare | 1 | pending |
| line-3 | line-3-0774-0341-s007028 | reverse | spare | 1 | pending |
| line-3 | line-3-0648-0454-s010812 | forward | spare | 1 | pending |
| line-3 | line-3-0648-0454-s010812 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**168 trainsets exceed the reference platform envelope**, requiring **9,996.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0334-0571-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0458-0515-s003002 | 12 | 2 | 10 | 595.0 |
| line-1-0582-0458-s006013 | 12 | 2 | 10 | 595.0 |
| line-1-0773-0371-s010636 | 12 | 4 | 8 | 476.0 |
| line-1-0950-0251-s015264 | 6 | 2 | 4 | 238.0 |
| line-2-0222-0124-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0415-0366-s007009 | 14 | 2 | 12 | 714.0 |
| line-2-0494-0474-s010035 | 14 | 2 | 12 | 714.0 |
| line-2-0548-0548-s012056 | 14 | 4 | 10 | 595.0 |
| line-2-0602-0621-s014057 | 12 | 2 | 10 | 595.0 |
| line-2-0654-0692-s016072 | 12 | 2 | 10 | 595.0 |
| line-2-0853-1088-s025819 | 6 | 2 | 4 | 238.0 |
| line-3-0068-0951-s027547 | 8 | 2 | 6 | 357.0 |
| line-3-0448-0633-s016834 | 16 | 2 | 14 | 833.0 |
| line-3-0546-0546-s013896 | 16 | 4 | 12 | 714.0 |
| line-3-0648-0454-s010812 | 18 | 2 | 16 | 952.0 |
| line-3-0774-0341-s007028 | 18 | 4 | 14 | 833.0 |
| line-3-1031-0151-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Tanta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
