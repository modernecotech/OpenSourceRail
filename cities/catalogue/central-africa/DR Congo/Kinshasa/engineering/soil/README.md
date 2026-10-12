# Kinshasa civil soil screening

18,177 route/station sample locations; 18,140 complete profiles; 37 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 18116 |
| coverage-gap | 37 |
| fine-soil-plasticity-and-shrink-swell-tests | 18140 |
| granular-density-and-groundwater-tests | 5670 |
| organic-content-and-compressibility-tests | 16 |
| silt-moisture-frost-and-erosion-review | 151 |

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
| 0..30cm | clay | % | 24–36 | 7–49 | 18140 |
| 0..30cm | sand | % | 34–59 | 7–93 | 18140 |
| 0..30cm | silt | % | 17–30 | 0–49 | 18140 |
| 0..30cm | bd.core | kg/m3 | 1110–1400 | 800–1620 | 18140 |
| 0..30cm | soc | g/kg | 6.3–21.2 | 2.4–43.8 | 18140 |
| 0..30cm | ph.h2o | pH | 5.3–6.6 | 4.4–7.8 | 18140 |
| 30..60cm | clay | % | 28–40 | 8–54 | 18140 |
| 30..60cm | sand | % | 31–57 | 8–91 | 18140 |
| 30..60cm | silt | % | 15–31 | 0–51 | 18140 |
| 30..60cm | bd.core | kg/m3 | 1170–1440 | 830–1640 | 18140 |
| 30..60cm | soc | g/kg | 3.9–18 | 1.4–45.2 | 18140 |
| 30..60cm | ph.h2o | pH | 5.2–6.6 | 4.4–7.7 | 18140 |
| 60..100cm | clay | % | 28–42 | 7–55 | 18140 |
| 60..100cm | sand | % | 30–55 | 5–91 | 18140 |
| 60..100cm | silt | % | 15–31 | 0–51 | 18140 |
| 60..100cm | bd.core | kg/m3 | 1150–1440 | 680–1660 | 18140 |
| 60..100cm | soc | g/kg | 3.6–14.2 | 1.1–64.6 | 18140 |
| 60..100cm | ph.h2o | pH | 5.3–6.7 | 4.6–7.9 | 18140 |
