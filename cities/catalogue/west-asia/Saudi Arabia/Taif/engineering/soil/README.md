# Taif civil soil screening

857 route/station sample locations; 762 complete profiles; 95 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 95 |
| fine-soil-plasticity-and-shrink-swell-tests | 741 |
| granular-density-and-groundwater-tests | 762 |

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
| 0..30cm | clay | % | 18–26 | 6–39 | 762 |
| 0..30cm | sand | % | 49–64 | 25–88 | 762 |
| 0..30cm | silt | % | 18–24 | 3–39 | 762 |
| 0..30cm | bd.core | kg/m3 | 1430–1510 | 1290–1660 | 762 |
| 0..30cm | soc | g/kg | 2–5.3 | 0.7–12.9 | 762 |
| 0..30cm | ph.h2o | pH | 7.9–8.6 | 7.5–9.5 | 762 |
| 30..60cm | clay | % | 19–27 | 5–43 | 762 |
| 30..60cm | sand | % | 47–62 | 17–92 | 762 |
| 30..60cm | silt | % | 19–26 | 3–43 | 762 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1250–1730 | 762 |
| 30..60cm | soc | g/kg | 1.4–3.8 | 0.3–7.3 | 762 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.7–9.5 | 762 |
| 60..100cm | clay | % | 20–29 | 4–45 | 762 |
| 60..100cm | sand | % | 46–62 | 13–92 | 762 |
| 60..100cm | silt | % | 18–26 | 2–44 | 762 |
| 60..100cm | bd.core | kg/m3 | 1460–1600 | 1240–1810 | 762 |
| 60..100cm | soc | g/kg | 1.2–2.8 | 0–6.1 | 762 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.8–9.7 | 762 |
