# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 15 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0420-0384-s000000 | forward | 4 | pending |
| line-1 | line-1-0451-0487-s003008 | forward | 4 | pending |
| line-1 | line-1-0451-0487-s003008 | reverse | 3 | pending |
| line-1 | line-1-0552-0547-s006117 | forward | 3 | pending |
| line-1 | line-1-0552-0547-s006117 | reverse | 3 | pending |
| line-1 | line-1-0613-0614-s008850 | forward | 3 | pending |
| line-1 | line-1-0613-0614-s008850 | reverse | 3 | pending |
| line-1 | line-1-0712-0672-s011599 | reverse | 3 | pending |
| line-2 | line-2-0571-0334-s000000 | forward | 3 | pending |
| line-2 | line-2-0589-0466-s003011 | forward | 3 | pending |
| line-2 | line-2-0589-0466-s003011 | reverse | 3 | pending |
| line-2 | line-2-0552-0547-s005672 | forward | 3 | pending |
| line-2 | line-2-0552-0547-s005672 | reverse | 3 | pending |
| line-2 | line-2-0471-0638-s008339 | forward | 3 | pending |
| line-2 | line-2-0471-0638-s008339 | reverse | 3 | pending |
| line-2 | line-2-0447-0711-s010996 | reverse | 3 | pending |
| line-3 | line-3-0164-1077-s000000 | forward | 6 | pending |
| line-3 | line-3-0467-0606-s012698 | forward | 6 | pending |
| line-3 | line-3-0467-0606-s012698 | reverse | 5 | pending |
| line-3 | line-3-0552-0547-s014922 | forward | 5 | pending |
| line-3 | line-3-0552-0547-s014922 | reverse | 5 | pending |
| line-3 | line-3-0655-0533-s017325 | forward | 5 | pending |
| line-3 | line-3-0655-0533-s017325 | reverse | 5 | pending |
| line-3 | line-3-0762-0506-s019717 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Mymensingh/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
