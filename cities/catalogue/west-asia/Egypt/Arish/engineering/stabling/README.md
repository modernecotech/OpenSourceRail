# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **38 trainsets at 8 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0697-0528-s000000 | forward | 4 | pending |
| line-1 | line-1-0437-0446-s006727 | forward | 4 | pending |
| line-1 | line-1-0437-0446-s006727 | reverse | 3 | pending |
| line-1 | line-1-0381-0389-s008785 | forward | 3 | pending |
| line-1 | line-1-0381-0389-s008785 | reverse | 3 | pending |
| line-1 | line-1-0359-0450-s010861 | forward | 3 | pending |
| line-1 | line-1-0359-0450-s010861 | reverse | 3 | pending |
| line-1 | line-1-0307-0518-s012933 | reverse | 3 | pending |
| line-2 | line-2-0368-0517-s000000 | forward | 3 | pending |
| line-2 | line-2-0381-0389-s003032 | forward | 3 | pending |
| line-2 | line-2-0381-0389-s003032 | reverse | 3 | pending |
| line-2 | line-2-0349-0427-s004328 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Arish/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
