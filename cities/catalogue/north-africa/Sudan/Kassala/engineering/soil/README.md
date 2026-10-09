# Kassala civil soil screening

816 route/station sample locations; 816 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 816 |
| granular-density-and-groundwater-tests | 45 |
| silt-moisture-frost-and-erosion-review | 158 |

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
| 0..30cm | clay | % | 26–34 | 11–43 | 816 |
| 0..30cm | sand | % | 25–41 | 8–71 | 816 |
| 0..30cm | silt | % | 31–42 | 16–52 | 816 |
| 0..30cm | bd.core | kg/m3 | 1450–1530 | 1210–1740 | 816 |
| 0..30cm | soc | g/kg | 3–6.5 | 1.1–12.6 | 816 |
| 0..30cm | ph.h2o | pH | 7.3–7.9 | 6–9 | 816 |
| 30..60cm | clay | % | 27–36 | 9–45 | 816 |
| 30..60cm | sand | % | 22–39 | 8–75 | 816 |
| 30..60cm | silt | % | 32–42 | 14–54 | 816 |
| 30..60cm | bd.core | kg/m3 | 1460–1520 | 1250–1720 | 816 |
| 30..60cm | soc | g/kg | 1.8–3 | 0.2–7.7 | 816 |
| 30..60cm | ph.h2o | pH | 8–8.5 | 6.5–9.6 | 816 |
| 60..100cm | clay | % | 26–36 | 9–45 | 816 |
| 60..100cm | sand | % | 24–40 | 8–76 | 816 |
| 60..100cm | silt | % | 31–41 | 10–53 | 816 |
| 60..100cm | bd.core | kg/m3 | 1440–1520 | 1240–1750 | 816 |
| 60..100cm | soc | g/kg | 1.4–2.2 | 0.2–4.8 | 816 |
| 60..100cm | ph.h2o | pH | 8.1–8.5 | 6.7–10 | 816 |
