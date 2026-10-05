# Basra civil soil screening

1,585 route/station sample locations; 964 complete profiles; 621 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 621 |
| fine-soil-plasticity-and-shrink-swell-tests | 870 |
| granular-density-and-groundwater-tests | 809 |
| silt-moisture-frost-and-erosion-review | 136 |

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
| 0..30cm | clay | % | 16–28 | 2–38 | 964 |
| 0..30cm | sand | % | 31–58 | 13–84 | 964 |
| 0..30cm | silt | % | 25–42 | 11–55 | 964 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1190–1730 | 964 |
| 0..30cm | soc | g/kg | 2.4–5.7 | 0.4–12.7 | 964 |
| 0..30cm | ph.h2o | pH | 7.7–8.4 | 6.9–9.3 | 964 |
| 30..60cm | clay | % | 17–30 | 2–41 | 964 |
| 30..60cm | sand | % | 32–59 | 10–93 | 964 |
| 30..60cm | silt | % | 23–39 | 3–50 | 964 |
| 30..60cm | bd.core | kg/m3 | 1390–1520 | 1090–1760 | 964 |
| 30..60cm | soc | g/kg | 1.5–3.6 | 0–8.9 | 964 |
| 30..60cm | ph.h2o | pH | 8–8.7 | 6.7–10.2 | 964 |
| 60..100cm | clay | % | 17–29 | 2–42 | 964 |
| 60..100cm | sand | % | 33–59 | 9–93 | 964 |
| 60..100cm | silt | % | 24–39 | 4–54 | 964 |
| 60..100cm | bd.core | kg/m3 | 1360–1510 | 1090–1780 | 964 |
| 60..100cm | soc | g/kg | 1.4–3.7 | 0–9.8 | 964 |
| 60..100cm | ph.h2o | pH | 8.1–8.7 | 6.8–10.2 | 964 |
