# Onitsha civil soil screening

869 route/station sample locations; 829 complete profiles; 40 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 829 |
| coverage-gap | 40 |
| fine-soil-plasticity-and-shrink-swell-tests | 829 |
| granular-density-and-groundwater-tests | 695 |

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
| 0..30cm | clay | % | 22–36 | 3–50 | 829 |
| 0..30cm | sand | % | 42–67 | 16–96 | 829 |
| 0..30cm | silt | % | 10–23 | 0–38 | 829 |
| 0..30cm | bd.core | kg/m3 | 1130–1480 | 770–1630 | 829 |
| 0..30cm | soc | g/kg | 5.9–17.3 | 1.9–34 | 829 |
| 0..30cm | ph.h2o | pH | 5.1–6.2 | 4.6–7 | 829 |
| 30..60cm | clay | % | 23–39 | 4–50 | 829 |
| 30..60cm | sand | % | 40–66 | 17–96 | 829 |
| 30..60cm | silt | % | 9–23 | 0–38 | 829 |
| 30..60cm | bd.core | kg/m3 | 1140–1500 | 660–1660 | 829 |
| 30..60cm | soc | g/kg | 3.1–11.3 | 0.9–39.8 | 829 |
| 30..60cm | ph.h2o | pH | 5.1–6.2 | 4.6–7.1 | 829 |
| 60..100cm | clay | % | 24–39 | 4–53 | 829 |
| 60..100cm | sand | % | 36–67 | 12–96 | 829 |
| 60..100cm | silt | % | 9–24 | 0–39 | 829 |
| 60..100cm | bd.core | kg/m3 | 1180–1500 | 590–1680 | 829 |
| 60..100cm | soc | g/kg | 2.5–12.8 | 0.6–49.1 | 829 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.6–7.2 | 829 |
