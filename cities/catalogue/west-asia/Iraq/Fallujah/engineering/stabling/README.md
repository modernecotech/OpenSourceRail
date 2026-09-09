# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **122 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **109 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0297-0015-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0415-0292-s006644 | forward | revenue | 3 | pending |
| line-1 | line-1-0415-0292-s006644 | reverse | revenue | 3 | pending |
| line-1 | line-1-0450-0414-s009650 | forward | revenue | 3 | pending |
| line-1 | line-1-0450-0414-s009650 | reverse | revenue | 3 | pending |
| line-1 | line-1-0527-0439-s011625 | forward | revenue | 3 | pending |
| line-1 | line-1-0527-0439-s011625 | reverse | revenue | 3 | pending |
| line-1 | line-1-0557-0512-s013619 | forward | revenue | 3 | pending |
| line-1 | line-1-0557-0512-s013619 | reverse | revenue | 3 | pending |
| line-1 | line-1-0585-0569-s015667 | forward | revenue | 3 | pending |
| line-1 | line-1-0585-0569-s015667 | reverse | revenue | 3 | pending |
| line-1 | line-1-0682-0603-s018667 | forward | revenue | 3 | pending |
| line-1 | line-1-0682-0603-s018667 | reverse | revenue | 3 | pending |
| line-1 | line-1-0748-0658-s021003 | reverse | revenue | 2 | pending |
| line-1 | line-1-0748-0658-s021003 | reverse | spare | 1 | pending |
| line-1 | line-1-0297-0015-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0292-s006644 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0292-s006644 | reverse | spare | 1 | pending |
| line-1 | line-1-0450-0414-s009650 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0204-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0518-0325-s004272 | forward | revenue | 3 | pending |
| line-2 | line-2-0518-0325-s004272 | reverse | revenue | 3 | pending |
| line-2 | line-2-0558-0422-s007275 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0422-s007275 | reverse | revenue | 3 | pending |
| line-2 | line-2-0557-0512-s009430 | forward | revenue | 3 | pending |
| line-2 | line-2-0557-0512-s009430 | reverse | revenue | 3 | pending |
| line-2 | line-2-0530-0627-s012867 | forward | revenue | 3 | pending |
| line-2 | line-2-0530-0627-s012867 | reverse | revenue | 3 | pending |
| line-2 | line-2-0524-0761-s015752 | reverse | revenue | 3 | pending |
| line-2 | line-2-0518-0325-s004272 | forward | spare | 1 | pending |
| line-2 | line-2-0518-0325-s004272 | reverse | spare | 1 | pending |
| line-2 | line-2-0558-0422-s007275 | forward | spare | 1 | pending |
| line-2 | line-2-0558-0422-s007275 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0868-0951-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0736-0710-s006160 | forward | revenue | 3 | pending |
| line-3 | line-3-0736-0710-s006160 | reverse | revenue | 3 | pending |
| line-3 | line-3-0609-0652-s009332 | forward | revenue | 3 | pending |
| line-3 | line-3-0609-0652-s009332 | reverse | revenue | 3 | pending |
| line-3 | line-3-0622-0513-s012348 | forward | revenue | 3 | pending |
| line-3 | line-3-0622-0513-s012348 | reverse | revenue | 3 | pending |
| line-3 | line-3-0557-0512-s013751 | forward | revenue | 3 | pending |
| line-3 | line-3-0557-0512-s013751 | reverse | revenue | 3 | pending |
| line-3 | line-3-0605-0473-s015355 | forward | revenue | 3 | pending |
| line-3 | line-3-0605-0473-s015355 | reverse | revenue | 3 | pending |
| line-3 | line-3-0616-0325-s019023 | reverse | revenue | 3 | pending |
| line-3 | line-3-0736-0710-s006160 | forward | spare | 1 | pending |
| line-3 | line-3-0736-0710-s006160 | reverse | spare | 1 | pending |
| line-3 | line-3-0609-0652-s009332 | forward | spare | 1 | pending |
| line-3 | line-3-0609-0652-s009332 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **4,403.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0015-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0415-0292-s006644 | 8 | 2 | 6 | 357.0 |
| line-1-0450-0414-s009650 | 7 | 2 | 5 | 297.5 |
| line-1-0527-0439-s011625 | 6 | 2 | 4 | 238.0 |
| line-1-0557-0512-s013619 | 6 | 4 | 2 | 119.0 |
| line-1-0585-0569-s015667 | 6 | 2 | 4 | 238.0 |
| line-1-0682-0603-s018667 | 6 | 2 | 4 | 238.0 |
| line-1-0748-0658-s021003 | 3 | 2 | 1 | 59.5 |
| line-2-0518-0325-s004272 | 8 | 2 | 6 | 357.0 |
| line-2-0524-0761-s015752 | 3 | 2 | 1 | 59.5 |
| line-2-0530-0627-s012867 | 6 | 2 | 4 | 238.0 |
| line-2-0532-0204-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0557-0512-s009430 | 6 | 4 | 2 | 119.0 |
| line-2-0558-0422-s007275 | 8 | 2 | 6 | 357.0 |
| line-3-0557-0512-s013751 | 6 | 4 | 2 | 119.0 |
| line-3-0605-0473-s015355 | 6 | 2 | 4 | 238.0 |
| line-3-0609-0652-s009332 | 8 | 2 | 6 | 357.0 |
| line-3-0616-0325-s019023 | 3 | 2 | 1 | 59.5 |
| line-3-0622-0513-s012348 | 6 | 2 | 4 | 238.0 |
| line-3-0736-0710-s006160 | 8 | 2 | 6 | 357.0 |
| line-3-0868-0951-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Fallujah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
