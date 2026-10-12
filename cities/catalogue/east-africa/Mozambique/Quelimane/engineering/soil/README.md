# Quelimane civil soil screening

217 route/station sample locations; 217 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 150 |
| fine-soil-plasticity-and-shrink-swell-tests | 217 |
| granular-density-and-groundwater-tests | 217 |

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
| 0..30cm | clay | % | 24–35 | 10–52 | 217 |
| 0..30cm | sand | % | 41–62 | 7–87 | 217 |
| 0..30cm | silt | % | 14–23 | 0–39 | 217 |
| 0..30cm | bd.core | kg/m3 | 1250–1320 | 1010–1510 | 217 |
| 0..30cm | soc | g/kg | 5.4–10.4 | 2.2–21.2 | 217 |
| 0..30cm | ph.h2o | pH | 6.4–6.9 | 5.4–7.9 | 217 |
| 30..60cm | clay | % | 26–38 | 10–55 | 217 |
| 30..60cm | sand | % | 41–61 | 10–88 | 217 |
| 30..60cm | silt | % | 13–22 | 0–37 | 217 |
| 30..60cm | bd.core | kg/m3 | 1180–1310 | 840–1590 | 217 |
| 30..60cm | soc | g/kg | 3.3–6.3 | 1.4–12.3 | 217 |
| 30..60cm | ph.h2o | pH | 6.6–7.1 | 5.6–8.3 | 217 |
| 60..100cm | clay | % | 27–39 | 10–58 | 217 |
| 60..100cm | sand | % | 41–60 | 9–89 | 217 |
| 60..100cm | silt | % | 12–20 | 0–37 | 217 |
| 60..100cm | bd.core | kg/m3 | 1120–1260 | 760–1670 | 217 |
| 60..100cm | soc | g/kg | 3.4–5.6 | 1.3–11.1 | 217 |
| 60..100cm | ph.h2o | pH | 6.7–7 | 5–8.6 | 217 |
