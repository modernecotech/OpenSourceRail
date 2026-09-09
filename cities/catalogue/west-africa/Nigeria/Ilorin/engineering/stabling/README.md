# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **124 trainsets at 25 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

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
