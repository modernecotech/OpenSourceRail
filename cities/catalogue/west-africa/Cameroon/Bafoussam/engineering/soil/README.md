# Bafoussam civil soil screening

195 route/station sample locations; 195 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 195 |
| fine-soil-plasticity-and-shrink-swell-tests | 195 |
| granular-density-and-groundwater-tests | 30 |
| organic-content-and-compressibility-tests | 22 |

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
| 0..30cm | clay | % | 26–40 | 13–53 | 195 |
| 0..30cm | sand | % | 32–54 | 9–76 | 195 |
| 0..30cm | silt | % | 21–30 | 5–44 | 195 |
| 0..30cm | bd.core | kg/m3 | 1090–1270 | 890–1470 | 195 |
| 0..30cm | soc | g/kg | 12.6–31.3 | 4.9–64.3 | 195 |
| 0..30cm | ph.h2o | pH | 5–5.4 | 4.5–6.2 | 195 |
| 30..60cm | clay | % | 28–42 | 13–57 | 195 |
| 30..60cm | sand | % | 31–52 | 7–77 | 195 |
| 30..60cm | silt | % | 20–29 | 0–46 | 195 |
| 30..60cm | bd.core | kg/m3 | 1170–1350 | 970–1550 | 195 |
| 30..60cm | soc | g/kg | 7.5–14 | 3.5–23.2 | 195 |
| 30..60cm | ph.h2o | pH | 5–5.6 | 4.5–6.5 | 195 |
| 60..100cm | clay | % | 27–43 | 13–59 | 195 |
| 60..100cm | sand | % | 31–53 | 6–79 | 195 |
| 60..100cm | silt | % | 20–29 | 1–46 | 195 |
| 60..100cm | bd.core | kg/m3 | 1220–1360 | 990–1580 | 195 |
| 60..100cm | soc | g/kg | 6.1–9.8 | 3.3–20.6 | 195 |
| 60..100cm | ph.h2o | pH | 5.1–5.7 | 4.6–6.5 | 195 |
