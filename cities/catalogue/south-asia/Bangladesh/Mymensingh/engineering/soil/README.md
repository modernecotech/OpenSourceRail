# Mymensingh civil soil screening

1,634 route/station sample locations; 1,633 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1633 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1633 |
| granular-density-and-groundwater-tests | 1145 |
| organic-content-and-compressibility-tests | 967 |
| silt-moisture-frost-and-erosion-review | 88 |

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
| 0..30cm | clay | % | 23–31 | 6–47 | 1633 |
| 0..30cm | sand | % | 37–54 | 10–83 | 1633 |
| 0..30cm | silt | % | 23–32 | 0–50 | 1633 |
| 0..30cm | bd.core | kg/m3 | 840–1080 | 430–1370 | 1633 |
| 0..30cm | soc | g/kg | 11.8–24.8 | 4.2–80.5 | 1633 |
| 0..30cm | ph.h2o | pH | 5.4–6 | 4.4–7.4 | 1633 |
| 30..60cm | clay | % | 23–31 | 5–46 | 1633 |
| 30..60cm | sand | % | 37–53 | 10–83 | 1633 |
| 30..60cm | silt | % | 24–32 | 0–50 | 1633 |
| 30..60cm | bd.core | kg/m3 | 870–1140 | 520–1470 | 1633 |
| 30..60cm | soc | g/kg | 5.4–18.4 | 1.4–67.7 | 1633 |
| 30..60cm | ph.h2o | pH | 5.5–6.2 | 4.4–7.7 | 1633 |
| 60..100cm | clay | % | 24–32 | 6–46 | 1633 |
| 60..100cm | sand | % | 36–51 | 7–82 | 1633 |
| 60..100cm | silt | % | 24–32 | 2–51 | 1633 |
| 60..100cm | bd.core | kg/m3 | 920–1120 | 510–1490 | 1633 |
| 60..100cm | soc | g/kg | 4.6–15.9 | 1.3–221.2 | 1633 |
| 60..100cm | ph.h2o | pH | 5.6–6.4 | 4.4–8 | 1633 |
