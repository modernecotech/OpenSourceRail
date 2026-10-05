# Kassala civil soil screening

280 route/station sample locations; 280 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 280 |
| granular-density-and-groundwater-tests | 9 |
| silt-moisture-frost-and-erosion-review | 42 |

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
| 0..30cm | clay | % | 27–34 | 12–43 | 280 |
| 0..30cm | sand | % | 25–39 | 11–70 | 280 |
| 0..30cm | silt | % | 33–41 | 19–52 | 280 |
| 0..30cm | bd.core | kg/m3 | 1460–1520 | 1210–1710 | 280 |
| 0..30cm | soc | g/kg | 3–6.5 | 1.1–11.2 | 280 |
| 0..30cm | ph.h2o | pH | 7.3–7.8 | 6–9 | 280 |
| 30..60cm | clay | % | 27–36 | 9–44 | 280 |
| 30..60cm | sand | % | 24–38 | 9–75 | 280 |
| 30..60cm | silt | % | 34–41 | 16–51 | 280 |
| 30..60cm | bd.core | kg/m3 | 1470–1520 | 1250–1720 | 280 |
| 30..60cm | soc | g/kg | 1.8–3 | 0.3–6.1 | 280 |
| 30..60cm | ph.h2o | pH | 8.2–8.5 | 7.1–9.6 | 280 |
| 60..100cm | clay | % | 26–35 | 9–44 | 280 |
| 60..100cm | sand | % | 25–40 | 10–72 | 280 |
| 60..100cm | silt | % | 33–40 | 16–52 | 280 |
| 60..100cm | bd.core | kg/m3 | 1460–1520 | 1240–1730 | 280 |
| 60..100cm | soc | g/kg | 1.4–2.1 | 0.3–4.8 | 280 |
| 60..100cm | ph.h2o | pH | 8.3–8.5 | 7.3–10 | 280 |
