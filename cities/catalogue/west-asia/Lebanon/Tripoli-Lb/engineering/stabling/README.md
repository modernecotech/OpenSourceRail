# Station and depot overnight allocation

Plan: **40 trainsets at stations + 59 at depots = 99 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0805-0404-s018834 | 59 | 3,510.5 | 15 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0437-0368-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0506-0476-s003018 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0476-s003018 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0550-s005091 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0550-s005091 | station | reverse | revenue | 1 |
| line-1 | line-1-0605-0651-s007583 | station | forward | revenue | 1 |
| line-1 | line-1-0605-0651-s007583 | station | reverse | revenue | 1 |
| line-1 | line-1-0706-0705-s010074 | station | forward | revenue | 1 |
| line-1 | line-1-0706-0705-s010074 | station | reverse | revenue | 1 |
| line-1 | line-1-0793-0767-s012575 | station | reverse | revenue | 2 |
| line-2 | line-2-0296-0968-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0388-0832-s003515 | station | forward | revenue | 1 |
| line-2 | line-2-0388-0832-s003515 | station | reverse | revenue | 1 |
| line-2 | line-2-0439-0678-s007018 | station | forward | revenue | 1 |
| line-2 | line-2-0439-0678-s007018 | station | reverse | revenue | 1 |
| line-2 | line-2-0481-0592-s009086 | station | forward | revenue | 1 |
| line-2 | line-2-0481-0592-s009086 | station | reverse | revenue | 1 |
| line-2 | line-2-0556-0550-s011177 | station | forward | revenue | 1 |
| line-2 | line-2-0556-0550-s011177 | station | reverse | revenue | 1 |
| line-2 | line-2-0632-0547-s013033 | station | forward | revenue | 1 |
| line-2 | line-2-0632-0547-s013033 | station | reverse | revenue | 1 |
| line-2 | line-2-0750-0503-s015935 | station | forward | revenue | 1 |
| line-2 | line-2-0750-0503-s015935 | station | reverse | revenue | 1 |
| line-2 | line-2-0805-0404-s018834 | station | reverse | revenue | 2 |
| line-3 | line-3-0555-0469-s002305 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0469-s002305 | station | reverse | revenue | 1 |
| line-3 | line-3-0556-0550-s004198 | station | forward | revenue | 1 |
| line-3 | line-3-0556-0550-s004198 | station | reverse | revenue | 1 |
| line-3 | line-3-0575-0388-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0634-0604-s006274 | station | forward | revenue | 1 |
| line-3 | line-3-0634-0604-s006274 | station | reverse | revenue | 1 |
| line-3 | line-3-0706-0669-s008334 | station | forward | revenue | 1 |
| line-3 | line-3-0706-0669-s008334 | station | reverse | revenue | 1 |
| line-3 | line-3-0927-0774-s014203 | station | reverse | revenue | 2 |
| line-1 | line-2-0805-0404-s018834 | depot | — | revenue | 12 |
| line-1 | line-2-0805-0404-s018834 | depot | — | spare | 2 |
| line-1 | line-2-0805-0404-s018834 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0805-0404-s018834 | depot | — | revenue | 21 |
| line-2 | line-2-0805-0404-s018834 | depot | — | spare | 3 |
| line-2 | line-2-0805-0404-s018834 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0805-0404-s018834 | depot | — | revenue | 16 |
| line-3 | line-2-0805-0404-s018834 | depot | — | spare | 2 |
| line-3 | line-2-0805-0404-s018834 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (15 trains), line-3 (19 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **99 trainsets at 20 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **89 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **59 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0437-0368-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0506-0476-s003018 | forward | revenue | 3 | pending |
| line-1 | line-1-0506-0476-s003018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0556-0550-s005091 | forward | revenue | 3 | pending |
| line-1 | line-1-0556-0550-s005091 | reverse | revenue | 2 | pending |
| line-1 | line-1-0605-0651-s007583 | forward | revenue | 2 | pending |
| line-1 | line-1-0605-0651-s007583 | reverse | revenue | 2 | pending |
| line-1 | line-1-0706-0705-s010074 | forward | revenue | 2 | pending |
| line-1 | line-1-0706-0705-s010074 | reverse | revenue | 2 | pending |
| line-1 | line-1-0793-0767-s012575 | reverse | revenue | 2 | pending |
| line-1 | line-1-0556-0550-s005091 | reverse | spare | 1 | pending |
| line-1 | line-1-0605-0651-s007583 | forward | spare | 1 | pending |
| line-1 | line-1-0605-0651-s007583 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0296-0968-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0388-0832-s003515 | forward | revenue | 3 | pending |
| line-2 | line-2-0388-0832-s003515 | reverse | revenue | 3 | pending |
| line-2 | line-2-0439-0678-s007018 | forward | revenue | 3 | pending |
| line-2 | line-2-0439-0678-s007018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0481-0592-s009086 | forward | revenue | 3 | pending |
| line-2 | line-2-0481-0592-s009086 | reverse | revenue | 3 | pending |
| line-2 | line-2-0556-0550-s011177 | forward | revenue | 3 | pending |
| line-2 | line-2-0556-0550-s011177 | reverse | revenue | 3 | pending |
| line-2 | line-2-0632-0547-s013033 | forward | revenue | 2 | pending |
| line-2 | line-2-0632-0547-s013033 | reverse | revenue | 2 | pending |
| line-2 | line-2-0750-0503-s015935 | forward | revenue | 2 | pending |
| line-2 | line-2-0750-0503-s015935 | reverse | revenue | 2 | pending |
| line-2 | line-2-0805-0404-s018834 | reverse | revenue | 2 | pending |
| line-2 | line-2-0632-0547-s013033 | forward | spare | 1 | pending |
| line-2 | line-2-0632-0547-s013033 | reverse | spare | 1 | pending |
| line-2 | line-2-0750-0503-s015935 | forward | spare | 1 | pending |
| line-2 | line-2-0750-0503-s015935 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0575-0388-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0469-s002305 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0469-s002305 | reverse | revenue | 3 | pending |
| line-3 | line-3-0556-0550-s004198 | forward | revenue | 3 | pending |
| line-3 | line-3-0556-0550-s004198 | reverse | revenue | 3 | pending |
| line-3 | line-3-0634-0604-s006274 | forward | revenue | 3 | pending |
| line-3 | line-3-0634-0604-s006274 | reverse | revenue | 3 | pending |
| line-3 | line-3-0706-0669-s008334 | forward | revenue | 3 | pending |
| line-3 | line-3-0706-0669-s008334 | reverse | revenue | 2 | pending |
| line-3 | line-3-0927-0774-s014203 | reverse | revenue | 2 | pending |
| line-3 | line-3-0706-0669-s008334 | reverse | spare | 1 | pending |
| line-3 | line-3-0927-0774-s014203 | reverse | spare | 1 | pending |
| line-3 | line-3-0575-0388-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**53 trainsets exceed the reference platform envelope**, requiring **3,153.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0437-0368-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0506-0476-s003018 | 6 | 2 | 4 | 238.0 |
| line-1-0556-0550-s005091 | 6 | 4 | 2 | 119.0 |
| line-1-0605-0651-s007583 | 6 | 2 | 4 | 238.0 |
| line-1-0706-0705-s010074 | 4 | 2 | 2 | 119.0 |
| line-1-0793-0767-s012575 | 2 | 2 | 0 | 0.0 |
| line-2-0296-0968-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0388-0832-s003515 | 6 | 2 | 4 | 238.0 |
| line-2-0439-0678-s007018 | 6 | 2 | 4 | 238.0 |
| line-2-0481-0592-s009086 | 6 | 2 | 4 | 238.0 |
| line-2-0556-0550-s011177 | 6 | 4 | 2 | 119.0 |
| line-2-0632-0547-s013033 | 6 | 2 | 4 | 238.0 |
| line-2-0750-0503-s015935 | 6 | 2 | 4 | 238.0 |
| line-2-0805-0404-s018834 | 2 | 2 | 0 | 0.0 |
| line-3-0555-0469-s002305 | 6 | 2 | 4 | 238.0 |
| line-3-0556-0550-s004198 | 6 | 4 | 2 | 119.0 |
| line-3-0575-0388-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0634-0604-s006274 | 6 | 2 | 4 | 238.0 |
| line-3-0706-0669-s008334 | 6 | 2 | 4 | 238.0 |
| line-3-0927-0774-s014203 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Lebanon/Tripoli-Lb/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
