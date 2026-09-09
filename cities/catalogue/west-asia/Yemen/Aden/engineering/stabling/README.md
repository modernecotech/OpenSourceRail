# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **97 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **87 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0110-0325-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0224-0376-s003009 | forward | revenue | 4 | pending |
| line-1 | line-1-0224-0376-s003009 | reverse | revenue | 3 | pending |
| line-1 | line-1-0465-0544-s009995 | forward | revenue | 3 | pending |
| line-1 | line-1-0465-0544-s009995 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0598-s012014 | forward | revenue | 3 | pending |
| line-1 | line-1-0543-0598-s012014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0631-0598-s014274 | forward | revenue | 3 | pending |
| line-1 | line-1-0631-0598-s014274 | reverse | revenue | 3 | pending |
| line-1 | line-1-0702-0621-s016544 | reverse | revenue | 3 | pending |
| line-1 | line-1-0224-0376-s003009 | reverse | spare | 1 | pending |
| line-1 | line-1-0465-0544-s009995 | forward | spare | 1 | pending |
| line-1 | line-1-0465-0544-s009995 | reverse | spare | 1 | pending |
| line-1 | line-1-0543-0598-s012014 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0325-0696-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0460-0668-s003015 | forward | revenue | 4 | pending |
| line-2 | line-2-0460-0668-s003015 | reverse | revenue | 4 | pending |
| line-2 | line-2-0543-0598-s006066 | forward | revenue | 3 | pending |
| line-2 | line-2-0543-0598-s006066 | reverse | revenue | 3 | pending |
| line-2 | line-2-0605-0492-s009052 | forward | revenue | 3 | pending |
| line-2 | line-2-0605-0492-s009052 | reverse | revenue | 3 | pending |
| line-2 | line-2-0649-0299-s014203 | reverse | revenue | 3 | pending |
| line-2 | line-2-0543-0598-s006066 | forward | spare | 1 | pending |
| line-2 | line-2-0543-0598-s006066 | reverse | spare | 1 | pending |
| line-2 | line-2-0605-0492-s009052 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0363-0598-s006156 | forward | revenue | 3 | pending |
| line-3 | line-3-0363-0598-s006156 | reverse | revenue | 3 | pending |
| line-3 | line-3-0481-0594-s009158 | forward | revenue | 3 | pending |
| line-3 | line-3-0481-0594-s009158 | reverse | revenue | 3 | pending |
| line-3 | line-3-0543-0598-s010597 | forward | revenue | 3 | pending |
| line-3 | line-3-0543-0598-s010597 | reverse | revenue | 3 | pending |
| line-3 | line-3-0600-0642-s012172 | forward | revenue | 3 | pending |
| line-3 | line-3-0600-0642-s012172 | reverse | revenue | 2 | pending |
| line-3 | line-3-0710-0680-s015095 | reverse | revenue | 2 | pending |
| line-3 | line-3-0600-0642-s012172 | reverse | spare | 1 | pending |
| line-3 | line-3-0710-0680-s015095 | reverse | spare | 1 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**57 trainsets exceed the reference platform envelope**, requiring **3,391.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0110-0325-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0224-0376-s003009 | 8 | 2 | 6 | 357.0 |
| line-1-0465-0544-s009995 | 8 | 2 | 6 | 357.0 |
| line-1-0543-0598-s012014 | 7 | 4 | 3 | 178.5 |
| line-1-0631-0598-s014274 | 6 | 2 | 4 | 238.0 |
| line-1-0702-0621-s016544 | 3 | 2 | 1 | 59.5 |
| line-2-0325-0696-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0460-0668-s003015 | 8 | 2 | 6 | 357.0 |
| line-2-0543-0598-s006066 | 8 | 4 | 4 | 238.0 |
| line-2-0605-0492-s009052 | 7 | 2 | 5 | 297.5 |
| line-2-0649-0299-s014203 | 3 | 2 | 1 | 59.5 |
| line-3-0134-0492-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0363-0598-s006156 | 6 | 2 | 4 | 238.0 |
| line-3-0481-0594-s009158 | 6 | 2 | 4 | 238.0 |
| line-3-0543-0598-s010597 | 6 | 4 | 2 | 119.0 |
| line-3-0600-0642-s012172 | 6 | 2 | 4 | 238.0 |
| line-3-0710-0680-s015095 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Aden/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
