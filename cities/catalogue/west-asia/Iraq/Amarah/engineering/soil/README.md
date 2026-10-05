# Amarah civil soil screening

133 route/station sample locations; 120 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 98 |
| granular-density-and-groundwater-tests | 107 |
| silt-moisture-frost-and-erosion-review | 49 |

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
| 0..30cm | clay | % | 18–29 | 5–36 | 120 |
| 0..30cm | sand | % | 30–54 | 14–76 | 120 |
| 0..30cm | silt | % | 28–41 | 12–58 | 120 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1240–1690 | 120 |
| 0..30cm | soc | g/kg | 2.8–4.9 | 0.7–9.7 | 120 |
| 0..30cm | ph.h2o | pH | 7.7–8 | 7.1–8.7 | 120 |
| 30..60cm | clay | % | 19–31 | 1–41 | 120 |
| 30..60cm | sand | % | 31–54 | 14–90 | 120 |
| 30..60cm | silt | % | 25–38 | 2–56 | 120 |
| 30..60cm | bd.core | kg/m3 | 1340–1440 | 960–1750 | 120 |
| 30..60cm | soc | g/kg | 1.6–3 | 0–7.9 | 120 |
| 30..60cm | ph.h2o | pH | 8–8.3 | 7.2–9 | 120 |
| 60..100cm | clay | % | 19–31 | 2–41 | 120 |
| 60..100cm | sand | % | 32–55 | 14–88 | 120 |
| 60..100cm | silt | % | 25–37 | 3–54 | 120 |
| 60..100cm | bd.core | kg/m3 | 1270–1400 | 760–1730 | 120 |
| 60..100cm | soc | g/kg | 1.5–2.6 | 0–7.4 | 120 |
| 60..100cm | ph.h2o | pH | 8–8.6 | 7.2–9.3 | 120 |
