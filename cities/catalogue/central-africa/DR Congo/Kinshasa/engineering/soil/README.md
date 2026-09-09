# Kinshasa civil soil screening

1,077 route/station sample locations; 1,027 complete profiles; 50 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1026 |
| coverage-gap | 50 |
| fine-soil-plasticity-and-shrink-swell-tests | 1027 |
| granular-density-and-groundwater-tests | 232 |
| organic-content-and-compressibility-tests | 2 |
| silt-moisture-frost-and-erosion-review | 15 |

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
| 0..30cm | clay | % | 26–35 | 9–48 | 1027 |
| 0..30cm | sand | % | 37–55 | 10–81 | 1027 |
| 0..30cm | silt | % | 19–29 | 1–48 | 1027 |
| 0..30cm | bd.core | kg/m3 | 1170–1400 | 910–1600 | 1027 |
| 0..30cm | soc | g/kg | 6.3–15.2 | 2.5–35.1 | 1027 |
| 0..30cm | ph.h2o | pH | 5.4–6.6 | 4.4–7.7 | 1027 |
| 30..60cm | clay | % | 28–40 | 9–54 | 1027 |
| 30..60cm | sand | % | 33–52 | 8–86 | 1027 |
| 30..60cm | silt | % | 17–30 | 0–51 | 1027 |
| 30..60cm | bd.core | kg/m3 | 1190–1440 | 870–1640 | 1027 |
| 30..60cm | soc | g/kg | 4.1–12.1 | 1.5–35.9 | 1027 |
| 30..60cm | ph.h2o | pH | 5.4–6.7 | 4.6–7.6 | 1027 |
| 60..100cm | clay | % | 28–42 | 8–55 | 1027 |
| 60..100cm | sand | % | 31–51 | 5–87 | 1027 |
| 60..100cm | silt | % | 17–31 | 0–51 | 1027 |
| 60..100cm | bd.core | kg/m3 | 1150–1430 | 780–1660 | 1027 |
| 60..100cm | soc | g/kg | 3.7–13.7 | 1.1–50.5 | 1027 |
| 60..100cm | ph.h2o | pH | 5.5–6.6 | 4.6–7.8 | 1027 |
