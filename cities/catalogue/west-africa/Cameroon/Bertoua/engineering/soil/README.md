# Bertoua civil soil screening

69 route/station sample locations; 69 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 69 |
| fine-soil-plasticity-and-shrink-swell-tests | 69 |
| granular-density-and-groundwater-tests | 68 |

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
| 0..30cm | clay | % | 24–29 | 9–43 | 69 |
| 0..30cm | sand | % | 49–57 | 22–83 | 69 |
| 0..30cm | silt | % | 18–22 | 2–36 | 69 |
| 0..30cm | bd.core | kg/m3 | 1160–1410 | 1020–1570 | 69 |
| 0..30cm | soc | g/kg | 7–16.7 | 3.2–28.1 | 69 |
| 0..30cm | ph.h2o | pH | 5.5–6.1 | 4.5–6.9 | 69 |
| 30..60cm | clay | % | 27–33 | 8–51 | 69 |
| 30..60cm | sand | % | 43–54 | 14–82 | 69 |
| 30..60cm | silt | % | 19–25 | 0–42 | 69 |
| 30..60cm | bd.core | kg/m3 | 1260–1460 | 1090–1700 | 69 |
| 30..60cm | soc | g/kg | 3.4–6.8 | 1.6–10.9 | 69 |
| 30..60cm | ph.h2o | pH | 5.6–6.1 | 4.5–6.8 | 69 |
| 60..100cm | clay | % | 28–36 | 8–52 | 69 |
| 60..100cm | sand | % | 38–52 | 12–80 | 69 |
| 60..100cm | silt | % | 20–27 | 1–45 | 69 |
| 60..100cm | bd.core | kg/m3 | 1250–1480 | 1050–1740 | 69 |
| 60..100cm | soc | g/kg | 4–5.2 | 2.1–10.3 | 69 |
| 60..100cm | ph.h2o | pH | 5.7–6.2 | 4.6–7.1 | 69 |
