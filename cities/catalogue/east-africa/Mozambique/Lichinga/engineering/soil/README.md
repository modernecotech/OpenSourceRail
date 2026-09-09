# Lichinga civil soil screening

44 route/station sample locations; 44 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 44 |
| fine-soil-plasticity-and-shrink-swell-tests | 44 |
| granular-density-and-groundwater-tests | 19 |

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
| 0..30cm | clay | % | 36–43 | 18–56 | 44 |
| 0..30cm | sand | % | 34–48 | 9–79 | 44 |
| 0..30cm | silt | % | 16–23 | 1–37 | 44 |
| 0..30cm | bd.core | kg/m3 | 1110–1360 | 720–1490 | 44 |
| 0..30cm | soc | g/kg | 7.5–13.5 | 4.1–22.5 | 44 |
| 0..30cm | ph.h2o | pH | 5.6–6 | 5–6.8 | 44 |
| 30..60cm | clay | % | 42–47 | 21–60 | 44 |
| 30..60cm | sand | % | 28–40 | 7–71 | 44 |
| 30..60cm | silt | % | 18–24 | 0–42 | 44 |
| 30..60cm | bd.core | kg/m3 | 1100–1350 | 670–1540 | 44 |
| 30..60cm | soc | g/kg | 5.2–6.8 | 2.8–11.8 | 44 |
| 30..60cm | ph.h2o | pH | 5.8–6.2 | 5–7.1 | 44 |
| 60..100cm | clay | % | 41–48 | 16–61 | 44 |
| 60..100cm | sand | % | 27–38 | 3–81 | 44 |
| 60..100cm | silt | % | 19–25 | 0–47 | 44 |
| 60..100cm | bd.core | kg/m3 | 1020–1370 | 150–1600 | 44 |
| 60..100cm | soc | g/kg | 3.6–4.8 | 1.6–9.8 | 44 |
| 60..100cm | ph.h2o | pH | 6–6.5 | 4.9–7.7 | 44 |
