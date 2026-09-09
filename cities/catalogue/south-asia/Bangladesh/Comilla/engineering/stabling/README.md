# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **114 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0430-0223-s000000 | forward | 4 | pending |
| line-1 | line-1-0507-0407-s005071 | forward | 4 | pending |
| line-1 | line-1-0507-0407-s005071 | reverse | 4 | pending |
| line-1 | line-1-0511-0538-s008090 | forward | 4 | pending |
| line-1 | line-1-0511-0538-s008090 | reverse | 4 | pending |
| line-1 | line-1-0558-0542-s009652 | forward | 3 | pending |
| line-1 | line-1-0558-0542-s009652 | reverse | 3 | pending |
| line-1 | line-1-0620-0607-s012703 | forward | 3 | pending |
| line-1 | line-1-0620-0607-s012703 | reverse | 3 | pending |
| line-1 | line-1-0618-0753-s016405 | forward | 3 | pending |
| line-1 | line-1-0618-0753-s016405 | reverse | 3 | pending |
| line-1 | line-1-0647-0900-s020123 | reverse | 3 | pending |
| line-2 | line-2-0923-0150-s000000 | forward | 4 | pending |
| line-2 | line-2-0756-0332-s006850 | forward | 4 | pending |
| line-2 | line-2-0756-0332-s006850 | reverse | 4 | pending |
| line-2 | line-2-0714-0444-s009853 | forward | 4 | pending |
| line-2 | line-2-0714-0444-s009853 | reverse | 4 | pending |
| line-2 | line-2-0616-0480-s012867 | forward | 3 | pending |
| line-2 | line-2-0616-0480-s012867 | reverse | 3 | pending |
| line-2 | line-2-0558-0542-s015541 | forward | 3 | pending |
| line-2 | line-2-0558-0542-s015541 | reverse | 3 | pending |
| line-2 | line-2-0560-0637-s017942 | forward | 3 | pending |
| line-2 | line-2-0560-0637-s017942 | reverse | 3 | pending |
| line-2 | line-2-0513-0710-s020342 | reverse | 3 | pending |
| line-3 | line-3-0358-0684-s000000 | forward | 3 | pending |
| line-3 | line-3-0480-0651-s003001 | forward | 3 | pending |
| line-3 | line-3-0480-0651-s003001 | reverse | 3 | pending |
| line-3 | line-3-0508-0558-s006011 | forward | 3 | pending |
| line-3 | line-3-0508-0558-s006011 | reverse | 3 | pending |
| line-3 | line-3-0558-0542-s007212 | forward | 3 | pending |
| line-3 | line-3-0558-0542-s007212 | reverse | 3 | pending |
| line-3 | line-3-0582-0432-s010643 | forward | 3 | pending |
| line-3 | line-3-0582-0432-s010643 | reverse | 2 | pending |
| line-3 | line-3-0639-0359-s012848 | forward | 2 | pending |
| line-3 | line-3-0639-0359-s012848 | reverse | 2 | pending |
| line-3 | line-3-0708-0301-s015054 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Comilla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
