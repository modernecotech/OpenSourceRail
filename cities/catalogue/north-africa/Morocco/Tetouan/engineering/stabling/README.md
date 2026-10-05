# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 118 at depots = 148 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0584-0314-s000000 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0929-0303-s019780 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0393-0182-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0316-0975-s016053 | station | reverse | revenue | 2 |
| line-1 | line-1-0382-0871-s012977 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0871-s012977 | station | reverse | revenue | 1 |
| line-1 | line-1-0443-0702-s009034 | station | forward | revenue | 1 |
| line-1 | line-1-0443-0702-s009034 | station | reverse | revenue | 1 |
| line-1 | line-1-0490-0572-s006021 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0572-s006021 | station | reverse | revenue | 1 |
| line-1 | line-1-0537-0443-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0537-0443-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0584-0314-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0327-0929-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0548-0727-s007017 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0727-s007017 | station | reverse | revenue | 1 |
| line-2 | line-2-0636-0625-s010032 | station | forward | revenue | 1 |
| line-2 | line-2-0636-0625-s010032 | station | reverse | revenue | 1 |
| line-2 | line-2-0722-0523-s013042 | station | forward | revenue | 1 |
| line-2 | line-2-0722-0523-s013042 | station | reverse | revenue | 1 |
| line-2 | line-2-0929-0303-s019780 | station | reverse | revenue | 2 |
| line-3 | line-3-0393-0182-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0516-0432-s006160 | station | forward | revenue | 1 |
| line-3 | line-3-0516-0432-s006160 | station | reverse | revenue | 1 |
| line-3 | line-3-0576-0548-s009047 | station | forward | revenue | 1 |
| line-3 | line-3-0576-0548-s009047 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0656-s011733 | station | reverse | revenue | 2 |
| line-1 | line-1-0584-0314-s000000 | depot | — | revenue | 34 |
| line-1 | line-1-0584-0314-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0584-0314-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0929-0303-s019780 | depot | — | revenue | 45 |
| line-2 | line-2-0929-0303-s019780 | depot | — | spare | 5 |
| line-2 | line-2-0929-0303-s019780 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0393-0182-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0393-0182-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0393-0182-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tetouan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **148 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **133 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **118 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0584-0314-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0537-0443-s003005 | forward | revenue | 5 | pending |
| line-1 | line-1-0537-0443-s003005 | reverse | revenue | 5 | pending |
| line-1 | line-1-0490-0572-s006021 | forward | revenue | 5 | pending |
| line-1 | line-1-0490-0572-s006021 | reverse | revenue | 5 | pending |
| line-1 | line-1-0443-0702-s009034 | forward | revenue | 5 | pending |
| line-1 | line-1-0443-0702-s009034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0382-0871-s012977 | forward | revenue | 4 | pending |
| line-1 | line-1-0382-0871-s012977 | reverse | revenue | 4 | pending |
| line-1 | line-1-0316-0975-s016053 | reverse | revenue | 4 | pending |
| line-1 | line-1-0443-0702-s009034 | reverse | spare | 1 | pending |
| line-1 | line-1-0382-0871-s012977 | forward | spare | 1 | pending |
| line-1 | line-1-0382-0871-s012977 | reverse | spare | 1 | pending |
| line-1 | line-1-0316-0975-s016053 | reverse | spare | 1 | pending |
| line-1 | line-1-0584-0314-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0327-0929-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0548-0727-s007017 | forward | revenue | 7 | pending |
| line-2 | line-2-0548-0727-s007017 | reverse | revenue | 7 | pending |
| line-2 | line-2-0636-0625-s010032 | forward | revenue | 7 | pending |
| line-2 | line-2-0636-0625-s010032 | reverse | revenue | 7 | pending |
| line-2 | line-2-0722-0523-s013042 | forward | revenue | 7 | pending |
| line-2 | line-2-0722-0523-s013042 | reverse | revenue | 7 | pending |
| line-2 | line-2-0929-0303-s019780 | reverse | revenue | 6 | pending |
| line-2 | line-2-0929-0303-s019780 | reverse | spare | 1 | pending |
| line-2 | line-2-0327-0929-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0727-s007017 | forward | spare | 1 | pending |
| line-2 | line-2-0548-0727-s007017 | reverse | spare | 1 | pending |
| line-2 | line-2-0636-0625-s010032 | forward | spare | 1 | pending |
| line-2 | line-2-0636-0625-s010032 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0393-0182-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0516-0432-s006160 | forward | revenue | 6 | pending |
| line-3 | line-3-0516-0432-s006160 | reverse | revenue | 5 | pending |
| line-3 | line-3-0576-0548-s009047 | forward | revenue | 5 | pending |
| line-3 | line-3-0576-0548-s009047 | reverse | revenue | 5 | pending |
| line-3 | line-3-0631-0656-s011733 | reverse | revenue | 5 | pending |
| line-3 | line-3-0516-0432-s006160 | reverse | spare | 1 | pending |
| line-3 | line-3-0576-0548-s009047 | forward | spare | 1 | pending |
| line-3 | line-3-0576-0548-s009047 | reverse | spare | 1 | pending |
| line-3 | line-3-0631-0656-s011733 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**112 trainsets exceed the reference platform envelope**, requiring **6,664.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0975-s016053 | 5 | 2 | 3 | 178.5 |
| line-1-0382-0871-s012977 | 10 | 2 | 8 | 476.0 |
| line-1-0443-0702-s009034 | 10 | 2 | 8 | 476.0 |
| line-1-0490-0572-s006021 | 10 | 2 | 8 | 476.0 |
| line-1-0537-0443-s003005 | 10 | 4 | 6 | 357.0 |
| line-1-0584-0314-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0327-0929-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0548-0727-s007017 | 16 | 2 | 14 | 833.0 |
| line-2-0636-0625-s010032 | 16 | 4 | 12 | 714.0 |
| line-2-0722-0523-s013042 | 14 | 2 | 12 | 714.0 |
| line-2-0929-0303-s019780 | 7 | 2 | 5 | 297.5 |
| line-3-0393-0182-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0516-0432-s006160 | 12 | 4 | 8 | 476.0 |
| line-3-0576-0548-s009047 | 12 | 2 | 10 | 595.0 |
| line-3-0631-0656-s011733 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Tetouan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
