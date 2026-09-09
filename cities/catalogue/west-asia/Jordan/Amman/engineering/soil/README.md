# Amman civil soil screening

661 route/station sample locations; 647 complete profiles; 14 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 14 |
| fine-soil-plasticity-and-shrink-swell-tests | 646 |
| granular-density-and-groundwater-tests | 507 |
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
| 0..30cm | clay | % | 20–30 | 5–43 | 647 |
| 0..30cm | sand | % | 35–55 | 9–83 | 647 |
| 0..30cm | silt | % | 24–37 | 8–53 | 647 |
| 0..30cm | bd.core | kg/m3 | 1360–1450 | 1150–1620 | 647 |
| 0..30cm | soc | g/kg | 2.4–12.5 | 0.8–26.4 | 647 |
| 0..30cm | ph.h2o | pH | 7.4–8 | 6.8–8.8 | 647 |
| 30..60cm | clay | % | 22–33 | 4–47 | 647 |
| 30..60cm | sand | % | 33–56 | 9–87 | 647 |
| 30..60cm | silt | % | 22–36 | 3–53 | 647 |
| 30..60cm | bd.core | kg/m3 | 1430–1570 | 1260–1790 | 647 |
| 30..60cm | soc | g/kg | 1.6–5.1 | 0.4–12 | 647 |
| 30..60cm | ph.h2o | pH | 7.4–8.3 | 6.6–9.3 | 647 |
| 60..100cm | clay | % | 22–34 | 4–50 | 647 |
| 60..100cm | sand | % | 33–56 | 7–89 | 647 |
| 60..100cm | silt | % | 22–36 | 0–54 | 647 |
| 60..100cm | bd.core | kg/m3 | 1440–1610 | 1230–1830 | 647 |
| 60..100cm | soc | g/kg | 1.4–3.7 | 0.2–8.5 | 647 |
| 60..100cm | ph.h2o | pH | 7.4–8.4 | 6.5–9.4 | 647 |
