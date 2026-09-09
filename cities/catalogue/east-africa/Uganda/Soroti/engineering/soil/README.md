# Soroti civil soil screening

25 route/station sample locations; 25 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 21 |
| fine-soil-plasticity-and-shrink-swell-tests | 13 |
| granular-density-and-groundwater-tests | 25 |

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
| 0..30cm | clay | % | 21–26 | 10–36 | 25 |
| 0..30cm | sand | % | 51–61 | 32–84 | 25 |
| 0..30cm | silt | % | 18–23 | 5–36 | 25 |
| 0..30cm | bd.core | kg/m3 | 1230–1290 | 1040–1480 | 25 |
| 0..30cm | soc | g/kg | 10.2–14.7 | 5.8–22.5 | 25 |
| 0..30cm | ph.h2o | pH | 6.1–6.2 | 5.5–6.9 | 25 |
| 30..60cm | clay | % | 21–26 | 10–40 | 25 |
| 30..60cm | sand | % | 50–60 | 25–83 | 25 |
| 30..60cm | silt | % | 19–24 | 4–41 | 25 |
| 30..60cm | bd.core | kg/m3 | 1280–1350 | 1100–1570 | 25 |
| 30..60cm | soc | g/kg | 5.4–7.1 | 3–12.4 | 25 |
| 30..60cm | ph.h2o | pH | 6.1–6.4 | 5.3–7.3 | 25 |
| 60..100cm | clay | % | 21–26 | 8–42 | 25 |
| 60..100cm | sand | % | 50–60 | 25–84 | 25 |
| 60..100cm | silt | % | 19–24 | 4–42 | 25 |
| 60..100cm | bd.core | kg/m3 | 1320–1380 | 1060–1610 | 25 |
| 60..100cm | soc | g/kg | 4.4–5.2 | 2.4–9.2 | 25 |
| 60..100cm | ph.h2o | pH | 6.3–6.7 | 5–8 | 25 |
