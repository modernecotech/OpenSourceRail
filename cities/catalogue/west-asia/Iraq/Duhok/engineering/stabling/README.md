# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 173 at depots = 213 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0682-0744-s000000 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0530-0094-s000000 | line-2 | declared-depot | 44 | 2,618.0 | 8 |
| line-3-0540-0838-s021640 | line-3 | declared-depot | 55 | 3,272.5 | 10 |
| line-4-0667-0070-s000000 | line-4 | declared-depot | 35 | 2,082.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0584-0017-s017357 | station | reverse | revenue | 2 |
| line-1 | line-1-0587-0205-s012295 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0205-s012295 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0106-s014831 | station | forward | revenue | 1 |
| line-1 | line-1-0603-0106-s014831 | station | reverse | revenue | 1 |
| line-1 | line-1-0616-0360-s008954 | station | forward | revenue | 1 |
| line-1 | line-1-0616-0360-s008954 | station | reverse | revenue | 1 |
| line-1 | line-1-0639-0485-s006264 | station | forward | revenue | 1 |
| line-1 | line-1-0639-0485-s006264 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0582-s004175 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0582-s004175 | station | reverse | revenue | 1 |
| line-1 | line-1-0682-0744-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0523-0228-s003005 | station | forward | revenue | 1 |
| line-2 | line-2-0523-0228-s003005 | station | reverse | revenue | 1 |
| line-2 | line-2-0530-0094-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0533-0854-s018320 | station | reverse | revenue | 2 |
| line-2 | line-2-0539-0432-s007556 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0432-s007556 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0667-s013673 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0667-s013673 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0432-s011602 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0432-s011602 | station | reverse | revenue | 1 |
| line-3 | line-3-0540-0838-s021640 | station | reverse | revenue | 2 |
| line-3 | line-3-0616-0360-s008562 | station | forward | revenue | 1 |
| line-3 | line-3-0616-0360-s008562 | station | reverse | revenue | 1 |
| line-3 | line-3-0638-0211-s005142 | station | forward | revenue | 1 |
| line-3 | line-3-0638-0211-s005142 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0007-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0667-0070-s001650 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0070-s001650 | station | reverse | revenue | 1 |
| line-4 | line-4-0667-0070-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-1037-0012-s011128 | station | reverse | revenue | 2 |
| line-1 | line-1-0682-0744-s000000 | depot | — | revenue | 34 |
| line-1 | line-1-0682-0744-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0682-0744-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0530-0094-s000000 | depot | — | revenue | 39 |
| line-2 | line-2-0530-0094-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0530-0094-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0540-0838-s021640 | depot | — | revenue | 48 |
| line-3 | line-3-0540-0838-s021640 | depot | — | spare | 6 |
| line-3 | line-3-0540-0838-s021640 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0667-0070-s000000 | depot | — | revenue | 31 |
| line-4 | line-4-0667-0070-s000000 | depot | — | spare | 3 |
| line-4 | line-4-0667-0070-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/duhok-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **213 trainsets at 20 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **192 revenue, 17 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **173 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0682-0744-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0582-s004175 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0582-s004175 | reverse | revenue | 4 | pending |
| line-1 | line-1-0639-0485-s006264 | forward | revenue | 4 | pending |
| line-1 | line-1-0639-0485-s006264 | reverse | revenue | 4 | pending |
| line-1 | line-1-0616-0360-s008954 | forward | revenue | 4 | pending |
| line-1 | line-1-0616-0360-s008954 | reverse | revenue | 4 | pending |
| line-1 | line-1-0587-0205-s012295 | forward | revenue | 4 | pending |
| line-1 | line-1-0587-0205-s012295 | reverse | revenue | 4 | pending |
| line-1 | line-1-0603-0106-s014831 | forward | revenue | 4 | pending |
| line-1 | line-1-0603-0106-s014831 | reverse | revenue | 4 | pending |
| line-1 | line-1-0584-0017-s017357 | reverse | revenue | 4 | pending |
| line-1 | line-1-0682-0744-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0582-s004175 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0582-s004175 | reverse | spare | 1 | pending |
| line-1 | line-1-0639-0485-s006264 | forward | spare | 1 | pending |
| line-1 | line-1-0639-0485-s006264 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0523-0228-s003005 | forward | revenue | 6 | pending |
| line-2 | line-2-0523-0228-s003005 | reverse | revenue | 6 | pending |
| line-2 | line-2-0539-0432-s007556 | forward | revenue | 6 | pending |
| line-2 | line-2-0539-0432-s007556 | reverse | revenue | 6 | pending |
| line-2 | line-2-0543-0667-s013673 | forward | revenue | 6 | pending |
| line-2 | line-2-0543-0667-s013673 | reverse | revenue | 6 | pending |
| line-2 | line-2-0533-0854-s018320 | reverse | revenue | 6 | pending |
| line-2 | line-2-0523-0228-s003005 | forward | spare | 1 | pending |
| line-2 | line-2-0523-0228-s003005 | reverse | spare | 1 | pending |
| line-2 | line-2-0539-0432-s007556 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0432-s007556 | reverse | spare | 1 | pending |
| line-2 | line-2-0543-0667-s013673 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0658-0007-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0667-0070-s001650 | forward | revenue | 6 | pending |
| line-3 | line-3-0667-0070-s001650 | reverse | revenue | 6 | pending |
| line-3 | line-3-0638-0211-s005142 | forward | revenue | 6 | pending |
| line-3 | line-3-0638-0211-s005142 | reverse | revenue | 6 | pending |
| line-3 | line-3-0616-0360-s008562 | forward | revenue | 6 | pending |
| line-3 | line-3-0616-0360-s008562 | reverse | revenue | 6 | pending |
| line-3 | line-3-0539-0432-s011602 | forward | revenue | 6 | pending |
| line-3 | line-3-0539-0432-s011602 | reverse | revenue | 6 | pending |
| line-3 | line-3-0540-0838-s021640 | reverse | revenue | 6 | pending |
| line-3 | line-3-0658-0007-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0667-0070-s001650 | forward | spare | 1 | pending |
| line-3 | line-3-0667-0070-s001650 | reverse | spare | 1 | pending |
| line-3 | line-3-0638-0211-s005142 | forward | spare | 1 | pending |
| line-3 | line-3-0638-0211-s005142 | reverse | spare | 1 | pending |
| line-3 | line-3-0616-0360-s008562 | forward | spare | 1 | pending |
| line-3 | line-3-0616-0360-s008562 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0667-0070-s000000 | forward | revenue | 18 | pending |
| line-4 | line-4-1037-0012-s011128 | reverse | revenue | 17 | pending |
| line-4 | line-4-1037-0012-s011128 | reverse | spare | 2 | pending |
| line-4 | line-4-0667-0070-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0667-0070-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**163 trainsets exceed the reference platform envelope**, requiring **9,698.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0584-0017-s017357 | 4 | 2 | 2 | 119.0 |
| line-1-0587-0205-s012295 | 8 | 2 | 6 | 357.0 |
| line-1-0603-0106-s014831 | 8 | 2 | 6 | 357.0 |
| line-1-0616-0360-s008954 | 8 | 4 | 4 | 238.0 |
| line-1-0639-0485-s006264 | 10 | 2 | 8 | 476.0 |
| line-1-0657-0582-s004175 | 10 | 2 | 8 | 476.0 |
| line-1-0682-0744-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0523-0228-s003005 | 14 | 2 | 12 | 714.0 |
| line-2-0530-0094-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0533-0854-s018320 | 6 | 2 | 4 | 238.0 |
| line-2-0539-0432-s007556 | 14 | 4 | 10 | 595.0 |
| line-2-0543-0667-s013673 | 13 | 2 | 11 | 654.5 |
| line-3-0539-0432-s011602 | 12 | 4 | 8 | 476.0 |
| line-3-0540-0838-s021640 | 6 | 2 | 4 | 238.0 |
| line-3-0616-0360-s008562 | 14 | 4 | 10 | 595.0 |
| line-3-0638-0211-s005142 | 14 | 2 | 12 | 714.0 |
| line-3-0658-0007-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0667-0070-s001650 | 14 | 4 | 10 | 595.0 |
| line-4-0667-0070-s000000 | 20 | 2 | 18 | 1,071.0 |
| line-4-1037-0012-s011128 | 19 | 2 | 17 | 1,011.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Duhok/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
