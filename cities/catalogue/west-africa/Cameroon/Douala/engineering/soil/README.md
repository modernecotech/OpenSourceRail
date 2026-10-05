# Douala civil soil screening

513 route/station sample locations; 480 complete profiles; 33 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 480 |
| coverage-gap | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 480 |
| granular-density-and-groundwater-tests | 305 |
| organic-content-and-compressibility-tests | 247 |
| silt-moisture-frost-and-erosion-review | 20 |

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
| 0..30cm | clay | % | 24–39 | 7–53 | 480 |
| 0..30cm | sand | % | 33–58 | 9–89 | 480 |
| 0..30cm | silt | % | 17–31 | 0–49 | 480 |
| 0..30cm | bd.core | kg/m3 | 620–1220 | 280–1510 | 480 |
| 0..30cm | soc | g/kg | 10.1–52.6 | 3.8–104.3 | 480 |
| 0..30cm | ph.h2o | pH | 5.2–5.8 | 4.3–7 | 480 |
| 30..60cm | clay | % | 24–40 | 6–57 | 480 |
| 30..60cm | sand | % | 31–56 | 6–86 | 480 |
| 30..60cm | silt | % | 20–34 | 0–55 | 480 |
| 30..60cm | bd.core | kg/m3 | 670–1280 | 200–1600 | 480 |
| 30..60cm | soc | g/kg | 5.1–60.1 | 1.4–115.7 | 480 |
| 30..60cm | ph.h2o | pH | 5.3–5.9 | 4.1–7 | 480 |
| 60..100cm | clay | % | 24–40 | 6–59 | 480 |
| 60..100cm | sand | % | 32–58 | 4–86 | 480 |
| 60..100cm | silt | % | 19–33 | 0–53 | 480 |
| 60..100cm | bd.core | kg/m3 | 640–1340 | 190–1670 | 480 |
| 60..100cm | soc | g/kg | 5.3–66.2 | 1.5–143.5 | 480 |
| 60..100cm | ph.h2o | pH | 5.4–5.9 | 4.2–7.1 | 480 |
