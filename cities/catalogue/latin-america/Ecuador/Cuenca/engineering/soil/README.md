# Cuenca civil soil screening

1,906 route/station sample locations; 1,906 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 250 |
| fine-soil-plasticity-and-shrink-swell-tests | 1906 |
| granular-density-and-groundwater-tests | 264 |
| organic-content-and-compressibility-tests | 27 |

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
| 0..30cm | clay | % | 25–40 | 12–49 | 1906 |
| 0..30cm | sand | % | 28–53 | 10–80 | 1906 |
| 0..30cm | silt | % | 21–32 | 5–46 | 1906 |
| 0..30cm | bd.core | kg/m3 | 1070–1380 | 890–1610 | 1906 |
| 0..30cm | soc | g/kg | 5.7–38.9 | 2.1–66 | 1906 |
| 0..30cm | ph.h2o | pH | 5.6–7.6 | 5.1–8.2 | 1906 |
| 30..60cm | clay | % | 27–41 | 12–50 | 1906 |
| 30..60cm | sand | % | 27–51 | 10–81 | 1906 |
| 30..60cm | silt | % | 20–31 | 4–45 | 1906 |
| 30..60cm | bd.core | kg/m3 | 1130–1380 | 840–1630 | 1906 |
| 30..60cm | soc | g/kg | 5.1–26.6 | 1.3–47.1 | 1906 |
| 30..60cm | ph.h2o | pH | 5.6–7.6 | 5.1–8.2 | 1906 |
| 60..100cm | clay | % | 27–42 | 12–52 | 1906 |
| 60..100cm | sand | % | 28–51 | 9–82 | 1906 |
| 60..100cm | silt | % | 20–32 | 3–45 | 1906 |
| 60..100cm | bd.core | kg/m3 | 1160–1430 | 690–1680 | 1906 |
| 60..100cm | soc | g/kg | 3.2–26.3 | 0.7–66.8 | 1906 |
| 60..100cm | ph.h2o | pH | 5.7–7.6 | 5–8.4 | 1906 |
