# Jinja civil soil screening

1,106 route/station sample locations; 1,062 complete profiles; 44 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1054 |
| coverage-gap | 44 |
| fine-soil-plasticity-and-shrink-swell-tests | 1062 |
| granular-density-and-groundwater-tests | 52 |

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
| 0..30cm | clay | % | 35–47 | 17–56 | 1062 |
| 0..30cm | sand | % | 22–43 | 9–79 | 1062 |
| 0..30cm | silt | % | 22–33 | 6–43 | 1062 |
| 0..30cm | bd.core | kg/m3 | 1060–1260 | 770–1500 | 1062 |
| 0..30cm | soc | g/kg | 9.7–24 | 3.8–42.6 | 1062 |
| 0..30cm | ph.h2o | pH | 5.7–6.4 | 5–7.5 | 1062 |
| 30..60cm | clay | % | 37–50 | 18–60 | 1062 |
| 30..60cm | sand | % | 20–41 | 7–80 | 1062 |
| 30..60cm | silt | % | 21–31 | 3–45 | 1062 |
| 30..60cm | bd.core | kg/m3 | 1130–1290 | 890–1490 | 1062 |
| 30..60cm | soc | g/kg | 5.2–12 | 1.8–21.8 | 1062 |
| 30..60cm | ph.h2o | pH | 5.6–6.4 | 4.9–7.7 | 1062 |
| 60..100cm | clay | % | 38–50 | 18–61 | 1062 |
| 60..100cm | sand | % | 19–41 | 6–81 | 1062 |
| 60..100cm | silt | % | 21–31 | 0–45 | 1062 |
| 60..100cm | bd.core | kg/m3 | 1150–1310 | 850–1580 | 1062 |
| 60..100cm | soc | g/kg | 3.9–10 | 1.4–20.1 | 1062 |
| 60..100cm | ph.h2o | pH | 5.6–6.4 | 4.9–7.8 | 1062 |
