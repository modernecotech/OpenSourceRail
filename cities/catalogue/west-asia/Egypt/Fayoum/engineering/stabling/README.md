# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **190 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **171 revenue, 16 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0146-0238-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0358-0434-s007012 | forward | revenue | 6 | pending |
| line-1 | line-1-0358-0434-s007012 | reverse | revenue | 6 | pending |
| line-1 | line-1-0477-0472-s010023 | forward | revenue | 6 | pending |
| line-1 | line-1-0477-0472-s010023 | reverse | revenue | 6 | pending |
| line-1 | line-1-0565-0561-s012840 | forward | revenue | 6 | pending |
| line-1 | line-1-0565-0561-s012840 | reverse | revenue | 6 | pending |
| line-1 | line-1-0683-0594-s016455 | forward | revenue | 6 | pending |
| line-1 | line-1-0683-0594-s016455 | reverse | revenue | 6 | pending |
| line-1 | line-1-0970-0805-s025735 | forward | revenue | 6 | pending |
| line-1 | line-1-0970-0805-s025735 | reverse | revenue | 5 | pending |
| line-1 | line-1-1066-0823-s028462 | reverse | revenue | 5 | pending |
| line-1 | line-1-0970-0805-s025735 | reverse | spare | 1 | pending |
| line-1 | line-1-1066-0823-s028462 | reverse | spare | 1 | pending |
| line-1 | line-1-0146-0238-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0358-0434-s007012 | forward | spare | 1 | pending |
| line-1 | line-1-0358-0434-s007012 | reverse | spare | 1 | pending |
| line-1 | line-1-0477-0472-s010023 | forward | spare | 1 | pending |
| line-1 | line-1-0477-0472-s010023 | reverse | spare | 1 | pending |
| line-1 | line-1-0565-0561-s012840 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0946-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0610-0671-s007026 | forward | revenue | 4 | pending |
| line-2 | line-2-0610-0671-s007026 | reverse | revenue | 4 | pending |
| line-2 | line-2-0543-0610-s010033 | forward | revenue | 4 | pending |
| line-2 | line-2-0543-0610-s010033 | reverse | revenue | 4 | pending |
| line-2 | line-2-0565-0561-s011588 | forward | revenue | 4 | pending |
| line-2 | line-2-0565-0561-s011588 | reverse | revenue | 4 | pending |
| line-2 | line-2-0577-0501-s013039 | forward | revenue | 4 | pending |
| line-2 | line-2-0577-0501-s013039 | reverse | revenue | 4 | pending |
| line-2 | line-2-0475-0427-s015934 | forward | revenue | 4 | pending |
| line-2 | line-2-0475-0427-s015934 | reverse | revenue | 4 | pending |
| line-2 | line-2-0365-0369-s018823 | reverse | revenue | 4 | pending |
| line-2 | line-2-0610-0671-s007026 | forward | spare | 1 | pending |
| line-2 | line-2-0610-0671-s007026 | reverse | spare | 1 | pending |
| line-2 | line-2-0543-0610-s010033 | forward | spare | 1 | pending |
| line-2 | line-2-0543-0610-s010033 | reverse | spare | 1 | pending |
| line-2 | line-2-0565-0561-s011588 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0912-0331-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0635-0464-s006912 | forward | revenue | 6 | pending |
| line-3 | line-3-0635-0464-s006912 | reverse | revenue | 5 | pending |
| line-3 | line-3-0565-0561-s010076 | forward | revenue | 5 | pending |
| line-3 | line-3-0565-0561-s010076 | reverse | revenue | 5 | pending |
| line-3 | line-3-0484-0619-s012934 | forward | revenue | 5 | pending |
| line-3 | line-3-0484-0619-s012934 | reverse | revenue | 5 | pending |
| line-3 | line-3-0409-0773-s017204 | forward | revenue | 5 | pending |
| line-3 | line-3-0409-0773-s017204 | reverse | revenue | 5 | pending |
| line-3 | line-3-0244-0849-s021464 | reverse | revenue | 5 | pending |
| line-3 | line-3-0635-0464-s006912 | reverse | spare | 1 | pending |
| line-3 | line-3-0565-0561-s010076 | forward | spare | 1 | pending |
| line-3 | line-3-0565-0561-s010076 | reverse | spare | 1 | pending |
| line-3 | line-3-0484-0619-s012934 | forward | spare | 1 | pending |
| line-3 | line-3-0484-0619-s012934 | reverse | spare | 1 | pending |
| line-3 | line-3-0409-0773-s017204 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**144 trainsets exceed the reference platform envelope**, requiring **8,568.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0146-0238-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0358-0434-s007012 | 14 | 2 | 12 | 714.0 |
| line-1-0477-0472-s010023 | 14 | 2 | 12 | 714.0 |
| line-1-0565-0561-s012840 | 13 | 4 | 9 | 535.5 |
| line-1-0683-0594-s016455 | 12 | 2 | 10 | 595.0 |
| line-1-0970-0805-s025735 | 12 | 2 | 10 | 595.0 |
| line-1-1066-0823-s028462 | 6 | 2 | 4 | 238.0 |
| line-2-0365-0369-s018823 | 4 | 2 | 2 | 119.0 |
| line-2-0475-0427-s015934 | 8 | 2 | 6 | 357.0 |
| line-2-0543-0610-s010033 | 10 | 2 | 8 | 476.0 |
| line-2-0565-0561-s011588 | 9 | 4 | 5 | 297.5 |
| line-2-0577-0501-s013039 | 8 | 2 | 6 | 357.0 |
| line-2-0610-0671-s007026 | 10 | 2 | 8 | 476.0 |
| line-2-0695-0946-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0244-0849-s021464 | 5 | 2 | 3 | 178.5 |
| line-3-0409-0773-s017204 | 11 | 2 | 9 | 535.5 |
| line-3-0484-0619-s012934 | 12 | 2 | 10 | 595.0 |
| line-3-0565-0561-s010076 | 12 | 4 | 8 | 476.0 |
| line-3-0635-0464-s006912 | 12 | 2 | 10 | 595.0 |
| line-3-0912-0331-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Fayoum/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
