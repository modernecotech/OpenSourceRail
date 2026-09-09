# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **127 trainsets at 21 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1049-0499-s000000 | forward | 4 | pending |
| line-1 | line-1-0759-0518-s006445 | forward | 4 | pending |
| line-1 | line-1-0759-0518-s006445 | reverse | 4 | pending |
| line-1 | line-1-0706-0505-s008062 | forward | 4 | pending |
| line-1 | line-1-0706-0505-s008062 | reverse | 4 | pending |
| line-1 | line-1-0589-0510-s011086 | forward | 3 | pending |
| line-1 | line-1-0589-0510-s011086 | reverse | 3 | pending |
| line-1 | line-1-0554-0547-s012389 | forward | 3 | pending |
| line-1 | line-1-0554-0547-s012389 | reverse | 3 | pending |
| line-1 | line-1-0476-0543-s014093 | forward | 3 | pending |
| line-1 | line-1-0476-0543-s014093 | reverse | 3 | pending |
| line-1 | line-1-0252-0503-s019498 | reverse | 3 | pending |
| line-2 | line-2-0695-0203-s000000 | forward | 3 | pending |
| line-2 | line-2-0698-0331-s003013 | forward | 3 | pending |
| line-2 | line-2-0698-0331-s003013 | reverse | 3 | pending |
| line-2 | line-2-0613-0432-s006019 | forward | 3 | pending |
| line-2 | line-2-0613-0432-s006019 | reverse | 3 | pending |
| line-2 | line-2-0539-0476-s008047 | forward | 3 | pending |
| line-2 | line-2-0539-0476-s008047 | reverse | 3 | pending |
| line-2 | line-2-0554-0547-s010065 | forward | 3 | pending |
| line-2 | line-2-0554-0547-s010065 | reverse | 3 | pending |
| line-2 | line-2-0529-0603-s012037 | forward | 2 | pending |
| line-2 | line-2-0529-0603-s012037 | reverse | 2 | pending |
| line-2 | line-2-0424-0665-s014768 | forward | 2 | pending |
| line-2 | line-2-0424-0665-s014768 | reverse | 2 | pending |
| line-2 | line-2-0348-0748-s017472 | reverse | 2 | pending |
| line-3 | line-3-0638-0851-s000000 | forward | 5 | pending |
| line-3 | line-3-0617-0695-s003946 | forward | 5 | pending |
| line-3 | line-3-0617-0695-s003946 | reverse | 5 | pending |
| line-3 | line-3-0614-0601-s006953 | forward | 5 | pending |
| line-3 | line-3-0614-0601-s006953 | reverse | 5 | pending |
| line-3 | line-3-0554-0547-s009254 | forward | 5 | pending |
| line-3 | line-3-0554-0547-s009254 | reverse | 5 | pending |
| line-3 | line-3-0422-0472-s012970 | forward | 5 | pending |
| line-3 | line-3-0422-0472-s012970 | reverse | 5 | pending |
| line-3 | line-3-0198-0119-s023342 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Hebron/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
