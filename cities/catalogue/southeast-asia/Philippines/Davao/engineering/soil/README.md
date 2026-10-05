# Davao civil soil screening

1,496 route/station sample locations; 1,459 complete profiles; 37 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1459 |
| coverage-gap | 37 |
| fine-soil-plasticity-and-shrink-swell-tests | 1459 |
| granular-density-and-groundwater-tests | 1354 |
| organic-content-and-compressibility-tests | 207 |
| silt-moisture-frost-and-erosion-review | 164 |

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
| 0..30cm | clay | % | 20–37 | 1–50 | 1459 |
| 0..30cm | sand | % | 33–66 | 3–95 | 1459 |
| 0..30cm | silt | % | 14–31 | 0–55 | 1459 |
| 0..30cm | bd.core | kg/m3 | 610–1400 | 220–1690 | 1459 |
| 0..30cm | soc | g/kg | 5.3–36.8 | 1.2–90.6 | 1459 |
| 0..30cm | ph.h2o | pH | 4.9–6.7 | 3.9–8 | 1459 |
| 30..60cm | clay | % | 21–39 | 2–56 | 1459 |
| 30..60cm | sand | % | 31–67 | 3–96 | 1459 |
| 30..60cm | silt | % | 12–31 | 0–53 | 1459 |
| 30..60cm | bd.core | kg/m3 | 680–1490 | 230–1790 | 1459 |
| 30..60cm | soc | g/kg | 3.7–36.4 | 0.7–102.8 | 1459 |
| 30..60cm | ph.h2o | pH | 5–6.6 | 3.9–8 | 1459 |
| 60..100cm | clay | % | 22–39 | 2–56 | 1459 |
| 60..100cm | sand | % | 30–66 | 0–95 | 1459 |
| 60..100cm | silt | % | 13–32 | 0–54 | 1459 |
| 60..100cm | bd.core | kg/m3 | 680–1510 | 260–1820 | 1459 |
| 60..100cm | soc | g/kg | 3–31.8 | 0.5–411.3 | 1459 |
| 60..100cm | ph.h2o | pH | 5.1–6.7 | 3.8–8.3 | 1459 |
