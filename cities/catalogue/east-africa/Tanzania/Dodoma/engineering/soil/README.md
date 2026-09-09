# Dodoma civil soil screening

132 route/station sample locations; 132 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 108 |
| fine-soil-plasticity-and-shrink-swell-tests | 132 |
| granular-density-and-groundwater-tests | 128 |

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
| 0..30cm | clay | % | 25–33 | 14–43 | 132 |
| 0..30cm | sand | % | 48–65 | 29–83 | 132 |
| 0..30cm | silt | % | 10–20 | 1–31 | 132 |
| 0..30cm | bd.core | kg/m3 | 1390–1480 | 1240–1620 | 132 |
| 0..30cm | soc | g/kg | 4.5–7.5 | 2.1–11.6 | 132 |
| 0..30cm | ph.h2o | pH | 5.6–6.9 | 4.8–8.2 | 132 |
| 30..60cm | clay | % | 28–38 | 16–51 | 132 |
| 30..60cm | sand | % | 41–59 | 14–81 | 132 |
| 30..60cm | silt | % | 13–22 | 0–36 | 132 |
| 30..60cm | bd.core | kg/m3 | 1400–1510 | 1200–1660 | 132 |
| 30..60cm | soc | g/kg | 2.9–5.3 | 1.1–10 | 132 |
| 30..60cm | ph.h2o | pH | 5.9–6.8 | 4.7–8 | 132 |
| 60..100cm | clay | % | 29–39 | 16–53 | 132 |
| 60..100cm | sand | % | 38–56 | 13–81 | 132 |
| 60..100cm | silt | % | 15–24 | 0–40 | 132 |
| 60..100cm | bd.core | kg/m3 | 1360–1520 | 1120–1730 | 132 |
| 60..100cm | soc | g/kg | 3–4.6 | 0.9–9.5 | 132 |
| 60..100cm | ph.h2o | pH | 6.1–6.9 | 4.8–8.4 | 132 |
