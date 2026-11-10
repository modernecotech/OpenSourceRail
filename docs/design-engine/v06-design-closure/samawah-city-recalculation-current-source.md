# Samawah outline recalculation — current body source

This is the current-source held outline calculation for the existing five-line
Samawah map. The previous calculation is retained separately as a historical
source snapshot. The new run accepts the regenerated compact-drive body under
its current evaluation identity; it does not change the city's physical
candidate or claim that the body has passed its engineering screen.

## Candidate and planning result

| Item | Current result |
| --- | --- |
| City physical candidate / evaluation | `9f37c5d864a34b56009030b07659abe0cc92d5dc97c5c1872384cc7b93a6b176` / `eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16` |
| Body physical candidate / evaluation | `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3` |
| Map | 5 radial lines, 57.873 km, 26 station markers |
| Conditional trainsets | 42 low / 59 base / 88 high, including 8 / 10 / 13 reserves |
| Base body mass scenario | 129.62 t tare; 150.32 t normally loaded; 201.62 t crowd-control |
| Guideway request | 5,794 reference 20 m beams, 2,902 shared bents, 231.493 km of running rail, 385,825 fastening sets |

Demand controls are 2,000 / 4,000 / 6,000 passengers per hour per direction,
not local passenger forecasts. The calculation assumes a 20 m/s cap, 0.4 m/s²
acceleration and 0.6 m/s² deceleration for point-train fleet requests; actual
available force, braking and grade are unknown. It retains the existing
79.977 m line-1 station spacing against a 120 m platform request as a
definition conflict. No stop was removed or merged.

The body has incomplete installed mass. Its upstream current-source geometry
screen remains **HOLD**, with 5,940 nominal findings and 3,942 continuous
interface holds. The city packet does not calculate a force-driven service,
braking distance, traction energy, detailed civil loads or a buildable station
assembly. All fourteen cost scopes are present, with incomplete costs and NPV
remaining `null`.

## Cost fragments, not project price

The separate cost bridge adds the candidate body's counted BOM/process subtotal
to five quantity-matched historical Class-C infrastructure rates. Its low /
base / high partial sums are **$70.38m / $173.54m / $603.82m**. The base is
$88.68m counted BOM/process plus $84.86m of rail, fastener, beam, bearing-pad
and joint/drain/lifting fragments. These sums exclude most project CAPEX and
all complete lifecycle pricing; `installed_capex_usd` and `whole_life_npv_usd`
remain `null`.

The five inherited rates are not supplier quotations or verified current
Chinese prices. The retained source's China-bulk and project make/buy rows have
the same rates for these matched quantities, and no additional project-volume
discount is evidenced. The body BOM has no same-candidate China reprice. The
beam's load basis is not validated against this body, and construction haul,
crane and erection rates remain excluded. These figures are useful only as
bounded outline fragments, not an investment estimate.

## Reproducible evidence

- The three-trial compact-drive replay and exact selected body are in
  [`compact-drive-source-replay-01/`](compact-drive-source-replay-01.md).
- The current-source city run packet, including exact body, city and policy
  inputs, is at
  [`samawah-city-recalculation-current-source/manifest.json`](samawah-city-recalculation-current-source/manifest.json).
  It completed in 2.924 s with 304,564 KiB child peak RSS under a 60 s CPU
  limit, 1 GiB address-space limit and 60 s parent timeout. No native solver
  ran; source-tree writes were possible, and no OS read-only sandbox is
  claimed. Packet ID: `a053772d86ce17abe67694f2275ee22d024d2eede3b67bcdbaa7c3ecec1a0f04`.
- The current-source cost bridge and all source/file hashes are at
  [`samawah-candidate-cost-bridge-current-source/manifest.json`](samawah-candidate-cost-bridge-current-source/manifest.json).
  It completed in 0.987 s, with 528,496 KiB process peak RSS and no hard
  resource limits. Packet ID: `8e636ef63bd1f7403f8bd3ad4f7e836fe1f06c5628169ef8c8ea5ac981d62a01`.

Neither calculation uses GIS solver, CAD, FEM, ERPNext, network access or
supplier lookup. Engineering, physical, manufacturing and operating
acceptance flags remain false. The earlier calculation remains at
[`samawah-city-recalculation/`](samawah-city-recalculation/manifest.json) as
historical evidence; it was not overwritten.
