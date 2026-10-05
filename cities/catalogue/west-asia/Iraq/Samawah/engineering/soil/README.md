# Samawah civil soil screening

222 route/station sample locations; 113 complete profiles; 109 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 109 |
| fine-soil-plasticity-and-shrink-swell-tests | 100 |
| granular-density-and-groundwater-tests | 86 |
| silt-moisture-frost-and-erosion-review | 20 |

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
| 0..30cm | clay | % | 17–29 | 0–41 | 113 |
| 0..30cm | sand | % | 32–56 | 11–83 | 113 |
| 0..30cm | silt | % | 27–39 | 12–54 | 113 |
| 0..30cm | bd.core | kg/m3 | 1440–1530 | 1240–1710 | 113 |
| 0..30cm | soc | g/kg | 1.9–5.3 | 0.3–11 | 113 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.1–9.3 | 113 |
| 30..60cm | clay | % | 18–30 | 0–42 | 113 |
| 30..60cm | sand | % | 33–56 | 12–92 | 113 |
| 30..60cm | silt | % | 25–38 | 5–51 | 113 |
| 30..60cm | bd.core | kg/m3 | 1450–1510 | 1190–1760 | 113 |
| 30..60cm | soc | g/kg | 1.7–3.1 | 0–8.7 | 113 |
| 30..60cm | ph.h2o | pH | 8.2–8.6 | 7.5–9.8 | 113 |
| 60..100cm | clay | % | 17–29 | 0–42 | 113 |
| 60..100cm | sand | % | 32–56 | 10–91 | 113 |
| 60..100cm | silt | % | 26–39 | 5–53 | 113 |
| 60..100cm | bd.core | kg/m3 | 1440–1580 | 1230–1900 | 113 |
| 60..100cm | soc | g/kg | 1.5–3.1 | 0–7.6 | 113 |
| 60..100cm | ph.h2o | pH | 8.1–8.7 | 7.1–10.1 | 113 |
