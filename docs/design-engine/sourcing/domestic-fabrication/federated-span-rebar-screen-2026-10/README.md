# Federated candidate domestic rebar screen — October 2026

This research-only screen applies the declared 120 kg/m³ reinforcement allowance to 81 exact nominal concrete span packages in candidate `9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f` (evaluation `1491f90b02485e6ad9df63ac79b528e9c30e9e6d87041a3dc46b02efd364077b`). It estimates source-priced rebar mass plus assumed cut/bend labour and one 20% uplift. It is not a supplier quotation or a complete precast/fabrication estimate.

## Network sensitivities

| Wage region | Assumed hours/input tonne | Modeled mass proxy (t) | Direct material (IQD m) | Direct labour (IQD m) | +20% partial screen (IQD m) |
|---|---:|---:|---:|---:|---:|
| Baghdad | 4 | 216.577 | 214.19 | 8.12 | 266.78 |
| Baghdad | 8 | 216.577 | 214.19 | 16.24 | 276.53 |
| Baghdad | 16 | 216.577 | 214.19 | 32.49 | 296.02 |
| Al-Muthanna | 4 | 216.577 | 214.19 | 6.50 | 264.83 |
| Al-Muthanna | 8 | 216.577 | 214.19 | 12.99 | 272.63 |
| Al-Muthanna | 16 | 216.577 | 214.19 | 25.99 | 288.22 |

The calculation is `(modeled reinforcement mass × CSO material statistic + assumed person-hours × regional CSO skilled base wage) × 1.20`. The wage is a published base-wage proxy normalized from a daily value using an 8-hour day. It is not a factory charge-out rate. The 20% uplift is unallocated and is applied once to direct material plus labour.

The 120 kg/m³ value is an explicit preliminary civil detailing rate, not a bar schedule. The modelled 216.577 t mass is a proxy for these 81 concrete packages; purchase yield, waste, bar diameters, grades, bending schedule, lap lengths, cages, welds, placing labour and commercial order quantity remain unknown. The rebar obligation IDs remain unlocated in the procurement BOM and are linked to their concrete packages for context only; this estimate does not turn those associations into package membership.

Domestic leads include Alpha Steel, Hadeed Iraq, Darin Steel, Al-Anmaa and Qaiwan Steel. They are discovery leads only: no current offer, product specification match, available capacity, delivered price or order is present. The CSO statistical rate is not a supplier quote.

Prestress, anchorages, direct fasteners, concrete ingredients, moulds, QA, utilities, employer burden, taxes, profit, transport, crane lifting, foundations, erection, maintenance and warranty are excluded. The report retains these as unknown rather than zero. It does not change the selected reference or the procurement BOM.

Source hashes, line-level span identities, account links and all six regional/hour cases per span are in [federated-span-rebar-screen.json](federated-span-rebar-screen.json). The exact source inputs are recorded in [manifest.json](manifest.json).
