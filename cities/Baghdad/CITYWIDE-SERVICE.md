# Baghdad citywide operating decision

Use the fourteen connected main routes for network planning. Keep the airport extension on M05. Defer passenger service on the five access sections below. The published citywide capital retains every section. Baghdad’s operator and funding authority still need to adopt the service and approve the physical sites.

| Costed and operated scope | Route-km |
|---|---:|
| Connected passenger routes | 552.562 |
| Five deferred access sections | 2.990 |
| Six reserved links and infill sections | 50.099 |
| Full costed guideway | 605.652 |

| Original group | Deferred section | Costed km | Where it reaches its main line |
|---|---|---:|---|
| M04 | B-A02 | 0.427 | 2,323 m from its nearest point |
| M04 | B-A03 | 0.571 | 2,710 m from its nearest point |
| M09 | B-A04 | 0.111 | Touches the interior on the schematic map |
| M01 | B-A05 | 0.499 | Touches the interior on the schematic map |
| M02 | B-A06 | 1.382 | Touches the interior on the schematic map |

M01 and M02 omit the Jadriya access branches. M04 omits both Sadr City branches. M09 circulates around the ring in both directions and omits the eastern spur. Confirm entrances, transfers, accessible paths and junction geometry in the field. Survey both M04 gaps before pricing links across them.

## Two service offers

| Operating day | Published peak offer | Clockface test |
|---|---:|---:|
| Shortest scheduled headway | 150 s | 30 min |
| Places/hour/direction | 16,800 | 1,400 |
| Passenger workings/day | 6,384 | 1,008 |
| Passenger train-km/year | 91,968,471 | 14,521,338 |
| Working trainsets | 725 | 70 |
| Separate staging movements, train-km/year | Outside original ledger | 12,775 |

The original full proposal assigns 51.97m train-km to connected workings and 40.50m to unresolved paths. The fourteen-route peak offer drops 497,724 annual train-km. Its 150-second peak needs shorter signalling blocks and additional terminal capacity. The existing cost includes 934 sets, with 122 above the budgeted active fleet.

The clockface case keeps the six-car, 700-place train and provides one directional block between each pair of stops. Each line end has one exclusive throat, one face and a local staging lead. M09 has a separate lap face and lead per direction. Each train starts from and returns to a local staging area. The two directions finish the day with their initial stock counts.

At 15 and 20 minutes, the evaluated departure phases could not clear every shared junction. The 30-minute option clears all 38 shared map hints in the model. The smallest clear intervals are 1068 s between directional block occupations, 1361 s at a platform face and 150 s at a throat. Passenger transfers need a separate walking and accessibility survey.

| Group | Terminal stops or lap | One-way km | Run min | Working sets | First origin phase, s after 06:00 |
|---|---|---:|---:|---:|---:|
| M01 | M-001 → M-017 | 48.86 | 87.0 | 6 | 615 |
| M02 | M-032 → M-045 | 52.59 | 87.0 | 6 | 885 |
| M03 | M-046 → M-061 | 49.28 | 87.0 | 6 | 0 |
| M04 | M-062 → M-073 | 41.70 | 72.0 | 5 | 510 |
| M05 | airport-terminal → M-089 | 50.16 | 87.0 | 6 | 585 |
| M06 | M-090 → M-105 | 52.26 | 87.0 | 6 | 0 |
| M07 | M-106 → M-118 | 39.74 | 72.0 | 5 | 0 |
| M08 | M-119 → M-133 | 47.92 | 87.0 | 6 | 1065 |
| M09 | M-134 → M-134-lap | 97.19 | 177.0 | 12 | 0 |
| M10 | M-160 → M-168 | 12.04 | 27.0 | 2 | 0 |
| M11 | M-169 → M-175 | 10.02 | 27.0 | 2 | 0 |
| M12 | M-187 → M-200 | 21.50 | 42.0 | 3 | 0 |
| M13 | M-201 → M-209 | 12.68 | 27.0 | 2 | 0 |
| M14 | M-210 → M-220 | 16.63 | 42.0 | 3 | 0 |

Each direction departs for 18 hours. The second origin has its own offset in the record. The model places a 35-second dwell at each intermediate call, reserves three minutes at turns and books 10 km/h terminal approach and departure movements with a full stop at the clear side of each throat. It allows for the 104.5 m train tail and route release. Running time covers acceleration at 0.60 m/s² net, the 72 km/h cap and a 0.60 m/s² level brake reduced by 2% downhill gravity. Survey gradients and curves, then verify tractive effort, adhesion, braking and the signal overlap at the measured train weight.

On M05, markers M-075 and M-076 are 104.27 m apart. The clockface case uses M-076 for a single call serving these adjacent markers. Check actual sightlines, entrances, luggage and wheelchair access at the site. The earlier peak comparison retains both calls.

## Money and equipment

The central Iraqi estimate retains **$32.995bn** of full-network capital. The fourteen-route peak offer has **$736.4m/year** of estimated operations. The clockface case prices **$386.2m/year** for existing scopes, keeping common staffing, stations, fleet and conductor maintenance while scaling purchased electricity and net variable train costs by passenger and yard kilometres. Its incremental site works and upkeep await quotations.

The operating trial needs 28 faces and 28 dedicated 250 m leads, with overnight space for 70 working sets. Check how these facilities connect to the 12 budgeted depots. The investment ledger includes 280 station allowances and 100 traction supply sites. The protected conductor feeds the train continuously. The 65 kWh service battery supports independent essential loads. Verify citywide feed outages, repeated braking heat, isolation and recovery against the local timetable. The 12 km Airport feeder result belongs to its own design.

Fare income at the reduced frequency requires directional counts, passenger response and paid journeys. The phased seven-line funding scenario belongs to the first programme. Citywide construction draws, funded price and opening dates require an owner programme.

## Operator and buyer records

Export one group’s complete train movements and station times. Times are local seconds after midnight and may extend into the following day. Open the [machine record](citywide-service.json) for section identities, scenarios, stop patterns, stock positions and phase searches.

```sh
python3 -m cities.Baghdad.citywide_service --check
python3 -m cities.Baghdad.citywide_service --events M05 > build/m05-workings.csv
python3 -m cities.Baghdad.citywide_service --return-template > build/citywide-return.json
python3 -m cities.Baghdad.citywide_service --assess-return build/citywide-return.json
```

Place attachments beside the return file. A peak return records passengers on a named load section across one full hour, direction A_to_B or B_to_A, the local observation period, evidence filename and SHA-256. The result reports remaining capacity for that observed hour. Each review document takes a file and SHA-256. Local checks establish file integrity. Acceptance requires independent authentication, complete demand by direction, physical measurements, supplier scope review and an owner decision.
