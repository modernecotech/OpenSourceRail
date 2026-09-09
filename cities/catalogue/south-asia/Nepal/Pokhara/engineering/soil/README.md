# Pokhara civil soil screening

228 route/station sample locations; 227 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 227 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 165 |
| granular-density-and-groundwater-tests | 188 |
| organic-content-and-compressibility-tests | 1 |

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
| 0..30cm | clay | % | 16–27 | 7–39 | 227 |
| 0..30cm | sand | % | 44–60 | 19–80 | 227 |
| 0..30cm | silt | % | 23–31 | 9–47 | 227 |
| 0..30cm | bd.core | kg/m3 | 910–1280 | 610–1550 | 227 |
| 0..30cm | soc | g/kg | 9–19 | 2.7–51.4 | 227 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.6–6.8 | 227 |
| 30..60cm | clay | % | 15–27 | 6–39 | 227 |
| 30..60cm | sand | % | 44–63 | 17–82 | 227 |
| 30..60cm | silt | % | 22–31 | 8–48 | 227 |
| 30..60cm | bd.core | kg/m3 | 980–1330 | 540–1600 | 227 |
| 30..60cm | soc | g/kg | 5.3–13.3 | 1.2–37.3 | 227 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 4.7–6.9 | 227 |
| 60..100cm | clay | % | 16–27 | 6–39 | 227 |
| 60..100cm | sand | % | 44–62 | 18–82 | 227 |
| 60..100cm | silt | % | 22–31 | 8–48 | 227 |
| 60..100cm | bd.core | kg/m3 | 1040–1340 | 610–1630 | 227 |
| 60..100cm | soc | g/kg | 3.1–9.2 | 0.7–30.9 | 227 |
| 60..100cm | ph.h2o | pH | 5.5–6 | 4.8–6.9 | 227 |
