# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0198-1067-s000000 | forward | 4 | pending |
| line-1 | line-1-0401-0806-s007019 | forward | 4 | pending |
| line-1 | line-1-0401-0806-s007019 | reverse | 4 | pending |
| line-1 | line-1-0471-0694-s010022 | forward | 4 | pending |
| line-1 | line-1-0471-0694-s010022 | reverse | 4 | pending |
| line-1 | line-1-0529-0600-s013032 | forward | 4 | pending |
| line-1 | line-1-0529-0600-s013032 | reverse | 4 | pending |
| line-1 | line-1-0550-0548-s014441 | forward | 4 | pending |
| line-1 | line-1-0550-0548-s014441 | reverse | 4 | pending |
| line-1 | line-1-0548-0449-s017673 | forward | 4 | pending |
| line-1 | line-1-0548-0449-s017673 | reverse | 4 | pending |
| line-1 | line-1-0648-0369-s020673 | forward | 4 | pending |
| line-1 | line-1-0648-0369-s020673 | reverse | 3 | pending |
| line-1 | line-1-0737-0167-s026410 | reverse | 3 | pending |
| line-2 | line-2-0375-0601-s000000 | forward | 5 | pending |
| line-2 | line-2-0475-0547-s003014 | forward | 5 | pending |
| line-2 | line-2-0475-0547-s003014 | reverse | 5 | pending |
| line-2 | line-2-0550-0548-s005032 | forward | 4 | pending |
| line-2 | line-2-0550-0548-s005032 | reverse | 4 | pending |
| line-2 | line-2-0639-0486-s007636 | forward | 4 | pending |
| line-2 | line-2-0639-0486-s007636 | reverse | 4 | pending |
| line-2 | line-2-0928-0268-s015651 | reverse | 4 | pending |
| line-3 | line-3-0487-0404-s000000 | forward | 3 | pending |
| line-3 | line-3-0517-0516-s003003 | forward | 3 | pending |
| line-3 | line-3-0517-0516-s003003 | reverse | 3 | pending |
| line-3 | line-3-0550-0548-s004206 | forward | 3 | pending |
| line-3 | line-3-0550-0548-s004206 | reverse | 2 | pending |
| line-3 | line-3-0488-0597-s006296 | forward | 2 | pending |
| line-3 | line-3-0488-0597-s006296 | reverse | 2 | pending |
| line-3 | line-3-0445-0677-s008377 | forward | 2 | pending |
| line-3 | line-3-0445-0677-s008377 | reverse | 2 | pending |
| line-3 | line-3-0455-0763-s010463 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Maroua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
