# Gazipur civil soil screening

6,335 route/station sample locations; 6,331 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6331 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 6330 |
| granular-density-and-groundwater-tests | 6028 |
| organic-content-and-compressibility-tests | 2169 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 20–30 | 6–47 | 6331 |
| 0..30cm | sand | % | 40–60 | 9–90 | 6331 |
| 0..30cm | silt | % | 19–31 | 0–50 | 6331 |
| 0..30cm | bd.core | kg/m3 | 800–1370 | 430–1610 | 6331 |
| 0..30cm | soc | g/kg | 10.9–30.2 | 3.7–87.6 | 6331 |
| 0..30cm | ph.h2o | pH | 5.6–6.2 | 4.1–7.6 | 6331 |
| 30..60cm | clay | % | 21–31 | 4–49 | 6331 |
| 30..60cm | sand | % | 39–61 | 7–90 | 6331 |
| 30..60cm | silt | % | 17–31 | 0–49 | 6331 |
| 30..60cm | bd.core | kg/m3 | 890–1390 | 530–1600 | 6331 |
| 30..60cm | soc | g/kg | 4.9–24.6 | 1.2–82.5 | 6331 |
| 30..60cm | ph.h2o | pH | 5.8–6.5 | 4.6–7.9 | 6331 |
| 60..100cm | clay | % | 22–32 | 5–50 | 6331 |
| 60..100cm | sand | % | 38–57 | 8–89 | 6331 |
| 60..100cm | silt | % | 18–31 | 0–49 | 6331 |
| 60..100cm | bd.core | kg/m3 | 910–1390 | 460–1620 | 6331 |
| 60..100cm | soc | g/kg | 3.4–16.9 | 1–67.5 | 6331 |
| 60..100cm | ph.h2o | pH | 6–6.7 | 4.6–8.2 | 6331 |
