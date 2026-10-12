# Surabaya civil soil screening

7,930 route/station sample locations; 7,621 complete profiles; 309 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 7621 |
| coverage-gap | 309 |
| fine-soil-plasticity-and-shrink-swell-tests | 7621 |
| granular-density-and-groundwater-tests | 7443 |
| organic-content-and-compressibility-tests | 322 |
| silt-moisture-frost-and-erosion-review | 39 |

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
| 0..30cm | clay | % | 19–38 | 2–54 | 7621 |
| 0..30cm | sand | % | 34–67 | 7–95 | 7621 |
| 0..30cm | silt | % | 14–30 | 0–49 | 7621 |
| 0..30cm | bd.core | kg/m3 | 1050–1400 | 620–1660 | 7621 |
| 0..30cm | soc | g/kg | 4.7–27.2 | 1.1–87.6 | 7621 |
| 0..30cm | ph.h2o | pH | 5.5–6.4 | 4.3–7.6 | 7621 |
| 30..60cm | clay | % | 20–40 | 3–57 | 7621 |
| 30..60cm | sand | % | 35–67 | 4–93 | 7621 |
| 30..60cm | silt | % | 12–29 | 0–50 | 7621 |
| 30..60cm | bd.core | kg/m3 | 1060–1480 | 510–1760 | 7621 |
| 30..60cm | soc | g/kg | 3.1–23.4 | 0.8–61.9 | 7621 |
| 30..60cm | ph.h2o | pH | 5.6–6.4 | 4.5–7.8 | 7621 |
| 60..100cm | clay | % | 21–41 | 3–61 | 7621 |
| 60..100cm | sand | % | 33–66 | 4–93 | 7621 |
| 60..100cm | silt | % | 12–29 | 0–51 | 7621 |
| 60..100cm | bd.core | kg/m3 | 1010–1510 | 380–1780 | 7621 |
| 60..100cm | soc | g/kg | 2.6–23.7 | 0.3–109.4 | 7621 |
| 60..100cm | ph.h2o | pH | 5.6–6.5 | 4.6–7.9 | 7621 |
