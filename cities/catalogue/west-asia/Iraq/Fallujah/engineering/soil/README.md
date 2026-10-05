# Fallujah civil soil screening

113 route/station sample locations; 81 complete profiles; 32 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 32 |
| fine-soil-plasticity-and-shrink-swell-tests | 41 |
| granular-density-and-groundwater-tests | 53 |
| silt-moisture-frost-and-erosion-review | 30 |

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
| 0..30cm | clay | % | 16–30 | 4–40 | 81 |
| 0..30cm | sand | % | 31–57 | 8–86 | 81 |
| 0..30cm | silt | % | 26–40 | 10–56 | 81 |
| 0..30cm | bd.core | kg/m3 | 1450–1520 | 1260–1720 | 81 |
| 0..30cm | soc | g/kg | 2.5–6.1 | 0.5–10.8 | 81 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.3–9.2 | 81 |
| 30..60cm | clay | % | 18–30 | 3–42 | 81 |
| 30..60cm | sand | % | 32–56 | 7–89 | 81 |
| 30..60cm | silt | % | 25–38 | 7–54 | 81 |
| 30..60cm | bd.core | kg/m3 | 1420–1550 | 1230–1730 | 81 |
| 30..60cm | soc | g/kg | 1.7–3.2 | 0–11.3 | 81 |
| 30..60cm | ph.h2o | pH | 8.1–8.8 | 7.1–10.2 | 81 |
| 60..100cm | clay | % | 17–30 | 2–41 | 81 |
| 60..100cm | sand | % | 32–57 | 6–89 | 81 |
| 60..100cm | silt | % | 25–39 | 7–54 | 81 |
| 60..100cm | bd.core | kg/m3 | 1440–1600 | 1230–1890 | 81 |
| 60..100cm | soc | g/kg | 1.7–2.8 | 0–9.6 | 81 |
| 60..100cm | ph.h2o | pH | 7.9–8.9 | 6.4–10.2 | 81 |
