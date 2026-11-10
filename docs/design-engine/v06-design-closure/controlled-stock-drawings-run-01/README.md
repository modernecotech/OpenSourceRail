# Candidate 9f6d source-stock drawings — bounded research packet

This packet contains three generated orthographic SVGs derived from the exact source-stock shapes in the sealed six-car installation candidate and its matching delivery proposal. The sheets are useful geometry references for the bogie frame, secondary support and inter-car coupler work.

| Part ID | Source-stock shape | Dimensions from source | Quantity per train | Material hypothesis |
| --- | --- | --- | ---: | --- |
| `running/frame-primary-seat` | Box blank | 260 × 240 × 25 mm | 48 | S355 steel |
| `running/bolster-main-rhs` | RHS blank | 2,100 × 220 × 250 mm; 14 mm wall | 12 | S355 steel |
| `running/intercar-mount-clevis` | Box blank | 320 × 240 × 30 mm | 20 | S355 steel |

The drawings show **gross source stock only**. The source explicitly has `finished_geometry_verified=false`. Cut profiles, weld preparation, holes, mating faces, fits, production datums, inspection limits, process times, material traceability, and part qualification are not supplied. They remain held; the packet is not a fabrication release.

The exporter found zero parts with complete controlled research drawing, inspection, and route records (`documented_part_ids=[]`). Whole-vehicle finished-drawing coverage remains false. All physical, engineering, manufacturing, operating, and movement-authority release flags remain false. The larger vehicle-document coverage audit therefore remains open.

## Source and reproducibility

- Body candidate: `9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba`
- Body engineering revision: `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`
- Delivery proposal: `7b88d05f9e0a16ada127d60e51d8ebfdc23b0dcb90ba0c906b2050d4e65a5775`
- Export manifest: [`export/manifest.json`](export/manifest.json)
- Execution record with input and artifact hashes, resource limits, and isolation boundary: [`execution.json`](execution.json)
- Authenticated geometry scope: [`scope.json`](scope.json)

The bounded exporter generated three SVGs in separate 30-second commands, with a 1 GiB address-space limit. Peak observed RSS was about 268 MiB. No CAD/FEA application, ERP/Frappe transaction, supplier lookup, or external network lookup was run. Process limits were applied, but the environment did not provide an OS sandbox.
