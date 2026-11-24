# Compare supply spacing and conductor resistance

Use the moving-train calculation to compare a working day on five supported supply layouts. Use the electrical snapshot to investigate other spacings before committing timetable or procurement work. Both read the same surveyed-data gaps, passenger forecasts, installed vehicle mass estimates, assisted dwell and HVAC load as the integrated service model.

| Layout | Source positions on the 12 km route | Conductors |
|---|---|---|
| `radial30` | Issued 30-site arrangement | Single positive path |
| `paired6` | Six issued station sites | Two positive paths |
| `paired6_shifted` | Four interior sites shift alternately by 300 m | Two positive paths |
| `paired6_heavy` | Six station sites | Two paths with 75% of the reference longitudinal loop resistance |
| `paired8` | Eight equally spaced sites, including the ends | Two positive paths |

## Run a passenger service

```sh
python3 -m cities.Baghdad.engineering.simulation.feeder_options \
  --moving paired8 --loop-resistance-factor 0.9 --cars 3 --condition combined
```

This example runs three steel cars every 15 minutes with 350 normal places, a 35-second assisted dwell and a level alignment. The estimated loaded train is 99.57 t and occupies 52 m of the 125 m platform. The diagram allows one open face at each terminus, reserves blocks until the tail clears and includes six depot movements. Three sets work the service and the planning fleet holds three in reserve. Power comes from a continuous protected conductor. Regeneration is limited by other loads and unused braking energy is dissipated.

With site and path 4 out, this example completed 144 of 144 passenger workings. The lowest energized collector voltage was 1,477.3 V, the peak site current was 0.649 kA and the maximum arrival delay was six seconds. Seven source sections remained live. The calculation uses a 1,350–1,650 V equipment window and source droop. Real current-limiting, protection timing, touch voltage, installed thermal ratings and grid connection remain open. The eight-site layout requires a new equipment and installation price. Results for a single outage location do not cover every combination.

Use `--headway-min`, `--grade-pct`, `--material`, `--demand` and `--ambient-c` to change the operating case. `--condition` chooses normal, hot, site outage, path outage or their combined stress case. For a relevant outage, choose a zero-based `--failed-site` or `--failed-path`. Ambient temperature changes passenger cooling demand. Hot and combined electrical cases use the existing solver's resistance multipliers. A separate `--loop-resistance-factor` scales both longitudinal outward and return resistance within the model’s tested 0.5–1.5 range. Suppliers can propose a different conductor for a further evaluation. Converter and controller settings remain fixed in this equipment study.

## Check another spacing

```sh
python3 -m cities.Baghdad.engineering.simulation.feeder_options \
  --snapshot-spacing-km 2.1 --cars 3 --condition combined
```

The requested maximum bay length yields six 2 km bays and seven endpoint-inclusive paired sites. The existing nonlinear DC circuit places one train at each source coordinate and each side of the surviving section boundaries in turn. Under the combined stress and rated demand, the minimum sampled collector voltage is 1,455.3 V. The JSON records requested and delivered power and numerical residuals. No train moves in this test. Coincident trains, overall service completion, installed prices and protection need further evaluation. An arbitrary spacing found this way requires a matching layout in the moving evaluator before it can support a railway service comparison.

Any finite positive maximum spacing can define a layout. A 0.3 km maximum gives 41 sites on this route. A 13 km maximum gives one 12 km bay with two endpoint sites. The default snapshot computation budget allows 128 sites. For a 50 m spacing use `--snapshot-spacing-km 0.05 --snapshot-site-budget 241`. The budget controls the size of the calculation. Each result records the requested maximum, the actual bay length, the site count and the number of sampled positions.

Each result identifies the vehicle, corridor, source files, physical arrangement and evaluation. Compare effective spacing, service and failure indices when requesting quotations. A changed conductor, new rectifier or changed source arrangement needs a matching enquiry. [Coupled motion and electrical model](MOTION-POWER.md) · [Service and cost comparison](JOINT-COMPARISON.md)
