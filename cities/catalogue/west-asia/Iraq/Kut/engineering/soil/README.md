# Kut civil soil screening

350 route/station sample locations; 346 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 282 |
| granular-density-and-groundwater-tests | 204 |
| silt-moisture-frost-and-erosion-review | 152 |

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
| 0..30cm | clay | % | 17–31 | 6–41 | 346 |
| 0..30cm | sand | % | 27–55 | 9–78 | 346 |
| 0..30cm | silt | % | 28–42 | 12–55 | 346 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1250–1660 | 346 |
| 0..30cm | soc | g/kg | 2.4–5 | 0.7–11 | 346 |
| 0..30cm | ph.h2o | pH | 7.7–8.1 | 7–8.9 | 346 |
| 30..60cm | clay | % | 19–32 | 2–43 | 346 |
| 30..60cm | sand | % | 31–56 | 11–88 | 346 |
| 30..60cm | silt | % | 25–37 | 8–54 | 346 |
| 30..60cm | bd.core | kg/m3 | 1410–1560 | 1180–1730 | 346 |
| 30..60cm | soc | g/kg | 1.8–3.3 | 0–8.4 | 346 |
| 30..60cm | ph.h2o | pH | 7.8–8.5 | 6.7–10.1 | 346 |
| 60..100cm | clay | % | 19–32 | 3–44 | 346 |
| 60..100cm | sand | % | 33–56 | 11–87 | 346 |
| 60..100cm | silt | % | 23–36 | 6–52 | 346 |
| 60..100cm | bd.core | kg/m3 | 1400–1620 | 1180–1920 | 346 |
| 60..100cm | soc | g/kg | 1.7–2.9 | 0–7.9 | 346 |
| 60..100cm | ph.h2o | pH | 7.9–8.6 | 6.7–10.2 | 346 |
