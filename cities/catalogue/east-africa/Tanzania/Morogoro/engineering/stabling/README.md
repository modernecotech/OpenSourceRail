# Station and depot overnight allocation

Plan: **46 trainsets at stations + 74 at depots = 120 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0392-0381-s022051 | line-1 | declared-depot | 32 | 1,904.0 | 18 |
| line-2-0329-0733-s016169 | line-2 | storage-at-existing-powered-service-point | 22 | 1,309.0 | 0 |
| line-3-0357-0378-s016833 | line-3 | storage-at-existing-powered-service-point | 20 | 1,190.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0392-0381-s022051 | station | reverse | revenue | 2 |
| line-1 | line-1-0400-1089-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0432-0482-s019092 | station | forward | revenue | 1 |
| line-1 | line-1-0432-0482-s019092 | station | reverse | revenue | 1 |
| line-1 | line-1-0490-0810-s007023 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0810-s007023 | station | reverse | revenue | 1 |
| line-1 | line-1-0491-0520-s017070 | station | forward | revenue | 1 |
| line-1 | line-1-0491-0520-s017070 | station | reverse | revenue | 1 |
| line-1 | line-1-0523-0598-s013069 | station | forward | revenue | 1 |
| line-1 | line-1-0523-0598-s013069 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0552-s015061 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0552-s015061 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0701-s010043 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0701-s010043 | station | reverse | revenue | 1 |
| line-2 | line-2-0329-0733-s016169 | station | reverse | revenue | 2 |
| line-2 | line-2-0388-0640-s013726 | station | forward | revenue | 1 |
| line-2 | line-2-0388-0640-s013726 | station | reverse | revenue | 1 |
| line-2 | line-2-0451-0579-s011279 | station | forward | revenue | 1 |
| line-2 | line-2-0451-0579-s011279 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0552-s008847 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0552-s008847 | station | reverse | revenue | 1 |
| line-2 | line-2-0617-0519-s006919 | station | forward | revenue | 1 |
| line-2 | line-2-0617-0519-s006919 | station | reverse | revenue | 1 |
| line-2 | line-2-0693-0468-s004977 | station | forward | revenue | 1 |
| line-2 | line-2-0693-0468-s004977 | station | reverse | revenue | 1 |
| line-2 | line-2-0869-0325-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0357-0378-s016833 | station | reverse | revenue | 2 |
| line-3 | line-3-0375-0462-s014711 | station | forward | revenue | 1 |
| line-3 | line-3-0375-0462-s014711 | station | reverse | revenue | 1 |
| line-3 | line-3-0449-0465-s012607 | station | forward | revenue | 1 |
| line-3 | line-3-0449-0465-s012607 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0552-s007996 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0552-s007996 | station | reverse | revenue | 1 |
| line-3 | line-3-0548-0496-s009584 | station | forward | revenue | 1 |
| line-3 | line-3-0548-0496-s009584 | station | reverse | revenue | 1 |
| line-3 | line-3-0572-0591-s006583 | station | forward | revenue | 1 |
| line-3 | line-3-0572-0591-s006583 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0606-s003579 | station | forward | revenue | 1 |
| line-3 | line-3-0711-0606-s003579 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0618-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0392-0381-s022051 | depot | — | revenue | 27 |
| line-1 | line-1-0392-0381-s022051 | depot | — | spare | 4 |
| line-1 | line-1-0392-0381-s022051 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0329-0733-s016169 | depot | — | revenue | 18 |
| line-2 | line-2-0329-0733-s016169 | depot | — | spare | 3 |
| line-2 | line-2-0329-0733-s016169 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0357-0378-s016833 | depot | — | revenue | 16 |
| line-3 | line-3-0357-0378-s016833 | depot | — | spare | 3 |
| line-3 | line-3-0357-0378-s016833 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/morogoro-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **120 trainsets at 23 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **107 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **74 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1089-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0490-0810-s007023 | forward | revenue | 3 | pending |
| line-1 | line-1-0490-0810-s007023 | reverse | revenue | 3 | pending |
| line-1 | line-1-0556-0701-s010043 | forward | revenue | 3 | pending |
| line-1 | line-1-0556-0701-s010043 | reverse | revenue | 3 | pending |
| line-1 | line-1-0523-0598-s013069 | forward | revenue | 3 | pending |
| line-1 | line-1-0523-0598-s013069 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0552-s015061 | forward | revenue | 3 | pending |
| line-1 | line-1-0543-0552-s015061 | reverse | revenue | 3 | pending |
| line-1 | line-1-0491-0520-s017070 | forward | revenue | 3 | pending |
| line-1 | line-1-0491-0520-s017070 | reverse | revenue | 3 | pending |
| line-1 | line-1-0432-0482-s019092 | forward | revenue | 3 | pending |
| line-1 | line-1-0432-0482-s019092 | reverse | revenue | 3 | pending |
| line-1 | line-1-0392-0381-s022051 | reverse | revenue | 3 | pending |
| line-1 | line-1-0490-0810-s007023 | forward | spare | 1 | pending |
| line-1 | line-1-0490-0810-s007023 | reverse | spare | 1 | pending |
| line-1 | line-1-0556-0701-s010043 | forward | spare | 1 | pending |
| line-1 | line-1-0556-0701-s010043 | reverse | spare | 1 | pending |
| line-1 | line-1-0523-0598-s013069 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0869-0325-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0693-0468-s004977 | forward | revenue | 3 | pending |
| line-2 | line-2-0693-0468-s004977 | reverse | revenue | 3 | pending |
| line-2 | line-2-0617-0519-s006919 | forward | revenue | 3 | pending |
| line-2 | line-2-0617-0519-s006919 | reverse | revenue | 3 | pending |
| line-2 | line-2-0543-0552-s008847 | forward | revenue | 3 | pending |
| line-2 | line-2-0543-0552-s008847 | reverse | revenue | 3 | pending |
| line-2 | line-2-0451-0579-s011279 | forward | revenue | 3 | pending |
| line-2 | line-2-0451-0579-s011279 | reverse | revenue | 2 | pending |
| line-2 | line-2-0388-0640-s013726 | forward | revenue | 2 | pending |
| line-2 | line-2-0388-0640-s013726 | reverse | revenue | 2 | pending |
| line-2 | line-2-0329-0733-s016169 | reverse | revenue | 2 | pending |
| line-2 | line-2-0451-0579-s011279 | reverse | spare | 1 | pending |
| line-2 | line-2-0388-0640-s013726 | forward | spare | 1 | pending |
| line-2 | line-2-0388-0640-s013726 | reverse | spare | 1 | pending |
| line-2 | line-2-0329-0733-s016169 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0885-0618-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0711-0606-s003579 | forward | revenue | 3 | pending |
| line-3 | line-3-0711-0606-s003579 | reverse | revenue | 3 | pending |
| line-3 | line-3-0572-0591-s006583 | forward | revenue | 3 | pending |
| line-3 | line-3-0572-0591-s006583 | reverse | revenue | 2 | pending |
| line-3 | line-3-0543-0552-s007996 | forward | revenue | 2 | pending |
| line-3 | line-3-0543-0552-s007996 | reverse | revenue | 2 | pending |
| line-3 | line-3-0548-0496-s009584 | forward | revenue | 2 | pending |
| line-3 | line-3-0548-0496-s009584 | reverse | revenue | 2 | pending |
| line-3 | line-3-0449-0465-s012607 | forward | revenue | 2 | pending |
| line-3 | line-3-0449-0465-s012607 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0462-s014711 | forward | revenue | 2 | pending |
| line-3 | line-3-0375-0462-s014711 | reverse | revenue | 2 | pending |
| line-3 | line-3-0357-0378-s016833 | reverse | revenue | 2 | pending |
| line-3 | line-3-0572-0591-s006583 | reverse | spare | 1 | pending |
| line-3 | line-3-0543-0552-s007996 | forward | spare | 1 | pending |
| line-3 | line-3-0543-0552-s007996 | reverse | spare | 1 | pending |
| line-3 | line-3-0548-0496-s009584 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**64 trainsets exceed the reference platform envelope**, requiring **3,808.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0392-0381-s022051 | 3 | 2 | 1 | 59.5 |
| line-1-0400-1089-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0432-0482-s019092 | 6 | 4 | 2 | 119.0 |
| line-1-0490-0810-s007023 | 8 | 2 | 6 | 357.0 |
| line-1-0491-0520-s017070 | 6 | 2 | 4 | 238.0 |
| line-1-0523-0598-s013069 | 7 | 2 | 5 | 297.5 |
| line-1-0543-0552-s015061 | 6 | 4 | 2 | 119.0 |
| line-1-0556-0701-s010043 | 8 | 2 | 6 | 357.0 |
| line-2-0329-0733-s016169 | 3 | 2 | 1 | 59.5 |
| line-2-0388-0640-s013726 | 6 | 2 | 4 | 238.0 |
| line-2-0451-0579-s011279 | 6 | 2 | 4 | 238.0 |
| line-2-0543-0552-s008847 | 6 | 4 | 2 | 119.0 |
| line-2-0617-0519-s006919 | 6 | 2 | 4 | 238.0 |
| line-2-0693-0468-s004977 | 6 | 2 | 4 | 238.0 |
| line-2-0869-0325-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0357-0378-s016833 | 2 | 2 | 0 | 0.0 |
| line-3-0375-0462-s014711 | 4 | 2 | 2 | 119.0 |
| line-3-0449-0465-s012607 | 4 | 4 | 0 | 0.0 |
| line-3-0543-0552-s007996 | 6 | 4 | 2 | 119.0 |
| line-3-0548-0496-s009584 | 5 | 2 | 3 | 178.5 |
| line-3-0572-0591-s006583 | 6 | 2 | 4 | 238.0 |
| line-3-0711-0606-s003579 | 6 | 2 | 4 | 238.0 |
| line-3-0885-0618-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Morogoro/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
