# Baghdad civil soil screening

825 route/station sample locations; 796 complete profiles; 29 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 29 |
| fine-soil-plasticity-and-shrink-swell-tests | 741 |
| granular-density-and-groundwater-tests | 458 |
| silt-moisture-frost-and-erosion-review | 534 |

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
| 0..30cm | clay | % | 16–32 | 3–41 | 796 |
| 0..30cm | sand | % | 25–57 | 5–84 | 796 |
| 0..30cm | silt | % | 27–44 | 11–58 | 796 |
| 0..30cm | bd.core | kg/m3 | 1420–1500 | 1210–1720 | 796 |
| 0..30cm | soc | g/kg | 2.2–6.1 | 0.5–13.7 | 796 |
| 0..30cm | ph.h2o | pH | 7.6–8.3 | 6.8–9.1 | 796 |
| 30..60cm | clay | % | 18–33 | 2–43 | 796 |
| 30..60cm | sand | % | 27–56 | 5–91 | 796 |
| 30..60cm | silt | % | 25–41 | 5–60 | 796 |
| 30..60cm | bd.core | kg/m3 | 1410–1560 | 1150–1770 | 796 |
| 30..60cm | soc | g/kg | 1.7–3.6 | 0–9.9 | 796 |
| 30..60cm | ph.h2o | pH | 7.7–8.6 | 6.4–10.1 | 796 |
| 60..100cm | clay | % | 19–34 | 3–44 | 796 |
| 60..100cm | sand | % | 28–57 | 7–90 | 796 |
| 60..100cm | silt | % | 23–41 | 2–58 | 796 |
| 60..100cm | bd.core | kg/m3 | 1410–1630 | 1210–1940 | 796 |
| 60..100cm | soc | g/kg | 1.5–2.8 | 0–8.3 | 796 |
| 60..100cm | ph.h2o | pH | 7.6–8.7 | 6.2–10.1 | 796 |
