# Hyderabad-Pk civil soil screening

624 route/station sample locations; 619 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 24 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 332 |
| granular-density-and-groundwater-tests | 619 |

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
| 0..30cm | clay | % | 13–22 | 0–37 | 619 |
| 0..30cm | sand | % | 49–68 | 26–94 | 619 |
| 0..30cm | silt | % | 19–29 | 3–42 | 619 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1220–1700 | 619 |
| 0..30cm | soc | g/kg | 2.2–5.8 | 0.5–12.8 | 619 |
| 0..30cm | ph.h2o | pH | 6.5–8.3 | 4.9–9.1 | 619 |
| 30..60cm | clay | % | 15–24 | 0–42 | 619 |
| 30..60cm | sand | % | 49–68 | 21–97 | 619 |
| 30..60cm | silt | % | 16–27 | 1–44 | 619 |
| 30..60cm | bd.core | kg/m3 | 1460–1570 | 1210–1740 | 619 |
| 30..60cm | soc | g/kg | 1.2–3.8 | 0–10.9 | 619 |
| 30..60cm | ph.h2o | pH | 6.3–8.8 | 4.3–9.6 | 619 |
| 60..100cm | clay | % | 16–24 | 0–42 | 619 |
| 60..100cm | sand | % | 50–68 | 17–96 | 619 |
| 60..100cm | silt | % | 16–26 | 0–44 | 619 |
| 60..100cm | bd.core | kg/m3 | 1460–1580 | 1240–1820 | 619 |
| 60..100cm | soc | g/kg | 1–3.2 | 0–7.8 | 619 |
| 60..100cm | ph.h2o | pH | 6.4–8.9 | 4.3–10.2 | 619 |
