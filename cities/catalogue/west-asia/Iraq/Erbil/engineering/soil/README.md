# Erbil civil soil screening

229 route/station sample locations; 229 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 229 |
| granular-density-and-groundwater-tests | 60 |
| silt-moisture-frost-and-erosion-review | 97 |

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
| 0..30cm | clay | % | 22–38 | 7–51 | 229 |
| 0..30cm | sand | % | 21–48 | 4–72 | 229 |
| 0..30cm | silt | % | 29–42 | 13–58 | 229 |
| 0..30cm | bd.core | kg/m3 | 1330–1460 | 1110–1630 | 229 |
| 0..30cm | soc | g/kg | 2.5–7.3 | 0.9–13.4 | 229 |
| 0..30cm | ph.h2o | pH | 7.1–7.5 | 5.9–8.2 | 229 |
| 30..60cm | clay | % | 24–41 | 4–53 | 229 |
| 30..60cm | sand | % | 25–54 | 5–85 | 229 |
| 30..60cm | silt | % | 22–37 | 5–53 | 229 |
| 30..60cm | bd.core | kg/m3 | 1400–1560 | 1170–1750 | 229 |
| 30..60cm | soc | g/kg | 2.5–4.5 | 1.1–9.3 | 229 |
| 30..60cm | ph.h2o | pH | 7.1–7.5 | 6–8.2 | 229 |
| 60..100cm | clay | % | 24–41 | 5–55 | 229 |
| 60..100cm | sand | % | 27–58 | 7–86 | 229 |
| 60..100cm | silt | % | 18–34 | 0–52 | 229 |
| 60..100cm | bd.core | kg/m3 | 1390–1600 | 1170–1860 | 229 |
| 60..100cm | soc | g/kg | 1.9–3.3 | 0.5–6.7 | 229 |
| 60..100cm | ph.h2o | pH | 7–7.5 | 5.9–8.2 | 229 |
