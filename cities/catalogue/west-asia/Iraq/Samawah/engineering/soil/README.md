# Samawah civil soil screening

94 route/station sample locations; 79 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 60 |
| granular-density-and-groundwater-tests | 66 |
| silt-moisture-frost-and-erosion-review | 13 |

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
| 0..30cm | clay | % | 17–28 | 4–39 | 79 |
| 0..30cm | sand | % | 34–57 | 14–82 | 79 |
| 0..30cm | silt | % | 27–37 | 12–51 | 79 |
| 0..30cm | bd.core | kg/m3 | 1460–1530 | 1260–1710 | 79 |
| 0..30cm | soc | g/kg | 1.8–5.1 | 0.3–10.1 | 79 |
| 0..30cm | ph.h2o | pH | 8–8.5 | 7.1–9.4 | 79 |
| 30..60cm | clay | % | 18–30 | 3–40 | 79 |
| 30..60cm | sand | % | 35–57 | 14–90 | 79 |
| 30..60cm | silt | % | 25–36 | 6–50 | 79 |
| 30..60cm | bd.core | kg/m3 | 1450–1510 | 1190–1760 | 79 |
| 30..60cm | soc | g/kg | 1.7–3.1 | 0–8.7 | 79 |
| 30..60cm | ph.h2o | pH | 8.2–8.7 | 7.5–9.9 | 79 |
| 60..100cm | clay | % | 17–29 | 3–40 | 79 |
| 60..100cm | sand | % | 35–57 | 12–90 | 79 |
| 60..100cm | silt | % | 26–37 | 6–52 | 79 |
| 60..100cm | bd.core | kg/m3 | 1440–1560 | 1230–1820 | 79 |
| 60..100cm | soc | g/kg | 1.5–2.7 | 0–7.3 | 79 |
| 60..100cm | ph.h2o | pH | 8.2–8.7 | 7.5–10.2 | 79 |
