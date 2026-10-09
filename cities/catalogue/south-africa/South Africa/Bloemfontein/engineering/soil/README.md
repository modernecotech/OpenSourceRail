# Bloemfontein civil soil screening

413 route/station sample locations; 413 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 393 |
| fine-soil-plasticity-and-shrink-swell-tests | 413 |
| granular-density-and-groundwater-tests | 412 |

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
| 0..30cm | clay | % | 25–40 | 9–54 | 413 |
| 0..30cm | sand | % | 32–58 | 9–86 | 413 |
| 0..30cm | silt | % | 16–28 | 0–43 | 413 |
| 0..30cm | bd.core | kg/m3 | 1220–1450 | 950–1620 | 413 |
| 0..30cm | soc | g/kg | 5.3–16.1 | 2.3–36.9 | 413 |
| 0..30cm | ph.h2o | pH | 6.4–8.1 | 5.3–8.8 | 413 |
| 30..60cm | clay | % | 27–41 | 8–57 | 413 |
| 30..60cm | sand | % | 33–58 | 9–87 | 413 |
| 30..60cm | silt | % | 15–27 | 0–42 | 413 |
| 30..60cm | bd.core | kg/m3 | 1290–1530 | 950–1690 | 413 |
| 30..60cm | soc | g/kg | 3–8.4 | 1.3–17.5 | 413 |
| 30..60cm | ph.h2o | pH | 6.4–8.1 | 5.3–9.2 | 413 |
| 60..100cm | clay | % | 27–41 | 9–56 | 413 |
| 60..100cm | sand | % | 33–58 | 7–88 | 413 |
| 60..100cm | silt | % | 15–27 | 0–45 | 413 |
| 60..100cm | bd.core | kg/m3 | 1210–1570 | 370–1760 | 413 |
| 60..100cm | soc | g/kg | 2–4.8 | 0.5–10.2 | 413 |
| 60..100cm | ph.h2o | pH | 6.2–8.1 | 5–8.9 | 413 |
