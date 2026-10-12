# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 153 at depots = 195 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0748-0658-s017953 | line-1 | declared-depot | 46 | 2,737.0 | 8 |
| line-2-0532-0204-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 7 |
| line-3-0868-0951-s000000 | line-3 | declared-depot | 39 | 2,320.5 | 7 |
| line-4-0447-0329-s000000 | line-4 | declared-depot | 18 | 1,071.0 | 4 |
| line-5-0597-0268-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0015-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0447-0329-s007966 | station | forward | revenue | 1 |
| line-1 | line-1-0447-0329-s007966 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0448-s011589 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0448-s011589 | station | reverse | revenue | 1 |
| line-1 | line-1-0744-0654-s017828 | station | forward | revenue | 1 |
| line-1 | line-1-0744-0654-s017828 | station | reverse | revenue | 1 |
| line-1 | line-1-0748-0658-s017953 | station | reverse | revenue | 2 |
| line-2 | line-2-0509-0570-s011333 | station | forward | revenue | 1 |
| line-2 | line-2-0509-0570-s011333 | station | reverse | revenue | 1 |
| line-2 | line-2-0524-0761-s015752 | station | reverse | revenue | 2 |
| line-2 | line-2-0532-0204-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0556-0448-s008076 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0448-s008076 | station | reverse | revenue | 1 |
| line-2 | line-2-0597-0268-s002006 | station | forward | revenue | 1 |
| line-2 | line-2-0597-0268-s002006 | station | reverse | revenue | 1 |
| line-2 | line-2-0597-0271-s002066 | station | forward | revenue | 1 |
| line-2 | line-2-0597-0271-s002066 | station | reverse | revenue | 1 |
| line-3 | line-3-0616-0325-s014936 | station | reverse | revenue | 2 |
| line-3 | line-3-0649-0410-s012927 | station | forward | revenue | 1 |
| line-3 | line-3-0649-0410-s012927 | station | reverse | revenue | 1 |
| line-3 | line-3-0682-0495-s010930 | station | forward | revenue | 1 |
| line-3 | line-3-0682-0495-s010930 | station | reverse | revenue | 1 |
| line-3 | line-3-0744-0654-s007190 | station | forward | revenue | 1 |
| line-3 | line-3-0744-0654-s007190 | station | reverse | revenue | 1 |
| line-3 | line-3-0868-0951-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0430-0432-s003049 | station | forward | revenue | 1 |
| line-4 | line-4-0430-0432-s003049 | station | reverse | revenue | 1 |
| line-4 | line-4-0447-0329-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0509-0570-s006944 | station | reverse | revenue | 2 |
| line-5 | line-5-0597-0268-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0779-0231-s004626 | station | reverse | revenue | 2 |
| line-1 | line-1-0748-0658-s017953 | depot | — | revenue | 40 |
| line-1 | line-1-0748-0658-s017953 | depot | — | spare | 5 |
| line-1 | line-1-0748-0658-s017953 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0532-0204-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0532-0204-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0532-0204-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0868-0951-s000000 | depot | — | revenue | 34 |
| line-3 | line-3-0868-0951-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0868-0951-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0447-0329-s000000 | depot | — | revenue | 15 |
| line-4 | line-4-0447-0329-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0447-0329-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0597-0268-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0597-0268-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0597-0268-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fallujah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **195 trainsets at 21 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **174 revenue, 16 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **153 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0297-0015-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0447-0329-s007966 | forward | revenue | 7 | pending |
| line-1 | line-1-0447-0329-s007966 | reverse | revenue | 6 | pending |
| line-1 | line-1-0556-0448-s011589 | forward | revenue | 6 | pending |
| line-1 | line-1-0556-0448-s011589 | reverse | revenue | 6 | pending |
| line-1 | line-1-0744-0654-s017828 | forward | revenue | 6 | pending |
| line-1 | line-1-0744-0654-s017828 | reverse | revenue | 6 | pending |
| line-1 | line-1-0748-0658-s017953 | reverse | revenue | 6 | pending |
| line-1 | line-1-0447-0329-s007966 | reverse | spare | 1 | pending |
| line-1 | line-1-0556-0448-s011589 | forward | spare | 1 | pending |
| line-1 | line-1-0556-0448-s011589 | reverse | spare | 1 | pending |
| line-1 | line-1-0744-0654-s017828 | forward | spare | 1 | pending |
| line-1 | line-1-0744-0654-s017828 | reverse | spare | 1 | pending |
| line-1 | line-1-0748-0658-s017953 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0204-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0597-0268-s002006 | forward | revenue | 5 | pending |
| line-2 | line-2-0597-0268-s002006 | reverse | revenue | 5 | pending |
| line-2 | line-2-0597-0271-s002066 | forward | revenue | 5 | pending |
| line-2 | line-2-0597-0271-s002066 | reverse | revenue | 5 | pending |
| line-2 | line-2-0556-0448-s008076 | forward | revenue | 4 | pending |
| line-2 | line-2-0556-0448-s008076 | reverse | revenue | 4 | pending |
| line-2 | line-2-0509-0570-s011333 | forward | revenue | 4 | pending |
| line-2 | line-2-0509-0570-s011333 | reverse | revenue | 4 | pending |
| line-2 | line-2-0524-0761-s015752 | reverse | revenue | 4 | pending |
| line-2 | line-2-0556-0448-s008076 | forward | spare | 1 | pending |
| line-2 | line-2-0556-0448-s008076 | reverse | spare | 1 | pending |
| line-2 | line-2-0509-0570-s011333 | forward | spare | 1 | pending |
| line-2 | line-2-0509-0570-s011333 | reverse | spare | 1 | pending |
| line-2 | line-2-0524-0761-s015752 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0744-0654-s007190 | forward | revenue | 6 | pending |
| line-3 | line-3-0744-0654-s007190 | reverse | revenue | 6 | pending |
| line-3 | line-3-0682-0495-s010930 | forward | revenue | 6 | pending |
| line-3 | line-3-0682-0495-s010930 | reverse | revenue | 5 | pending |
| line-3 | line-3-0649-0410-s012927 | forward | revenue | 5 | pending |
| line-3 | line-3-0649-0410-s012927 | reverse | revenue | 5 | pending |
| line-3 | line-3-0616-0325-s014936 | reverse | revenue | 5 | pending |
| line-3 | line-3-0682-0495-s010930 | reverse | spare | 1 | pending |
| line-3 | line-3-0649-0410-s012927 | forward | spare | 1 | pending |
| line-3 | line-3-0649-0410-s012927 | reverse | spare | 1 | pending |
| line-3 | line-3-0616-0325-s014936 | reverse | spare | 1 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0447-0329-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0430-0432-s003049 | forward | revenue | 5 | pending |
| line-4 | line-4-0430-0432-s003049 | reverse | revenue | 5 | pending |
| line-4 | line-4-0509-0570-s006944 | reverse | revenue | 5 | pending |
| line-4 | line-4-0430-0432-s003049 | forward | spare | 1 | pending |
| line-4 | line-4-0430-0432-s003049 | reverse | spare | 1 | pending |
| line-4 | line-4-0509-0570-s006944 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0597-0268-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0779-0231-s004626 | reverse | revenue | 7 | pending |
| line-5 | line-5-0597-0268-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0779-0231-s004626 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**137 trainsets exceed the reference platform envelope**, requiring **8,151.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0015-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0447-0329-s007966 | 14 | 4 | 10 | 595.0 |
| line-1-0556-0448-s011589 | 14 | 4 | 10 | 595.0 |
| line-1-0744-0654-s017828 | 14 | 4 | 10 | 595.0 |
| line-1-0748-0658-s017953 | 7 | 2 | 5 | 297.5 |
| line-2-0509-0570-s011333 | 10 | 4 | 6 | 357.0 |
| line-2-0524-0761-s015752 | 5 | 2 | 3 | 178.5 |
| line-2-0532-0204-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0556-0448-s008076 | 10 | 4 | 6 | 357.0 |
| line-2-0597-0268-s002006 | 10 | 4 | 6 | 357.0 |
| line-2-0597-0271-s002066 | 10 | 4 | 6 | 357.0 |
| line-3-0616-0325-s014936 | 6 | 2 | 4 | 238.0 |
| line-3-0649-0410-s012927 | 12 | 2 | 10 | 595.0 |
| line-3-0682-0495-s010930 | 12 | 2 | 10 | 595.0 |
| line-3-0744-0654-s007190 | 12 | 4 | 8 | 476.0 |
| line-3-0868-0951-s000000 | 7 | 2 | 5 | 297.5 |
| line-4-0430-0432-s003049 | 12 | 2 | 10 | 595.0 |
| line-4-0447-0329-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0509-0570-s006944 | 6 | 2 | 4 | 238.0 |
| line-5-0597-0268-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0779-0231-s004626 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Fallujah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
