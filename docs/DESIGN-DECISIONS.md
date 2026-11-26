# Current railway design decisions

Use one configuration when assessing route length, service, vehicle loads, supply, civil stock, construction and costs. Project preferences include local production, repairability, elevated construction in Baghdad and catenary-free operation where feasible. Passenger protection, stopping, accessible boarding, evacuation and structural integrity are engineering obligations. [Requirements policy](../engineering/design_search/requirement_policy.py) · [Standards and evidence](certification/README.md)

## Current Baghdad configuration

| Decision | Engineering basis | Work needed before purchase |
|---|---|---|
| Network and access | Three rings and four cross-Tigris trunks form the Baghdad planning default. All three named suburbs can board a through train. The broader two-ring benchmark reaches more residents within the 1.3 km street-walk limit. [Network and passenger evidence](../cities/Baghdad/METROPOLITAN-NETWORK.md) | Verify corridor rights, station access, demand and degraded service. Use the [route-edit comparison](../cities/Baghdad/THREE-RING-STUDY.md) to test changes. |
| Viaduct and logistics | Recurring **20 m U-girders on shared piers**, paired curved pieces and separate closure or special structures. Terminal yards feed the two advancing erection fronts where the finished deck can carry the temporary loads. [Stock and construction basis](../cities/Baghdad/engineering/mechanical/civil/LIVE-STOCK.md) | Verify girder, bearings, soil and footing designs under governing service and temporary actions. Demonstrate the loaded flatbed, gantry, pick, deck extension and access. Price river spans and interfaces separately. |
| Train and power | The metropolitan planning offer uses a six-car powered-wheel train and protected conductor supply. The Airport case assesses service, loading, power and protection on a separate route. [Vehicle](../cities/Baghdad/VEHICLE.md) · [Airport digital reference](../cities/Baghdad/engineering/simulation/PROJECT-REFERENCE.md) | Match the installed mass, moving current, thermal duty, protection, safe isolation and degraded service to equipment and measured inputs. |
| Stopping, accessibility and controls | Apply route-specific stopping, berth, door, traction interlock and rescue cases. [Station bench](../cities/Baghdad/engineering/controls/STATION-BENCH.md) · [Passenger and emergency-load checks](../cities/Baghdad/engineering/simulation/passenger-guide.md) | Measure braking response, body movement, clearances and hot-weather essential power. Verify wayside functions and independent protection with the selected train, stations and interfaces. |
| Local industrial delivery and value | Use priced civil quantities, shifts, fleet and renewals for the same network. [Delivery and costs](../cities/Baghdad/METROPOLITAN-DELIVERY.md) · [Matched supplier scope](../cities/Baghdad/BUYER-COMPARISON.md) | Request witnessed output, loaded shifts, renewal prices, supplier origin and local inspection and repair methods. Reprice construction and cash when the design or programme changes. |

## Maintain the design record

Enter specification changes in their controlling source. Recalculate dependent quantities and source-bound reports. The fast coherence check reads current specs, implementations and published values across the declared live scope. The detailed evaluators remain the source for engineering and cost results.

```sh
./osr coherence
./osr design railway baghdad-network --check
```

A priced design screen supports planning and enquiry. Fabrication release and passenger operation require their own physical evidence and independent acceptance. [Evidence and release rules](../AGENTS.md)
