# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **97 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0110-0325-s000000 | forward | 4 | pending |
| line-1 | line-1-0224-0376-s003009 | forward | 4 | pending |
| line-1 | line-1-0224-0376-s003009 | reverse | 4 | pending |
| line-1 | line-1-0465-0544-s009995 | forward | 4 | pending |
| line-1 | line-1-0465-0544-s009995 | reverse | 4 | pending |
| line-1 | line-1-0543-0598-s012014 | forward | 4 | pending |
| line-1 | line-1-0543-0598-s012014 | reverse | 3 | pending |
| line-1 | line-1-0631-0598-s014274 | forward | 3 | pending |
| line-1 | line-1-0631-0598-s014274 | reverse | 3 | pending |
| line-1 | line-1-0702-0621-s016544 | reverse | 3 | pending |
| line-2 | line-2-0325-0696-s000000 | forward | 4 | pending |
| line-2 | line-2-0460-0668-s003015 | forward | 4 | pending |
| line-2 | line-2-0460-0668-s003015 | reverse | 4 | pending |
| line-2 | line-2-0543-0598-s006066 | forward | 4 | pending |
| line-2 | line-2-0543-0598-s006066 | reverse | 4 | pending |
| line-2 | line-2-0605-0492-s009052 | forward | 4 | pending |
| line-2 | line-2-0605-0492-s009052 | reverse | 3 | pending |
| line-2 | line-2-0649-0299-s014203 | reverse | 3 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | 4 | pending |
| line-3 | line-3-0363-0598-s006156 | forward | 3 | pending |
| line-3 | line-3-0363-0598-s006156 | reverse | 3 | pending |
| line-3 | line-3-0481-0594-s009158 | forward | 3 | pending |
| line-3 | line-3-0481-0594-s009158 | reverse | 3 | pending |
| line-3 | line-3-0543-0598-s010597 | forward | 3 | pending |
| line-3 | line-3-0543-0598-s010597 | reverse | 3 | pending |
| line-3 | line-3-0600-0642-s012172 | forward | 3 | pending |
| line-3 | line-3-0600-0642-s012172 | reverse | 3 | pending |
| line-3 | line-3-0710-0680-s015095 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Aden/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
