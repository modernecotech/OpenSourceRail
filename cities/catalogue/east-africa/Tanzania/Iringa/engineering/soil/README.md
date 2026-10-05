# Iringa civil soil screening

82 route/station sample locations; 82 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 68 |
| fine-soil-plasticity-and-shrink-swell-tests | 60 |
| granular-density-and-groundwater-tests | 82 |

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
| 0..30cm | clay | % | 19–27 | 11–36 | 82 |
| 0..30cm | sand | % | 52–67 | 35–83 | 82 |
| 0..30cm | silt | % | 13–21 | 5–31 | 82 |
| 0..30cm | bd.core | kg/m3 | 1260–1450 | 1070–1610 | 82 |
| 0..30cm | soc | g/kg | 5.2–15.3 | 2.1–31.4 | 82 |
| 0..30cm | ph.h2o | pH | 5.6–6.9 | 4.5–8 | 82 |
| 30..60cm | clay | % | 22–29 | 10–40 | 82 |
| 30..60cm | sand | % | 48–62 | 31–84 | 82 |
| 30..60cm | silt | % | 16–23 | 2–36 | 82 |
| 30..60cm | bd.core | kg/m3 | 1280–1490 | 1070–1630 | 82 |
| 30..60cm | soc | g/kg | 4.8–7.5 | 2.2–12.1 | 82 |
| 30..60cm | ph.h2o | pH | 5.8–6.8 | 4.9–7.9 | 82 |
| 60..100cm | clay | % | 21–29 | 8–42 | 82 |
| 60..100cm | sand | % | 46–61 | 21–87 | 82 |
| 60..100cm | silt | % | 17–25 | 2–40 | 82 |
| 60..100cm | bd.core | kg/m3 | 1250–1520 | 860–1690 | 82 |
| 60..100cm | soc | g/kg | 4.1–6.1 | 1.5–12.5 | 82 |
| 60..100cm | ph.h2o | pH | 6.1–7 | 4.8–8.3 | 82 |
