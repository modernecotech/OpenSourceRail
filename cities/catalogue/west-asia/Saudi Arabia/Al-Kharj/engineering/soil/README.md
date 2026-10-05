# Al-Kharj civil soil screening

151 route/station sample locations; 99 complete profiles; 52 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 52 |
| fine-soil-plasticity-and-shrink-swell-tests | 14 |
| granular-density-and-groundwater-tests | 98 |
| silt-moisture-frost-and-erosion-review | 22 |

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
| 0..30cm | clay | % | 10–21 | 0–34 | 99 |
| 0..30cm | sand | % | 43–66 | 18–87 | 99 |
| 0..30cm | silt | % | 24–36 | 9–53 | 99 |
| 0..30cm | bd.core | kg/m3 | 1410–1490 | 1230–1660 | 99 |
| 0..30cm | soc | g/kg | 3.1–4.4 | 0.7–13.6 | 99 |
| 0..30cm | ph.h2o | pH | 8.1–8.4 | 7.3–9.4 | 99 |
| 30..60cm | clay | % | 15–23 | 0–41 | 99 |
| 30..60cm | sand | % | 43–60 | 16–91 | 99 |
| 30..60cm | silt | % | 25–34 | 4–50 | 99 |
| 30..60cm | bd.core | kg/m3 | 1360–1480 | 1170–1670 | 99 |
| 30..60cm | soc | g/kg | 2–3.3 | 0.3–11.6 | 99 |
| 30..60cm | ph.h2o | pH | 8.1–8.7 | 7–9.7 | 99 |
| 60..100cm | clay | % | 15–22 | 0–40 | 99 |
| 60..100cm | sand | % | 44–59 | 16–92 | 99 |
| 60..100cm | silt | % | 26–34 | 4–53 | 99 |
| 60..100cm | bd.core | kg/m3 | 1420–1500 | 1230–1740 | 99 |
| 60..100cm | soc | g/kg | 1.6–2.7 | 0.5–7.8 | 99 |
| 60..100cm | ph.h2o | pH | 8.1–8.7 | 7.4–10.1 | 99 |
