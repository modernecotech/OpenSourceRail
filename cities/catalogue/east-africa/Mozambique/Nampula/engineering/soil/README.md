# Nampula civil soil screening

116 route/station sample locations; 116 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 35 |
| fine-soil-plasticity-and-shrink-swell-tests | 116 |
| granular-density-and-groundwater-tests | 116 |

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
| 0..30cm | clay | % | 23–30 | 9–43 | 116 |
| 0..30cm | sand | % | 51–66 | 30–89 | 116 |
| 0..30cm | silt | % | 11–19 | 0–30 | 116 |
| 0..30cm | bd.core | kg/m3 | 1320–1440 | 1160–1590 | 116 |
| 0..30cm | soc | g/kg | 5.7–8.5 | 2.8–14.4 | 116 |
| 0..30cm | ph.h2o | pH | 6.1–6.5 | 5.4–7.8 | 116 |
| 30..60cm | clay | % | 28–37 | 10–52 | 116 |
| 30..60cm | sand | % | 44–63 | 20–89 | 116 |
| 30..60cm | silt | % | 10–19 | 0–33 | 116 |
| 30..60cm | bd.core | kg/m3 | 1340–1470 | 1170–1620 | 116 |
| 30..60cm | soc | g/kg | 3.4–4.8 | 1.5–8.3 | 116 |
| 30..60cm | ph.h2o | pH | 6.2–6.6 | 5.4–7.6 | 116 |
| 60..100cm | clay | % | 30–40 | 10–55 | 116 |
| 60..100cm | sand | % | 40–61 | 15–89 | 116 |
| 60..100cm | silt | % | 10–20 | 0–37 | 116 |
| 60..100cm | bd.core | kg/m3 | 1300–1510 | 1070–1720 | 116 |
| 60..100cm | soc | g/kg | 2.9–3.7 | 1.3–6.8 | 116 |
| 60..100cm | ph.h2o | pH | 6.3–6.9 | 5.3–8.2 | 116 |
