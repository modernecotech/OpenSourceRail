# Quetta civil soil screening

222 route/station sample locations; 222 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 104 |
| granular-density-and-groundwater-tests | 220 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 16–22 | 3–33 | 222 |
| 0..30cm | sand | % | 42–60 | 17–81 | 222 |
| 0..30cm | silt | % | 24–36 | 10–51 | 222 |
| 0..30cm | bd.core | kg/m3 | 1390–1490 | 1220–1610 | 222 |
| 0..30cm | soc | g/kg | 2.7–9.4 | 0.9–19.3 | 222 |
| 0..30cm | ph.h2o | pH | 7.3–8.1 | 6.6–8.6 | 222 |
| 30..60cm | clay | % | 15–23 | 1–38 | 222 |
| 30..60cm | sand | % | 43–63 | 15–86 | 222 |
| 30..60cm | silt | % | 22–34 | 7–49 | 222 |
| 30..60cm | bd.core | kg/m3 | 1390–1520 | 1180–1700 | 222 |
| 30..60cm | soc | g/kg | 2.3–5.5 | 0.8–10.9 | 222 |
| 30..60cm | ph.h2o | pH | 7.5–8.5 | 6.6–9.3 | 222 |
| 60..100cm | clay | % | 15–24 | 1–41 | 222 |
| 60..100cm | sand | % | 44–64 | 10–87 | 222 |
| 60..100cm | silt | % | 20–32 | 5–50 | 222 |
| 60..100cm | bd.core | kg/m3 | 1420–1550 | 1030–1740 | 222 |
| 60..100cm | soc | g/kg | 1.7–3.3 | 0.5–6.5 | 222 |
| 60..100cm | ph.h2o | pH | 7.7–8.7 | 6.7–9.5 | 222 |
