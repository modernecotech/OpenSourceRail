# Douala civil soil screening

1,079 route/station sample locations; 1,066 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1066 |
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 1066 |
| granular-density-and-groundwater-tests | 677 |
| organic-content-and-compressibility-tests | 513 |
| silt-moisture-frost-and-erosion-review | 31 |

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
| 0..30cm | clay | % | 24–39 | 7–54 | 1066 |
| 0..30cm | sand | % | 33–60 | 9–90 | 1066 |
| 0..30cm | silt | % | 16–31 | 0–49 | 1066 |
| 0..30cm | bd.core | kg/m3 | 640–1210 | 300–1510 | 1066 |
| 0..30cm | soc | g/kg | 9.8–52.6 | 3.6–124.6 | 1066 |
| 0..30cm | ph.h2o | pH | 5.2–5.8 | 4.3–7 | 1066 |
| 30..60cm | clay | % | 24–40 | 5–58 | 1066 |
| 30..60cm | sand | % | 30–57 | 7–89 | 1066 |
| 30..60cm | silt | % | 19–34 | 0–55 | 1066 |
| 30..60cm | bd.core | kg/m3 | 630–1280 | 200–1600 | 1066 |
| 30..60cm | soc | g/kg | 5.1–56.1 | 1.4–116.6 | 1066 |
| 30..60cm | ph.h2o | pH | 5.3–5.9 | 4.1–7 | 1066 |
| 60..100cm | clay | % | 23–40 | 5–58 | 1066 |
| 60..100cm | sand | % | 31–58 | 5–86 | 1066 |
| 60..100cm | silt | % | 18–33 | 0–53 | 1066 |
| 60..100cm | bd.core | kg/m3 | 610–1330 | 190–1670 | 1066 |
| 60..100cm | soc | g/kg | 5.6–61.7 | 1.5–134.2 | 1066 |
| 60..100cm | ph.h2o | pH | 5.3–5.9 | 4.1–7.1 | 1066 |
