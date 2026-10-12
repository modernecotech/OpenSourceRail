# Douala civil soil screening

6,749 route/station sample locations; 6,727 complete profiles; 22 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6727 |
| coverage-gap | 22 |
| fine-soil-plasticity-and-shrink-swell-tests | 6727 |
| granular-density-and-groundwater-tests | 4601 |
| organic-content-and-compressibility-tests | 1881 |
| silt-moisture-frost-and-erosion-review | 251 |

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
| 0..30cm | clay | % | 24–39 | 5–53 | 6727 |
| 0..30cm | sand | % | 32–59 | 8–89 | 6727 |
| 0..30cm | silt | % | 17–31 | 0–50 | 6727 |
| 0..30cm | bd.core | kg/m3 | 620–1220 | 230–1550 | 6727 |
| 0..30cm | soc | g/kg | 10–57.4 | 3.5–126.7 | 6727 |
| 0..30cm | ph.h2o | pH | 5.2–5.8 | 4.2–7 | 6727 |
| 30..60cm | clay | % | 24–40 | 4–60 | 6727 |
| 30..60cm | sand | % | 30–56 | 6–90 | 6727 |
| 30..60cm | silt | % | 18–34 | 0–55 | 6727 |
| 30..60cm | bd.core | kg/m3 | 630–1260 | 190–1600 | 6727 |
| 30..60cm | soc | g/kg | 5–62.3 | 1.4–121.4 | 6727 |
| 30..60cm | ph.h2o | pH | 5.3–5.9 | 4.1–7 | 6727 |
| 60..100cm | clay | % | 24–40 | 4–60 | 6727 |
| 60..100cm | sand | % | 31–58 | 3–91 | 6727 |
| 60..100cm | silt | % | 17–33 | 0–53 | 6727 |
| 60..100cm | bd.core | kg/m3 | 610–1310 | 180–1670 | 6727 |
| 60..100cm | soc | g/kg | 5.1–69.5 | 1.4–157.1 | 6727 |
| 60..100cm | ph.h2o | pH | 5.3–5.9 | 4.2–7.1 | 6727 |
