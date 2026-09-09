# Rangpur civil soil screening

80 route/station sample locations; 80 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 80 |
| fine-soil-plasticity-and-shrink-swell-tests | 60 |
| granular-density-and-groundwater-tests | 80 |
| organic-content-and-compressibility-tests | 8 |

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
| 0..30cm | clay | % | 19–25 | 5–42 | 80 |
| 0..30cm | sand | % | 48–61 | 18–84 | 80 |
| 0..30cm | silt | % | 20–26 | 2–45 | 80 |
| 0..30cm | bd.core | kg/m3 | 1000–1140 | 760–1400 | 80 |
| 0..30cm | soc | g/kg | 13.8–21 | 4.7–66.3 | 80 |
| 0..30cm | ph.h2o | pH | 5.7–6 | 4.6–7.6 | 80 |
| 30..60cm | clay | % | 18–26 | 4–42 | 80 |
| 30..60cm | sand | % | 49–62 | 16–86 | 80 |
| 30..60cm | silt | % | 20–26 | 3–47 | 80 |
| 30..60cm | bd.core | kg/m3 | 1060–1180 | 760–1470 | 80 |
| 30..60cm | soc | g/kg | 6.7–15.6 | 2–46.1 | 80 |
| 30..60cm | ph.h2o | pH | 6–6.3 | 4.6–7.9 | 80 |
| 60..100cm | clay | % | 18–26 | 4–42 | 80 |
| 60..100cm | sand | % | 48–61 | 15–86 | 80 |
| 60..100cm | silt | % | 20–27 | 3–49 | 80 |
| 60..100cm | bd.core | kg/m3 | 1030–1130 | 530–1470 | 80 |
| 60..100cm | soc | g/kg | 5.7–11.4 | 1.5–31.5 | 80 |
| 60..100cm | ph.h2o | pH | 6.2–6.6 | 4.6–8.1 | 80 |
