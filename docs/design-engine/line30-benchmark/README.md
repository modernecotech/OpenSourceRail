# 30 km / 12 station cost benchmark

**Provisional engineering budget, not a supplier quotation or physical release.**
Analysis baseline: **cable-capstan**, 30 route-km / 60 track-km, 12 stations including terminals, six 17 m cars, 276 places/train, 72 km/h, 1.0 m/s² and 120 s headway.
Conditional budget timetable: **41.69 min one-way**; **45 active + 7 reserve = 52 trainsets / 312 cars**. Offered capacity: 8,280 places/hour/direction. Launch jerk ramps and a 5% running-time recovery allowance enter the fleet budget; neither is an accepted timetable.
Two production/construction shifts; 18 operating hours in two shifts. The result also calculates a separate 24-hour/three-shift operating and renewal sensitivity.

| Budget measure | Low | Base | High |
|---|---:|---:|---:|
|Installed capital, USD million|205.44|737.99|3,661.55|
|USD million per ROUTE km|6.85|24.60|122.05|
|Installed capital, IQD billion|310.21|1,114.37|5,528.93|
|30-year whole-life NPV, USD million|432.72|1,568.31|7,913.55|

Installed capital includes rolling stock, spare trains, elevated civil works, stations/access, launch and auxiliary power, depot, production/tooling, land/utility allowances, testing, tax provision and contingency. Financing is shown separately in the machine-readable result.

| Initial capital category | Base USD million |
|---|---:|
|Delivered rolling stock and launch interfaces|225.28|
|Elevated guideway, foundations, erection and protected access|107.70|
|Launch machinery and traction power|71.94|
|Stations, accessible access, controls and turnbacks|45.18|
|Auxiliary charging and grid capacity|11.92|
|Production buildings, yards and tooling|10.07|
|Depot, land and utility relocations|38.81|
|Fleet component spares and commissioning|18.68|
|Recovery assets|3.31|
|Engineering prototypes independent testing|42.63|
|Tax and import duty provision|14.86|
|Project risk contingency|147.60|

| Launch budget comparison, same service and common electrical rates | Base USD million / route-km |
|---|---:|
|cable-capstan|24.60|
|common-drive-rollers|24.80|
|compact-launch-LIM|25.19|

These are cost hypotheses with overlapping uncertainty, not a qualified winner. The cable baseline is a stable analysis anchor. A different drive must supply its own force/contact/thermal evidence and installation details.
Formation, bogies, seating arrangement and acceleration are revisable design hypotheses. The functional comparison fixes route/access, minimum offered capacity, maximum headway, comfort policy and accounting basis; a different vehicle needs its own quantities and service evaluator.
USD translation uses **IQD 1,510/USD**, recorded from the [CBI](https://cbi.iq/) on 4 November 2026. The [motor](https://www.automationdirect.com/adc/shopping/catalog/motors/ac_motors/general_purpose_and_inverter_rated/mtcp2-300-3d18) and [VFD](https://www.automationdirect.com/adc/shopping/catalog/drives_-a-_soft_starters/ac_variable_frequency_drives_(vfd)/high-performance_vfds/gs4-4300) catalogue observations calibrate bare equipment only.

The ledger calculates rail and complete 8 kg fastening assemblies from material, labour, processing and QA. Labour workplaces are not priced as complete factories. Converter capacities count all outgoing launch sites, not just two tracks.

The retained source vehicle price includes mass-reserve sensitivities. Here residual-account prices/process-hours are normalized back to the same base mass, so price uncertainty does not secretly change the service mass.

Important holds: actual available propulsion, independent braking, structural and soil qualification, turnback conflicts, one-sided-door interfaces, battery charge acceptance and complete installed mass. A +1% route grade can invalidate station-only coasting; high auxiliary load needs a revised service case.

Reproduce into a fresh directory:
```bash
python -m engineering.design_search.line_benchmark --output build/my-line30-benchmark
python -m engineering.design_search.line_benchmark --verify --output build/my-line30-benchmark
```

[Versioned criteria](../../../campaigns/line30-affordable-benchmark.toml) · [Analysis baseline selector](../../../engineering/analysis-baseline.toml) · [Complete quantities, assumptions and ledger](result.json) · [Receipt](manifest.json)

Requirements `a18e0f20b6ec40e067aff40213b312ae756f7f3389ee5b43059225cf92d05ff4`; evaluation `69b499d62d769ca26079a460dd38a0fde257bfb8fef7bf65653930be38eb5204`.
