# OpenSourceRail v0.7.0 — digital railway reference

v0.7.0 publishes one [selected digital railway](../../reference-v07/README.md) with a candidate-linked car, native beam analysis, production plan, one cost estimate and construction programme. The release also includes the Workbench corridor edit and the separate Samawah and Baghdad planning applications.

| Reference result | Value |
|---|---:|
| Synthetic corridor | 30 km, two tracks, twelve stations |
| Six-car normal capacity | 276 places; 8,280 offered places/hour/direction at the 120 s comparison headway |
| Fleet and structure | 51 trainsets including reserve; 6,000 thirteen-strand 10 m beams |
| Installed capital, 2026 USD | US$1,025.2272m |
| Thirty-year present cost at 4% real | US$1,667.647m |
| Construction programme | 43 months after an approved route and funding decision |

The [release gate](../../RELEASE-v0.7.md) records the checks and scope. The [cost ledger](../../reference-v07/cost/README.md) has one central estimate across fourteen capital scopes. [Baghdad](../../../cities/Baghdad/PROPOSAL.md) uses a separate 700-place train and its own 148.2 km and 605.652 km costed networks.

## Small source installation

A sparse checkout supports the reference calculation without materialising historical campaign outputs:

```sh
git clone --filter=blob:none --sparse --branch v0.7.0 \
  https://github.com/modernecotech/OpenSourceRail.git
cd OpenSourceRail
git sparse-checkout set --no-cone \
  /osr /tools/automation/osr-python /tools/automation/toolchain-release.sh \
  /engineering/__init__.py /engineering/v07_reference_journey.py \
  '/docs/reference-v07/**'
./osr reference v07
./osr reference v07 --stations 13
python3 docs/reference-v07/digital/production/generate.py --check
```

The first calculation reproduces the selected 30 km estimate. The second makes a new corridor candidate with 13 stations and recalculates fleet, energy allowance, civil and production quantities, installed capital and whole-life present cost. The production handoff check verifies the selected twelve-station reference. The full Workbench and native FEM use the broader project setup in [tools/README.md](../../../tools/README.md).

## Engineering boundary

The released material is a digital design and planning package. The vehicle mass and CG account, traction and brake ratings, global beam model, foundations and unit prices have declared assumptions. The native beam model is gross elastic; its prestress screen is analytical. Supplier drawings and quotations, route and ground data, hardware tests, fabrication approvals and independent rail safety review are future project work. This version grants no authority to manufacture or carry passengers.
