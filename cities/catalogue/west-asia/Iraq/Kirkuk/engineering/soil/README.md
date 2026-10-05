# Kirkuk civil soil screening

234 route/station sample locations; 229 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 229 |
| granular-density-and-groundwater-tests | 69 |
| silt-moisture-frost-and-erosion-review | 204 |

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
| 0..30cm | clay | % | 20–34 | 10–43 | 229 |
| 0..30cm | sand | % | 20–46 | 2–72 | 229 |
| 0..30cm | silt | % | 33–47 | 17–61 | 229 |
| 0..30cm | bd.core | kg/m3 | 1360–1450 | 1140–1650 | 229 |
| 0..30cm | soc | g/kg | 2.6–7.5 | 0.9–12.7 | 229 |
| 0..30cm | ph.h2o | pH | 7.3–7.7 | 6.4–8.1 | 229 |
| 30..60cm | clay | % | 21–35 | 3–45 | 229 |
| 30..60cm | sand | % | 24–52 | 4–85 | 229 |
| 30..60cm | silt | % | 27–41 | 8–59 | 229 |
| 30..60cm | bd.core | kg/m3 | 1350–1530 | 1140–1750 | 229 |
| 30..60cm | soc | g/kg | 2.6–4.7 | 1.1–9 | 229 |
| 30..60cm | ph.h2o | pH | 7.2–7.6 | 6.4–8.6 | 229 |
| 60..100cm | clay | % | 23–37 | 3–48 | 229 |
| 60..100cm | sand | % | 26–53 | 4–85 | 229 |
| 60..100cm | silt | % | 24–38 | 4–59 | 229 |
| 60..100cm | bd.core | kg/m3 | 1330–1580 | 1060–1890 | 229 |
| 60..100cm | soc | g/kg | 2.1–3.1 | 0.5–6.7 | 229 |
| 60..100cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.9 | 229 |
