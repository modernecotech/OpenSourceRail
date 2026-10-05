# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 153 at depots = 195 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0216-1056-s000000 | line-1 | declared-depot | 45 | 2,677.5 | 8 |
| line-2-0101-0902-s000000 | line-2 | declared-depot | 46 | 2,737.0 | 9 |
| line-3-0905-0994-s025119 | line-3 | declared-depot | 62 | 3,689.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0216-1056-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0473-0901-s006670 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0901-s006670 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0831-s009691 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0831-s009691 | station | reverse | revenue | 1 |
| line-1 | line-1-0687-0772-s012230 | station | forward | revenue | 1 |
| line-1 | line-1-0687-0772-s012230 | station | reverse | revenue | 1 |
| line-1 | line-1-0796-0706-s015085 | station | forward | revenue | 1 |
| line-1 | line-1-0796-0706-s015085 | station | reverse | revenue | 1 |
| line-1 | line-1-0890-0663-s017936 | station | reverse | revenue | 2 |
| line-2 | line-2-0101-0902-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0233-0868-s003613 | station | forward | revenue | 1 |
| line-2 | line-2-0233-0868-s003613 | station | reverse | revenue | 1 |
| line-2 | line-2-0342-0787-s006617 | station | forward | revenue | 1 |
| line-2 | line-2-0342-0787-s006617 | station | reverse | revenue | 1 |
| line-2 | line-2-0450-0708-s009630 | station | forward | revenue | 1 |
| line-2 | line-2-0450-0708-s009630 | station | reverse | revenue | 1 |
| line-2 | line-2-0572-0618-s013033 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0618-s013033 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0548-s015654 | station | forward | revenue | 1 |
| line-2 | line-2-0665-0548-s015654 | station | reverse | revenue | 1 |
| line-2 | line-2-0789-0457-s019075 | station | reverse | revenue | 2 |
| line-3 | line-3-0197-0196-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0394-s007012 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0394-s007012 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0570-s011895 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0570-s011895 | station | reverse | revenue | 1 |
| line-3 | line-3-0572-0618-s013300 | station | forward | revenue | 1 |
| line-3 | line-3-0572-0618-s013300 | station | reverse | revenue | 1 |
| line-3 | line-3-0612-0673-s014897 | station | forward | revenue | 1 |
| line-3 | line-3-0612-0673-s014897 | station | reverse | revenue | 1 |
| line-3 | line-3-0687-0772-s017710 | station | forward | revenue | 1 |
| line-3 | line-3-0687-0772-s017710 | station | reverse | revenue | 1 |
| line-3 | line-3-0790-0909-s021408 | station | forward | revenue | 1 |
| line-3 | line-3-0790-0909-s021408 | station | reverse | revenue | 1 |
| line-3 | line-3-0905-0994-s025119 | station | reverse | revenue | 2 |
| line-1 | line-1-0216-1056-s000000 | depot | — | revenue | 39 |
| line-1 | line-1-0216-1056-s000000 | depot | — | spare | 5 |
| line-1 | line-1-0216-1056-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0101-0902-s000000 | depot | — | revenue | 40 |
| line-2 | line-2-0101-0902-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0101-0902-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0905-0994-s025119 | depot | — | revenue | 54 |
| line-3 | line-3-0905-0994-s025119 | depot | — | spare | 7 |
| line-3 | line-3-0905-0994-s025119 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/vientiane-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **195 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **175 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **153 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0216-1056-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0473-0901-s006670 | forward | revenue | 5 | pending |
| line-1 | line-1-0473-0901-s006670 | reverse | revenue | 5 | pending |
| line-1 | line-1-0588-0831-s009691 | forward | revenue | 5 | pending |
| line-1 | line-1-0588-0831-s009691 | reverse | revenue | 5 | pending |
| line-1 | line-1-0687-0772-s012230 | forward | revenue | 5 | pending |
| line-1 | line-1-0687-0772-s012230 | reverse | revenue | 5 | pending |
| line-1 | line-1-0796-0706-s015085 | forward | revenue | 5 | pending |
| line-1 | line-1-0796-0706-s015085 | reverse | revenue | 5 | pending |
| line-1 | line-1-0890-0663-s017936 | reverse | revenue | 5 | pending |
| line-1 | line-1-0473-0901-s006670 | forward | spare | 1 | pending |
| line-1 | line-1-0473-0901-s006670 | reverse | spare | 1 | pending |
| line-1 | line-1-0588-0831-s009691 | forward | spare | 1 | pending |
| line-1 | line-1-0588-0831-s009691 | reverse | spare | 1 | pending |
| line-1 | line-1-0687-0772-s012230 | forward | spare | 1 | pending |
| line-1 | line-1-0687-0772-s012230 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0101-0902-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0233-0868-s003613 | forward | revenue | 5 | pending |
| line-2 | line-2-0233-0868-s003613 | reverse | revenue | 5 | pending |
| line-2 | line-2-0342-0787-s006617 | forward | revenue | 5 | pending |
| line-2 | line-2-0342-0787-s006617 | reverse | revenue | 5 | pending |
| line-2 | line-2-0450-0708-s009630 | forward | revenue | 5 | pending |
| line-2 | line-2-0450-0708-s009630 | reverse | revenue | 4 | pending |
| line-2 | line-2-0572-0618-s013033 | forward | revenue | 4 | pending |
| line-2 | line-2-0572-0618-s013033 | reverse | revenue | 4 | pending |
| line-2 | line-2-0665-0548-s015654 | forward | revenue | 4 | pending |
| line-2 | line-2-0665-0548-s015654 | reverse | revenue | 4 | pending |
| line-2 | line-2-0789-0457-s019075 | reverse | revenue | 4 | pending |
| line-2 | line-2-0450-0708-s009630 | reverse | spare | 1 | pending |
| line-2 | line-2-0572-0618-s013033 | forward | spare | 1 | pending |
| line-2 | line-2-0572-0618-s013033 | reverse | spare | 1 | pending |
| line-2 | line-2-0665-0548-s015654 | forward | spare | 1 | pending |
| line-2 | line-2-0665-0548-s015654 | reverse | spare | 1 | pending |
| line-2 | line-2-0789-0457-s019075 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0197-0196-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0403-0394-s007012 | forward | revenue | 5 | pending |
| line-3 | line-3-0403-0394-s007012 | reverse | revenue | 5 | pending |
| line-3 | line-3-0535-0570-s011895 | forward | revenue | 5 | pending |
| line-3 | line-3-0535-0570-s011895 | reverse | revenue | 5 | pending |
| line-3 | line-3-0572-0618-s013300 | forward | revenue | 5 | pending |
| line-3 | line-3-0572-0618-s013300 | reverse | revenue | 5 | pending |
| line-3 | line-3-0612-0673-s014897 | forward | revenue | 5 | pending |
| line-3 | line-3-0612-0673-s014897 | reverse | revenue | 5 | pending |
| line-3 | line-3-0687-0772-s017710 | forward | revenue | 5 | pending |
| line-3 | line-3-0687-0772-s017710 | reverse | revenue | 5 | pending |
| line-3 | line-3-0790-0909-s021408 | forward | revenue | 5 | pending |
| line-3 | line-3-0790-0909-s021408 | reverse | revenue | 5 | pending |
| line-3 | line-3-0905-0994-s025119 | reverse | revenue | 5 | pending |
| line-3 | line-3-0197-0196-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0394-s007012 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0394-s007012 | reverse | spare | 1 | pending |
| line-3 | line-3-0535-0570-s011895 | forward | spare | 1 | pending |
| line-3 | line-3-0535-0570-s011895 | reverse | spare | 1 | pending |
| line-3 | line-3-0572-0618-s013300 | forward | spare | 1 | pending |
| line-3 | line-3-0572-0618-s013300 | reverse | spare | 1 | pending |
| line-3 | line-3-0612-0673-s014897 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**145 trainsets exceed the reference platform envelope**, requiring **8,627.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0216-1056-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0473-0901-s006670 | 12 | 2 | 10 | 595.0 |
| line-1-0588-0831-s009691 | 12 | 2 | 10 | 595.0 |
| line-1-0687-0772-s012230 | 12 | 4 | 8 | 476.0 |
| line-1-0796-0706-s015085 | 10 | 2 | 8 | 476.0 |
| line-1-0890-0663-s017936 | 5 | 2 | 3 | 178.5 |
| line-2-0101-0902-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0233-0868-s003613 | 10 | 2 | 8 | 476.0 |
| line-2-0342-0787-s006617 | 10 | 2 | 8 | 476.0 |
| line-2-0450-0708-s009630 | 10 | 2 | 8 | 476.0 |
| line-2-0572-0618-s013033 | 10 | 4 | 6 | 357.0 |
| line-2-0665-0548-s015654 | 10 | 2 | 8 | 476.0 |
| line-2-0789-0457-s019075 | 5 | 2 | 3 | 178.5 |
| line-3-0197-0196-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0403-0394-s007012 | 12 | 2 | 10 | 595.0 |
| line-3-0535-0570-s011895 | 12 | 2 | 10 | 595.0 |
| line-3-0572-0618-s013300 | 12 | 4 | 8 | 476.0 |
| line-3-0612-0673-s014897 | 11 | 2 | 9 | 535.5 |
| line-3-0687-0772-s017710 | 10 | 4 | 6 | 357.0 |
| line-3-0790-0909-s021408 | 10 | 2 | 8 | 476.0 |
| line-3-0905-0994-s025119 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/southeast-asia/Laos/Vientiane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
