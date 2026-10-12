# Visakhapatnam civil soil screening

8,658 route/station sample locations; 8,646 complete profiles; 12 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1 |
| coverage-gap | 12 |
| fine-soil-plasticity-and-shrink-swell-tests | 8646 |
| granular-density-and-groundwater-tests | 8544 |
| silt-moisture-frost-and-erosion-review | 8 |

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
| 0..30cm | clay | % | 20–34 | 3–49 | 8646 |
| 0..30cm | sand | % | 37–62 | 8–90 | 8646 |
| 0..30cm | silt | % | 17–31 | 1–50 | 8646 |
| 0..30cm | bd.core | kg/m3 | 1170–1510 | 840–1700 | 8646 |
| 0..30cm | soc | g/kg | 4.8–14.6 | 1.4–37.9 | 8646 |
| 0..30cm | ph.h2o | pH | 6.5–7.4 | 5.5–8.3 | 8646 |
| 30..60cm | clay | % | 20–35 | 2–51 | 8646 |
| 30..60cm | sand | % | 37–64 | 6–93 | 8646 |
| 30..60cm | silt | % | 15–29 | 0–49 | 8646 |
| 30..60cm | bd.core | kg/m3 | 1150–1520 | 690–1760 | 8646 |
| 30..60cm | soc | g/kg | 3–11.4 | 0.9–36.5 | 8646 |
| 30..60cm | ph.h2o | pH | 6.7–7.5 | 5.5–8.5 | 8646 |
| 60..100cm | clay | % | 20–35 | 1–51 | 8646 |
| 60..100cm | sand | % | 36–64 | 6–93 | 8646 |
| 60..100cm | silt | % | 16–29 | 0–49 | 8646 |
| 60..100cm | bd.core | kg/m3 | 1040–1550 | 460–1820 | 8646 |
| 60..100cm | soc | g/kg | 2.2–9.8 | 0.7–28.5 | 8646 |
| 60..100cm | ph.h2o | pH | 6.8–7.7 | 5.3–8.8 | 8646 |
