# Agadir civil soil screening

170 route/station sample locations; 168 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 153 |
| granular-density-and-groundwater-tests | 167 |

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
| 0..30cm | clay | % | 16–29 | 5–44 | 168 |
| 0..30cm | sand | % | 42–66 | 15–87 | 168 |
| 0..30cm | silt | % | 17–31 | 5–48 | 168 |
| 0..30cm | bd.core | kg/m3 | 1350–1470 | 1110–1630 | 168 |
| 0..30cm | soc | g/kg | 3.5–9 | 1.3–18.5 | 168 |
| 0..30cm | ph.h2o | pH | 7.4–7.9 | 6.8–8.5 | 168 |
| 30..60cm | clay | % | 19–31 | 6–43 | 168 |
| 30..60cm | sand | % | 43–64 | 10–88 | 168 |
| 30..60cm | silt | % | 18–29 | 3–48 | 168 |
| 30..60cm | bd.core | kg/m3 | 1430–1600 | 1190–1820 | 168 |
| 30..60cm | soc | g/kg | 2.2–5.1 | 0.8–11.2 | 168 |
| 30..60cm | ph.h2o | pH | 7.6–8.2 | 6.7–8.9 | 168 |
| 60..100cm | clay | % | 19–30 | 5–44 | 168 |
| 60..100cm | sand | % | 44–63 | 12–91 | 168 |
| 60..100cm | silt | % | 18–29 | 2–48 | 168 |
| 60..100cm | bd.core | kg/m3 | 1460–1610 | 1160–1810 | 168 |
| 60..100cm | soc | g/kg | 1.4–3.6 | 0.2–7.5 | 168 |
| 60..100cm | ph.h2o | pH | 7.7–8.3 | 6.9–9.2 | 168 |
