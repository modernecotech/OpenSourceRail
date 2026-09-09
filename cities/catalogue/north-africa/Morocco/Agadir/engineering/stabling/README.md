# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **172 trainsets at 30 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1093-1079-s000000 | forward | 3 | pending |
| line-1 | line-1-0939-0927-s004761 | forward | 3 | pending |
| line-1 | line-1-0939-0927-s004761 | reverse | 3 | pending |
| line-1 | line-1-0895-0863-s006650 | forward | 3 | pending |
| line-1 | line-1-0895-0863-s006650 | reverse | 3 | pending |
| line-1 | line-1-0794-0863-s009656 | forward | 3 | pending |
| line-1 | line-1-0794-0863-s009656 | reverse | 3 | pending |
| line-1 | line-1-0758-0727-s012674 | forward | 3 | pending |
| line-1 | line-1-0758-0727-s012674 | reverse | 3 | pending |
| line-1 | line-1-0668-0636-s015702 | forward | 3 | pending |
| line-1 | line-1-0668-0636-s015702 | reverse | 3 | pending |
| line-1 | line-1-0618-0642-s017317 | forward | 3 | pending |
| line-1 | line-1-0618-0642-s017317 | reverse | 3 | pending |
| line-1 | line-1-0575-0579-s019225 | forward | 3 | pending |
| line-1 | line-1-0575-0579-s019225 | reverse | 3 | pending |
| line-1 | line-1-0536-0536-s021283 | forward | 3 | pending |
| line-1 | line-1-0536-0536-s021283 | reverse | 3 | pending |
| line-1 | line-1-0554-0448-s023342 | forward | 2 | pending |
| line-1 | line-1-0554-0448-s023342 | reverse | 2 | pending |
| line-1 | line-1-0513-0343-s025953 | forward | 2 | pending |
| line-1 | line-1-0513-0343-s025953 | reverse | 2 | pending |
| line-1 | line-1-0435-0260-s028576 | reverse | 2 | pending |
| line-2 | line-2-0137-0141-s000000 | forward | 4 | pending |
| line-2 | line-2-0363-0283-s005743 | forward | 4 | pending |
| line-2 | line-2-0363-0283-s005743 | reverse | 4 | pending |
| line-2 | line-2-0463-0384-s008761 | forward | 4 | pending |
| line-2 | line-2-0463-0384-s008761 | reverse | 4 | pending |
| line-2 | line-2-0569-0490-s011782 | forward | 3 | pending |
| line-2 | line-2-0569-0490-s011782 | reverse | 3 | pending |
| line-2 | line-2-0575-0579-s014269 | forward | 3 | pending |
| line-2 | line-2-0575-0579-s014269 | reverse | 3 | pending |
| line-2 | line-2-0601-0692-s017805 | forward | 3 | pending |
| line-2 | line-2-0601-0692-s017805 | reverse | 3 | pending |
| line-2 | line-2-0679-0778-s020818 | forward | 3 | pending |
| line-2 | line-2-0679-0778-s020818 | reverse | 3 | pending |
| line-2 | line-2-0704-0892-s023350 | forward | 3 | pending |
| line-2 | line-2-0704-0892-s023350 | reverse | 3 | pending |
| line-2 | line-2-0790-0952-s025865 | reverse | 3 | pending |
| line-3 | line-3-1061-0928-s000000 | forward | 4 | pending |
| line-3 | line-3-0979-0869-s003008 | forward | 4 | pending |
| line-3 | line-3-0979-0869-s003008 | reverse | 4 | pending |
| line-3 | line-3-0879-0836-s005801 | forward | 4 | pending |
| line-3 | line-3-0879-0836-s005801 | reverse | 4 | pending |
| line-3 | line-3-0772-0880-s008809 | forward | 4 | pending |
| line-3 | line-3-0772-0880-s008809 | reverse | 4 | pending |
| line-3 | line-3-0703-0778-s011818 | forward | 4 | pending |
| line-3 | line-3-0703-0778-s011818 | reverse | 4 | pending |
| line-3 | line-3-0585-0762-s014842 | forward | 4 | pending |
| line-3 | line-3-0585-0762-s014842 | reverse | 3 | pending |
| line-3 | line-3-0475-0709-s017858 | forward | 3 | pending |
| line-3 | line-3-0475-0709-s017858 | reverse | 3 | pending |
| line-3 | line-3-0367-0641-s020880 | forward | 3 | pending |
| line-3 | line-3-0367-0641-s020880 | reverse | 3 | pending |
| line-3 | line-3-0104-0580-s027049 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Agadir/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
