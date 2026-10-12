# Damascus civil soil screening

7,981 route/station sample locations; 7,971 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 7946 |
| granular-density-and-groundwater-tests | 6441 |
| silt-moisture-frost-and-erosion-review | 175 |

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
| 0..30cm | clay | % | 18–29 | 4–43 | 7971 |
| 0..30cm | sand | % | 36–60 | 10–86 | 7971 |
| 0..30cm | silt | % | 22–37 | 6–52 | 7971 |
| 0..30cm | bd.core | kg/m3 | 1350–1470 | 1160–1640 | 7971 |
| 0..30cm | soc | g/kg | 2.3–11.2 | 0.9–26.2 | 7971 |
| 0..30cm | ph.h2o | pH | 7.4–8.1 | 7–8.7 | 7971 |
| 30..60cm | clay | % | 20–31 | 5–47 | 7971 |
| 30..60cm | sand | % | 36–57 | 9–89 | 7971 |
| 30..60cm | silt | % | 22–34 | 4–51 | 7971 |
| 30..60cm | bd.core | kg/m3 | 1410–1580 | 1240–1770 | 7971 |
| 30..60cm | soc | g/kg | 1.7–5.5 | 0.4–12.3 | 7971 |
| 30..60cm | ph.h2o | pH | 7.3–8.4 | 6.3–9.5 | 7971 |
| 60..100cm | clay | % | 21–32 | 5–48 | 7971 |
| 60..100cm | sand | % | 36–56 | 8–86 | 7971 |
| 60..100cm | silt | % | 22–33 | 0–51 | 7971 |
| 60..100cm | bd.core | kg/m3 | 1420–1630 | 1200–1920 | 7971 |
| 60..100cm | soc | g/kg | 1.4–4.2 | 0.3–11.4 | 7971 |
| 60..100cm | ph.h2o | pH | 7.3–8.6 | 6.5–9.5 | 7971 |
