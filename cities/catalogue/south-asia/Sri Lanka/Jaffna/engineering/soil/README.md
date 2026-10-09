# Jaffna civil soil screening

721 route/station sample locations; 715 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 13 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 715 |
| granular-density-and-groundwater-tests | 715 |
| organic-content-and-compressibility-tests | 30 |

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
| 0..30cm | clay | % | 21–30 | 2–49 | 715 |
| 0..30cm | sand | % | 47–65 | 7–95 | 715 |
| 0..30cm | silt | % | 14–23 | 0–43 | 715 |
| 0..30cm | bd.core | kg/m3 | 1020–1330 | 590–1640 | 715 |
| 0..30cm | soc | g/kg | 6.7–21.6 | 2.3–58.2 | 715 |
| 0..30cm | ph.h2o | pH | 6.3–7.2 | 5.3–8.3 | 715 |
| 30..60cm | clay | % | 21–31 | 1–53 | 715 |
| 30..60cm | sand | % | 47–66 | 12–95 | 715 |
| 30..60cm | silt | % | 13–23 | 0–46 | 715 |
| 30..60cm | bd.core | kg/m3 | 1020–1310 | 540–1650 | 715 |
| 30..60cm | soc | g/kg | 4.4–19.3 | 0.8–48.3 | 715 |
| 30..60cm | ph.h2o | pH | 6.7–7.4 | 5.5–8.4 | 715 |
| 60..100cm | clay | % | 22–31 | 1–52 | 715 |
| 60..100cm | sand | % | 48–65 | 12–95 | 715 |
| 60..100cm | silt | % | 12–22 | 0–45 | 715 |
| 60..100cm | bd.core | kg/m3 | 990–1260 | 440–1710 | 715 |
| 60..100cm | soc | g/kg | 4–19.1 | 0.6–55 | 715 |
| 60..100cm | ph.h2o | pH | 6.8–7.5 | 5.5–8.6 | 715 |
