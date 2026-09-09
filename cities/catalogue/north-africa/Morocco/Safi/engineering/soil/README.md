# Safi civil soil screening

71 route/station sample locations; 71 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 71 |
| granular-density-and-groundwater-tests | 65 |

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
| 0..30cm | clay | % | 24–31 | 9–44 | 71 |
| 0..30cm | sand | % | 38–49 | 12–79 | 71 |
| 0..30cm | silt | % | 25–32 | 8–48 | 71 |
| 0..30cm | bd.core | kg/m3 | 1350–1400 | 1120–1610 | 71 |
| 0..30cm | soc | g/kg | 5.7–10.2 | 2.5–22.5 | 71 |
| 0..30cm | ph.h2o | pH | 7.4–7.9 | 6.6–8.4 | 71 |
| 30..60cm | clay | % | 23–30 | 10–46 | 71 |
| 30..60cm | sand | % | 40–53 | 11–83 | 71 |
| 30..60cm | silt | % | 24–30 | 3–48 | 71 |
| 30..60cm | bd.core | kg/m3 | 1450–1600 | 1220–1830 | 71 |
| 30..60cm | soc | g/kg | 3.2–5.8 | 1.3–12.3 | 71 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.6–8.7 | 71 |
| 60..100cm | clay | % | 23–30 | 8–45 | 71 |
| 60..100cm | sand | % | 41–54 | 10–85 | 71 |
| 60..100cm | silt | % | 23–30 | 3–49 | 71 |
| 60..100cm | bd.core | kg/m3 | 1480–1640 | 1200–1870 | 71 |
| 60..100cm | soc | g/kg | 2.4–4.1 | 0.9–9.5 | 71 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.6–8.9 | 71 |
