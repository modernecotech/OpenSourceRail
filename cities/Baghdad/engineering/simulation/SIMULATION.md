# Reproducing the 12 km Airport simulation

For the revised 17.46 km horizontal alignment, its timetable, outage cases and supplier enquiry, start with the [current design audit](AUDIT-RESULTS.md). The figures below reproduce the earlier six-stop schematic.

Open the Airport simulation from the main Workbench to change the service, train, electricity supply, span or weather. The local server recalculates a case and exports its vehicle, service, passenger, production and cash records in one ZIP. Opening the simulation page directly from disk gives access to 15 precomputed comparisons. The export contains a scenario-specific IFC layout and planning schedules under `candidate/`. These carry the selected train dimensions, spans, supply sites, workcells, quantities and procurement lots. The parent enquiry inside the export retains its original car and civil drawings. A three-car formation or a different span needs its own released drawings. [Interactive Workbench](index.html) · [Ten engineering assignments and acceptance conditions](PLAN.md)

## A journey through the model

The published parent is the 12 km, six-stop proposal with six six-car steel sets and 30 protected-conductor supply sites. Its procurement estimate is $1,124.32 million. The simulation distributes the parent's 4.015 million annual journeys, including 3.694 million paid journeys, across hours, stops and directions. The busiest central-demand leg at 15-minute headways carries an estimated 103 passengers. Passenger counts and stop access still need surveys. In particular, the sequence of the five mapped area centroids spans at least 15.09 km even before the missing station is located. A 12 km railway cannot serve those five centroids in that order. The earlier schematic retains its chainages for reproduction.

The central equipped mass estimate gives 146.14 t tare and 198.64 t fully loaded. The motion solver adjusts payload by leg. Cooling demand uses peak onboard occupancy rounded up to a whole passenger and capped at vehicle capacity. Waiting passengers remain in the boarding model. The headway and doorway assessment set the dwell allowance. The default service day has about 11,000.6 requested journeys. About 10,977.4 complete and 23.2 arrive after the final boarding opportunity. These end-of-day passengers reduce fare receipts separately from capacity-related denials. The motion solver then updates position, speed, available electrical power, energy, block occupancy and lateness. A constant grade tests a vertical-profile hypothesis on the unsurveyed alignment. [Passenger circulation and climate](passenger-guide.md) · [Motion, DC network and external checks](MOTION-POWER.md)

| Same 15-minute service at 40°C | 30-site radial | Six-site paired |
|---|---:|---:|
| Completed ordinary passenger workings per day | 144 | 144 |
| Lowest ordinary collector voltage | 1,487.1 V | 1,493.5 V |
| Completed passenger workings in the combined outage trial | 0 | 144 |
| Priced opening capital | $1,124.32m | $807.86m |
| Modelled ordinary annual operating expense | $12.10m | $10.43m |

The paired price replaces the three named parent supply lots with the alternative enquiry. The difference of about $316.46m is a comparison of priced scope. Its excluded renewals, switchgear fault duties, thermal ratings and grid arrangements need matching returns. Likewise, the ordinary radial voltage comes from moving trains at the modelled demand. The commissioning study's 0.57 V margin concerns its hot, coincident design load. Both tests apply to the review. The radial combined-outage simulation withholds movements across isolated track. Read completed trips alongside voltage so a lightly loaded or de-energised railway cannot receive credit for meeting its service requirement. [Commissioning stress cases](../commissioning/COMMISSIONING.md)

## What the factory and operator can take from a case

The production model uses the actual diagrammed fleet plus the three-set reserve, the selected civil quantities, annual train-kilometres and energy at the wayside source. Annual accounts use ordinary service even when the displayed test is an outage. The central 15-minute radial case delivers about 640,027 train-km per year. The asset, opening-service and annual-upkeep estimates remain separate. Reference equipment and CAM files travel with the parent enquiry. Review the candidate's own quantity and cost records before requesting a revised bid. [Production scenarios, cost coverage and local industry](production-guide.md) · [First-article enquiry](../prototype/PROCUREMENT-PLAN.md)

Eight beam moulds require the assumed daily release. The trial 10 m beam also needs site bearings and soil evidence. With the current cage, the proposed 20, 25 and 30 m spans miss the stressed-service screen. The nominal door aperture has a small tolerance allowance. The essential battery has a 1.6 kWh new-pack margin and an 8.8 kWh deficit at 80% remaining capacity. The Workbench keeps all of these cases available for engineering and excludes unresolved cases from selection. [Vehicle and civil screens](PLAN.md) · [Six-package production release register](../prototype/PRODUCTION-READINESS.md)

For interactive machining, the same wax drawing has now been edited, simulated and posted in both CamCraft and FreeCAD. The guide includes the fixture collision, residual stock and overcut trials. [CamCraft versus FreeCAD](CAM-COMPARISON.md)

## Reproduce a decision

From the repository root, run the commands below. The standard-library simulation requires the compact Airport sources. Native SUMO, pandapower, FreeCAD, IfcOpenShell, JuPedSim and CalculiX comparisons retain their versions, input boundaries and evidence alongside the results. Each comparison can be rerun independently with its documented tools.

```sh
./osr design railway simulation --check
./osr design railway simulation --headway-min 20 --cars 3 --topology paired6 --export build/airport-20min-three.zip
./osr design railway simulation --check-catalogue
python3 -m cities.Baghdad.engineering.simulation.controls_check
./osr workbench
```

Each stage cache key includes its inputs, source digests, recipe and Python version. Reuse also requires a matching stored-result digest. For example, changing a shop cost leaves the demand and power stages reusable. A different outdoor temperature changes thermal demand, the motion load and its downstream costs. The CLI reports stage reuse, wall time, cache bytes and process peak memory. Exports carry hashes for every member and the physical and evaluation identities. The six-stop register accompanies a five-mapped-stop GTFS planning feed. Its route times use the evaluated dwell. Real walking access and a through six-stop multimodal journey need the missing station position and verified street connections. [OpenTripPlanner data requirements](https://docs.opentripplanner.org/en/latest/Building-Graphs/)

A physical demonstration still requires a dated article, authenticated measurements, reviewed operating limits and independent approval. The controls evidence here is a Rust software replay on the six-car configuration. A changed formation retains that evidence as a parent reference until its own interface replay is issued. No physical or financial commitment follows from a software pass.
