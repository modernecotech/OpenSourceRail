# Surabaya civil soil screening

1,758 route/station sample locations; 1,723 complete profiles; 35 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1723 |
| coverage-gap | 35 |
| fine-soil-plasticity-and-shrink-swell-tests | 1723 |
| granular-density-and-groundwater-tests | 1708 |
| organic-content-and-compressibility-tests | 57 |
| silt-moisture-frost-and-erosion-review | 9 |

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
| 0..30cm | clay | % | 19–38 | 2–54 | 1723 |
| 0..30cm | sand | % | 37–66 | 8–95 | 1723 |
| 0..30cm | silt | % | 15–29 | 0–49 | 1723 |
| 0..30cm | bd.core | kg/m3 | 1050–1400 | 670–1670 | 1723 |
| 0..30cm | soc | g/kg | 4.6–27.2 | 1.3–68.1 | 1723 |
| 0..30cm | ph.h2o | pH | 5.7–6.4 | 4.5–7.6 | 1723 |
| 30..60cm | clay | % | 20–39 | 3–57 | 1723 |
| 30..60cm | sand | % | 35–66 | 4–94 | 1723 |
| 30..60cm | silt | % | 14–29 | 0–52 | 1723 |
| 30..60cm | bd.core | kg/m3 | 1050–1480 | 540–1740 | 1723 |
| 30..60cm | soc | g/kg | 3–21.9 | 0.9–57.8 | 1723 |
| 30..60cm | ph.h2o | pH | 5.8–6.4 | 4.5–7.7 | 1723 |
| 60..100cm | clay | % | 21–40 | 3–59 | 1723 |
| 60..100cm | sand | % | 33–65 | 5–94 | 1723 |
| 60..100cm | silt | % | 13–30 | 0–50 | 1723 |
| 60..100cm | bd.core | kg/m3 | 1000–1510 | 460–1730 | 1723 |
| 60..100cm | soc | g/kg | 2.5–24.6 | 0.3–116.4 | 1723 |
| 60..100cm | ph.h2o | pH | 5.8–6.5 | 4.7–7.9 | 1723 |
