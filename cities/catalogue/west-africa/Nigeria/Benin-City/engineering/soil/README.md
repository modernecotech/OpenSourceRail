# Benin-City civil soil screening

1,848 route/station sample locations; 1,848 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1848 |
| fine-soil-plasticity-and-shrink-swell-tests | 1340 |
| granular-density-and-groundwater-tests | 1631 |
| silt-moisture-frost-and-erosion-review | 172 |

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
| 0..30cm | clay | % | 17–31 | 6–43 | 1848 |
| 0..30cm | sand | % | 38–65 | 16–88 | 1848 |
| 0..30cm | silt | % | 16–33 | 0–51 | 1848 |
| 0..30cm | bd.core | kg/m3 | 930–1380 | 400–1550 | 1848 |
| 0..30cm | soc | g/kg | 7.4–21.2 | 3.5–42 | 1848 |
| 0..30cm | ph.h2o | pH | 5.2–5.8 | 4.4–7 | 1848 |
| 30..60cm | clay | % | 18–32 | 6–44 | 1848 |
| 30..60cm | sand | % | 36–65 | 14–88 | 1848 |
| 30..60cm | silt | % | 14–34 | 0–55 | 1848 |
| 30..60cm | bd.core | kg/m3 | 940–1400 | 420–1600 | 1848 |
| 30..60cm | soc | g/kg | 3.8–9.8 | 1.5–19.9 | 1848 |
| 30..60cm | ph.h2o | pH | 5.3–5.9 | 4.5–7 | 1848 |
| 60..100cm | clay | % | 19–33 | 6–46 | 1848 |
| 60..100cm | sand | % | 33–64 | 10–90 | 1848 |
| 60..100cm | silt | % | 15–34 | 0–54 | 1848 |
| 60..100cm | bd.core | kg/m3 | 950–1430 | 280–1630 | 1848 |
| 60..100cm | soc | g/kg | 3.2–6.7 | 1.1–20.7 | 1848 |
| 60..100cm | ph.h2o | pH | 5.4–6 | 4.5–7 | 1848 |
