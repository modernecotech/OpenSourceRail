# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **122 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0297-0015-s000000 | forward | 4 | pending |
| line-1 | line-1-0415-0292-s006644 | forward | 4 | pending |
| line-1 | line-1-0415-0292-s006644 | reverse | 4 | pending |
| line-1 | line-1-0450-0414-s009650 | forward | 4 | pending |
| line-1 | line-1-0450-0414-s009650 | reverse | 3 | pending |
| line-1 | line-1-0527-0439-s011625 | forward | 3 | pending |
| line-1 | line-1-0527-0439-s011625 | reverse | 3 | pending |
| line-1 | line-1-0557-0512-s013619 | forward | 3 | pending |
| line-1 | line-1-0557-0512-s013619 | reverse | 3 | pending |
| line-1 | line-1-0585-0569-s015667 | forward | 3 | pending |
| line-1 | line-1-0585-0569-s015667 | reverse | 3 | pending |
| line-1 | line-1-0682-0603-s018667 | forward | 3 | pending |
| line-1 | line-1-0682-0603-s018667 | reverse | 3 | pending |
| line-1 | line-1-0748-0658-s021003 | reverse | 3 | pending |
| line-2 | line-2-0532-0204-s000000 | forward | 4 | pending |
| line-2 | line-2-0518-0325-s004272 | forward | 4 | pending |
| line-2 | line-2-0518-0325-s004272 | reverse | 4 | pending |
| line-2 | line-2-0558-0422-s007275 | forward | 4 | pending |
| line-2 | line-2-0558-0422-s007275 | reverse | 4 | pending |
| line-2 | line-2-0557-0512-s009430 | forward | 3 | pending |
| line-2 | line-2-0557-0512-s009430 | reverse | 3 | pending |
| line-2 | line-2-0530-0627-s012867 | forward | 3 | pending |
| line-2 | line-2-0530-0627-s012867 | reverse | 3 | pending |
| line-2 | line-2-0524-0761-s015752 | reverse | 3 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | 4 | pending |
| line-3 | line-3-0736-0710-s006160 | forward | 4 | pending |
| line-3 | line-3-0736-0710-s006160 | reverse | 4 | pending |
| line-3 | line-3-0609-0652-s009332 | forward | 4 | pending |
| line-3 | line-3-0609-0652-s009332 | reverse | 4 | pending |
| line-3 | line-3-0622-0513-s012348 | forward | 3 | pending |
| line-3 | line-3-0622-0513-s012348 | reverse | 3 | pending |
| line-3 | line-3-0557-0512-s013751 | forward | 3 | pending |
| line-3 | line-3-0557-0512-s013751 | reverse | 3 | pending |
| line-3 | line-3-0605-0473-s015355 | forward | 3 | pending |
| line-3 | line-3-0605-0473-s015355 | reverse | 3 | pending |
| line-3 | line-3-0616-0325-s019023 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Fallujah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
