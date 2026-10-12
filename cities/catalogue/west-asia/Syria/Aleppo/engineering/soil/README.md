# Aleppo civil soil screening

5,506 route/station sample locations; 5,501 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 5501 |
| granular-density-and-groundwater-tests | 1958 |
| silt-moisture-frost-and-erosion-review | 754 |

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
| 0..30cm | clay | % | 22–30 | 9–42 | 5501 |
| 0..30cm | sand | % | 34–49 | 12–76 | 5501 |
| 0..30cm | silt | % | 29–37 | 11–54 | 5501 |
| 0..30cm | bd.core | kg/m3 | 1340–1470 | 1150–1650 | 5501 |
| 0..30cm | soc | g/kg | 2.9–10.5 | 1.1–18.4 | 5501 |
| 0..30cm | ph.h2o | pH | 7.6–8 | 6.9–8.5 | 5501 |
| 30..60cm | clay | % | 23–33 | 6–49 | 5501 |
| 30..60cm | sand | % | 34–53 | 11–84 | 5501 |
| 30..60cm | silt | % | 24–34 | 3–52 | 5501 |
| 30..60cm | bd.core | kg/m3 | 1420–1600 | 1240–1770 | 5501 |
| 30..60cm | soc | g/kg | 2.2–5 | 1–9.3 | 5501 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.7–8.7 | 5501 |
| 60..100cm | clay | % | 24–35 | 7–52 | 5501 |
| 60..100cm | sand | % | 35–54 | 8–85 | 5501 |
| 60..100cm | silt | % | 22–32 | 0–54 | 5501 |
| 60..100cm | bd.core | kg/m3 | 1420–1640 | 1200–1930 | 5501 |
| 60..100cm | soc | g/kg | 1.9–3.5 | 0.4–8 | 5501 |
| 60..100cm | ph.h2o | pH | 7.4–8.1 | 6.7–8.8 | 5501 |
