# Kisii civil soil screening

59 route/station sample locations; 59 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 59 |
| fine-soil-plasticity-and-shrink-swell-tests | 59 |

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
| 0..30cm | clay | % | 41–48 | 25–57 | 59 |
| 0..30cm | sand | % | 25–39 | 11–64 | 59 |
| 0..30cm | silt | % | 21–27 | 6–38 | 59 |
| 0..30cm | bd.core | kg/m3 | 1090–1210 | 900–1410 | 59 |
| 0..30cm | soc | g/kg | 12.2–25.4 | 7.2–40.4 | 59 |
| 0..30cm | ph.h2o | pH | 5.5–5.9 | 5.3–6.2 | 59 |
| 30..60cm | clay | % | 40–48 | 28–56 | 59 |
| 30..60cm | sand | % | 22–37 | 8–59 | 59 |
| 30..60cm | silt | % | 23–30 | 10–44 | 59 |
| 30..60cm | bd.core | kg/m3 | 1110–1240 | 910–1430 | 59 |
| 30..60cm | soc | g/kg | 7.6–14.7 | 4.2–26.1 | 59 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 5.2–6.2 | 59 |
| 60..100cm | clay | % | 40–49 | 28–57 | 59 |
| 60..100cm | sand | % | 21–37 | 8–64 | 59 |
| 60..100cm | silt | % | 23–31 | 10–44 | 59 |
| 60..100cm | bd.core | kg/m3 | 1140–1240 | 930–1490 | 59 |
| 60..100cm | soc | g/kg | 6–11 | 2.9–19.1 | 59 |
| 60..100cm | ph.h2o | pH | 5.5–5.8 | 5–6.3 | 59 |
