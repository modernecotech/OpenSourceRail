# Entebbe civil soil screening

190 route/station sample locations; 190 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 190 |
| fine-soil-plasticity-and-shrink-swell-tests | 190 |
| granular-density-and-groundwater-tests | 157 |
| organic-content-and-compressibility-tests | 23 |

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
| 0..30cm | clay | % | 27–37 | 12–52 | 190 |
| 0..30cm | sand | % | 36–53 | 12–84 | 190 |
| 0..30cm | silt | % | 18–28 | 3–44 | 190 |
| 0..30cm | bd.core | kg/m3 | 830–1220 | 210–1420 | 190 |
| 0..30cm | soc | g/kg | 10.9–32.9 | 4.8–87 | 190 |
| 0..30cm | ph.h2o | pH | 5.7–6.2 | 4.9–7.3 | 190 |
| 30..60cm | clay | % | 30–40 | 10–55 | 190 |
| 30..60cm | sand | % | 35–51 | 11–84 | 190 |
| 30..60cm | silt | % | 19–27 | 1–46 | 190 |
| 30..60cm | bd.core | kg/m3 | 860–1270 | 210–1460 | 190 |
| 30..60cm | soc | g/kg | 6.6–16.9 | 1.9–32.8 | 190 |
| 30..60cm | ph.h2o | pH | 5.6–6.3 | 4.9–7.4 | 190 |
| 60..100cm | clay | % | 31–41 | 9–55 | 190 |
| 60..100cm | sand | % | 33–51 | 10–84 | 190 |
| 60..100cm | silt | % | 18–27 | 0–49 | 190 |
| 60..100cm | bd.core | kg/m3 | 890–1280 | 200–1510 | 190 |
| 60..100cm | soc | g/kg | 4.8–18.7 | 1.5–63.3 | 190 |
| 60..100cm | ph.h2o | pH | 5.6–6.3 | 4.8–7.4 | 190 |
