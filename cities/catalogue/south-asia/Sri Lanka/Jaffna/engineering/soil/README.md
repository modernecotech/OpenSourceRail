# Jaffna civil soil screening

97 route/station sample locations; 97 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 97 |
| granular-density-and-groundwater-tests | 97 |
| organic-content-and-compressibility-tests | 2 |

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
| 0..30cm | clay | % | 23–29 | 4–46 | 97 |
| 0..30cm | sand | % | 49–63 | 16–92 | 97 |
| 0..30cm | silt | % | 14–22 | 0–42 | 97 |
| 0..30cm | bd.core | kg/m3 | 1090–1350 | 710–1620 | 97 |
| 0..30cm | soc | g/kg | 8.6–19.3 | 3.3–55.6 | 97 |
| 0..30cm | ph.h2o | pH | 6.3–7.2 | 5.2–8.2 | 97 |
| 30..60cm | clay | % | 24–29 | 3–51 | 97 |
| 30..60cm | sand | % | 49–63 | 17–91 | 97 |
| 30..60cm | silt | % | 13–23 | 0–44 | 97 |
| 30..60cm | bd.core | kg/m3 | 1060–1320 | 670–1640 | 97 |
| 30..60cm | soc | g/kg | 6.8–14.7 | 2.7–45 | 97 |
| 30..60cm | ph.h2o | pH | 6.6–7.3 | 5.5–8.3 | 97 |
| 60..100cm | clay | % | 24–29 | 2–51 | 97 |
| 60..100cm | sand | % | 50–64 | 17–92 | 97 |
| 60..100cm | silt | % | 12–21 | 0–43 | 97 |
| 60..100cm | bd.core | kg/m3 | 1000–1270 | 460–1710 | 97 |
| 60..100cm | soc | g/kg | 6.1–11.9 | 1.9–35.2 | 97 |
| 60..100cm | ph.h2o | pH | 6.9–7.5 | 5.5–8.6 | 97 |
