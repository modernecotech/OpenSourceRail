# Luanda civil soil screening

5,958 route/station sample locations; 5,958 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1344 |
| fine-soil-plasticity-and-shrink-swell-tests | 4974 |
| granular-density-and-groundwater-tests | 5934 |
| organic-content-and-compressibility-tests | 15 |
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
| 0..30cm | clay | % | 17–34 | 2–47 | 5958 |
| 0..30cm | sand | % | 38–71 | 16–95 | 5958 |
| 0..30cm | silt | % | 10–28 | 0–41 | 5958 |
| 0..30cm | bd.core | kg/m3 | 1210–1490 | 950–1710 | 5958 |
| 0..30cm | soc | g/kg | 3.5–18.1 | 1.3–40.4 | 5958 |
| 0..30cm | ph.h2o | pH | 6.3–8.1 | 5.3–9 | 5958 |
| 30..60cm | clay | % | 18–36 | 2–51 | 5958 |
| 30..60cm | sand | % | 38–68 | 11–93 | 5958 |
| 30..60cm | silt | % | 9–27 | 0–50 | 5958 |
| 30..60cm | bd.core | kg/m3 | 1220–1520 | 870–1750 | 5958 |
| 30..60cm | soc | g/kg | 2.5–14.8 | 0.4–50.6 | 5958 |
| 30..60cm | ph.h2o | pH | 6.4–8.2 | 5.2–9.2 | 5958 |
| 60..100cm | clay | % | 18–35 | 2–53 | 5958 |
| 60..100cm | sand | % | 39–68 | 10–94 | 5958 |
| 60..100cm | silt | % | 9–26 | 0–52 | 5958 |
| 60..100cm | bd.core | kg/m3 | 1160–1520 | 710–1830 | 5958 |
| 60..100cm | soc | g/kg | 1.8–13.2 | 0–93.6 | 5958 |
| 60..100cm | ph.h2o | pH | 6.4–8.3 | 4.9–9.4 | 5958 |
