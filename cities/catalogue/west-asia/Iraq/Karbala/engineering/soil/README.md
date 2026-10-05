# Karbala civil soil screening

327 route/station sample locations; 312 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 190 |
| granular-density-and-groundwater-tests | 278 |
| silt-moisture-frost-and-erosion-review | 36 |

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
| 0..30cm | clay | % | 14–29 | 2–41 | 312 |
| 0..30cm | sand | % | 33–60 | 10–87 | 312 |
| 0..30cm | silt | % | 24–38 | 8–54 | 312 |
| 0..30cm | bd.core | kg/m3 | 1430–1510 | 1210–1710 | 312 |
| 0..30cm | soc | g/kg | 2.4–6 | 0.5–13.2 | 312 |
| 0..30cm | ph.h2o | pH | 7.9–8.6 | 6.8–9.7 | 312 |
| 30..60cm | clay | % | 16–30 | 2–42 | 312 |
| 30..60cm | sand | % | 34–60 | 10–92 | 312 |
| 30..60cm | silt | % | 24–37 | 5–51 | 312 |
| 30..60cm | bd.core | kg/m3 | 1430–1600 | 1220–1770 | 312 |
| 30..60cm | soc | g/kg | 1.9–4.1 | 0–12.8 | 312 |
| 30..60cm | ph.h2o | pH | 7.7–9.1 | 6.3–10.2 | 312 |
| 60..100cm | clay | % | 16–29 | 2–40 | 312 |
| 60..100cm | sand | % | 33–60 | 8–91 | 312 |
| 60..100cm | silt | % | 24–38 | 5–55 | 312 |
| 60..100cm | bd.core | kg/m3 | 1420–1670 | 1230–1950 | 312 |
| 60..100cm | soc | g/kg | 1.5–3.3 | 0–8.1 | 312 |
| 60..100cm | ph.h2o | pH | 7.5–9.1 | 5.5–10.2 | 312 |
