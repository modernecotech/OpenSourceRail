# Independent research-campaign replay and stock audit

OpenSourceRail develops simple fixed lines, affordable construction and repair, and high passenger throughput. These records verify digital traceability and known-stock quantities for a component research candidate. Physical qualification remains open.

Campaign `f60de0526feabfb9b2b9b590f9aaa53fe64d9c40cc22a6afe7d7f7f8f5853d9a` retains five candidates, 25 primary calculations and five arithmetic/source confirmations. The fresh-state replay checked **321 archive files, 29 source bindings and 30 sealed worker attempts**, reproduced the declared selections and left extracted state unchanged. No solvers ran.

The separate quantity audit reads the candidate inventory and actual serialized CAD/IFC/BOM data directly. Initial added-carrier counts are **0 / 64 / 80**. The baseline FCStd and IFC each contain **845 objects**, zero added carrier objects and exactly six concrete solids. Bundle, native data and one-span manufacturing quantities agree at **18.056 m³ / 45,140 kg of concrete**.

[Replay report](independent-replay-report.json) · [Quantity report](quantity-audit.json) · [Replay script as executed](replay-as-run.py) · [Quantity script as executed](quantity-as-run.py)

The scripts preserve their original host paths and execution context. A checkout can replay the portable state through the maintained interface:

```bash
mkdir -p build/replayed-design
tar -xzf docs/design-engine/design-search/run-evidence.tar.gz -C build/replayed-design
./osr design campaign compare f60de0526feabfb9b2b9b590f9aaa53fe64d9c40cc22a6afe7d7f7f8f5853d9a --state build/replayed-design
```

The retained archive contains ordinary data files. The as-run replay additionally checks traversal, duplicate/member/size limits and payload identities before extraction. These are reproduction and stock-arithmetic audits; independent magnetic, structural, thermal and operating confirmation remains required. No integrated baseline, complete installed design, physical acceptance or changed qualification disposition is established.

[Campaign and scope](../../../../docs/design-engine/design-search/README.md) · [Engineering interpretation](../../../../docs/design-engine/design-search-interpretation.md) · [Project introduction](../../../../README.md)
