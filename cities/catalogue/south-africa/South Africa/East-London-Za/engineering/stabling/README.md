# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **139 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **125 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0250-0950-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0295-0853-s003002 | forward | revenue | 3 | pending |
| line-1 | line-1-0295-0853-s003002 | reverse | revenue | 3 | pending |
| line-1 | line-1-0409-0795-s006023 | forward | revenue | 3 | pending |
| line-1 | line-1-0409-0795-s006023 | reverse | revenue | 3 | pending |
| line-1 | line-1-0395-0730-s007970 | forward | revenue | 3 | pending |
| line-1 | line-1-0395-0730-s007970 | reverse | revenue | 3 | pending |
| line-1 | line-1-0411-0668-s010987 | forward | revenue | 3 | pending |
| line-1 | line-1-0411-0668-s010987 | reverse | revenue | 3 | pending |
| line-1 | line-1-0510-0567-s014588 | forward | revenue | 3 | pending |
| line-1 | line-1-0510-0567-s014588 | reverse | revenue | 3 | pending |
| line-1 | line-1-0587-0545-s017008 | forward | revenue | 2 | pending |
| line-1 | line-1-0587-0545-s017008 | reverse | revenue | 2 | pending |
| line-1 | line-1-0676-0516-s020018 | forward | revenue | 2 | pending |
| line-1 | line-1-0676-0516-s020018 | reverse | revenue | 2 | pending |
| line-1 | line-1-0778-0438-s023067 | reverse | revenue | 2 | pending |
| line-1 | line-1-0587-0545-s017008 | forward | spare | 1 | pending |
| line-1 | line-1-0587-0545-s017008 | reverse | spare | 1 | pending |
| line-1 | line-1-0676-0516-s020018 | forward | spare | 1 | pending |
| line-1 | line-1-0676-0516-s020018 | reverse | spare | 1 | pending |
| line-1 | line-1-0778-0438-s023067 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0548-0772-s001936 | forward | revenue | 3 | pending |
| line-2 | line-2-0548-0772-s001936 | reverse | revenue | 3 | pending |
| line-2 | line-2-0583-0691-s003846 | forward | revenue | 3 | pending |
| line-2 | line-2-0583-0691-s003846 | reverse | revenue | 3 | pending |
| line-2 | line-2-0510-0567-s007027 | forward | revenue | 3 | pending |
| line-2 | line-2-0510-0567-s007027 | reverse | revenue | 3 | pending |
| line-2 | line-2-0426-0496-s009866 | forward | revenue | 3 | pending |
| line-2 | line-2-0426-0496-s009866 | reverse | revenue | 3 | pending |
| line-2 | line-2-0294-0406-s013380 | forward | revenue | 3 | pending |
| line-2 | line-2-0294-0406-s013380 | reverse | revenue | 3 | pending |
| line-2 | line-2-0201-0299-s016881 | forward | revenue | 3 | pending |
| line-2 | line-2-0201-0299-s016881 | reverse | revenue | 3 | pending |
| line-2 | line-2-0000-0177-s023239 | reverse | revenue | 3 | pending |
| line-2 | line-2-0548-0772-s001936 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0772-s001936 | reverse | spare | 1 | pending |
| line-2 | line-2-0583-0691-s003846 | forward | spare | 1 | pending |
| line-2 | line-2-0583-0691-s003846 | reverse | spare | 1 | pending |
| line-2 | line-2-0510-0567-s007027 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0185-0375-s006866 | forward | revenue | 4 | pending |
| line-3 | line-3-0185-0375-s006866 | reverse | revenue | 4 | pending |
| line-3 | line-3-0209-0502-s009877 | forward | revenue | 4 | pending |
| line-3 | line-3-0209-0502-s009877 | reverse | revenue | 4 | pending |
| line-3 | line-3-0225-0639-s012882 | forward | revenue | 4 | pending |
| line-3 | line-3-0225-0639-s012882 | reverse | revenue | 4 | pending |
| line-3 | line-3-0270-0761-s015892 | forward | revenue | 4 | pending |
| line-3 | line-3-0270-0761-s015892 | reverse | revenue | 4 | pending |
| line-3 | line-3-0308-0981-s021177 | reverse | revenue | 3 | pending |
| line-3 | line-3-0308-0981-s021177 | reverse | spare | 1 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0185-0375-s006866 | forward | spare | 1 | pending |
| line-3 | line-3-0185-0375-s006866 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**89 trainsets exceed the reference platform envelope**, requiring **5,295.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0250-0950-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0295-0853-s003002 | 6 | 2 | 4 | 238.0 |
| line-1-0395-0730-s007970 | 6 | 2 | 4 | 238.0 |
| line-1-0409-0795-s006023 | 6 | 2 | 4 | 238.0 |
| line-1-0411-0668-s010987 | 6 | 2 | 4 | 238.0 |
| line-1-0510-0567-s014588 | 6 | 4 | 2 | 119.0 |
| line-1-0587-0545-s017008 | 6 | 2 | 4 | 238.0 |
| line-1-0676-0516-s020018 | 6 | 2 | 4 | 238.0 |
| line-1-0778-0438-s023067 | 3 | 2 | 1 | 59.5 |
| line-2-0000-0177-s023239 | 3 | 2 | 1 | 59.5 |
| line-2-0201-0299-s016881 | 6 | 2 | 4 | 238.0 |
| line-2-0294-0406-s013380 | 6 | 2 | 4 | 238.0 |
| line-2-0426-0496-s009866 | 6 | 2 | 4 | 238.0 |
| line-2-0510-0567-s007027 | 7 | 4 | 3 | 178.5 |
| line-2-0548-0772-s001936 | 8 | 2 | 6 | 357.0 |
| line-2-0576-0798-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0583-0691-s003846 | 8 | 2 | 6 | 357.0 |
| line-3-0139-0104-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0185-0375-s006866 | 10 | 2 | 8 | 476.0 |
| line-3-0209-0502-s009877 | 8 | 2 | 6 | 357.0 |
| line-3-0225-0639-s012882 | 8 | 2 | 6 | 357.0 |
| line-3-0270-0761-s015892 | 8 | 2 | 6 | 357.0 |
| line-3-0308-0981-s021177 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/East-London-Za/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
