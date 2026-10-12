# Mombasa civil soil screening

4,264 route/station sample locations; 4,239 complete profiles; 25 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3521 |
| coverage-gap | 25 |
| fine-soil-plasticity-and-shrink-swell-tests | 2116 |
| granular-density-and-groundwater-tests | 4010 |
| organic-content-and-compressibility-tests | 221 |

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
| 0..30cm | clay | % | 8–37 | 1–51 | 4239 |
| 0..30cm | sand | % | 31–84 | 3–98 | 4239 |
| 0..30cm | silt | % | 8–32 | 0–47 | 4239 |
| 0..30cm | bd.core | kg/m3 | 660–1480 | 460–1650 | 4239 |
| 0..30cm | soc | g/kg | 4–48.8 | 1.6–109.1 | 4239 |
| 0..30cm | ph.h2o | pH | 6.1–7 | 5–8 | 4239 |
| 30..60cm | clay | % | 7–40 | 1–55 | 4239 |
| 30..60cm | sand | % | 29–86 | 1–97 | 4239 |
| 30..60cm | silt | % | 6–32 | 0–49 | 4239 |
| 30..60cm | bd.core | kg/m3 | 630–1520 | 440–1730 | 4239 |
| 30..60cm | soc | g/kg | 3.1–50.6 | 0.9–103.6 | 4239 |
| 30..60cm | ph.h2o | pH | 6–7.2 | 5.1–8.2 | 4239 |
| 60..100cm | clay | % | 7–40 | 1–54 | 4239 |
| 60..100cm | sand | % | 29–85 | 1–97 | 4239 |
| 60..100cm | silt | % | 7–32 | 0–49 | 4239 |
| 60..100cm | bd.core | kg/m3 | 640–1540 | 410–1810 | 4239 |
| 60..100cm | soc | g/kg | 2.1–44.5 | 0.6–111.2 | 4239 |
| 60..100cm | ph.h2o | pH | 6–7.2 | 4.7–8.5 | 4239 |
