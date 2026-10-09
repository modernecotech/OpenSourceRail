# Idlib civil soil screening

278 route/station sample locations; 278 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 277 |
| granular-density-and-groundwater-tests | 49 |
| silt-moisture-frost-and-erosion-review | 137 |

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
| 0..30cm | clay | % | 23–32 | 11–43 | 278 |
| 0..30cm | sand | % | 30–46 | 10–68 | 278 |
| 0..30cm | silt | % | 31–39 | 17–55 | 278 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1240–1660 | 278 |
| 0..30cm | soc | g/kg | 4.2–11.7 | 1.6–19.5 | 278 |
| 0..30cm | ph.h2o | pH | 7–7.7 | 6.1–8.4 | 278 |
| 30..60cm | clay | % | 25–36 | 10–48 | 278 |
| 30..60cm | sand | % | 31–48 | 10–80 | 278 |
| 30..60cm | silt | % | 27–36 | 10–50 | 278 |
| 30..60cm | bd.core | kg/m3 | 1490–1630 | 1270–1820 | 278 |
| 30..60cm | soc | g/kg | 2.5–5.5 | 0.8–8.8 | 278 |
| 30..60cm | ph.h2o | pH | 7.2–7.7 | 6.1–8.4 | 278 |
| 60..100cm | clay | % | 25–37 | 10–50 | 278 |
| 60..100cm | sand | % | 32–50 | 10–80 | 278 |
| 60..100cm | silt | % | 24–33 | 5–51 | 278 |
| 60..100cm | bd.core | kg/m3 | 1490–1670 | 1280–1840 | 278 |
| 60..100cm | soc | g/kg | 2–3.9 | 0.6–7.2 | 278 |
| 60..100cm | ph.h2o | pH | 7.3–7.8 | 6.3–8.7 | 278 |
