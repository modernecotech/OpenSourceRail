# Representative car: prototype planning handoff

[Machine-readable plan](plan.json) `6242099f3e3478d203443f0a9d67006278c80ad02d15b1da77dd71ce49eacfdc` links the selected six-car passive-wheel reference (`756a6887…`) to seven **separate research-child** structural and running-gear quote scopes. Each scope maps leaf quantities, material and stock, make/buy, provisional direct cost, process, inspection and removal. The child BOM is verified, but its gross stock masses and direct part/process allowances are not added to the selected car's installed mass or price.

The car-local frame is x forward, y left, z up with rail running surface z=0. The selected four axle positions are x = −7.45, −5.35, 5.35 and 7.45 m, giving nominal bogie centres at ±6.4 m. Two 1.4 m door apertures are centred at ±4.5 m on the +y side. The research door's 2.9 m guide and two proposed 0.72 m leaf travels leave only **30 mm ideal stock at each guide end**. That is a one-dimensional screen, not a tolerance or three-dimensional motion clearance.

The selected account is 19,221.998 kg/car, comprising 9,131.799 kg of located geometry and **10,090.200 kg of residual or unlocated account**. Whole-car installed mass, CG, inertia and axle reactions remain unknown. The plan identifies mating, swept-envelope, lifting, removal, material, process and QA measurements required before a controlled prototype fabrication instruction can be issued. Its seven quote scopes carry one base direct-cost allowance each for supplier discussion; they are not a complete vehicle cost or accepted quotations.

Reproduce from the current source-bound selected packet and the verified research parts bundle:

```bash
python3 -m engineering.vehicle_parts.prototype_plan build --output /tmp/fresh-v07-car-plan.json
python3 -m engineering.vehicle_parts.prototype_plan verify --output docs/design-engine/v07-representative-car/plan.json
python3 -m pytest -q engineering/vehicle_parts/tests/test_prototype_plan.py
```

The selected reference, research child and door installed-candidate identities stay distinct. All production, engineering and physical acceptance flags remain false.
