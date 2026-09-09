# Fort-Portal civil soil screening

72 route/station sample locations; 72 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 71 |
| fine-soil-plasticity-and-shrink-swell-tests | 72 |
| granular-density-and-groundwater-tests | 8 |

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
| 0..30cm | clay | % | 31–39 | 18–50 | 72 |
| 0..30cm | sand | % | 37–47 | 17–71 | 72 |
| 0..30cm | silt | % | 22–26 | 8–39 | 72 |
| 0..30cm | bd.core | kg/m3 | 1060–1220 | 840–1460 | 72 |
| 0..30cm | soc | g/kg | 12.3–24.4 | 7.8–47.6 | 72 |
| 0..30cm | ph.h2o | pH | 5.7–6.4 | 4.9–7.5 | 72 |
| 30..60cm | clay | % | 32–41 | 19–56 | 72 |
| 30..60cm | sand | % | 37–48 | 16–73 | 72 |
| 30..60cm | silt | % | 19–24 | 5–38 | 72 |
| 30..60cm | bd.core | kg/m3 | 1050–1290 | 670–1530 | 72 |
| 30..60cm | soc | g/kg | 7.3–14.7 | 4.4–29.4 | 72 |
| 30..60cm | ph.h2o | pH | 5.8–6.5 | 4.9–7.9 | 72 |
| 60..100cm | clay | % | 31–42 | 16–57 | 72 |
| 60..100cm | sand | % | 36–50 | 16–78 | 72 |
| 60..100cm | silt | % | 18–24 | 3–39 | 72 |
| 60..100cm | bd.core | kg/m3 | 1040–1290 | 670–1610 | 72 |
| 60..100cm | soc | g/kg | 5.9–15.9 | 2.7–42.6 | 72 |
| 60..100cm | ph.h2o | pH | 5.9–6.8 | 4.8–8 | 72 |
