# Kafr-El-Sheikh civil soil screening

59 route/station sample locations; 59 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 52 |
| granular-density-and-groundwater-tests | 59 |
| organic-content-and-compressibility-tests | 3 |

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
| 0..30cm | clay | % | 19–25 | 7–40 | 59 |
| 0..30cm | sand | % | 47–60 | 18–86 | 59 |
| 0..30cm | silt | % | 21–29 | 7–44 | 59 |
| 0..30cm | bd.core | kg/m3 | 1160–1440 | 900–1650 | 59 |
| 0..30cm | soc | g/kg | 2.3–22.5 | 0.9–65.5 | 59 |
| 0..30cm | ph.h2o | pH | 7.6–8.3 | 6.7–9 | 59 |
| 30..60cm | clay | % | 20–26 | 5–41 | 59 |
| 30..60cm | sand | % | 47–60 | 17–87 | 59 |
| 30..60cm | silt | % | 20–27 | 5–43 | 59 |
| 30..60cm | bd.core | kg/m3 | 1280–1550 | 900–1770 | 59 |
| 30..60cm | soc | g/kg | 1.4–14.8 | 0–36.3 | 59 |
| 30..60cm | ph.h2o | pH | 7.1–8.3 | 5.2–9.1 | 59 |
| 60..100cm | clay | % | 19–26 | 6–40 | 59 |
| 60..100cm | sand | % | 47–61 | 17–87 | 59 |
| 60..100cm | silt | % | 20–27 | 4–42 | 59 |
| 60..100cm | bd.core | kg/m3 | 1270–1580 | 740–1910 | 59 |
| 60..100cm | soc | g/kg | 1.2–11.3 | 0.1–44.3 | 59 |
| 60..100cm | ph.h2o | pH | 6.8–8.3 | 3.3–9.4 | 59 |
