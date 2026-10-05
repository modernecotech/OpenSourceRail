# Jalalabad-Af civil soil screening

133 route/station sample locations; 131 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 98 |
| granular-density-and-groundwater-tests | 90 |
| silt-moisture-frost-and-erosion-review | 24 |

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
| 0..30cm | clay | % | 19–24 | 6–37 | 131 |
| 0..30cm | sand | % | 44–54 | 17–75 | 131 |
| 0..30cm | silt | % | 27–33 | 11–51 | 131 |
| 0..30cm | bd.core | kg/m3 | 1360–1490 | 1090–1670 | 131 |
| 0..30cm | soc | g/kg | 3.8–6.5 | 1.7–14.8 | 131 |
| 0..30cm | ph.h2o | pH | 7.4–8.1 | 6.4–8.6 | 131 |
| 30..60cm | clay | % | 20–26 | 7–38 | 131 |
| 30..60cm | sand | % | 42–52 | 18–81 | 131 |
| 30..60cm | silt | % | 27–33 | 9–49 | 131 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1250–1770 | 131 |
| 30..60cm | soc | g/kg | 2.6–4.4 | 1–9 | 131 |
| 30..60cm | ph.h2o | pH | 7.4–8.2 | 6.6–8.9 | 131 |
| 60..100cm | clay | % | 20–26 | 7–39 | 131 |
| 60..100cm | sand | % | 42–53 | 14–82 | 131 |
| 60..100cm | silt | % | 26–33 | 8–52 | 131 |
| 60..100cm | bd.core | kg/m3 | 1510–1610 | 1290–1880 | 131 |
| 60..100cm | soc | g/kg | 2–3.3 | 0.4–9.1 | 131 |
| 60..100cm | ph.h2o | pH | 7.5–8.3 | 6.2–9 | 131 |
