# Vientiane civil soil screening

132 route/station sample locations; 128 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 128 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 128 |
| granular-density-and-groundwater-tests | 114 |
| silt-moisture-frost-and-erosion-review | 38 |

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
| 0..30cm | clay | % | 21–29 | 7–41 | 128 |
| 0..30cm | sand | % | 36–53 | 11–80 | 128 |
| 0..30cm | silt | % | 26–36 | 8–53 | 128 |
| 0..30cm | bd.core | kg/m3 | 1240–1410 | 960–1600 | 128 |
| 0..30cm | soc | g/kg | 5.7–12.2 | 2.9–30.5 | 128 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.7–7.6 | 128 |
| 30..60cm | clay | % | 22–29 | 7–42 | 128 |
| 30..60cm | sand | % | 36–51 | 7–87 | 128 |
| 30..60cm | silt | % | 26–35 | 8–54 | 128 |
| 30..60cm | bd.core | kg/m3 | 1240–1440 | 880–1680 | 128 |
| 30..60cm | soc | g/kg | 3.7–8 | 1.4–19.2 | 128 |
| 30..60cm | ph.h2o | pH | 5.9–6.3 | 4.9–7.8 | 128 |
| 60..100cm | clay | % | 23–30 | 6–42 | 128 |
| 60..100cm | sand | % | 35–51 | 6–86 | 128 |
| 60..100cm | silt | % | 26–35 | 8–55 | 128 |
| 60..100cm | bd.core | kg/m3 | 1210–1430 | 840–1690 | 128 |
| 60..100cm | soc | g/kg | 2.6–7.1 | 1–19.2 | 128 |
| 60..100cm | ph.h2o | pH | 6.1–6.5 | 4.8–8 | 128 |
