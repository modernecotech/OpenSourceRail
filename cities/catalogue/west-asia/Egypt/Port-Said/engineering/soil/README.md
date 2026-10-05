# Port-Said civil soil screening

37 route/station sample locations; 33 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 21 |
| granular-density-and-groundwater-tests | 33 |

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
| 0..30cm | clay | % | 16–23 | 1–35 | 33 |
| 0..30cm | sand | % | 50–66 | 31–91 | 33 |
| 0..30cm | silt | % | 18–27 | 4–38 | 33 |
| 0..30cm | bd.core | kg/m3 | 1400–1460 | 1100–1670 | 33 |
| 0..30cm | soc | g/kg | 3–5 | 0.9–10.9 | 33 |
| 0..30cm | ph.h2o | pH | 7.9–8.5 | 7.2–9 | 33 |
| 30..60cm | clay | % | 18–24 | 1–37 | 33 |
| 30..60cm | sand | % | 51–63 | 28–92 | 33 |
| 30..60cm | silt | % | 19–26 | 0–39 | 33 |
| 30..60cm | bd.core | kg/m3 | 1490–1580 | 1250–1840 | 33 |
| 30..60cm | soc | g/kg | 1.6–3.5 | 0.1–8.9 | 33 |
| 30..60cm | ph.h2o | pH | 8–8.5 | 6.5–9.3 | 33 |
| 60..100cm | clay | % | 18–24 | 1–38 | 33 |
| 60..100cm | sand | % | 51–64 | 27–91 | 33 |
| 60..100cm | silt | % | 18–25 | 0–40 | 33 |
| 60..100cm | bd.core | kg/m3 | 1480–1600 | 1110–1890 | 33 |
| 60..100cm | soc | g/kg | 1.3–4 | 0.2–9.5 | 33 |
| 60..100cm | ph.h2o | pH | 8–8.6 | 7–9.5 | 33 |
