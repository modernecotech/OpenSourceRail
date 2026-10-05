# Tete civil soil screening

526 route/station sample locations; 524 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 127 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 524 |
| granular-density-and-groundwater-tests | 515 |

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
| 0..30cm | clay | % | 22–32 | 8–45 | 524 |
| 0..30cm | sand | % | 46–64 | 26–88 | 524 |
| 0..30cm | silt | % | 13–22 | 0–34 | 524 |
| 0..30cm | bd.core | kg/m3 | 1340–1550 | 1180–1680 | 524 |
| 0..30cm | soc | g/kg | 4.5–10.6 | 1.7–23.2 | 524 |
| 0..30cm | ph.h2o | pH | 6.3–7.5 | 5.2–8.3 | 524 |
| 30..60cm | clay | % | 26–34 | 7–47 | 524 |
| 30..60cm | sand | % | 46–58 | 20–89 | 524 |
| 30..60cm | silt | % | 14–22 | 0–41 | 524 |
| 30..60cm | bd.core | kg/m3 | 1420–1550 | 1230–1690 | 524 |
| 30..60cm | soc | g/kg | 2.5–6 | 1–11.9 | 524 |
| 30..60cm | ph.h2o | pH | 6.5–7.8 | 5.6–8.8 | 524 |
| 60..100cm | clay | % | 27–36 | 9–51 | 524 |
| 60..100cm | sand | % | 42–57 | 11–89 | 524 |
| 60..100cm | silt | % | 15–23 | 0–44 | 524 |
| 60..100cm | bd.core | kg/m3 | 1440–1560 | 1220–1770 | 524 |
| 60..100cm | soc | g/kg | 2.3–4.7 | 1.1–10.2 | 524 |
| 60..100cm | ph.h2o | pH | 6.6–7.9 | 5.5–8.9 | 524 |
