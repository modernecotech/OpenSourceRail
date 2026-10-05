# Faisalabad civil soil screening

470 route/station sample locations; 470 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 432 |
| granular-density-and-groundwater-tests | 470 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 16–25 | 5–39 | 470 |
| 0..30cm | sand | % | 46–63 | 20–86 | 470 |
| 0..30cm | silt | % | 21–31 | 8–47 | 470 |
| 0..30cm | bd.core | kg/m3 | 1410–1530 | 1190–1710 | 470 |
| 0..30cm | soc | g/kg | 4–6.8 | 1.5–16.6 | 470 |
| 0..30cm | ph.h2o | pH | 7.7–8.1 | 6.7–8.9 | 470 |
| 30..60cm | clay | % | 18–26 | 6–40 | 470 |
| 30..60cm | sand | % | 44–59 | 19–86 | 470 |
| 30..60cm | silt | % | 22–32 | 6–51 | 470 |
| 30..60cm | bd.core | kg/m3 | 1450–1580 | 1220–1760 | 470 |
| 30..60cm | soc | g/kg | 2.2–4 | 0.5–8.2 | 470 |
| 30..60cm | ph.h2o | pH | 7.9–8.4 | 6.8–9.4 | 470 |
| 60..100cm | clay | % | 19–26 | 6–40 | 470 |
| 60..100cm | sand | % | 43–59 | 17–87 | 470 |
| 60..100cm | silt | % | 21–32 | 6–52 | 470 |
| 60..100cm | bd.core | kg/m3 | 1500–1620 | 1220–1860 | 470 |
| 60..100cm | soc | g/kg | 1.5–3.2 | 0.2–7.7 | 470 |
| 60..100cm | ph.h2o | pH | 7.9–8.5 | 7.2–9.3 | 470 |
