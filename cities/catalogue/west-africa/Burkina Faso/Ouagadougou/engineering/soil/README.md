# Ouagadougou civil soil screening

360 route/station sample locations; 359 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 352 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 222 |
| granular-density-and-groundwater-tests | 356 |

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
| 0..30cm | clay | % | 11–30 | 5–43 | 359 |
| 0..30cm | sand | % | 37–75 | 12–88 | 359 |
| 0..30cm | silt | % | 14–33 | 5–45 | 359 |
| 0..30cm | bd.core | kg/m3 | 1400–1550 | 1200–1730 | 359 |
| 0..30cm | soc | g/kg | 3–8.3 | 1.4–14.2 | 359 |
| 0..30cm | ph.h2o | pH | 5.8–7.2 | 5–8.2 | 359 |
| 30..60cm | clay | % | 16–30 | 5–46 | 359 |
| 30..60cm | sand | % | 39–69 | 11–91 | 359 |
| 30..60cm | silt | % | 15–30 | 3–46 | 359 |
| 30..60cm | bd.core | kg/m3 | 1380–1530 | 1110–1750 | 359 |
| 30..60cm | soc | g/kg | 2.1–4.2 | 0.8–7.8 | 359 |
| 30..60cm | ph.h2o | pH | 6–7.6 | 5.3–8.5 | 359 |
| 60..100cm | clay | % | 19–31 | 4–47 | 359 |
| 60..100cm | sand | % | 39–63 | 11–91 | 359 |
| 60..100cm | silt | % | 17–30 | 3–46 | 359 |
| 60..100cm | bd.core | kg/m3 | 1340–1520 | 900–1780 | 359 |
| 60..100cm | soc | g/kg | 1.8–3 | 0.3–7.8 | 359 |
| 60..100cm | ph.h2o | pH | 6.3–7.9 | 5.3–8.9 | 359 |
