# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **124 trainsets at 25 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0669-0351-s000000 | forward | 3 | pending |
| line-1 | line-1-0656-0444-s003016 | forward | 3 | pending |
| line-1 | line-1-0656-0444-s003016 | reverse | 3 | pending |
| line-1 | line-1-0640-0515-s004952 | forward | 3 | pending |
| line-1 | line-1-0640-0515-s004952 | reverse | 3 | pending |
| line-1 | line-1-0603-0582-s006928 | forward | 3 | pending |
| line-1 | line-1-0603-0582-s006928 | reverse | 3 | pending |
| line-1 | line-1-0563-0562-s008892 | forward | 3 | pending |
| line-1 | line-1-0563-0562-s008892 | reverse | 3 | pending |
| line-1 | line-1-0522-0641-s010995 | forward | 2 | pending |
| line-1 | line-1-0522-0641-s010995 | reverse | 2 | pending |
| line-1 | line-1-0595-0669-s013301 | forward | 2 | pending |
| line-1 | line-1-0595-0669-s013301 | reverse | 2 | pending |
| line-1 | line-1-0640-0782-s016311 | forward | 2 | pending |
| line-1 | line-1-0640-0782-s016311 | reverse | 2 | pending |
| line-1 | line-1-0616-0868-s018595 | forward | 2 | pending |
| line-1 | line-1-0616-0868-s018595 | reverse | 2 | pending |
| line-1 | line-1-0628-0925-s020892 | reverse | 2 | pending |
| line-2 | line-2-0559-0305-s000000 | forward | 3 | pending |
| line-2 | line-2-0599-0412-s003011 | forward | 3 | pending |
| line-2 | line-2-0599-0412-s003011 | reverse | 3 | pending |
| line-2 | line-2-0546-0490-s006015 | forward | 3 | pending |
| line-2 | line-2-0546-0490-s006015 | reverse | 3 | pending |
| line-2 | line-2-0563-0562-s008055 | forward | 3 | pending |
| line-2 | line-2-0563-0562-s008055 | reverse | 3 | pending |
| line-2 | line-2-0497-0610-s010090 | forward | 3 | pending |
| line-2 | line-2-0497-0610-s010090 | reverse | 3 | pending |
| line-2 | line-2-0445-0674-s012117 | forward | 3 | pending |
| line-2 | line-2-0445-0674-s012117 | reverse | 3 | pending |
| line-2 | line-2-0431-0751-s014139 | forward | 3 | pending |
| line-2 | line-2-0431-0751-s014139 | reverse | 3 | pending |
| line-2 | line-2-0460-0807-s016022 | forward | 3 | pending |
| line-2 | line-2-0460-0807-s016022 | reverse | 3 | pending |
| line-2 | line-2-0332-0976-s021688 | reverse | 3 | pending |
| line-3 | line-3-0384-0457-s000000 | forward | 4 | pending |
| line-3 | line-3-0488-0398-s003009 | forward | 3 | pending |
| line-3 | line-3-0488-0398-s003009 | reverse | 3 | pending |
| line-3 | line-3-0617-0351-s006028 | forward | 3 | pending |
| line-3 | line-3-0617-0351-s006028 | reverse | 3 | pending |
| line-3 | line-3-0680-0337-s008074 | forward | 3 | pending |
| line-3 | line-3-0680-0337-s008074 | reverse | 3 | pending |
| line-3 | line-3-0755-0324-s010118 | forward | 3 | pending |
| line-3 | line-3-0755-0324-s010118 | reverse | 3 | pending |
| line-3 | line-3-0890-0291-s014228 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Ilorin/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
