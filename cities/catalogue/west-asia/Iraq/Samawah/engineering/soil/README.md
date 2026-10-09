# Samawah civil soil screening

514 route/station sample locations; 360 complete profiles; 154 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 154 |
| fine-soil-plasticity-and-shrink-swell-tests | 283 |
| granular-density-and-groundwater-tests | 318 |
| silt-moisture-frost-and-erosion-review | 36 |

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
| 0..30cm | clay | % | 17–29 | 0–41 | 360 |
| 0..30cm | sand | % | 31–56 | 10–83 | 360 |
| 0..30cm | silt | % | 27–40 | 12–54 | 360 |
| 0..30cm | bd.core | kg/m3 | 1440–1540 | 1220–1710 | 360 |
| 0..30cm | soc | g/kg | 1.9–5.4 | 0.3–11 | 360 |
| 0..30cm | ph.h2o | pH | 8–8.5 | 7.1–9.4 | 360 |
| 30..60cm | clay | % | 18–30 | 0–42 | 360 |
| 30..60cm | sand | % | 32–56 | 9–92 | 360 |
| 30..60cm | silt | % | 25–38 | 5–52 | 360 |
| 30..60cm | bd.core | kg/m3 | 1440–1520 | 1190–1760 | 360 |
| 30..60cm | soc | g/kg | 1.7–3.1 | 0–8.8 | 360 |
| 30..60cm | ph.h2o | pH | 8.2–9 | 7.2–10.1 | 360 |
| 60..100cm | clay | % | 17–29 | 0–42 | 360 |
| 60..100cm | sand | % | 32–56 | 7–91 | 360 |
| 60..100cm | silt | % | 26–39 | 5–54 | 360 |
| 60..100cm | bd.core | kg/m3 | 1430–1590 | 1230–1920 | 360 |
| 60..100cm | soc | g/kg | 1.4–3.1 | 0–7.6 | 360 |
| 60..100cm | ph.h2o | pH | 8.1–9 | 7.1–10.2 | 360 |
