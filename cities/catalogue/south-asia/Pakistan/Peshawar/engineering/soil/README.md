# Peshawar civil soil screening

349 route/station sample locations; 349 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 349 |
| granular-density-and-groundwater-tests | 174 |
| silt-moisture-frost-and-erosion-review | 31 |

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
| 0..30cm | clay | % | 22–29 | 7–46 | 349 |
| 0..30cm | sand | % | 37–49 | 11–80 | 349 |
| 0..30cm | silt | % | 27–35 | 10–51 | 349 |
| 0..30cm | bd.core | kg/m3 | 1300–1520 | 1060–1670 | 349 |
| 0..30cm | soc | g/kg | 4.3–7.6 | 1.7–19.1 | 349 |
| 0..30cm | ph.h2o | pH | 7–7.8 | 5.9–8.6 | 349 |
| 30..60cm | clay | % | 22–30 | 8–46 | 349 |
| 30..60cm | sand | % | 37–51 | 11–80 | 349 |
| 30..60cm | silt | % | 27–35 | 10–52 | 349 |
| 30..60cm | bd.core | kg/m3 | 1400–1560 | 1130–1750 | 349 |
| 30..60cm | soc | g/kg | 2.7–5 | 0.7–10.9 | 349 |
| 30..60cm | ph.h2o | pH | 7–8 | 5.9–9 | 349 |
| 60..100cm | clay | % | 23–30 | 8–46 | 349 |
| 60..100cm | sand | % | 38–51 | 12–80 | 349 |
| 60..100cm | silt | % | 26–35 | 8–52 | 349 |
| 60..100cm | bd.core | kg/m3 | 1450–1590 | 1170–1820 | 349 |
| 60..100cm | soc | g/kg | 2–3.9 | 0.6–8.1 | 349 |
| 60..100cm | ph.h2o | pH | 7–8.2 | 5.8–9.2 | 349 |
