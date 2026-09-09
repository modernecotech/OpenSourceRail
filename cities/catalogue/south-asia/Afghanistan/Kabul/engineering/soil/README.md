# Kabul civil soil screening

717 route/station sample locations; 716 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 270 |
| granular-density-and-groundwater-tests | 72 |
| silt-moisture-frost-and-erosion-review | 706 |

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
| 0..30cm | clay | % | 17–26 | 1–36 | 716 |
| 0..30cm | sand | % | 28–49 | 10–75 | 716 |
| 0..30cm | silt | % | 31–46 | 17–63 | 716 |
| 0..30cm | bd.core | kg/m3 | 1340–1460 | 1150–1610 | 716 |
| 0..30cm | soc | g/kg | 3.3–12.8 | 1.1–23.2 | 716 |
| 0..30cm | ph.h2o | pH | 7.2–8 | 6.3–8.6 | 716 |
| 30..60cm | clay | % | 17–28 | 1–39 | 716 |
| 30..60cm | sand | % | 25–48 | 8–81 | 716 |
| 30..60cm | silt | % | 31–48 | 14–64 | 716 |
| 30..60cm | bd.core | kg/m3 | 1400–1520 | 1150–1720 | 716 |
| 30..60cm | soc | g/kg | 2.3–7.2 | 0.7–13.7 | 716 |
| 30..60cm | ph.h2o | pH | 7.3–8.1 | 6.3–9.1 | 716 |
| 60..100cm | clay | % | 16–28 | 2–39 | 716 |
| 60..100cm | sand | % | 26–50 | 6–86 | 716 |
| 60..100cm | silt | % | 30–48 | 10–63 | 716 |
| 60..100cm | bd.core | kg/m3 | 1420–1550 | 1180–1840 | 716 |
| 60..100cm | soc | g/kg | 1.9–5.2 | 0–10.3 | 716 |
| 60..100cm | ph.h2o | pH | 7.3–8.2 | 6.4–9.3 | 716 |
