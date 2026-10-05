# Basra civil soil screening

1,003 route/station sample locations; 674 complete profiles; 329 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 329 |
| fine-soil-plasticity-and-shrink-swell-tests | 618 |
| granular-density-and-groundwater-tests | 584 |
| silt-moisture-frost-and-erosion-review | 89 |

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
| 0..30cm | clay | % | 16–28 | 2–38 | 674 |
| 0..30cm | sand | % | 31–58 | 14–83 | 674 |
| 0..30cm | silt | % | 25–40 | 11–55 | 674 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1190–1730 | 674 |
| 0..30cm | soc | g/kg | 2.4–5.7 | 0.4–12.7 | 674 |
| 0..30cm | ph.h2o | pH | 7.8–8.4 | 7.1–9.3 | 674 |
| 30..60cm | clay | % | 17–30 | 2–41 | 674 |
| 30..60cm | sand | % | 32–59 | 10–92 | 674 |
| 30..60cm | silt | % | 23–38 | 4–50 | 674 |
| 30..60cm | bd.core | kg/m3 | 1390–1520 | 1090–1760 | 674 |
| 30..60cm | soc | g/kg | 1.5–3.6 | 0–9.8 | 674 |
| 30..60cm | ph.h2o | pH | 8.1–8.6 | 6.9–10.2 | 674 |
| 60..100cm | clay | % | 17–29 | 2–42 | 674 |
| 60..100cm | sand | % | 33–59 | 9–92 | 674 |
| 60..100cm | silt | % | 24–38 | 4–54 | 674 |
| 60..100cm | bd.core | kg/m3 | 1360–1510 | 1090–1780 | 674 |
| 60..100cm | soc | g/kg | 1.4–3.7 | 0–9.8 | 674 |
| 60..100cm | ph.h2o | pH | 8.1–8.7 | 7–10.2 | 674 |
