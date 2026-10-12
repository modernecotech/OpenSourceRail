# Nasiriyah civil soil screening

811 route/station sample locations; 760 complete profiles; 51 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 51 |
| fine-soil-plasticity-and-shrink-swell-tests | 650 |
| granular-density-and-groundwater-tests | 595 |
| silt-moisture-frost-and-erosion-review | 99 |

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
| 0..30cm | clay | % | 17–28 | 3–37 | 760 |
| 0..30cm | sand | % | 34–55 | 14–83 | 760 |
| 0..30cm | silt | % | 26–38 | 11–53 | 760 |
| 0..30cm | bd.core | kg/m3 | 1460–1550 | 1270–1720 | 760 |
| 0..30cm | soc | g/kg | 1.9–5.3 | 0.5–11.3 | 760 |
| 0..30cm | ph.h2o | pH | 7.9–8.4 | 7.1–9.6 | 760 |
| 30..60cm | clay | % | 20–29 | 2–40 | 760 |
| 30..60cm | sand | % | 36–54 | 14–91 | 760 |
| 30..60cm | silt | % | 26–36 | 5–49 | 760 |
| 30..60cm | bd.core | kg/m3 | 1430–1530 | 1190–1770 | 760 |
| 30..60cm | soc | g/kg | 1.7–3.5 | 0–8.8 | 760 |
| 30..60cm | ph.h2o | pH | 8.1–8.9 | 7.4–10.2 | 760 |
| 60..100cm | clay | % | 19–28 | 2–40 | 760 |
| 60..100cm | sand | % | 36–54 | 13–91 | 760 |
| 60..100cm | silt | % | 26–36 | 5–50 | 760 |
| 60..100cm | bd.core | kg/m3 | 1430–1560 | 1230–1820 | 760 |
| 60..100cm | soc | g/kg | 1.5–2.9 | 0–7 | 760 |
| 60..100cm | ph.h2o | pH | 8–9 | 7.3–10.2 | 760 |
