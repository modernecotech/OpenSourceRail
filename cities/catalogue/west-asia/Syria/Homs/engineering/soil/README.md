# Homs civil soil screening

92 route/station sample locations; 92 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 92 |
| granular-density-and-groundwater-tests | 7 |
| silt-moisture-frost-and-erosion-review | 50 |

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
| 0..30cm | clay | % | 26–32 | 12–43 | 92 |
| 0..30cm | sand | % | 29–41 | 9–68 | 92 |
| 0..30cm | silt | % | 33–40 | 17–56 | 92 |
| 0..30cm | bd.core | kg/m3 | 1370–1430 | 1160–1600 | 92 |
| 0..30cm | soc | g/kg | 3.2–11.6 | 1.6–23.7 | 92 |
| 0..30cm | ph.h2o | pH | 7.5–7.9 | 6.9–8.4 | 92 |
| 30..60cm | clay | % | 28–34 | 12–46 | 92 |
| 30..60cm | sand | % | 28–39 | 7–67 | 92 |
| 30..60cm | silt | % | 32–38 | 16–51 | 92 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1250–1720 | 92 |
| 30..60cm | soc | g/kg | 2.3–5.1 | 0.8–9.7 | 92 |
| 30..60cm | ph.h2o | pH | 7.3–7.9 | 6.7–8.4 | 92 |
| 60..100cm | clay | % | 28–35 | 12–49 | 92 |
| 60..100cm | sand | % | 29–41 | 6–72 | 92 |
| 60..100cm | silt | % | 30–36 | 11–52 | 92 |
| 60..100cm | bd.core | kg/m3 | 1480–1590 | 1260–1800 | 92 |
| 60..100cm | soc | g/kg | 1.8–3.4 | 0.4–6.6 | 92 |
| 60..100cm | ph.h2o | pH | 7.3–7.8 | 6.5–8.6 | 92 |
