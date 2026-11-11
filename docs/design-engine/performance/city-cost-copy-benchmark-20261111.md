# City cost copy reduction benchmark

Date: 2026-11-11

Baseline source: `f990fc24ba9c1c2adcd8afb4456ded5c4753209a`
Workload: current Samawah outline input `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`, five mapped lines and 26 original stop records.

Baseline cost evaluation: `539c7f92bff6a97378d45decd1d1649667ac272ab66c5b1e730b357e97323d5e`

Updated cost evaluation: `3c0f6ed7a6f1c9c5c810ae3543ddcf14b58aab507b8dfdbcf45be1a6984ad864`

Producer SHA-256, baseline: `c219b086c0b216c7680df466f2f989fbe6d96a1236f17438040d105ae9ccf469`

Producer SHA-256, updated: `051b90e43872a6822c634937f6f770b87997c5fde4a145ba501145a808fe9332`

The change removes full deep copies of the city and line-service packages in
`engineering/outline/city_project_cost.py`. It builds only the access graph
needed for stop/interchange calculations, shallow-copies the one service row
whose `jerk_bound` default is set, and copies only the small city metadata
record returned to callers.

| Measurement | Before | After |
| --- | ---: | ---: |
| Median city cost evaluation, five warm runs | 0.186 s | 0.171 s |
| One cProfile run wall time | 3.406 s | 2.712 s |
| cProfile cumulative `deepcopy` time | 2.998 s | 2.300 s |
| cProfile calls, all functions | 1,182,551 | 928,801 |
| Peak RSS in profiled process | 264 MiB | 265 MiB |

The warm-run median fell by 8.1%. The profile is instrumented and its elapsed
time is not representative of an unprofiled run. Peak RSS did not improve in
this sample. The pre-change and post-change Samawah outputs matched exactly for
cost lines, quantities, scope totals, service identity, and all accounting
ledgers. Only the expected `city_project_cost.py` source hash and enclosing
evaluation ID changed. The Samawah city input ID remained unchanged.

Regression command:

```sh
.venv/bin/python -m pytest -q tests/test_outline_city_project_cost.py tests/test_outline_completion.py
```

Result: **39 passed**. The new access-graph case checks operational-stop
replacement, interchange remapping, input immutability, and output metadata
isolation.

This is one bounded software-performance sample, not an all-city throughput
claim or physical engineering evidence. The current 266-city publication must
be regenerated from the changed producer before it is treated as current.
