# Damietta civil soil screening

137 route/station sample locations; 130 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 20 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 129 |
| granular-density-and-groundwater-tests | 124 |
| organic-content-and-compressibility-tests | 45 |

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
| 0..30cm | clay | % | 20–28 | 6–41 | 130 |
| 0..30cm | sand | % | 41–59 | 12–82 | 130 |
| 0..30cm | silt | % | 21–31 | 8–48 | 130 |
| 0..30cm | bd.core | kg/m3 | 1010–1460 | 730–1660 | 130 |
| 0..30cm | soc | g/kg | 3.4–21.7 | 1.7–71 | 130 |
| 0..30cm | ph.h2o | pH | 7.5–8.4 | 6.3–9.1 | 130 |
| 30..60cm | clay | % | 22–30 | 6–43 | 130 |
| 30..60cm | sand | % | 41–57 | 13–84 | 130 |
| 30..60cm | silt | % | 21–30 | 6–47 | 130 |
| 30..60cm | bd.core | kg/m3 | 1050–1530 | 740–1780 | 130 |
| 30..60cm | soc | g/kg | 2.5–18.9 | 0.7–63.1 | 130 |
| 30..60cm | ph.h2o | pH | 7.1–8.5 | 5.2–9.5 | 130 |
| 60..100cm | clay | % | 22–30 | 5–44 | 130 |
| 60..100cm | sand | % | 41–58 | 13–84 | 130 |
| 60..100cm | silt | % | 20–30 | 4–45 | 130 |
| 60..100cm | bd.core | kg/m3 | 1060–1550 | 600–1880 | 130 |
| 60..100cm | soc | g/kg | 1.9–25.1 | 0.5–142.4 | 130 |
| 60..100cm | ph.h2o | pH | 6.8–8.7 | 3.3–9.7 | 130 |
