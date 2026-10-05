# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 158 at depots = 188 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0541-0831-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 7 |
| line-2-0071-0128-s024816 | line-2 | declared-depot | 64 | 3,808.0 | 11 |
| line-3-0065-1031-s000000 | line-3 | declared-depot | 54 | 3,213.0 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0528-0122-s016109 | station | reverse | revenue | 2 |
| line-1 | line-1-0541-0831-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0549-0678-s003126 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0678-s003126 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0557-s005596 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0557-s005596 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0441-s007966 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0441-s007966 | station | reverse | revenue | 1 |
| line-2 | line-2-0071-0128-s024816 | station | reverse | revenue | 2 |
| line-2 | line-2-0359-0447-s014437 | station | forward | revenue | 1 |
| line-2 | line-2-0359-0447-s014437 | station | reverse | revenue | 1 |
| line-2 | line-2-0457-0568-s010936 | station | forward | revenue | 1 |
| line-2 | line-2-0457-0568-s010936 | station | reverse | revenue | 1 |
| line-2 | line-2-0541-0672-s007926 | station | forward | revenue | 1 |
| line-2 | line-2-0541-0672-s007926 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0777-s004923 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0777-s004923 | station | reverse | revenue | 1 |
| line-2 | line-2-0783-0930-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0065-1031-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0478-0625-s013947 | station | forward | revenue | 1 |
| line-3 | line-3-0478-0625-s013947 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0560-s016113 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0560-s016113 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0454-s019636 | station | reverse | revenue | 2 |
| line-1 | line-1-0541-0831-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-0541-0831-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0541-0831-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0071-0128-s024816 | depot | — | revenue | 57 |
| line-2 | line-2-0071-0128-s024816 | depot | — | spare | 6 |
| line-2 | line-2-0071-0128-s024816 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0065-1031-s000000 | depot | — | revenue | 48 |
| line-3 | line-3-0065-1031-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0065-1031-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nablus-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **188 trainsets at 15 stations**; largest initial station queue **21**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **170 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **158 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0541-0831-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0549-0678-s003126 | forward | revenue | 6 | pending |
| line-1 | line-1-0549-0678-s003126 | reverse | revenue | 6 | pending |
| line-1 | line-1-0555-0557-s005596 | forward | revenue | 6 | pending |
| line-1 | line-1-0555-0557-s005596 | reverse | revenue | 6 | pending |
| line-1 | line-1-0561-0441-s007966 | forward | revenue | 5 | pending |
| line-1 | line-1-0561-0441-s007966 | reverse | revenue | 5 | pending |
| line-1 | line-1-0528-0122-s016109 | reverse | revenue | 5 | pending |
| line-1 | line-1-0561-0441-s007966 | forward | spare | 1 | pending |
| line-1 | line-1-0561-0441-s007966 | reverse | spare | 1 | pending |
| line-1 | line-1-0528-0122-s016109 | reverse | spare | 1 | pending |
| line-1 | line-1-0541-0831-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0549-0678-s003126 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0783-0930-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0626-0777-s004923 | forward | revenue | 7 | pending |
| line-2 | line-2-0626-0777-s004923 | reverse | revenue | 7 | pending |
| line-2 | line-2-0541-0672-s007926 | forward | revenue | 7 | pending |
| line-2 | line-2-0541-0672-s007926 | reverse | revenue | 7 | pending |
| line-2 | line-2-0457-0568-s010936 | forward | revenue | 7 | pending |
| line-2 | line-2-0457-0568-s010936 | reverse | revenue | 7 | pending |
| line-2 | line-2-0359-0447-s014437 | forward | revenue | 7 | pending |
| line-2 | line-2-0359-0447-s014437 | reverse | revenue | 7 | pending |
| line-2 | line-2-0071-0128-s024816 | reverse | revenue | 6 | pending |
| line-2 | line-2-0071-0128-s024816 | reverse | spare | 1 | pending |
| line-2 | line-2-0783-0930-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0777-s004923 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0777-s004923 | reverse | spare | 1 | pending |
| line-2 | line-2-0541-0672-s007926 | forward | spare | 1 | pending |
| line-2 | line-2-0541-0672-s007926 | reverse | spare | 1 | pending |
| line-2 | line-2-0457-0568-s010936 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0065-1031-s000000 | forward | revenue | 10 | pending |
| line-3 | line-3-0478-0625-s013947 | forward | revenue | 10 | pending |
| line-3 | line-3-0478-0625-s013947 | reverse | revenue | 9 | pending |
| line-3 | line-3-0550-0560-s016113 | forward | revenue | 9 | pending |
| line-3 | line-3-0550-0560-s016113 | reverse | revenue | 9 | pending |
| line-3 | line-3-0667-0454-s019636 | reverse | revenue | 9 | pending |
| line-3 | line-3-0478-0625-s013947 | reverse | spare | 1 | pending |
| line-3 | line-3-0550-0560-s016113 | forward | spare | 1 | pending |
| line-3 | line-3-0550-0560-s016113 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0454-s019636 | reverse | spare | 1 | pending |
| line-3 | line-3-0065-1031-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0478-0625-s013947 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**150 trainsets exceed the reference platform envelope**, requiring **8,925.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0528-0122-s016109 | 6 | 2 | 4 | 238.0 |
| line-1-0541-0831-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0549-0678-s003126 | 13 | 4 | 9 | 535.5 |
| line-1-0555-0557-s005596 | 12 | 4 | 8 | 476.0 |
| line-1-0561-0441-s007966 | 12 | 2 | 10 | 595.0 |
| line-2-0071-0128-s024816 | 7 | 2 | 5 | 297.5 |
| line-2-0359-0447-s014437 | 14 | 2 | 12 | 714.0 |
| line-2-0457-0568-s010936 | 15 | 2 | 13 | 773.5 |
| line-2-0541-0672-s007926 | 16 | 4 | 12 | 714.0 |
| line-2-0626-0777-s004923 | 16 | 2 | 14 | 833.0 |
| line-2-0783-0930-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0065-1031-s000000 | 11 | 2 | 9 | 535.5 |
| line-3-0478-0625-s013947 | 21 | 2 | 19 | 1,130.5 |
| line-3-0550-0560-s016113 | 20 | 4 | 16 | 952.0 |
| line-3-0667-0454-s019636 | 10 | 2 | 8 | 476.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Nablus/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
