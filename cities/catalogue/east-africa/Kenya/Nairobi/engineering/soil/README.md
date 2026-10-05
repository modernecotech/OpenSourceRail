# Nairobi civil soil screening

1,522 route/station sample locations; 1,522 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 105 |
| fine-soil-plasticity-and-shrink-swell-tests | 1461 |
| granular-density-and-groundwater-tests | 682 |
| organic-content-and-compressibility-tests | 6 |
| silt-moisture-frost-and-erosion-review | 40 |

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
| 0..30cm | clay | % | 22–44 | 13–55 | 1522 |
| 0..30cm | sand | % | 15–58 | 4–77 | 1522 |
| 0..30cm | silt | % | 20–41 | 5–50 | 1522 |
| 0..30cm | bd.core | kg/m3 | 1080–1430 | 920–1610 | 1522 |
| 0..30cm | soc | g/kg | 4.3–22.7 | 1.9–51.4 | 1522 |
| 0..30cm | ph.h2o | pH | 5.7–7.7 | 4.9–8.5 | 1522 |
| 30..60cm | clay | % | 19–45 | 7–59 | 1522 |
| 30..60cm | sand | % | 15–63 | 3–91 | 1522 |
| 30..60cm | silt | % | 18–42 | 0–52 | 1522 |
| 30..60cm | bd.core | kg/m3 | 1160–1450 | 990–1670 | 1522 |
| 30..60cm | soc | g/kg | 2.8–13.3 | 1–20.9 | 1522 |
| 30..60cm | ph.h2o | pH | 5.8–7.7 | 4.9–8.5 | 1522 |
| 60..100cm | clay | % | 20–45 | 7–59 | 1522 |
| 60..100cm | sand | % | 15–60 | 3–91 | 1522 |
| 60..100cm | silt | % | 19–42 | 0–53 | 1522 |
| 60..100cm | bd.core | kg/m3 | 1200–1480 | 970–1700 | 1522 |
| 60..100cm | soc | g/kg | 1.6–8.4 | 0.3–15.7 | 1522 |
| 60..100cm | ph.h2o | pH | 5.8–7.8 | 4.7–8.5 | 1522 |
