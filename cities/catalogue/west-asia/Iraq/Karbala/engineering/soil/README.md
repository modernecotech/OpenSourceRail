# Karbala civil soil screening

250 route/station sample locations; 239 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 146 |
| granular-density-and-groundwater-tests | 214 |
| silt-moisture-frost-and-erosion-review | 34 |

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
| 0..30cm | clay | % | 15–29 | 2–41 | 239 |
| 0..30cm | sand | % | 33–60 | 10–87 | 239 |
| 0..30cm | silt | % | 24–38 | 8–54 | 239 |
| 0..30cm | bd.core | kg/m3 | 1430–1510 | 1220–1710 | 239 |
| 0..30cm | soc | g/kg | 2.4–5.9 | 0.5–12.4 | 239 |
| 0..30cm | ph.h2o | pH | 7.9–8.6 | 6.8–9.7 | 239 |
| 30..60cm | clay | % | 16–30 | 2–42 | 239 |
| 30..60cm | sand | % | 34–59 | 9–92 | 239 |
| 30..60cm | silt | % | 24–37 | 5–55 | 239 |
| 30..60cm | bd.core | kg/m3 | 1400–1570 | 1220–1770 | 239 |
| 30..60cm | soc | g/kg | 1.8–3.5 | 0–10.5 | 239 |
| 30..60cm | ph.h2o | pH | 8–9.1 | 6.6–10.2 | 239 |
| 60..100cm | clay | % | 16–29 | 2–42 | 239 |
| 60..100cm | sand | % | 33–60 | 8–91 | 239 |
| 60..100cm | silt | % | 24–38 | 5–59 | 239 |
| 60..100cm | bd.core | kg/m3 | 1420–1630 | 1230–1940 | 239 |
| 60..100cm | soc | g/kg | 1.6–3 | 0–7.4 | 239 |
| 60..100cm | ph.h2o | pH | 7.8–9.1 | 6–10.2 | 239 |
