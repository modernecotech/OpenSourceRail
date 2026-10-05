# Kinshasa civil soil screening

811 route/station sample locations; 744 complete profiles; 67 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 743 |
| coverage-gap | 67 |
| fine-soil-plasticity-and-shrink-swell-tests | 744 |
| granular-density-and-groundwater-tests | 204 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 27–36 | 9–48 | 744 |
| 0..30cm | sand | % | 34–55 | 11–81 | 744 |
| 0..30cm | silt | % | 19–30 | 2–48 | 744 |
| 0..30cm | bd.core | kg/m3 | 1160–1400 | 890–1590 | 744 |
| 0..30cm | soc | g/kg | 6.7–16.9 | 2.5–28 | 744 |
| 0..30cm | ph.h2o | pH | 5.4–6.6 | 4.5–7.5 | 744 |
| 30..60cm | clay | % | 28–40 | 9–54 | 744 |
| 30..60cm | sand | % | 32–52 | 7–86 | 744 |
| 30..60cm | silt | % | 17–30 | 0–48 | 744 |
| 30..60cm | bd.core | kg/m3 | 1190–1430 | 870–1640 | 744 |
| 30..60cm | soc | g/kg | 4.4–11.3 | 1.5–39.3 | 744 |
| 30..60cm | ph.h2o | pH | 5.3–6.6 | 4.6–7.4 | 744 |
| 60..100cm | clay | % | 28–41 | 8–55 | 744 |
| 60..100cm | sand | % | 31–52 | 7–87 | 744 |
| 60..100cm | silt | % | 17–31 | 0–51 | 744 |
| 60..100cm | bd.core | kg/m3 | 1150–1430 | 780–1660 | 744 |
| 60..100cm | soc | g/kg | 3.8–13.5 | 1.4–39.3 | 744 |
| 60..100cm | ph.h2o | pH | 5.4–6.6 | 4.6–7.7 | 744 |
