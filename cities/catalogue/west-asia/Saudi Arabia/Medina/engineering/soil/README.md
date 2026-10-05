# Medina civil soil screening

739 route/station sample locations; 670 complete profiles; 69 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 69 |
| fine-soil-plasticity-and-shrink-swell-tests | 63 |
| granular-density-and-groundwater-tests | 670 |
| silt-moisture-frost-and-erosion-review | 66 |

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
| 0..30cm | clay | % | 11–22 | 0–36 | 670 |
| 0..30cm | sand | % | 46–68 | 17–89 | 670 |
| 0..30cm | silt | % | 21–32 | 7–48 | 670 |
| 0..30cm | bd.core | kg/m3 | 1340–1490 | 1080–1720 | 670 |
| 0..30cm | soc | g/kg | 1.9–4.9 | 0.3–12.9 | 670 |
| 0..30cm | ph.h2o | pH | 8.1–8.9 | 6.4–9.7 | 670 |
| 30..60cm | clay | % | 13–22 | 1–37 | 670 |
| 30..60cm | sand | % | 46–66 | 11–92 | 670 |
| 30..60cm | silt | % | 21–32 | 4–50 | 670 |
| 30..60cm | bd.core | kg/m3 | 1430–1570 | 1100–1760 | 670 |
| 30..60cm | soc | g/kg | 1.4–3.8 | 0–14.2 | 670 |
| 30..60cm | ph.h2o | pH | 8.2–9.1 | 6.9–10 | 670 |
| 60..100cm | clay | % | 12–21 | 0–39 | 670 |
| 60..100cm | sand | % | 47–65 | 10–92 | 670 |
| 60..100cm | silt | % | 22–32 | 4–54 | 670 |
| 60..100cm | bd.core | kg/m3 | 1450–1600 | 1240–1900 | 670 |
| 60..100cm | soc | g/kg | 1.4–3.7 | 0–14.5 | 670 |
| 60..100cm | ph.h2o | pH | 8.3–9.1 | 6.9–10.2 | 670 |
