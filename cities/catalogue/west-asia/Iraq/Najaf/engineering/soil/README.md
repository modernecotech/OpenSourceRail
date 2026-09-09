# Najaf civil soil screening

328 route/station sample locations; 292 complete profiles; 36 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 36 |
| fine-soil-plasticity-and-shrink-swell-tests | 110 |
| granular-density-and-groundwater-tests | 280 |
| silt-moisture-frost-and-erosion-review | 28 |

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
| 0..30cm | clay | % | 15–29 | 2–41 | 292 |
| 0..30cm | sand | % | 32–62 | 9–90 | 292 |
| 0..30cm | silt | % | 23–40 | 8–55 | 292 |
| 0..30cm | bd.core | kg/m3 | 1420–1520 | 1190–1710 | 292 |
| 0..30cm | soc | g/kg | 2.4–5.8 | 0.5–15.5 | 292 |
| 0..30cm | ph.h2o | pH | 7.6–8.7 | 6.1–9.7 | 292 |
| 30..60cm | clay | % | 16–30 | 1–42 | 292 |
| 30..60cm | sand | % | 33–62 | 11–91 | 292 |
| 30..60cm | silt | % | 22–37 | 4–55 | 292 |
| 30..60cm | bd.core | kg/m3 | 1410–1560 | 1220–1760 | 292 |
| 30..60cm | soc | g/kg | 1.6–3.7 | 0–10.4 | 292 |
| 30..60cm | ph.h2o | pH | 7.8–9.1 | 6.4–10.2 | 292 |
| 60..100cm | clay | % | 15–29 | 1–42 | 292 |
| 60..100cm | sand | % | 34–63 | 11–91 | 292 |
| 60..100cm | silt | % | 22–38 | 4–54 | 292 |
| 60..100cm | bd.core | kg/m3 | 1400–1620 | 1230–1910 | 292 |
| 60..100cm | soc | g/kg | 1.4–3.1 | 0–7.6 | 292 |
| 60..100cm | ph.h2o | pH | 7.8–9.2 | 6.1–10.2 | 292 |
