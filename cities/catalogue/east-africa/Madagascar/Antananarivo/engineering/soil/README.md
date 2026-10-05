# Antananarivo civil soil screening

1,627 route/station sample locations; 1,619 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1619 |
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 1619 |
| granular-density-and-groundwater-tests | 61 |
| silt-moisture-frost-and-erosion-review | 33 |

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
| 0..30cm | clay | % | 21–39 | 7–50 | 1619 |
| 0..30cm | sand | % | 31–61 | 15–86 | 1619 |
| 0..30cm | silt | % | 17–32 | 0–46 | 1619 |
| 0..30cm | bd.core | kg/m3 | 940–1340 | 610–1550 | 1619 |
| 0..30cm | soc | g/kg | 6.1–21.8 | 2.7–46.2 | 1619 |
| 0..30cm | ph.h2o | pH | 5.3–6.2 | 4.5–7.1 | 1619 |
| 30..60cm | clay | % | 24–41 | 4–54 | 1619 |
| 30..60cm | sand | % | 27–59 | 5–89 | 1619 |
| 30..60cm | silt | % | 17–32 | 0–48 | 1619 |
| 30..60cm | bd.core | kg/m3 | 980–1420 | 630–1680 | 1619 |
| 30..60cm | soc | g/kg | 3.2–14.7 | 1.4–29 | 1619 |
| 30..60cm | ph.h2o | pH | 5.3–6.2 | 4.5–7.2 | 1619 |
| 60..100cm | clay | % | 25–42 | 4–56 | 1619 |
| 60..100cm | sand | % | 26–56 | 4–90 | 1619 |
| 60..100cm | silt | % | 19–33 | 0–53 | 1619 |
| 60..100cm | bd.core | kg/m3 | 960–1480 | 120–1730 | 1619 |
| 60..100cm | soc | g/kg | 2.4–12.7 | 0.5–36.1 | 1619 |
| 60..100cm | ph.h2o | pH | 5.4–6.5 | 4.5–7.9 | 1619 |
