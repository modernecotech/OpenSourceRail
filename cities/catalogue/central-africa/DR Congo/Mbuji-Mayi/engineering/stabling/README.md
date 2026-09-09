# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **135 trainsets at 39 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0649-0303-s000000 | forward | 3 | pending |
| line-1 | line-1-0661-0415-s002356 | forward | 3 | pending |
| line-1 | line-1-0661-0415-s002356 | reverse | 3 | pending |
| line-1 | line-1-0646-0552-s005220 | forward | 3 | pending |
| line-1 | line-1-0646-0552-s005220 | reverse | 3 | pending |
| line-1 | line-1-0650-0695-s008246 | forward | 3 | pending |
| line-1 | line-1-0650-0695-s008246 | reverse | 3 | pending |
| line-1 | line-1-0689-0811-s011264 | forward | 3 | pending |
| line-1 | line-1-0689-0811-s011264 | reverse | 2 | pending |
| line-1 | line-1-0638-0838-s012532 | forward | 2 | pending |
| line-1 | line-1-0638-0838-s012532 | reverse | 2 | pending |
| line-1 | line-1-0700-0885-s014278 | forward | 2 | pending |
| line-1 | line-1-0700-0885-s014278 | reverse | 2 | pending |
| line-1 | line-1-0646-0965-s016394 | forward | 2 | pending |
| line-1 | line-1-0646-0965-s016394 | reverse | 2 | pending |
| line-1 | line-1-0679-1036-s018396 | forward | 2 | pending |
| line-1 | line-1-0679-1036-s018396 | reverse | 2 | pending |
| line-1 | line-1-0628-1110-s020299 | forward | 2 | pending |
| line-1 | line-1-0628-1110-s020299 | reverse | 2 | pending |
| line-1 | line-1-0654-1547-s029311 | reverse | 2 | pending |
| line-2 | line-2-0910-0600-s000000 | forward | 3 | pending |
| line-2 | line-2-0885-0738-s003014 | forward | 3 | pending |
| line-2 | line-2-0885-0738-s003014 | reverse | 3 | pending |
| line-2 | line-2-0853-0875-s006019 | forward | 3 | pending |
| line-2 | line-2-0853-0875-s006019 | reverse | 3 | pending |
| line-2 | line-2-0853-0983-s008179 | forward | 3 | pending |
| line-2 | line-2-0853-0983-s008179 | reverse | 3 | pending |
| line-2 | line-2-0872-1229-s013975 | forward | 2 | pending |
| line-2 | line-2-0872-1229-s013975 | reverse | 2 | pending |
| line-2 | line-2-0913-1349-s016841 | reverse | 2 | pending |
| line-3 | line-3-0176-1444-s000000 | forward | 4 | pending |
| line-3 | line-3-0553-1123-s012313 | forward | 4 | pending |
| line-3 | line-3-0553-1123-s012313 | reverse | 4 | pending |
| line-3 | line-3-0659-1017-s015311 | forward | 4 | pending |
| line-3 | line-3-0659-1017-s015311 | reverse | 4 | pending |
| line-3 | line-3-0792-0915-s018933 | forward | 4 | pending |
| line-3 | line-3-0792-0915-s018933 | reverse | 4 | pending |
| line-3 | line-3-0798-0850-s020659 | forward | 3 | pending |
| line-3 | line-3-0798-0850-s020659 | reverse | 3 | pending |
| line-3 | line-3-0895-0801-s023022 | forward | 3 | pending |
| line-3 | line-3-0895-0801-s023022 | reverse | 3 | pending |
| line-3 | line-3-1103-0659-s028865 | reverse | 3 | pending |
| line-4 | line-4-0501-0538-s004582 | forward | 1 | pending |
| line-4 | line-4-0501-0538-s004582 | reverse | 1 | pending |
| line-4 | line-4-0591-0638-s008014 | reverse | 1 | pending |
| line-4 | line-4-0617-0778-s011029 | reverse | 1 | pending |
| line-4 | line-4-0613-0837-s012242 | reverse | 1 | pending |
| line-4 | line-4-0621-0966-s014905 | forward | 1 | pending |
| line-4 | line-4-0678-1036-s016777 | forward | 1 | pending |
| line-4 | line-4-0800-1210-s021291 | forward | 1 | pending |
| line-4 | line-4-0863-1229-s024143 | forward | 1 | pending |
| line-4 | line-4-0863-1229-s024143 | reverse | 1 | pending |
| line-4 | line-4-0804-1041-s028982 | reverse | 1 | pending |
| line-4 | line-4-0827-0983-s030332 | reverse | 1 | pending |
| line-4 | line-4-0817-0916-s031937 | reverse | 1 | pending |
| line-4 | line-4-0798-0850-s033431 | forward | 1 | pending |
| line-4 | line-4-0759-0788-s034994 | forward | 1 | pending |
| line-4 | line-4-0712-0660-s038005 | forward | 1 | pending |
| line-4 | line-4-0661-0415-s043738 | forward | 1 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Mbuji-Mayi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
