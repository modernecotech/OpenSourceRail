# Beni-Mellal civil soil screening

231 route/station sample locations; 231 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 230 |
| granular-density-and-groundwater-tests | 50 |
| silt-moisture-frost-and-erosion-review | 11 |

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
| 0..30cm | clay | % | 22–30 | 10–42 | 231 |
| 0..30cm | sand | % | 35–50 | 9–73 | 231 |
| 0..30cm | silt | % | 27–35 | 11–51 | 231 |
| 0..30cm | bd.core | kg/m3 | 1300–1440 | 1080–1620 | 231 |
| 0..30cm | soc | g/kg | 5–9.4 | 2.2–19.3 | 231 |
| 0..30cm | ph.h2o | pH | 7.3–7.6 | 6.6–8.1 | 231 |
| 30..60cm | clay | % | 24–32 | 9–44 | 231 |
| 30..60cm | sand | % | 34–51 | 10–78 | 231 |
| 30..60cm | silt | % | 25–34 | 9–49 | 231 |
| 30..60cm | bd.core | kg/m3 | 1430–1540 | 1120–1750 | 231 |
| 30..60cm | soc | g/kg | 3.1–4.4 | 1.2–8.5 | 231 |
| 30..60cm | ph.h2o | pH | 7.3–7.8 | 6.5–8.4 | 231 |
| 60..100cm | clay | % | 24–32 | 8–45 | 231 |
| 60..100cm | sand | % | 34–52 | 8–80 | 231 |
| 60..100cm | silt | % | 24–34 | 6–49 | 231 |
| 60..100cm | bd.core | kg/m3 | 1490–1620 | 1260–1880 | 231 |
| 60..100cm | soc | g/kg | 2.2–3.4 | 0.9–6.6 | 231 |
| 60..100cm | ph.h2o | pH | 7.4–7.9 | 6.4–8.5 | 231 |
