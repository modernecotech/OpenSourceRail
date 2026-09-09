# Tetouan civil soil screening

104 route/station sample locations; 104 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 101 |
| granular-density-and-groundwater-tests | 94 |

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
| 0..30cm | clay | % | 20–29 | 3–44 | 104 |
| 0..30cm | sand | % | 41–59 | 12–88 | 104 |
| 0..30cm | silt | % | 21–34 | 6–48 | 104 |
| 0..30cm | bd.core | kg/m3 | 1270–1460 | 1100–1620 | 104 |
| 0..30cm | soc | g/kg | 4.9–16.4 | 1.8–34.3 | 104 |
| 0..30cm | ph.h2o | pH | 6.7–7.9 | 5.7–8.4 | 104 |
| 30..60cm | clay | % | 21–31 | 4–44 | 104 |
| 30..60cm | sand | % | 41–61 | 12–93 | 104 |
| 30..60cm | silt | % | 18–33 | 3–47 | 104 |
| 30..60cm | bd.core | kg/m3 | 1440–1550 | 1270–1720 | 104 |
| 30..60cm | soc | g/kg | 2.4–6.7 | 0.3–13.7 | 104 |
| 30..60cm | ph.h2o | pH | 6.5–7.9 | 5.4–8.6 | 104 |
| 60..100cm | clay | % | 22–32 | 2–47 | 104 |
| 60..100cm | sand | % | 42–61 | 15–93 | 104 |
| 60..100cm | silt | % | 18–31 | 0–47 | 104 |
| 60..100cm | bd.core | kg/m3 | 1490–1590 | 1250–1800 | 104 |
| 60..100cm | soc | g/kg | 1.2–5.7 | 0.1–15.6 | 104 |
| 60..100cm | ph.h2o | pH | 6.4–8 | 5.1–8.7 | 104 |
