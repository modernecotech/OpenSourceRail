# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **114 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0342-0395-s000000 | forward | 3 | pending |
| line-1 | line-1-0374-0465-s003012 | forward | 3 | pending |
| line-1 | line-1-0374-0465-s003012 | reverse | 3 | pending |
| line-1 | line-1-0504-0515-s006026 | forward | 3 | pending |
| line-1 | line-1-0504-0515-s006026 | reverse | 3 | pending |
| line-1 | line-1-0546-0564-s007838 | forward | 3 | pending |
| line-1 | line-1-0546-0564-s007838 | reverse | 3 | pending |
| line-1 | line-1-0513-0645-s009951 | forward | 3 | pending |
| line-1 | line-1-0513-0645-s009951 | reverse | 2 | pending |
| line-1 | line-1-0541-0714-s012054 | forward | 2 | pending |
| line-1 | line-1-0541-0714-s012054 | reverse | 2 | pending |
| line-1 | line-1-0607-0783-s014154 | forward | 2 | pending |
| line-1 | line-1-0607-0783-s014154 | reverse | 2 | pending |
| line-1 | line-1-0651-0859-s016234 | forward | 2 | pending |
| line-1 | line-1-0651-0859-s016234 | reverse | 2 | pending |
| line-1 | line-1-0684-0936-s018318 | reverse | 2 | pending |
| line-2 | line-2-0459-0399-s000000 | forward | 4 | pending |
| line-2 | line-2-0546-0490-s003007 | forward | 4 | pending |
| line-2 | line-2-0546-0490-s003007 | reverse | 4 | pending |
| line-2 | line-2-0546-0564-s004686 | forward | 4 | pending |
| line-2 | line-2-0546-0564-s004686 | reverse | 4 | pending |
| line-2 | line-2-0546-0630-s006023 | forward | 4 | pending |
| line-2 | line-2-0546-0630-s006023 | reverse | 4 | pending |
| line-2 | line-2-0484-0747-s009036 | forward | 3 | pending |
| line-2 | line-2-0484-0747-s009036 | reverse | 3 | pending |
| line-2 | line-2-0323-1016-s017716 | reverse | 3 | pending |
| line-3 | line-3-0681-0604-s000000 | forward | 4 | pending |
| line-3 | line-3-0546-0564-s003713 | forward | 4 | pending |
| line-3 | line-3-0546-0564-s003713 | reverse | 4 | pending |
| line-3 | line-3-0471-0628-s006029 | forward | 4 | pending |
| line-3 | line-3-0471-0628-s006029 | reverse | 4 | pending |
| line-3 | line-3-0522-0743-s009039 | forward | 4 | pending |
| line-3 | line-3-0522-0743-s009039 | reverse | 4 | pending |
| line-3 | line-3-0507-0816-s011090 | forward | 3 | pending |
| line-3 | line-3-0507-0816-s011090 | reverse | 3 | pending |
| line-3 | line-3-0383-1021-s017162 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Minya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
