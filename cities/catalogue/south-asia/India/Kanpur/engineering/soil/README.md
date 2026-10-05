# Kanpur civil soil screening

755 route/station sample locations; 755 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 348 |
| granular-density-and-groundwater-tests | 755 |

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
| 0..30cm | clay | % | 10–22 | 0–37 | 755 |
| 0..30cm | sand | % | 52–78 | 20–99 | 755 |
| 0..30cm | silt | % | 12–26 | 0–47 | 755 |
| 0..30cm | bd.core | kg/m3 | 1340–1530 | 1140–1710 | 755 |
| 0..30cm | soc | g/kg | 2.9–8.7 | 0.8–20.6 | 755 |
| 0..30cm | ph.h2o | pH | 6.4–7.3 | 5.4–8.2 | 755 |
| 30..60cm | clay | % | 12–25 | 0–40 | 755 |
| 30..60cm | sand | % | 47–76 | 14–99 | 755 |
| 30..60cm | silt | % | 11–28 | 0–48 | 755 |
| 30..60cm | bd.core | kg/m3 | 1440–1610 | 1200–1770 | 755 |
| 30..60cm | soc | g/kg | 1.8–5.3 | 0.3–12.1 | 755 |
| 30..60cm | ph.h2o | pH | 6.5–7.5 | 5.5–8.4 | 755 |
| 60..100cm | clay | % | 12–26 | 0–41 | 755 |
| 60..100cm | sand | % | 46–75 | 14–99 | 755 |
| 60..100cm | silt | % | 11–28 | 0–48 | 755 |
| 60..100cm | bd.core | kg/m3 | 1530–1650 | 1220–1860 | 755 |
| 60..100cm | soc | g/kg | 1.3–4 | 0.3–10.6 | 755 |
| 60..100cm | ph.h2o | pH | 6.6–7.6 | 5.5–8.5 | 755 |
