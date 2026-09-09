# Arua civil soil screening

72 route/station sample locations; 72 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 70 |
| fine-soil-plasticity-and-shrink-swell-tests | 72 |
| granular-density-and-groundwater-tests | 60 |

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
| 0..30cm | clay | % | 26–33 | 11–47 | 72 |
| 0..30cm | sand | % | 39–52 | 14–80 | 72 |
| 0..30cm | silt | % | 20–27 | 6–43 | 72 |
| 0..30cm | bd.core | kg/m3 | 1240–1410 | 1000–1560 | 72 |
| 0..30cm | soc | g/kg | 9–14.4 | 4–27.2 | 72 |
| 0..30cm | ph.h2o | pH | 6–6.5 | 5.4–7.6 | 72 |
| 30..60cm | clay | % | 28–34 | 12–49 | 72 |
| 30..60cm | sand | % | 40–52 | 12–82 | 72 |
| 30..60cm | silt | % | 18–26 | 1–43 | 72 |
| 30..60cm | bd.core | kg/m3 | 1300–1410 | 1110–1650 | 72 |
| 30..60cm | soc | g/kg | 4.9–7.3 | 2.4–12.6 | 72 |
| 30..60cm | ph.h2o | pH | 6.1–6.6 | 5.3–7.6 | 72 |
| 60..100cm | clay | % | 28–35 | 12–49 | 72 |
| 60..100cm | sand | % | 41–52 | 13–83 | 72 |
| 60..100cm | silt | % | 18–26 | 3–44 | 72 |
| 60..100cm | bd.core | kg/m3 | 1300–1420 | 1040–1690 | 72 |
| 60..100cm | soc | g/kg | 3.9–6 | 1.6–11.4 | 72 |
| 60..100cm | ph.h2o | pH | 6.1–6.8 | 4.8–8.1 | 72 |
