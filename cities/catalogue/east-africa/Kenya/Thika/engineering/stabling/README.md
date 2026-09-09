# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **161 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0901-0237-s000000 | forward | 5 | pending |
| line-1 | line-1-0718-0368-s007006 | forward | 5 | pending |
| line-1 | line-1-0718-0368-s007006 | reverse | 5 | pending |
| line-1 | line-1-0695-0454-s010034 | forward | 5 | pending |
| line-1 | line-1-0695-0454-s010034 | reverse | 5 | pending |
| line-1 | line-1-0600-0509-s013042 | forward | 5 | pending |
| line-1 | line-1-0600-0509-s013042 | reverse | 4 | pending |
| line-1 | line-1-0561-0543-s014517 | forward | 4 | pending |
| line-1 | line-1-0561-0543-s014517 | reverse | 4 | pending |
| line-1 | line-1-0503-0536-s016051 | forward | 4 | pending |
| line-1 | line-1-0503-0536-s016051 | reverse | 4 | pending |
| line-1 | line-1-0388-0608-s019064 | forward | 4 | pending |
| line-1 | line-1-0388-0608-s019064 | reverse | 4 | pending |
| line-1 | line-1-0016-0869-s029004 | reverse | 4 | pending |
| line-2 | line-2-0665-0928-s000000 | forward | 4 | pending |
| line-2 | line-2-0670-0778-s003795 | forward | 4 | pending |
| line-2 | line-2-0670-0778-s003795 | reverse | 4 | pending |
| line-2 | line-2-0613-0698-s006796 | forward | 4 | pending |
| line-2 | line-2-0613-0698-s006796 | reverse | 3 | pending |
| line-2 | line-2-0554-0600-s009823 | forward | 3 | pending |
| line-2 | line-2-0554-0600-s009823 | reverse | 3 | pending |
| line-2 | line-2-0561-0543-s011038 | forward | 3 | pending |
| line-2 | line-2-0561-0543-s011038 | reverse | 3 | pending |
| line-2 | line-2-0564-0467-s012838 | forward | 3 | pending |
| line-2 | line-2-0564-0467-s012838 | reverse | 3 | pending |
| line-2 | line-2-0534-0301-s017061 | forward | 3 | pending |
| line-2 | line-2-0534-0301-s017061 | reverse | 3 | pending |
| line-2 | line-2-0586-0120-s021310 | reverse | 3 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | 4 | pending |
| line-3 | line-3-0812-0413-s007009 | forward | 4 | pending |
| line-3 | line-3-0812-0413-s007009 | reverse | 4 | pending |
| line-3 | line-3-0713-0497-s010027 | forward | 4 | pending |
| line-3 | line-3-0713-0497-s010027 | reverse | 4 | pending |
| line-3 | line-3-0633-0522-s011905 | forward | 4 | pending |
| line-3 | line-3-0633-0522-s011905 | reverse | 4 | pending |
| line-3 | line-3-0561-0543-s013804 | forward | 4 | pending |
| line-3 | line-3-0561-0543-s013804 | reverse | 4 | pending |
| line-3 | line-3-0477-0609-s016043 | forward | 4 | pending |
| line-3 | line-3-0477-0609-s016043 | reverse | 4 | pending |
| line-3 | line-3-0453-0797-s020598 | forward | 3 | pending |
| line-3 | line-3-0453-0797-s020598 | reverse | 3 | pending |
| line-3 | line-3-0341-0923-s025158 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Thika/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
