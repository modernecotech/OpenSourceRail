# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **139 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0426-0909-s000000 | forward | 3 | pending |
| line-1 | line-1-0489-0763-s003536 | forward | 3 | pending |
| line-1 | line-1-0489-0763-s003536 | reverse | 3 | pending |
| line-1 | line-1-0532-0635-s006542 | forward | 3 | pending |
| line-1 | line-1-0532-0635-s006542 | reverse | 3 | pending |
| line-1 | line-1-0550-0555-s008302 | forward | 3 | pending |
| line-1 | line-1-0550-0555-s008302 | reverse | 3 | pending |
| line-1 | line-1-0517-0481-s010851 | forward | 3 | pending |
| line-1 | line-1-0517-0481-s010851 | reverse | 3 | pending |
| line-1 | line-1-0498-0369-s013414 | forward | 3 | pending |
| line-1 | line-1-0498-0369-s013414 | reverse | 3 | pending |
| line-1 | line-1-0454-0266-s015954 | reverse | 3 | pending |
| line-2 | line-2-0569-0988-s000000 | forward | 5 | pending |
| line-2 | line-2-0528-0892-s003233 | forward | 5 | pending |
| line-2 | line-2-0528-0892-s003233 | reverse | 5 | pending |
| line-2 | line-2-0574-0672-s008312 | forward | 5 | pending |
| line-2 | line-2-0574-0672-s008312 | reverse | 5 | pending |
| line-2 | line-2-0605-0586-s010317 | forward | 5 | pending |
| line-2 | line-2-0605-0586-s010317 | reverse | 5 | pending |
| line-2 | line-2-0550-0555-s012327 | forward | 5 | pending |
| line-2 | line-2-0550-0555-s012327 | reverse | 4 | pending |
| line-2 | line-2-0563-0485-s014346 | forward | 4 | pending |
| line-2 | line-2-0563-0485-s014346 | reverse | 4 | pending |
| line-2 | line-2-0809-0030-s026309 | reverse | 4 | pending |
| line-3 | line-3-0801-0064-s000000 | forward | 6 | pending |
| line-3 | line-3-0622-0500-s011591 | forward | 6 | pending |
| line-3 | line-3-0622-0500-s011591 | reverse | 6 | pending |
| line-3 | line-3-0550-0555-s013834 | forward | 6 | pending |
| line-3 | line-3-0550-0555-s013834 | reverse | 6 | pending |
| line-3 | line-3-0491-0617-s016656 | forward | 6 | pending |
| line-3 | line-3-0491-0617-s016656 | reverse | 6 | pending |
| line-3 | line-3-0461-0845-s021874 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Mazar-E-Sharif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
