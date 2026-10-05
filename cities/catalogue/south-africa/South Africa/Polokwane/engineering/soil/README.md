# Polokwane civil soil screening

97 route/station sample locations; 97 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 97 |
| granular-density-and-groundwater-tests | 81 |

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
| 0..30cm | clay | % | 27–37 | 14–49 | 97 |
| 0..30cm | sand | % | 42–61 | 18–80 | 97 |
| 0..30cm | silt | % | 12–21 | 0–34 | 97 |
| 0..30cm | bd.core | kg/m3 | 1250–1440 | 1040–1620 | 97 |
| 0..30cm | soc | g/kg | 5.2–13.3 | 2.7–26.2 | 97 |
| 0..30cm | ph.h2o | pH | 6.6–7.8 | 5.9–8.4 | 97 |
| 30..60cm | clay | % | 31–41 | 15–56 | 97 |
| 30..60cm | sand | % | 41–57 | 14–81 | 97 |
| 30..60cm | silt | % | 12–19 | 0–34 | 97 |
| 30..60cm | bd.core | kg/m3 | 1360–1500 | 1110–1720 | 97 |
| 30..60cm | soc | g/kg | 3.2–7.2 | 1.5–13.4 | 97 |
| 30..60cm | ph.h2o | pH | 6.8–7.8 | 5.9–8.7 | 97 |
| 60..100cm | clay | % | 32–41 | 16–57 | 97 |
| 60..100cm | sand | % | 41–55 | 15–81 | 97 |
| 60..100cm | silt | % | 13–20 | 0–35 | 97 |
| 60..100cm | bd.core | kg/m3 | 1350–1530 | 990–1730 | 97 |
| 60..100cm | soc | g/kg | 2.3–6.6 | 1–15.6 | 97 |
| 60..100cm | ph.h2o | pH | 6.9–7.8 | 5.9–8.6 | 97 |
