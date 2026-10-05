# Mosul civil soil screening

1,910 route/station sample locations; 1,842 complete profiles; 68 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 68 |
| fine-soil-plasticity-and-shrink-swell-tests | 1842 |
| granular-density-and-groundwater-tests | 517 |
| silt-moisture-frost-and-erosion-review | 1665 |

- No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.
- Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.
- Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.
- Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.
- No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.

Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.

## Sampled property ranges

Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.

| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |
|---|---|---|---:|---:|---:|
| 0..30cm | clay | % | 19–39 | 4–49 | 1842 |
| 0..30cm | sand | % | 19–50 | 4–78 | 1842 |
| 0..30cm | silt | % | 30–46 | 13–60 | 1842 |
| 0..30cm | bd.core | kg/m3 | 1360–1480 | 1150–1640 | 1842 |
| 0..30cm | soc | g/kg | 2.4–7.5 | 0.8–16 | 1842 |
| 0..30cm | ph.h2o | pH | 7.3–7.7 | 6.7–8.4 | 1842 |
| 30..60cm | clay | % | 22–41 | 4–51 | 1842 |
| 30..60cm | sand | % | 23–50 | 5–84 | 1842 |
| 30..60cm | silt | % | 24–40 | 4–55 | 1842 |
| 30..60cm | bd.core | kg/m3 | 1340–1560 | 1140–1760 | 1842 |
| 30..60cm | soc | g/kg | 2.4–4.6 | 0.8–8.9 | 1842 |
| 30..60cm | ph.h2o | pH | 7.2–8 | 6.3–8.7 | 1842 |
| 60..100cm | clay | % | 24–43 | 4–55 | 1842 |
| 60..100cm | sand | % | 25–53 | 7–84 | 1842 |
| 60..100cm | silt | % | 20–36 | 0–54 | 1842 |
| 60..100cm | bd.core | kg/m3 | 1320–1600 | 1060–1910 | 1842 |
| 60..100cm | soc | g/kg | 2–3.2 | 0.5–7.5 | 1842 |
| 60..100cm | ph.h2o | pH | 7.2–8 | 6.4–9.3 | 1842 |
