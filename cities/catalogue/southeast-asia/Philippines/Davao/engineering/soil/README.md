# Davao civil soil screening

553 route/station sample locations; 545 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 545 |
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 545 |
| granular-density-and-groundwater-tests | 488 |
| organic-content-and-compressibility-tests | 42 |
| silt-moisture-frost-and-erosion-review | 24 |

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
| 0..30cm | clay | % | 20–36 | 2–50 | 545 |
| 0..30cm | sand | % | 34–63 | 3–95 | 545 |
| 0..30cm | silt | % | 17–31 | 0–52 | 545 |
| 0..30cm | bd.core | kg/m3 | 720–1400 | 220–1690 | 545 |
| 0..30cm | soc | g/kg | 5.8–32.4 | 1.2–81.9 | 545 |
| 0..30cm | ph.h2o | pH | 5–6.6 | 3.9–7.9 | 545 |
| 30..60cm | clay | % | 21–36 | 1–54 | 545 |
| 30..60cm | sand | % | 34–62 | 2–97 | 545 |
| 30..60cm | silt | % | 15–31 | 0–51 | 545 |
| 30..60cm | bd.core | kg/m3 | 790–1490 | 230–1790 | 545 |
| 30..60cm | soc | g/kg | 3.4–26.1 | 0.8–95.6 | 545 |
| 30..60cm | ph.h2o | pH | 5.1–6.6 | 3.9–8 | 545 |
| 60..100cm | clay | % | 22–37 | 1–56 | 545 |
| 60..100cm | sand | % | 33–62 | 0–97 | 545 |
| 60..100cm | silt | % | 15–31 | 0–52 | 545 |
| 60..100cm | bd.core | kg/m3 | 800–1500 | 260–1810 | 545 |
| 60..100cm | soc | g/kg | 3–26.5 | 0.5–320.7 | 545 |
| 60..100cm | ph.h2o | pH | 5.1–6.7 | 3.8–8.3 | 545 |
