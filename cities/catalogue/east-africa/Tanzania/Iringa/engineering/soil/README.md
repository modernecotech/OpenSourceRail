# Iringa civil soil screening

116 route/station sample locations; 116 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 64 |
| fine-soil-plasticity-and-shrink-swell-tests | 69 |
| granular-density-and-groundwater-tests | 116 |

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
| 0..30cm | clay | % | 18–27 | 10–36 | 116 |
| 0..30cm | sand | % | 52–66 | 35–83 | 116 |
| 0..30cm | silt | % | 15–21 | 4–31 | 116 |
| 0..30cm | bd.core | kg/m3 | 1180–1450 | 880–1610 | 116 |
| 0..30cm | soc | g/kg | 4.6–14.9 | 1.9–24.6 | 116 |
| 0..30cm | ph.h2o | pH | 5.7–6.9 | 4.7–8 | 116 |
| 30..60cm | clay | % | 21–29 | 9–40 | 116 |
| 30..60cm | sand | % | 48–62 | 31–89 | 116 |
| 30..60cm | silt | % | 17–23 | 1–37 | 116 |
| 30..60cm | bd.core | kg/m3 | 1220–1490 | 780–1630 | 116 |
| 30..60cm | soc | g/kg | 4.6–7.1 | 2–12.7 | 116 |
| 30..60cm | ph.h2o | pH | 6–6.8 | 5.1–7.9 | 116 |
| 60..100cm | clay | % | 21–29 | 8–42 | 116 |
| 60..100cm | sand | % | 46–62 | 21–87 | 116 |
| 60..100cm | silt | % | 17–25 | 2–39 | 116 |
| 60..100cm | bd.core | kg/m3 | 1190–1520 | 320–1690 | 116 |
| 60..100cm | soc | g/kg | 3.9–5.9 | 1.6–12.8 | 116 |
| 60..100cm | ph.h2o | pH | 6.2–6.9 | 4.9–8.3 | 116 |
