# Station recovery economics

The tested no-store powered-wheel research alternative dominates the tested stores on base capital, whole-life NPV and total annual grid energy. This is an economic model result; the selected passive development reference is unchanged.

Frozen source: [`37788e925010`](https://github.com/modernecotech/OpenSourceRail/commit/37788e925010b9b53636809553271d68482bb6de). Study: `a8688d6410c562ba9a37bf9c4846a013eb2aea468b68e7c2d68ff30e8e9f54c0`.

All 32 nominal model cases complete 16/16 arrivals and the declared model screens. They use eleven physical variants, 276 normal places, 85% planning occupancy, 4,000 pphpd demand, 200 s headway, 90 s opposing phase, 3 active + 1 reserve trains, 35 s dwell, 45 s turnback, full-tail terminal clearance and a 190 s common travel planning bound. The route is 1.5 km, double-track, with two stations/four 125 m boarding faces and zero nominal grade.

The exact normally loaded mass is 153,593.336 kg without the store interface and 154,193.336 kg with it. These retain positive installation reserves and the parent powered-bogie packaging hold; they are not complete admitted installed designs. All candidates retain independent brakes, continuous auxiliary/grid feed, service batteries, backup/maintenance charging, protection and recovery allowances.

| Comparison | Traction kWh/16 | Annual total grid MWh | Base capital $m | 30-year base NPV $m |
|---|---:|---:|---:|---:|
| no-store | 122.26189 | 6939.31 | 37.6940 | 71.3069 |
| steel-0.25MJ-share0.2 | 122.48007 | 6990.26 | 38.9663 | 73.5538 |
| steel-4MJ-share0.8 | 121.51428 | 6977.98 | 39.4028 | 74.3044 |
| hydraulic-4MJ-share0.8 | 121.62790 | 6981.12 | 39.2793 | 74.0623 |
| hydraulic-4MJ-recovery-disabled | 122.54951 | 6966.07 | 39.2793 | 74.0346 |

Every store retains five capture stages over 250 m and a 200 m release window at each station. Force/power ceilings, slew 10,000 N/s, reserve factor 2, empty initial banks, reset duty, losses, cooling, interface mass, stock, supports and renewals are unchanged. Only technology/capacity is physical; release shares 0.2/0.5/0.8 are evaluation controls. No raw bank energy is credited as free traction or removed by an invented dump.

The cheapest tested storage case adds $1.2723m capital and $2.2469m NPV to no-store. For identical hydraulic 4 MJ hardware, enabling recovery changes traction by -0.92161 kWh over 16 journeys and reset consumption by +1.11111 kWh, changes annual total grid consumption by +15,052.18 kWh and changes NPV by $+27,766.66. Finite-run traction savings alone therefore do not establish complete-service savings.

The hydraulic 4 MJ state ends with 3.998599 MJ retained across the two stations; 9 releases and 7 captures are bypassed. The sealed finding contains final per-bank energy and exact ownership event times. Incoming capture owns station A from about397.5s before its400s departure until arrival+dwell reset at about513.17s; repeating shared-resource timing prevents its release. This is not repaired by capacity/share changes alone. Capacity/share changes do not remove that ownership conflict.

The next experiments are ranked independently of any integrated selection: first explicitly model capture/release dispatch priority and continuous force handover using the same hardware; second price and model separate transfer paths or split banks; third obtain detailed interface/machinery evidence before changing fixed mass or package prices. Each must retain lost-capture accounting, independent stopping, passenger service, reset duty and cost. None was executed in this cycle.

All fourteen capital/lifecycle scopes are present. Low/base/high figures are calculated outline rates and allowances, not supplier quotations. Actual force-speed-duty curves, spring fatigue, hydraulic flow, cooling, installed mounts, ground conditions and reliability remain unverified. Nominal zero-grade results do not establish grade/fault capability or physical acceptance. Finance, taxes, customs and exchange-rate policy remain separate excluded layers.

Files: [comparison.csv](comparison.csv),[sealed study](study.json),[ownership and next-experiment finding](finding.json),[run usage](usage.json),[sealed evidence archive](evidence.tar.gz),[packet manifest](manifest.json). The archive retains exact requests,outputs,receipts,logs,full case ledgers,body and civil packets. Rebuildable native target files and duplicate stdout are omitted; their original hashes remain in the untouched original run manifest.

Validation: the original source change passed 23 focused/new and existing closure tests; this run retained 32 native cases in 16 resource-bounded batches. The complete run used 122.28 s wall, 352.41 MiB coordinator peak RSS and 83.76 MiB disk. These are software/model checks, not physical validation.

Reproduce from the frozen source with `.venv/bin/python -m engineering.recovery_search run --output <new-private-directory>`. Recorded-run verification: `.venv/bin/python -m engineering.recovery_search verify --output <directory>`. Public packet verification from this repository: `.venv/bin/python tools/publish_recovery_economics.py verify --packet docs/design-engine/recovery-economics`. The actual original invocation also applied `prlimit --as=2147483648 --cpu=900 --`; each native two-case batch imposed1GiB address space,60CPU seconds and75wall seconds.

Content hashes verify recorded integrity. This is not an OS-enforced read-only environment, an independent solver rerun or a safety approval.
