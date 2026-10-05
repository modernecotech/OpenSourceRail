# Damanhur civil soil screening

69 route/station sample locations; 69 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 66 |
| granular-density-and-groundwater-tests | 69 |
| organic-content-and-compressibility-tests | 4 |

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
| 0..30cm | clay | % | 18–25 | 5–39 | 69 |
| 0..30cm | sand | % | 48–64 | 16–89 | 69 |
| 0..30cm | silt | % | 18–27 | 7–43 | 69 |
| 0..30cm | bd.core | kg/m3 | 1310–1460 | 1110–1660 | 69 |
| 0..30cm | soc | g/kg | 3.2–15.6 | 1.6–43.4 | 69 |
| 0..30cm | ph.h2o | pH | 7.6–8.5 | 6.8–9 | 69 |
| 30..60cm | clay | % | 18–27 | 6–42 | 69 |
| 30..60cm | sand | % | 47–65 | 16–88 | 69 |
| 30..60cm | silt | % | 17–26 | 1–42 | 69 |
| 30..60cm | bd.core | kg/m3 | 1400–1570 | 1110–1800 | 69 |
| 30..60cm | soc | g/kg | 1.8–10.9 | 0.5–43.2 | 69 |
| 30..60cm | ph.h2o | pH | 7.4–8.5 | 5.8–9.4 | 69 |
| 60..100cm | clay | % | 18–27 | 6–43 | 69 |
| 60..100cm | sand | % | 47–65 | 15–88 | 69 |
| 60..100cm | silt | % | 17–26 | 0–43 | 69 |
| 60..100cm | bd.core | kg/m3 | 1410–1580 | 1010–1890 | 69 |
| 60..100cm | soc | g/kg | 1.4–13.1 | 0.4–113.8 | 69 |
| 60..100cm | ph.h2o | pH | 7.1–8.6 | 3.5–9.3 | 69 |
