# Station and depot overnight allocation

Plan: **50 trainsets at stations + 84 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0548-0120-s018987 | line-1 | storage-at-existing-powered-service-point | 22 | 1,309.0 | 0 |
| line-2-0804-0434-s021286 | line-2 | storage-at-existing-powered-service-point | 30 | 1,785.0 | 0 |
| line-3-0729-0230-s022764 | line-3 | declared-depot | 32 | 1,904.0 | 21 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0283-0726-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0362-0640-s003001 | station | forward | revenue | 1 |
| line-1 | line-1-0362-0640-s003001 | station | reverse | revenue | 1 |
| line-1 | line-1-0462-0570-s006028 | station | forward | revenue | 1 |
| line-1 | line-1-0462-0570-s006028 | station | reverse | revenue | 1 |
| line-1 | line-1-0506-0376-s012055 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0376-s012055 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0533-s007802 | station | forward | revenue | 1 |
| line-1 | line-1-0531-0533-s007802 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0120-s018987 | station | reverse | revenue | 2 |
| line-1 | line-1-0557-0496-s009036 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0496-s009036 | station | reverse | revenue | 1 |
| line-1 | line-1-0569-0240-s015785 | station | forward | revenue | 1 |
| line-1 | line-1-0569-0240-s015785 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0176-s017374 | station | forward | revenue | 1 |
| line-1 | line-1-0582-0176-s017374 | station | reverse | revenue | 1 |
| line-2 | line-2-0000-0301-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0134-0317-s003125 | station | forward | revenue | 1 |
| line-2 | line-2-0134-0317-s003125 | station | reverse | revenue | 1 |
| line-2 | line-2-0277-0406-s006757 | station | forward | revenue | 1 |
| line-2 | line-2-0277-0406-s006757 | station | reverse | revenue | 1 |
| line-2 | line-2-0399-0459-s009769 | station | forward | revenue | 1 |
| line-2 | line-2-0399-0459-s009769 | station | reverse | revenue | 1 |
| line-2 | line-2-0531-0533-s013133 | station | forward | revenue | 1 |
| line-2 | line-2-0531-0533-s013133 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0556-s015786 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0556-s015786 | station | reverse | revenue | 1 |
| line-2 | line-2-0752-0514-s018787 | station | forward | revenue | 1 |
| line-2 | line-2-0752-0514-s018787 | station | reverse | revenue | 1 |
| line-2 | line-2-0804-0434-s021286 | station | reverse | revenue | 2 |
| line-3 | line-3-0259-1031-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0363-0788-s007018 | station | forward | revenue | 1 |
| line-3 | line-3-0363-0788-s007018 | station | reverse | revenue | 1 |
| line-3 | line-3-0461-0682-s010032 | station | forward | revenue | 1 |
| line-3 | line-3-0461-0682-s010032 | station | reverse | revenue | 1 |
| line-3 | line-3-0529-0614-s012025 | station | forward | revenue | 1 |
| line-3 | line-3-0529-0614-s012025 | station | reverse | revenue | 1 |
| line-3 | line-3-0531-0533-s014028 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0533-s014028 | station | reverse | revenue | 1 |
| line-3 | line-3-0602-0496-s016053 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0496-s016053 | station | reverse | revenue | 1 |
| line-3 | line-3-0678-0391-s019072 | station | forward | revenue | 1 |
| line-3 | line-3-0678-0391-s019072 | station | reverse | revenue | 1 |
| line-3 | line-3-0729-0230-s022764 | station | reverse | revenue | 2 |
| line-1 | line-1-0548-0120-s018987 | depot | — | revenue | 18 |
| line-1 | line-1-0548-0120-s018987 | depot | — | spare | 3 |
| line-1 | line-1-0548-0120-s018987 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0804-0434-s021286 | depot | — | revenue | 25 |
| line-2 | line-2-0804-0434-s021286 | depot | — | spare | 4 |
| line-2 | line-2-0804-0434-s021286 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0729-0230-s022764 | depot | — | revenue | 27 |
| line-3 | line-3-0729-0230-s022764 | depot | — | spare | 4 |
| line-3 | line-3-0729-0230-s022764 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tabuk-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 25 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **84 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0283-0726-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0362-0640-s003001 | forward | revenue | 3 | pending |
| line-1 | line-1-0362-0640-s003001 | reverse | revenue | 3 | pending |
| line-1 | line-1-0462-0570-s006028 | forward | revenue | 3 | pending |
| line-1 | line-1-0462-0570-s006028 | reverse | revenue | 2 | pending |
| line-1 | line-1-0531-0533-s007802 | forward | revenue | 2 | pending |
| line-1 | line-1-0531-0533-s007802 | reverse | revenue | 2 | pending |
| line-1 | line-1-0557-0496-s009036 | forward | revenue | 2 | pending |
| line-1 | line-1-0557-0496-s009036 | reverse | revenue | 2 | pending |
| line-1 | line-1-0506-0376-s012055 | forward | revenue | 2 | pending |
| line-1 | line-1-0506-0376-s012055 | reverse | revenue | 2 | pending |
| line-1 | line-1-0569-0240-s015785 | forward | revenue | 2 | pending |
| line-1 | line-1-0569-0240-s015785 | reverse | revenue | 2 | pending |
| line-1 | line-1-0582-0176-s017374 | forward | revenue | 2 | pending |
| line-1 | line-1-0582-0176-s017374 | reverse | revenue | 2 | pending |
| line-1 | line-1-0548-0120-s018987 | reverse | revenue | 2 | pending |
| line-1 | line-1-0462-0570-s006028 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0533-s007802 | forward | spare | 1 | pending |
| line-1 | line-1-0531-0533-s007802 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0496-s009036 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0134-0317-s003125 | forward | revenue | 3 | pending |
| line-2 | line-2-0134-0317-s003125 | reverse | revenue | 3 | pending |
| line-2 | line-2-0277-0406-s006757 | forward | revenue | 3 | pending |
| line-2 | line-2-0277-0406-s006757 | reverse | revenue | 3 | pending |
| line-2 | line-2-0399-0459-s009769 | forward | revenue | 3 | pending |
| line-2 | line-2-0399-0459-s009769 | reverse | revenue | 3 | pending |
| line-2 | line-2-0531-0533-s013133 | forward | revenue | 3 | pending |
| line-2 | line-2-0531-0533-s013133 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0556-s015786 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0556-s015786 | reverse | revenue | 3 | pending |
| line-2 | line-2-0752-0514-s018787 | forward | revenue | 3 | pending |
| line-2 | line-2-0752-0514-s018787 | reverse | revenue | 3 | pending |
| line-2 | line-2-0804-0434-s021286 | reverse | revenue | 2 | pending |
| line-2 | line-2-0804-0434-s021286 | reverse | spare | 1 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003125 | forward | spare | 1 | pending |
| line-2 | line-2-0134-0317-s003125 | reverse | spare | 1 | pending |
| line-2 | line-2-0277-0406-s006757 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0259-1031-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0363-0788-s007018 | forward | revenue | 3 | pending |
| line-3 | line-3-0363-0788-s007018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0461-0682-s010032 | forward | revenue | 3 | pending |
| line-3 | line-3-0461-0682-s010032 | reverse | revenue | 3 | pending |
| line-3 | line-3-0529-0614-s012025 | forward | revenue | 3 | pending |
| line-3 | line-3-0529-0614-s012025 | reverse | revenue | 3 | pending |
| line-3 | line-3-0531-0533-s014028 | forward | revenue | 3 | pending |
| line-3 | line-3-0531-0533-s014028 | reverse | revenue | 3 | pending |
| line-3 | line-3-0602-0496-s016053 | forward | revenue | 3 | pending |
| line-3 | line-3-0602-0496-s016053 | reverse | revenue | 3 | pending |
| line-3 | line-3-0678-0391-s019072 | forward | revenue | 3 | pending |
| line-3 | line-3-0678-0391-s019072 | reverse | revenue | 3 | pending |
| line-3 | line-3-0729-0230-s022764 | reverse | revenue | 3 | pending |
| line-3 | line-3-0363-0788-s007018 | forward | spare | 1 | pending |
| line-3 | line-3-0363-0788-s007018 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0682-s010032 | forward | spare | 1 | pending |
| line-3 | line-3-0461-0682-s010032 | reverse | spare | 1 | pending |
| line-3 | line-3-0529-0614-s012025 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**78 trainsets exceed the reference platform envelope**, requiring **4,641.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0283-0726-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0362-0640-s003001 | 6 | 2 | 4 | 238.0 |
| line-1-0462-0570-s006028 | 6 | 2 | 4 | 238.0 |
| line-1-0506-0376-s012055 | 4 | 2 | 2 | 119.0 |
| line-1-0531-0533-s007802 | 6 | 4 | 2 | 119.0 |
| line-1-0548-0120-s018987 | 2 | 2 | 0 | 0.0 |
| line-1-0557-0496-s009036 | 5 | 2 | 3 | 178.5 |
| line-1-0569-0240-s015785 | 4 | 2 | 2 | 119.0 |
| line-1-0582-0176-s017374 | 4 | 2 | 2 | 119.0 |
| line-2-0000-0301-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0134-0317-s003125 | 8 | 2 | 6 | 357.0 |
| line-2-0277-0406-s006757 | 7 | 2 | 5 | 297.5 |
| line-2-0399-0459-s009769 | 6 | 2 | 4 | 238.0 |
| line-2-0531-0533-s013133 | 6 | 4 | 2 | 119.0 |
| line-2-0626-0556-s015786 | 6 | 2 | 4 | 238.0 |
| line-2-0752-0514-s018787 | 6 | 2 | 4 | 238.0 |
| line-2-0804-0434-s021286 | 3 | 2 | 1 | 59.5 |
| line-3-0259-1031-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0363-0788-s007018 | 8 | 2 | 6 | 357.0 |
| line-3-0461-0682-s010032 | 8 | 2 | 6 | 357.0 |
| line-3-0529-0614-s012025 | 7 | 2 | 5 | 297.5 |
| line-3-0531-0533-s014028 | 6 | 4 | 2 | 119.0 |
| line-3-0602-0496-s016053 | 6 | 2 | 4 | 238.0 |
| line-3-0678-0391-s019072 | 6 | 2 | 4 | 238.0 |
| line-3-0729-0230-s022764 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Tabuk/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
