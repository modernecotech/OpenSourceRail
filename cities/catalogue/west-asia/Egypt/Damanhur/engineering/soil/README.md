# Damanhur civil soil screening

913 route/station sample locations; 913 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 54 |
| fine-soil-plasticity-and-shrink-swell-tests | 881 |
| granular-density-and-groundwater-tests | 913 |

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
| 0..30cm | clay | % | 17–26 | 5–39 | 913 |
| 0..30cm | sand | % | 46–64 | 16–89 | 913 |
| 0..30cm | silt | % | 18–28 | 5–45 | 913 |
| 0..30cm | bd.core | kg/m3 | 1260–1460 | 1050–1670 | 913 |
| 0..30cm | soc | g/kg | 3.2–18.1 | 1.5–48.7 | 913 |
| 0..30cm | ph.h2o | pH | 7.6–8.5 | 6.8–9.1 | 913 |
| 30..60cm | clay | % | 20–28 | 5–42 | 913 |
| 30..60cm | sand | % | 46–61 | 16–88 | 913 |
| 30..60cm | silt | % | 19–26 | 2–42 | 913 |
| 30..60cm | bd.core | kg/m3 | 1340–1570 | 1060–1820 | 913 |
| 30..60cm | soc | g/kg | 1.8–7.9 | 0.4–31.5 | 913 |
| 30..60cm | ph.h2o | pH | 7.3–8.5 | 5.7–9.4 | 913 |
| 60..100cm | clay | % | 20–28 | 6–43 | 913 |
| 60..100cm | sand | % | 47–62 | 15–88 | 913 |
| 60..100cm | silt | % | 18–26 | 1–43 | 913 |
| 60..100cm | bd.core | kg/m3 | 1310–1580 | 830–1900 | 913 |
| 60..100cm | soc | g/kg | 1.4–7.2 | 0.3–30.3 | 913 |
| 60..100cm | ph.h2o | pH | 7.1–8.5 | 3.5–9.6 | 913 |
