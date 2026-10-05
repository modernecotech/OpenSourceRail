# Peshawar civil soil screening

514 route/station sample locations; 514 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 514 |
| granular-density-and-groundwater-tests | 308 |
| silt-moisture-frost-and-erosion-review | 18 |

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
| 0..30cm | clay | % | 22–29 | 7–46 | 514 |
| 0..30cm | sand | % | 38–52 | 11–80 | 514 |
| 0..30cm | silt | % | 25–34 | 9–51 | 514 |
| 0..30cm | bd.core | kg/m3 | 1300–1530 | 1070–1670 | 514 |
| 0..30cm | soc | g/kg | 4.1–8 | 1.7–20.5 | 514 |
| 0..30cm | ph.h2o | pH | 6.9–7.8 | 5.9–8.6 | 514 |
| 30..60cm | clay | % | 23–31 | 8–46 | 514 |
| 30..60cm | sand | % | 38–52 | 10–81 | 514 |
| 30..60cm | silt | % | 24–34 | 6–53 | 514 |
| 30..60cm | bd.core | kg/m3 | 1410–1560 | 1150–1750 | 514 |
| 30..60cm | soc | g/kg | 2.8–5.4 | 0.8–12 | 514 |
| 30..60cm | ph.h2o | pH | 7–8.1 | 5.8–9.2 | 514 |
| 60..100cm | clay | % | 23–31 | 8–46 | 514 |
| 60..100cm | sand | % | 38–51 | 13–82 | 514 |
| 60..100cm | silt | % | 24–34 | 4–51 | 514 |
| 60..100cm | bd.core | kg/m3 | 1440–1600 | 1170–1870 | 514 |
| 60..100cm | soc | g/kg | 2–4.3 | 0.6–8.1 | 514 |
| 60..100cm | ph.h2o | pH | 6.9–8.1 | 5.8–9.3 | 514 |
