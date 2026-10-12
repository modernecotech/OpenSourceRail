# Lira civil soil screening

650 route/station sample locations; 650 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 301 |
| fine-soil-plasticity-and-shrink-swell-tests | 650 |
| granular-density-and-groundwater-tests | 487 |

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
| 0..30cm | clay | % | 22–33 | 11–44 | 650 |
| 0..30cm | sand | % | 37–57 | 13–79 | 650 |
| 0..30cm | silt | % | 21–29 | 7–43 | 650 |
| 0..30cm | bd.core | kg/m3 | 1220–1350 | 980–1580 | 650 |
| 0..30cm | soc | g/kg | 9.1–18.3 | 4.4–33 | 650 |
| 0..30cm | ph.h2o | pH | 6–6.3 | 5.5–7.1 | 650 |
| 30..60cm | clay | % | 22–35 | 10–48 | 650 |
| 30..60cm | sand | % | 35–57 | 12–79 | 650 |
| 30..60cm | silt | % | 20–30 | 2–47 | 650 |
| 30..60cm | bd.core | kg/m3 | 1270–1380 | 1020–1600 | 650 |
| 30..60cm | soc | g/kg | 5.3–7.8 | 2.3–13.2 | 650 |
| 30..60cm | ph.h2o | pH | 6.1–6.4 | 5.4–7.2 | 650 |
| 60..100cm | clay | % | 23–35 | 9–48 | 650 |
| 60..100cm | sand | % | 35–55 | 11–82 | 650 |
| 60..100cm | silt | % | 20–30 | 3–48 | 650 |
| 60..100cm | bd.core | kg/m3 | 1240–1400 | 950–1640 | 650 |
| 60..100cm | soc | g/kg | 4.4–5.6 | 1.7–13.1 | 650 |
| 60..100cm | ph.h2o | pH | 6.2–6.7 | 5.2–8.1 | 650 |
