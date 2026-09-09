# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **129 trainsets at 40 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **115 revenue, 10 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0703-0394-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0652-0504-s004057 | forward | revenue | 2 | pending |
| line-1 | line-1-0652-0504-s004057 | reverse | revenue | 2 | pending |
| line-1 | line-1-0686-0568-s005974 | forward | revenue | 2 | pending |
| line-1 | line-1-0686-0568-s005974 | reverse | revenue | 2 | pending |
| line-1 | line-1-0721-0644-s007876 | forward | revenue | 2 | pending |
| line-1 | line-1-0721-0644-s007876 | reverse | revenue | 2 | pending |
| line-1 | line-1-0777-0745-s010377 | forward | revenue | 2 | pending |
| line-1 | line-1-0777-0745-s010377 | reverse | revenue | 2 | pending |
| line-1 | line-1-0782-0832-s012785 | forward | revenue | 2 | pending |
| line-1 | line-1-0782-0832-s012785 | reverse | revenue | 2 | pending |
| line-1 | line-1-0779-0927-s015194 | forward | revenue | 2 | pending |
| line-1 | line-1-0779-0927-s015194 | reverse | revenue | 2 | pending |
| line-1 | line-1-0817-0999-s017287 | reverse | revenue | 2 | pending |
| line-1 | line-1-0703-0394-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0652-0504-s004057 | forward | spare | 1 | pending |
| line-1 | line-1-0652-0504-s004057 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0948-1026-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0877-0941-s003003 | forward | revenue | 2 | pending |
| line-2 | line-2-0877-0941-s003003 | reverse | revenue | 2 | pending |
| line-2 | line-2-0898-0862-s004935 | forward | revenue | 2 | pending |
| line-2 | line-2-0898-0862-s004935 | reverse | revenue | 2 | pending |
| line-2 | line-2-0854-0799-s006983 | forward | revenue | 2 | pending |
| line-2 | line-2-0854-0799-s006983 | reverse | revenue | 2 | pending |
| line-2 | line-2-0817-0724-s009056 | forward | revenue | 2 | pending |
| line-2 | line-2-0817-0724-s009056 | reverse | revenue | 2 | pending |
| line-2 | line-2-0827-0632-s011095 | forward | revenue | 2 | pending |
| line-2 | line-2-0827-0632-s011095 | reverse | revenue | 2 | pending |
| line-2 | line-2-0805-0560-s013121 | forward | revenue | 2 | pending |
| line-2 | line-2-0805-0560-s013121 | reverse | revenue | 2 | pending |
| line-2 | line-2-0791-0481-s015140 | reverse | revenue | 1 | pending |
| line-2 | line-2-0791-0481-s015140 | reverse | spare | 1 | pending |
| line-2 | line-2-0948-1026-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0877-0941-s003003 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0205-1392-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0501-0967-s011802 | forward | revenue | 3 | pending |
| line-3 | line-3-0501-0967-s011802 | reverse | revenue | 3 | pending |
| line-3 | line-3-0583-0909-s014014 | forward | revenue | 3 | pending |
| line-3 | line-3-0583-0909-s014014 | reverse | revenue | 3 | pending |
| line-3 | line-3-0667-0845-s017023 | forward | revenue | 3 | pending |
| line-3 | line-3-0667-0845-s017023 | reverse | revenue | 3 | pending |
| line-3 | line-3-0725-0736-s020030 | forward | revenue | 3 | pending |
| line-3 | line-3-0725-0736-s020030 | reverse | revenue | 2 | pending |
| line-3 | line-3-0777-0745-s021239 | forward | revenue | 2 | pending |
| line-3 | line-3-0777-0745-s021239 | reverse | revenue | 2 | pending |
| line-3 | line-3-0849-0728-s023034 | forward | revenue | 2 | pending |
| line-3 | line-3-0849-0728-s023034 | reverse | revenue | 2 | pending |
| line-3 | line-3-0918-0637-s025666 | forward | revenue | 2 | pending |
| line-3 | line-3-0918-0637-s025666 | reverse | revenue | 2 | pending |
| line-3 | line-3-1021-0609-s028298 | reverse | revenue | 2 | pending |
| line-3 | line-3-0725-0736-s020030 | reverse | spare | 1 | pending |
| line-3 | line-3-0777-0745-s021239 | forward | spare | 1 | pending |
| line-3 | line-3-0777-0745-s021239 | reverse | spare | 1 | pending |
| line-3 | line-3-0849-0728-s023034 | forward | spare | 1 | pending |
| line-3 | line-3-0849-0728-s023034 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0703-0394-s000827 | forward | revenue | 1 | pending |
| line-4 | line-4-0703-0394-s000827 | reverse | revenue | 1 | pending |
| line-4 | line-4-0652-0504-s003719 | forward | revenue | 1 | pending |
| line-4 | line-4-0652-0504-s003719 | reverse | revenue | 1 | pending |
| line-4 | line-4-0562-0593-s007003 | reverse | revenue | 1 | pending |
| line-4 | line-4-0431-0658-s010511 | forward | revenue | 1 | pending |
| line-4 | line-4-0431-0658-s010511 | reverse | revenue | 1 | pending |
| line-4 | line-4-0454-0905-s017527 | reverse | revenue | 1 | pending |
| line-4 | line-4-0501-0967-s022703 | forward | revenue | 1 | pending |
| line-4 | line-4-0501-0967-s022703 | reverse | revenue | 1 | pending |
| line-4 | line-4-0709-0983-s028059 | reverse | revenue | 1 | pending |
| line-4 | line-4-0779-0927-s029969 | forward | revenue | 1 | pending |
| line-4 | line-4-0779-0927-s029969 | reverse | revenue | 1 | pending |
| line-4 | line-4-0898-0862-s033380 | forward | revenue | 1 | pending |
| line-4 | line-4-0975-0870-s035308 | forward | revenue | 1 | pending |
| line-4 | line-4-0975-0870-s035308 | reverse | revenue | 1 | pending |
| line-4 | line-4-1070-0875-s037249 | forward | revenue | 1 | pending |
| line-4 | line-4-1073-0790-s041110 | forward | revenue | 1 | pending |
| line-4 | line-4-1073-0790-s041110 | reverse | revenue | 1 | pending |
| line-4 | line-4-1021-0609-s045442 | forward | revenue | 1 | pending |
| line-4 | line-4-0967-0502-s048137 | forward | spare | 1 | pending |
| line-4 | line-4-0967-0502-s048137 | reverse | spare | 1 | pending |
| line-4 | line-4-0851-0430-s051653 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**44 trainsets exceed the reference platform envelope**, requiring **3,740.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0652-0504-s004057 | 6 | 4 | 2 | 170.0 |
| line-1-0686-0568-s005974 | 4 | 2 | 2 | 170.0 |
| line-1-0703-0394-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0721-0644-s007876 | 4 | 2 | 2 | 170.0 |
| line-1-0777-0745-s010377 | 4 | 4 | 0 | 0.0 |
| line-1-0779-0927-s015194 | 4 | 4 | 0 | 0.0 |
| line-1-0782-0832-s012785 | 4 | 2 | 2 | 170.0 |
| line-1-0817-0999-s017287 | 2 | 2 | 0 | 0.0 |
| line-2-0791-0481-s015140 | 2 | 2 | 0 | 0.0 |
| line-2-0805-0560-s013121 | 4 | 2 | 2 | 170.0 |
| line-2-0817-0724-s009056 | 4 | 2 | 2 | 170.0 |
| line-2-0827-0632-s011095 | 4 | 2 | 2 | 170.0 |
| line-2-0854-0799-s006983 | 4 | 2 | 2 | 170.0 |
| line-2-0877-0941-s003003 | 5 | 2 | 3 | 255.0 |
| line-2-0898-0862-s004935 | 4 | 4 | 0 | 0.0 |
| line-2-0948-1026-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0205-1392-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0501-0967-s011802 | 6 | 4 | 2 | 170.0 |
| line-3-0583-0909-s014014 | 6 | 2 | 4 | 340.0 |
| line-3-0667-0845-s017023 | 6 | 2 | 4 | 340.0 |
| line-3-0725-0736-s020030 | 6 | 2 | 4 | 340.0 |
| line-3-0777-0745-s021239 | 6 | 4 | 2 | 170.0 |
| line-3-0849-0728-s023034 | 6 | 2 | 4 | 340.0 |
| line-3-0918-0637-s025666 | 4 | 2 | 2 | 170.0 |
| line-3-1021-0609-s028298 | 2 | 2 | 0 | 0.0 |
| line-4-0431-0658-s010511 | 2 | 2 | 0 | 0.0 |
| line-4-0454-0905-s017527 | 1 | 2 | 0 | 0.0 |
| line-4-0501-0967-s022703 | 2 | 4 | 0 | 0.0 |
| line-4-0562-0593-s007003 | 1 | 2 | 0 | 0.0 |
| line-4-0652-0504-s003719 | 2 | 4 | 0 | 0.0 |
| line-4-0703-0394-s000827 | 2 | 4 | 0 | 0.0 |
| line-4-0709-0983-s028059 | 1 | 2 | 0 | 0.0 |
| line-4-0779-0927-s029969 | 2 | 4 | 0 | 0.0 |
| line-4-0851-0430-s051653 | 1 | 2 | 0 | 0.0 |
| line-4-0898-0862-s033380 | 1 | 4 | 0 | 0.0 |
| line-4-0967-0502-s048137 | 2 | 2 | 0 | 0.0 |
| line-4-0975-0870-s035308 | 2 | 2 | 0 | 0.0 |
| line-4-1021-0609-s045442 | 1 | 4 | 0 | 0.0 |
| line-4-1070-0875-s037249 | 1 | 2 | 0 | 0.0 |
| line-4-1073-0790-s041110 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Sulaymaniyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
