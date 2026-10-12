# Rahim-Yar-Khan civil soil screening

1,254 route/station sample locations; 1,254 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 184 |
| granular-density-and-groundwater-tests | 1254 |

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
| 0..30cm | clay | % | 13–20 | 1–34 | 1254 |
| 0..30cm | sand | % | 53–67 | 29–91 | 1254 |
| 0..30cm | silt | % | 20–28 | 7–41 | 1254 |
| 0..30cm | bd.core | kg/m3 | 1450–1560 | 1300–1710 | 1254 |
| 0..30cm | soc | g/kg | 2.5–5.6 | 0.7–15.8 | 1254 |
| 0..30cm | ph.h2o | pH | 7.8–8.3 | 6.6–9.2 | 1254 |
| 30..60cm | clay | % | 15–22 | 0–38 | 1254 |
| 30..60cm | sand | % | 49–62 | 19–90 | 1254 |
| 30..60cm | silt | % | 22–29 | 6–45 | 1254 |
| 30..60cm | bd.core | kg/m3 | 1480–1600 | 1300–1790 | 1254 |
| 30..60cm | soc | g/kg | 1.6–2.9 | 0.3–7.9 | 1254 |
| 30..60cm | ph.h2o | pH | 7.9–8.6 | 6.3–9.4 | 1254 |
| 60..100cm | clay | % | 16–22 | 0–37 | 1254 |
| 60..100cm | sand | % | 48–62 | 19–89 | 1254 |
| 60..100cm | silt | % | 22–30 | 6–46 | 1254 |
| 60..100cm | bd.core | kg/m3 | 1480–1640 | 1240–1880 | 1254 |
| 60..100cm | soc | g/kg | 1.6–2.3 | 0.2–6.2 | 1254 |
| 60..100cm | ph.h2o | pH | 7.9–8.7 | 6.3–9.6 | 1254 |
