# Kano civil soil screening

757 route/station sample locations; 757 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 723 |
| fine-soil-plasticity-and-shrink-swell-tests | 657 |
| granular-density-and-groundwater-tests | 757 |

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
| 0..30cm | clay | % | 16–28 | 6–41 | 757 |
| 0..30cm | sand | % | 46–67 | 21–88 | 757 |
| 0..30cm | silt | % | 15–27 | 1–44 | 757 |
| 0..30cm | bd.core | kg/m3 | 1380–1540 | 1140–1720 | 757 |
| 0..30cm | soc | g/kg | 3.4–7.4 | 1.5–13 | 757 |
| 0..30cm | ph.h2o | pH | 5.7–6.4 | 5–7.1 | 757 |
| 30..60cm | clay | % | 19–27 | 4–43 | 757 |
| 30..60cm | sand | % | 49–64 | 15–91 | 757 |
| 30..60cm | silt | % | 15–26 | 0–44 | 757 |
| 30..60cm | bd.core | kg/m3 | 1390–1550 | 1060–1760 | 757 |
| 30..60cm | soc | g/kg | 2.4–4.6 | 0.9–10.5 | 757 |
| 30..60cm | ph.h2o | pH | 6.1–6.7 | 5.2–7.4 | 757 |
| 60..100cm | clay | % | 20–27 | 4–44 | 757 |
| 60..100cm | sand | % | 48–63 | 15–90 | 757 |
| 60..100cm | silt | % | 16–26 | 0–47 | 757 |
| 60..100cm | bd.core | kg/m3 | 1360–1520 | 770–1790 | 757 |
| 60..100cm | soc | g/kg | 1.9–3.9 | 0.5–7.8 | 757 |
| 60..100cm | ph.h2o | pH | 6.4–6.9 | 5.3–8.1 | 757 |
