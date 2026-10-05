# Port-Harcourt civil soil screening

810 route/station sample locations; 793 complete profiles; 17 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 793 |
| coverage-gap | 17 |
| fine-soil-plasticity-and-shrink-swell-tests | 793 |
| granular-density-and-groundwater-tests | 725 |
| organic-content-and-compressibility-tests | 702 |
| silt-moisture-frost-and-erosion-review | 44 |

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
| 0..30cm | clay | % | 19–32 | 6–49 | 793 |
| 0..30cm | sand | % | 42–63 | 10–86 | 793 |
| 0..30cm | silt | % | 15–29 | 0–48 | 793 |
| 0..30cm | bd.core | kg/m3 | 680–1320 | 270–1520 | 793 |
| 0..30cm | soc | g/kg | 9.5–86.1 | 2.4–330.7 | 793 |
| 0..30cm | ph.h2o | pH | 4.9–5.5 | 4.1–6.8 | 793 |
| 30..60cm | clay | % | 23–34 | 5–49 | 793 |
| 30..60cm | sand | % | 35–59 | 11–84 | 793 |
| 30..60cm | silt | % | 16–33 | 0–54 | 793 |
| 30..60cm | bd.core | kg/m3 | 700–1320 | 220–1560 | 793 |
| 30..60cm | soc | g/kg | 5.2–68.4 | 1.7–215.9 | 793 |
| 30..60cm | ph.h2o | pH | 5–5.5 | 4–6.5 | 793 |
| 60..100cm | clay | % | 24–36 | 7–51 | 793 |
| 60..100cm | sand | % | 31–58 | 7–83 | 793 |
| 60..100cm | silt | % | 15–35 | 0–54 | 793 |
| 60..100cm | bd.core | kg/m3 | 670–1330 | 170–1600 | 793 |
| 60..100cm | soc | g/kg | 4.4–63.2 | 1.3–386.3 | 793 |
| 60..100cm | ph.h2o | pH | 5–5.6 | 4–6.6 | 793 |
