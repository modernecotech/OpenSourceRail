# Antananarivo civil soil screening

7,593 route/station sample locations; 7,588 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 7588 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 7588 |
| granular-density-and-groundwater-tests | 489 |
| organic-content-and-compressibility-tests | 15 |
| silt-moisture-frost-and-erosion-review | 105 |

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
| 0..30cm | clay | % | 21–39 | 7–51 | 7588 |
| 0..30cm | sand | % | 31–61 | 14–86 | 7588 |
| 0..30cm | silt | % | 17–33 | 1–50 | 7588 |
| 0..30cm | bd.core | kg/m3 | 940–1370 | 590–1540 | 7588 |
| 0..30cm | soc | g/kg | 6–24.6 | 2.2–58.8 | 7588 |
| 0..30cm | ph.h2o | pH | 5.2–6.1 | 4.5–7 | 7588 |
| 30..60cm | clay | % | 24–42 | 4–55 | 7588 |
| 30..60cm | sand | % | 27–59 | 5–89 | 7588 |
| 30..60cm | silt | % | 17–33 | 0–49 | 7588 |
| 30..60cm | bd.core | kg/m3 | 960–1430 | 600–1680 | 7588 |
| 30..60cm | soc | g/kg | 3.2–14 | 1.3–36.1 | 7588 |
| 30..60cm | ph.h2o | pH | 5.2–6.2 | 4.5–7.2 | 7588 |
| 60..100cm | clay | % | 25–42 | 4–57 | 7588 |
| 60..100cm | sand | % | 25–56 | 4–90 | 7588 |
| 60..100cm | silt | % | 19–34 | 0–54 | 7588 |
| 60..100cm | bd.core | kg/m3 | 910–1490 | 100–1730 | 7588 |
| 60..100cm | soc | g/kg | 2.2–12.7 | 0.5–48.6 | 7588 |
| 60..100cm | ph.h2o | pH | 5.2–6.5 | 4.4–7.9 | 7588 |
