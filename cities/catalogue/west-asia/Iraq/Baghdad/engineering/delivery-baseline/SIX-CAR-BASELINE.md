# Baghdad controlled six-car planning product

Configuration **M6-A-DRAFT**, family metro-6car, covers **831 consists / 4986 cars** at 111 m, 204 t controlled tare, 720 passengers / 960 crush, 1,350 kWh gross / 1,080 usable battery, 675 V nominal and 50 C HVAC ambient. [Family BOM](six-car-bom.csv) and [interface/qualification register](six-car.json) are separate from LM3's detailed 120-product manufacturing reference. Every quote, supplier part, mass evidence, production BOM and acceptance remains null/unaccepted. Common architectural ideas do not grant six-car applicability.

| Six-car cost/mass category | Count / unit | Mass kg/consist | Allocated USD/consist |
| --- | --- | --- | --- |
| M6-carbody-structure | 6 car | 78,000 | 420,000 |
| M6-bogie-running-gear | 12 bogie | 45,000 | 300,000 |
| M6-traction-controls | 12 controller | 13,200 | 180,000 |
| M6-battery-modules | 6 225 kWh gross module | 8,700 | 270,000 |
| M6-interior-doors-glazing | 6 car kit | 42,000 | 240,000 |
| M6-thermal-roof-services | 6 car kit | 12,000 | 90,000 |
| M6-trainline-couplers | 1 six-car system | 1,500 | 70,000 |
| M6-assembly-qa-logistics | 1 consist | 0 | 110,000 |

Cost allocations sum to the existing **USD 1,680,000/train**. These are a control allocation of the price ceiling, not supplier estimates. The category mass subtotal is 200,400 kg and unallocated controlled-tare reserve 3,600 kg; no weighed closure is claimed. There are 24 reference axles: average tare load 8.50 t and crush load 11.50 t using an explicit 75 kg/passenger assumption. Individual axle/bogie imbalance, payload distribution and structural limits require calculations and weighing. The system schedule has 24 door cassettes and 36 window cassettes. Five inter-car interfaces, trainline/brake propagation, accessible platform/door interfaces, redundant controls, HV/charging, thermal/fire/EMC/harness interfaces each carry an acceptance requirement.

[Labour routes](six-car-labour-routing.csv) use the actual Baghdad factory stages, reference crew and cycle days. None is a measured six-car cycle. Rework, supplier queues and the 2.71% test-path margin need trials; scaling an LM3 cycle is not evidence. Factory production payroll stays within train procurement, separate from railway operating payroll and factory capital. Work Order / Job Card references remain null until production BOMs, method revisions, calibrated tools, qualified operators and independent inspections exist.

The first-article qualification work breakdown has a **USD 12.0m unquoted reference**. Its incremental funding is null because overlap with the factory's USD 20.0m design/training/qualification allowance remains unresolved. No automatic extra qualification or train premium is added. Supplier quotes, a detailed child-part BOM, structural/braking/trainline/thermal testing, acceptance labour and series-release authority must replace the planning controls before manufacture.
