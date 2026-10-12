# Morogoro civil soil screening

1,205 route/station sample locations; 1,205 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1021 |
| fine-soil-plasticity-and-shrink-swell-tests | 1197 |
| granular-density-and-groundwater-tests | 983 |
| organic-content-and-compressibility-tests | 2 |

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
| 0..30cm | clay | % | 22–41 | 10–54 | 1205 |
| 0..30cm | sand | % | 34–67 | 11–89 | 1205 |
| 0..30cm | silt | % | 9–27 | 0–40 | 1205 |
| 0..30cm | bd.core | kg/m3 | 1140–1420 | 930–1580 | 1205 |
| 0..30cm | soc | g/kg | 5.8–26.9 | 2.6–61.2 | 1205 |
| 0..30cm | ph.h2o | pH | 5.6–7.3 | 4.8–8.2 | 1205 |
| 30..60cm | clay | % | 23–44 | 10–55 | 1205 |
| 30..60cm | sand | % | 31–67 | 12–89 | 1205 |
| 30..60cm | silt | % | 9–27 | 0–42 | 1205 |
| 30..60cm | bd.core | kg/m3 | 1170–1440 | 960–1630 | 1205 |
| 30..60cm | soc | g/kg | 3.8–10 | 1.7–15.5 | 1205 |
| 30..60cm | ph.h2o | pH | 5.4–7.4 | 4.7–8.2 | 1205 |
| 60..100cm | clay | % | 23–45 | 10–56 | 1205 |
| 60..100cm | sand | % | 30–68 | 11–89 | 1205 |
| 60..100cm | silt | % | 8–28 | 0–43 | 1205 |
| 60..100cm | bd.core | kg/m3 | 1180–1450 | 980–1710 | 1205 |
| 60..100cm | soc | g/kg | 3.5–6.7 | 1.4–11.1 | 1205 |
| 60..100cm | ph.h2o | pH | 5.4–7.5 | 4.6–8.5 | 1205 |
