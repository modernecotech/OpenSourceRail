# Khulna civil soil screening

582 route/station sample locations; 572 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 571 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 572 |
| granular-density-and-groundwater-tests | 572 |
| organic-content-and-compressibility-tests | 335 |

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
| 0..30cm | clay | % | 19–29 | 4–46 | 572 |
| 0..30cm | sand | % | 41–63 | 8–89 | 572 |
| 0..30cm | silt | % | 19–30 | 2–48 | 572 |
| 0..30cm | bd.core | kg/m3 | 790–1120 | 400–1490 | 572 |
| 0..30cm | soc | g/kg | 11.5–46.2 | 3.6–149.7 | 572 |
| 0..30cm | ph.h2o | pH | 6–6.6 | 4.8–7.9 | 572 |
| 30..60cm | clay | % | 20–29 | 2–47 | 572 |
| 30..60cm | sand | % | 40–62 | 7–89 | 572 |
| 30..60cm | silt | % | 19–32 | 3–48 | 572 |
| 30..60cm | bd.core | kg/m3 | 860–1190 | 560–1560 | 572 |
| 30..60cm | soc | g/kg | 6.6–27.1 | 1.2–95.1 | 572 |
| 30..60cm | ph.h2o | pH | 6.2–6.8 | 4.8–8 | 572 |
| 60..100cm | clay | % | 21–30 | 2–47 | 572 |
| 60..100cm | sand | % | 39–59 | 8–90 | 572 |
| 60..100cm | silt | % | 20–32 | 1–49 | 572 |
| 60..100cm | bd.core | kg/m3 | 920–1190 | 540–1760 | 572 |
| 60..100cm | soc | g/kg | 4.8–18.1 | 1.2–82.3 | 572 |
| 60..100cm | ph.h2o | pH | 6.4–7.1 | 4.9–8.2 | 572 |
