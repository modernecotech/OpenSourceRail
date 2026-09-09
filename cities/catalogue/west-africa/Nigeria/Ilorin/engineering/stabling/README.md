# Station and depot overnight allocation

Plan: **50 trainsets at stations + 74 at depots = 124 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0628-0925-s020892 | line-1 | storage-at-existing-powered-service-point | 25 | 1,487.5 | 0 |
| line-2-0332-0976-s021688 | line-2 | declared-depot | 30 | 1,785.0 | 19 |
| line-3-0890-0291-s014228 | line-3 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0522-0641-s010995 | station | forward | revenue | 1 |
| line-1 | line-1-0522-0641-s010995 | station | reverse | revenue | 1 |
| line-1 | line-1-0563-0562-s008892 | station | forward | revenue | 1 |
| line-1 | line-1-0563-0562-s008892 | station | reverse | revenue | 1 |
| line-1 | line-1-0595-0669-s013301 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0669-s013301 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0582-s006928 | station | forward | revenue | 1 |
| line-1 | line-1-0603-0582-s006928 | station | reverse | revenue | 1 |
| line-1 | line-1-0616-0868-s018595 | station | forward | revenue | 1 |
| line-1 | line-1-0616-0868-s018595 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0925-s020892 | station | reverse | revenue | 2 |
| line-1 | line-1-0640-0515-s004952 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0515-s004952 | station | reverse | revenue | 1 |
| line-1 | line-1-0640-0782-s016311 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0782-s016311 | station | reverse | revenue | 1 |
| line-1 | line-1-0656-0444-s003016 | station | forward | revenue | 1 |
| line-1 | line-1-0656-0444-s003016 | station | reverse | revenue | 1 |
| line-1 | line-1-0669-0351-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0332-0976-s021688 | station | reverse | revenue | 2 |
| line-2 | line-2-0431-0751-s014139 | station | forward | revenue | 1 |
| line-2 | line-2-0431-0751-s014139 | station | reverse | revenue | 1 |
| line-2 | line-2-0445-0674-s012117 | station | forward | revenue | 1 |
| line-2 | line-2-0445-0674-s012117 | station | reverse | revenue | 1 |
| line-2 | line-2-0460-0807-s016022 | station | forward | revenue | 1 |
| line-2 | line-2-0460-0807-s016022 | station | reverse | revenue | 1 |
| line-2 | line-2-0497-0610-s010090 | station | forward | revenue | 1 |
| line-2 | line-2-0497-0610-s010090 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0490-s006015 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0490-s006015 | station | reverse | revenue | 1 |
| line-2 | line-2-0559-0305-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0563-0562-s008055 | station | forward | revenue | 1 |
| line-2 | line-2-0563-0562-s008055 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0412-s003011 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0412-s003011 | station | reverse | revenue | 1 |
| line-3 | line-3-0384-0457-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0488-0398-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0488-0398-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0617-0351-s006028 | station | forward | revenue | 1 |
| line-3 | line-3-0617-0351-s006028 | station | reverse | revenue | 1 |
| line-3 | line-3-0680-0337-s008074 | station | forward | revenue | 1 |
| line-3 | line-3-0680-0337-s008074 | station | reverse | revenue | 1 |
| line-3 | line-3-0755-0324-s010118 | station | forward | revenue | 1 |
| line-3 | line-3-0755-0324-s010118 | station | reverse | revenue | 1 |
| line-3 | line-3-0890-0291-s014228 | station | reverse | revenue | 2 |
| line-1 | line-1-0628-0925-s020892 | depot | — | revenue | 20 |
| line-1 | line-1-0628-0925-s020892 | depot | — | spare | 4 |
| line-1 | line-1-0628-0925-s020892 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0976-s021688 | depot | — | revenue | 25 |
| line-2 | line-2-0332-0976-s021688 | depot | — | spare | 4 |
| line-2 | line-2-0332-0976-s021688 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0890-0291-s014228 | depot | — | revenue | 16 |
| line-3 | line-3-0890-0291-s014228 | depot | — | spare | 2 |
| line-3 | line-3-0890-0291-s014228 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ilorin-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **124 trainsets at 25 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **74 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0669-0351-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0656-0444-s003016 | forward | revenue | 3 | pending |
| line-1 | line-1-0656-0444-s003016 | reverse | revenue | 3 | pending |
| line-1 | line-1-0640-0515-s004952 | forward | revenue | 3 | pending |
| line-1 | line-1-0640-0515-s004952 | reverse | revenue | 2 | pending |
| line-1 | line-1-0603-0582-s006928 | forward | revenue | 2 | pending |
| line-1 | line-1-0603-0582-s006928 | reverse | revenue | 2 | pending |
| line-1 | line-1-0563-0562-s008892 | forward | revenue | 2 | pending |
| line-1 | line-1-0563-0562-s008892 | reverse | revenue | 2 | pending |
| line-1 | line-1-0522-0641-s010995 | forward | revenue | 2 | pending |
| line-1 | line-1-0522-0641-s010995 | reverse | revenue | 2 | pending |
| line-1 | line-1-0595-0669-s013301 | forward | revenue | 2 | pending |
| line-1 | line-1-0595-0669-s013301 | reverse | revenue | 2 | pending |
| line-1 | line-1-0640-0782-s016311 | forward | revenue | 2 | pending |
| line-1 | line-1-0640-0782-s016311 | reverse | revenue | 2 | pending |
| line-1 | line-1-0616-0868-s018595 | forward | revenue | 2 | pending |
| line-1 | line-1-0616-0868-s018595 | reverse | revenue | 2 | pending |
| line-1 | line-1-0628-0925-s020892 | reverse | revenue | 2 | pending |
| line-1 | line-1-0640-0515-s004952 | reverse | spare | 1 | pending |
| line-1 | line-1-0603-0582-s006928 | forward | spare | 1 | pending |
| line-1 | line-1-0603-0582-s006928 | reverse | spare | 1 | pending |
| line-1 | line-1-0563-0562-s008892 | forward | spare | 1 | pending |
| line-1 | line-1-0563-0562-s008892 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0559-0305-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0599-0412-s003011 | forward | revenue | 3 | pending |
| line-2 | line-2-0599-0412-s003011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0490-s006015 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0490-s006015 | reverse | revenue | 3 | pending |
| line-2 | line-2-0563-0562-s008055 | forward | revenue | 3 | pending |
| line-2 | line-2-0563-0562-s008055 | reverse | revenue | 3 | pending |
| line-2 | line-2-0497-0610-s010090 | forward | revenue | 3 | pending |
| line-2 | line-2-0497-0610-s010090 | reverse | revenue | 3 | pending |
| line-2 | line-2-0445-0674-s012117 | forward | revenue | 3 | pending |
| line-2 | line-2-0445-0674-s012117 | reverse | revenue | 3 | pending |
| line-2 | line-2-0431-0751-s014139 | forward | revenue | 2 | pending |
| line-2 | line-2-0431-0751-s014139 | reverse | revenue | 2 | pending |
| line-2 | line-2-0460-0807-s016022 | forward | revenue | 2 | pending |
| line-2 | line-2-0460-0807-s016022 | reverse | revenue | 2 | pending |
| line-2 | line-2-0332-0976-s021688 | reverse | revenue | 2 | pending |
| line-2 | line-2-0431-0751-s014139 | forward | spare | 1 | pending |
| line-2 | line-2-0431-0751-s014139 | reverse | spare | 1 | pending |
| line-2 | line-2-0460-0807-s016022 | forward | spare | 1 | pending |
| line-2 | line-2-0460-0807-s016022 | reverse | spare | 1 | pending |
| line-2 | line-2-0332-0976-s021688 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0384-0457-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0488-0398-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0488-0398-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0617-0351-s006028 | forward | revenue | 3 | pending |
| line-3 | line-3-0617-0351-s006028 | reverse | revenue | 3 | pending |
| line-3 | line-3-0680-0337-s008074 | forward | revenue | 3 | pending |
| line-3 | line-3-0680-0337-s008074 | reverse | revenue | 3 | pending |
| line-3 | line-3-0755-0324-s010118 | forward | revenue | 3 | pending |
| line-3 | line-3-0755-0324-s010118 | reverse | revenue | 2 | pending |
| line-3 | line-3-0890-0291-s014228 | reverse | revenue | 2 | pending |
| line-3 | line-3-0755-0324-s010118 | reverse | spare | 1 | pending |
| line-3 | line-3-0890-0291-s014228 | reverse | spare | 1 | pending |
| line-3 | line-3-0384-0457-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**68 trainsets exceed the reference platform envelope**, requiring **4,046.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0522-0641-s010995 | 4 | 2 | 2 | 119.0 |
| line-1-0563-0562-s008892 | 6 | 4 | 2 | 119.0 |
| line-1-0595-0669-s013301 | 4 | 2 | 2 | 119.0 |
| line-1-0603-0582-s006928 | 6 | 2 | 4 | 238.0 |
| line-1-0616-0868-s018595 | 4 | 2 | 2 | 119.0 |
| line-1-0628-0925-s020892 | 2 | 2 | 0 | 0.0 |
| line-1-0640-0515-s004952 | 6 | 2 | 4 | 238.0 |
| line-1-0640-0782-s016311 | 4 | 2 | 2 | 119.0 |
| line-1-0656-0444-s003016 | 6 | 2 | 4 | 238.0 |
| line-1-0669-0351-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0332-0976-s021688 | 3 | 2 | 1 | 59.5 |
| line-2-0431-0751-s014139 | 6 | 2 | 4 | 238.0 |
| line-2-0445-0674-s012117 | 6 | 2 | 4 | 238.0 |
| line-2-0460-0807-s016022 | 6 | 2 | 4 | 238.0 |
| line-2-0497-0610-s010090 | 6 | 2 | 4 | 238.0 |
| line-2-0546-0490-s006015 | 6 | 2 | 4 | 238.0 |
| line-2-0559-0305-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0563-0562-s008055 | 6 | 4 | 2 | 119.0 |
| line-2-0599-0412-s003011 | 6 | 2 | 4 | 238.0 |
| line-3-0384-0457-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0488-0398-s003009 | 6 | 2 | 4 | 238.0 |
| line-3-0617-0351-s006028 | 6 | 2 | 4 | 238.0 |
| line-3-0680-0337-s008074 | 6 | 4 | 2 | 119.0 |
| line-3-0755-0324-s010118 | 6 | 2 | 4 | 238.0 |
| line-3-0890-0291-s014228 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Ilorin/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
