# Airport vehicle mass, stopping and fit review

The six-car steel calculation carries 700 passengers. Loaded mass is **165.836, 198.636 and 246.036 t** in the low, central and high planning cases. The largest static axle load in those cases is **7.019, 8.707 and 11.214 t**. These figures include gross frame stock, installed equipment allowances and payload. The issue has an unweighed installed bill of materials. The audit retains original BOM quantities and datums, uses separate mass groups with study centroids, and shows the signs and balance of the per-axle reactions. Off-axis load and installed quantities need measurement. [Vehicle and span calculation](vehicle_civil.py) · [Released steel BOM](../prototype/vehicle-factory/installed-fitout-bom.csv) · [Weighing instructions](../prototype/weight-guide.md)

## Independent stop from 72 km/h

This sensitivity uses a 2% descent, two seconds of coast and a 0.60 m/s² net stop. The fault case has no wheel braking, no regeneration and one unavailable rail module. Eleven active modules share the demand.

| Six-car steel load | Force per active module | Rail and shoe energy per active module | Peak rail interface power per active module | Stop at 14.6 kN per active module |
| --- | ---: | ---: | ---: | ---: |
| Central | 14.38 kN | 1.384 kWh | 293 kW | 379.9 m |
| High | 17.81 kN | 1.714 kWh | 363 kW | 495.7 m |

The stated net target needs 386.9 m including the two-second coast. The older **14.6 kN** figure is a rounded required force at a different crowd-mass basis. Holding that number constant increases the high-load stop by 108.8 m. At 1.0 m/s² net, the distance falls to 248.3 m, and one-out independent module demands rise to 21.60 and 26.75 kN. The unchanged service force corresponding to 0.60 m/s² on level track gives a longer downgrade stop. Wheel-braked cases constrain force by static load and adhesion and include loss of the heaviest axle. Authenticated force curves, response time, failed-channel behaviour, thermal fade, rail damage and battery excitation energy remain open. The constant-force calculation reports frictional heat shared by shoe and rail. The heat split, repetition limit and cooling are equipment properties. [Vehicle planning duty](../../VEHICLE.md) · [Level-track brake input](../mechanical/vehicle/section-trial.toml)

Supply a surveyed **front-to-protected-limit** distance and withheld overlap together to calculate stopping margin. The report also gives stop distance plus train length and overlap as an illustrative spatial separation. Establish block occupancy, turnout and tail-release limits with signalling and the actual alignment. Interstation distance and diagrammed blocks provide no protection limit.

## Traction, support and boarding

The selected vehicle has four driven axles per car. The traction comparison tests driving the forward pair, the rear pair and both bogies, then loses the heaviest driven axle in each arrangement. The force margin retains the system's 0.10 adhesion, resistance and reserve. On a 2% upgrade the combined duty requires 95.71% of static axle load on powered axles. Losing the heaviest driven axle leaves 95.62% centrally and 95.44% in the high case. This consumes the declared reserve in both cases. Request hot tractive effort versus speed, driven axle assignments and the converter fault split. [Local traction inputs](../../system.toml)

The independent 65 kWh service battery has 52.0 kWh usable when new against a 50.4 kWh request. At 80% retained capacity, usable energy falls to 41.6 kWh. At the same usable fraction, the minimum nominal capacity is 78.75 kWh before electrical power, hot degradation and integration are assessed.

The 156 mm nominal secondary-seat gap leaves +11, +1 and −9 mm before shims and tolerances for the three trial stacks. The 0.6 kN/mm spring consumes 40.2 mm of a provisional 40 mm payload stroke in the central case and 55.0 mm in the high case. The stock door allocation has 10 mm margin and 2 mm when loaded distortion doubles. The 75 mm static horizontal platform gap needs a boarding survey across actual wear, suspension and stopping poses. The bogie paths retain the bare-stock swept boxes and rigid transforms for both ends. Verify the equipped paths with tooling, lifting, restraint, cables and hoses. The alternative body materials inherit none of the steel fitted results. [Fitout and exchange procedure](../prototype/fitout-guide.md) · [Installed arrangement](../prototype/vehicle-factory/installed-ga.json)

## Reproduce or attach a return

```sh
python3 -m cities.Baghdad.engineering.simulation.vehicle_audit > build/vehicle-audit.json
python3 -m unittest cities.Baghdad.engineering.simulation.test_vehicle_audit
```

The output includes a physical candidate ID, duty ID, evaluation ID and source digests. A new load, grade, block assumption or source revision requires its own evaluation. Use the `return_template` as a separate local JSON file. Set `kind` to `supplier-declaration`, `physical-measurement` or `synthetic-fixture`. Under `documents`, record original local filenames with issuer, date and SHA-256. Under `returns`, name the evidence scope and cite the document, article serial, procedure revision and witness. Give the file to `--evidence-return`. The audit checks scope, identity and attachment integrity. Independent review still needs to authenticate instruments and witnesses, approve limits and determine whether the results meet them. Use the existing weighed-train intake for mass recalculation.
