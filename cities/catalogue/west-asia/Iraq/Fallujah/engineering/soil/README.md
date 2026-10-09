# Fallujah civil soil screening

398 route/station sample locations; 329 complete profiles; 69 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 69 |
| fine-soil-plasticity-and-shrink-swell-tests | 181 |
| granular-density-and-groundwater-tests | 262 |
| silt-moisture-frost-and-erosion-review | 88 |

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
| 0..30cm | clay | % | 16–30 | 4–40 | 329 |
| 0..30cm | sand | % | 31–58 | 8–86 | 329 |
| 0..30cm | silt | % | 26–40 | 10–56 | 329 |
| 0..30cm | bd.core | kg/m3 | 1450–1520 | 1260–1720 | 329 |
| 0..30cm | soc | g/kg | 2.2–6.1 | 0.4–10.8 | 329 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.2–9.3 | 329 |
| 30..60cm | clay | % | 18–30 | 2–42 | 329 |
| 30..60cm | sand | % | 32–57 | 7–91 | 329 |
| 30..60cm | silt | % | 25–39 | 6–54 | 329 |
| 30..60cm | bd.core | kg/m3 | 1420–1550 | 1190–1750 | 329 |
| 30..60cm | soc | g/kg | 1.7–3.2 | 0–11.3 | 329 |
| 30..60cm | ph.h2o | pH | 8.1–8.8 | 7.1–10.2 | 329 |
| 60..100cm | clay | % | 17–30 | 2–41 | 329 |
| 60..100cm | sand | % | 32–57 | 6–89 | 329 |
| 60..100cm | silt | % | 25–39 | 6–55 | 329 |
| 60..100cm | bd.core | kg/m3 | 1440–1600 | 1230–1890 | 329 |
| 60..100cm | soc | g/kg | 1.6–2.8 | 0–9.6 | 329 |
| 60..100cm | ph.h2o | pH | 7.9–8.9 | 6.4–10.2 | 329 |
