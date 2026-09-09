# Nakuru civil soil screening

91 route/station sample locations; 91 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 56 |
| granular-density-and-groundwater-tests | 73 |

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
| 0..30cm | clay | % | 21–36 | 12–48 | 91 |
| 0..30cm | sand | % | 37–60 | 11–82 | 91 |
| 0..30cm | silt | % | 18–29 | 6–45 | 91 |
| 0..30cm | bd.core | kg/m3 | 1210–1300 | 1010–1490 | 91 |
| 0..30cm | soc | g/kg | 8.2–20.3 | 3–35.9 | 91 |
| 0..30cm | ph.h2o | pH | 6.4–7.4 | 5.5–8.3 | 91 |
| 30..60cm | clay | % | 19–35 | 10–48 | 91 |
| 30..60cm | sand | % | 37–63 | 12–83 | 91 |
| 30..60cm | silt | % | 17–28 | 5–47 | 91 |
| 30..60cm | bd.core | kg/m3 | 1210–1370 | 990–1550 | 91 |
| 30..60cm | soc | g/kg | 6.4–10.4 | 2.7–16.3 | 91 |
| 30..60cm | ph.h2o | pH | 6.6–7.5 | 5.3–8.4 | 91 |
| 60..100cm | clay | % | 17–35 | 7–47 | 91 |
| 60..100cm | sand | % | 37–69 | 11–84 | 91 |
| 60..100cm | silt | % | 14–28 | 3–47 | 91 |
| 60..100cm | bd.core | kg/m3 | 1210–1390 | 950–1590 | 91 |
| 60..100cm | soc | g/kg | 4.5–7.3 | 1.4–14.8 | 91 |
| 60..100cm | ph.h2o | pH | 6.8–7.6 | 5.6–8.5 | 91 |
