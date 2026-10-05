# Deir-Ez-Zor civil soil screening

183 route/station sample locations; 172 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 164 |
| granular-density-and-groundwater-tests | 131 |

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
| 0..30cm | clay | % | 17–26 | 5–38 | 172 |
| 0..30cm | sand | % | 39–58 | 19–83 | 172 |
| 0..30cm | silt | % | 23–35 | 10–47 | 172 |
| 0..30cm | bd.core | kg/m3 | 1440–1510 | 1260–1700 | 172 |
| 0..30cm | soc | g/kg | 1.9–6.3 | 0.5–11.6 | 172 |
| 0..30cm | ph.h2o | pH | 7.8–8.2 | 7.1–9 | 172 |
| 30..60cm | clay | % | 19–28 | 3–41 | 172 |
| 30..60cm | sand | % | 40–59 | 14–92 | 172 |
| 30..60cm | silt | % | 22–32 | 5–48 | 172 |
| 30..60cm | bd.core | kg/m3 | 1440–1580 | 1240–1780 | 172 |
| 30..60cm | soc | g/kg | 1.2–3.6 | 0–8.5 | 172 |
| 30..60cm | ph.h2o | pH | 8–8.6 | 7–10.1 | 172 |
| 60..100cm | clay | % | 20–28 | 3–43 | 172 |
| 60..100cm | sand | % | 41–59 | 17–90 | 172 |
| 60..100cm | silt | % | 21–31 | 2–47 | 172 |
| 60..100cm | bd.core | kg/m3 | 1450–1620 | 1230–1920 | 172 |
| 60..100cm | soc | g/kg | 1–2.5 | 0–5.2 | 172 |
| 60..100cm | ph.h2o | pH | 8.1–8.8 | 7.2–10.1 | 172 |
