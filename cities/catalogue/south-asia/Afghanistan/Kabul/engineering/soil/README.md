# Kabul civil soil screening

679 route/station sample locations; 679 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 293 |
| granular-density-and-groundwater-tests | 60 |
| silt-moisture-frost-and-erosion-review | 665 |

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
| 0..30cm | clay | % | 17–27 | 0–37 | 679 |
| 0..30cm | sand | % | 27–50 | 9–75 | 679 |
| 0..30cm | silt | % | 32–46 | 18–63 | 679 |
| 0..30cm | bd.core | kg/m3 | 1340–1460 | 1150–1620 | 679 |
| 0..30cm | soc | g/kg | 2.9–11.5 | 1.1–19.2 | 679 |
| 0..30cm | ph.h2o | pH | 7.3–8 | 6.6–8.7 | 679 |
| 30..60cm | clay | % | 17–28 | 1–38 | 679 |
| 30..60cm | sand | % | 24–49 | 7–84 | 679 |
| 30..60cm | silt | % | 31–48 | 13–64 | 679 |
| 30..60cm | bd.core | kg/m3 | 1400–1520 | 1170–1720 | 679 |
| 30..60cm | soc | g/kg | 2.2–7.5 | 0.6–13.9 | 679 |
| 30..60cm | ph.h2o | pH | 7.4–8.2 | 6.4–9.1 | 679 |
| 60..100cm | clay | % | 17–28 | 2–39 | 679 |
| 60..100cm | sand | % | 25–51 | 5–88 | 679 |
| 60..100cm | silt | % | 30–47 | 6–63 | 679 |
| 60..100cm | bd.core | kg/m3 | 1430–1550 | 1170–1820 | 679 |
| 60..100cm | soc | g/kg | 1.9–5.5 | 0–11.6 | 679 |
| 60..100cm | ph.h2o | pH | 7.4–8.2 | 6.6–9.3 | 679 |
