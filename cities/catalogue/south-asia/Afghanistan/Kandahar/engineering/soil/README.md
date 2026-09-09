# Kandahar civil soil screening

86 route/station sample locations; 86 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 69 |
| granular-density-and-groundwater-tests | 70 |
| silt-moisture-frost-and-erosion-review | 15 |

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
| 0..30cm | clay | % | 15–29 | 0–38 | 86 |
| 0..30cm | sand | % | 31–59 | 12–88 | 86 |
| 0..30cm | silt | % | 26–40 | 9–55 | 86 |
| 0..30cm | bd.core | kg/m3 | 1440–1480 | 1260–1670 | 86 |
| 0..30cm | soc | g/kg | 2.2–5.5 | 0.6–9.9 | 86 |
| 0..30cm | ph.h2o | pH | 7.8–8.1 | 7.2–8.8 | 86 |
| 30..60cm | clay | % | 17–29 | 0–42 | 86 |
| 30..60cm | sand | % | 33–59 | 8–91 | 86 |
| 30..60cm | silt | % | 24–38 | 5–51 | 86 |
| 30..60cm | bd.core | kg/m3 | 1390–1510 | 1090–1690 | 86 |
| 30..60cm | soc | g/kg | 1.6–3.2 | 0.2–6.6 | 86 |
| 30..60cm | ph.h2o | pH | 8–8.5 | 7.1–9.5 | 86 |
| 60..100cm | clay | % | 17–30 | 0–43 | 86 |
| 60..100cm | sand | % | 32–60 | 9–91 | 86 |
| 60..100cm | silt | % | 23–38 | 3–54 | 86 |
| 60..100cm | bd.core | kg/m3 | 1390–1530 | 1090–1710 | 86 |
| 60..100cm | soc | g/kg | 1.4–2.2 | 0.2–4.9 | 86 |
| 60..100cm | ph.h2o | pH | 8–8.7 | 7–9.9 | 86 |
