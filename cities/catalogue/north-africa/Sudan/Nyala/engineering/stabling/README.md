# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **99 trainsets at 20 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0809-0277-s000000 | forward | 3 | pending |
| line-1 | line-1-0737-0368-s003007 | forward | 3 | pending |
| line-1 | line-1-0737-0368-s003007 | reverse | 3 | pending |
| line-1 | line-1-0682-0504-s006182 | forward | 3 | pending |
| line-1 | line-1-0682-0504-s006182 | reverse | 3 | pending |
| line-1 | line-1-0555-0554-s009562 | forward | 3 | pending |
| line-1 | line-1-0555-0554-s009562 | reverse | 3 | pending |
| line-1 | line-1-0600-0648-s012213 | forward | 3 | pending |
| line-1 | line-1-0600-0648-s012213 | reverse | 3 | pending |
| line-1 | line-1-0571-0755-s014633 | forward | 3 | pending |
| line-1 | line-1-0571-0755-s014633 | reverse | 3 | pending |
| line-1 | line-1-0551-0854-s017044 | forward | 3 | pending |
| line-1 | line-1-0551-0854-s017044 | reverse | 3 | pending |
| line-1 | line-1-0512-0958-s019447 | reverse | 2 | pending |
| line-2 | line-2-0344-0606-s000000 | forward | 3 | pending |
| line-2 | line-2-0462-0584-s003019 | forward | 3 | pending |
| line-2 | line-2-0462-0584-s003019 | reverse | 3 | pending |
| line-2 | line-2-0555-0554-s006128 | forward | 3 | pending |
| line-2 | line-2-0555-0554-s006128 | reverse | 3 | pending |
| line-2 | line-2-0691-0553-s009033 | forward | 3 | pending |
| line-2 | line-2-0691-0553-s009033 | reverse | 3 | pending |
| line-2 | line-2-0727-0613-s011123 | forward | 3 | pending |
| line-2 | line-2-0727-0613-s011123 | reverse | 2 | pending |
| line-2 | line-2-0799-0649-s013211 | forward | 2 | pending |
| line-2 | line-2-0799-0649-s013211 | reverse | 2 | pending |
| line-2 | line-2-0890-0681-s015312 | reverse | 2 | pending |
| line-3 | line-3-0738-0736-s000000 | forward | 4 | pending |
| line-3 | line-3-0645-0665-s003015 | forward | 4 | pending |
| line-3 | line-3-0645-0665-s003015 | reverse | 3 | pending |
| line-3 | line-3-0555-0554-s006618 | forward | 3 | pending |
| line-3 | line-3-0555-0554-s006618 | reverse | 3 | pending |
| line-3 | line-3-0483-0466-s009022 | forward | 3 | pending |
| line-3 | line-3-0483-0466-s009022 | reverse | 3 | pending |
| line-3 | line-3-0483-0321-s011922 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Nyala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
