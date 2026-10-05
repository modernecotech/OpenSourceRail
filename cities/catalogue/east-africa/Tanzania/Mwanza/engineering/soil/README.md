# Mwanza civil soil screening

279 route/station sample locations; 247 complete profiles; 32 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 242 |
| coverage-gap | 32 |
| fine-soil-plasticity-and-shrink-swell-tests | 247 |
| granular-density-and-groundwater-tests | 223 |

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
| 0..30cm | clay | % | 25–34 | 11–48 | 247 |
| 0..30cm | sand | % | 41–60 | 17–84 | 247 |
| 0..30cm | silt | % | 16–26 | 3–39 | 247 |
| 0..30cm | bd.core | kg/m3 | 1300–1520 | 1100–1700 | 247 |
| 0..30cm | soc | g/kg | 6.5–15 | 2.5–32.1 | 247 |
| 0..30cm | ph.h2o | pH | 5.7–6.6 | 4.9–7.9 | 247 |
| 30..60cm | clay | % | 26–36 | 8–50 | 247 |
| 30..60cm | sand | % | 41–59 | 14–86 | 247 |
| 30..60cm | silt | % | 14–24 | 0–40 | 247 |
| 30..60cm | bd.core | kg/m3 | 1320–1540 | 1100–1740 | 247 |
| 30..60cm | soc | g/kg | 4.6–9.9 | 1.8–20.3 | 247 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 4.9–8 | 247 |
| 60..100cm | clay | % | 26–36 | 8–53 | 247 |
| 60..100cm | sand | % | 40–60 | 14–86 | 247 |
| 60..100cm | silt | % | 14–24 | 0–43 | 247 |
| 60..100cm | bd.core | kg/m3 | 1290–1510 | 1020–1760 | 247 |
| 60..100cm | soc | g/kg | 4.1–8.1 | 1.7–18.5 | 247 |
| 60..100cm | ph.h2o | pH | 6.1–6.9 | 4.8–8.3 | 247 |
