# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0582-0451-s000000 | forward | 4 | pending |
| line-1 | line-1-0551-0552-s002731 | forward | 4 | pending |
| line-1 | line-1-0551-0552-s002731 | reverse | 4 | pending |
| line-1 | line-1-0571-0618-s004614 | forward | 3 | pending |
| line-1 | line-1-0571-0618-s004614 | reverse | 3 | pending |
| line-1 | line-1-0665-0763-s009379 | reverse | 3 | pending |
| line-2 | line-2-0512-0478-s000000 | forward | 4 | pending |
| line-2 | line-2-0551-0552-s002248 | forward | 4 | pending |
| line-2 | line-2-0551-0552-s002248 | reverse | 4 | pending |
| line-2 | line-2-0519-0638-s004896 | forward | 3 | pending |
| line-2 | line-2-0519-0638-s004896 | reverse | 3 | pending |
| line-2 | line-2-0458-0856-s010330 | reverse | 3 | pending |
| line-3 | line-3-0860-0665-s000000 | forward | 4 | pending |
| line-3 | line-3-0643-0551-s005714 | forward | 4 | pending |
| line-3 | line-3-0643-0551-s005714 | reverse | 4 | pending |
| line-3 | line-3-0551-0552-s008150 | forward | 3 | pending |
| line-3 | line-3-0551-0552-s008150 | reverse | 3 | pending |
| line-3 | line-3-0493-0543-s009644 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bertoua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
