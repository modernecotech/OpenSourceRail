# Using public GIS layers to model and price the Airport railway

Use the [published site study](GIS-SIMULATION.md) for the modelled railway price. The [earlier audit](AUDIT-RESULTS.md) remains the unprofiled comparison for the 17.46 km horizontal trace. The original 12 km case is retained for reproducing its results. The two current cases have distinct alignment and evaluation IDs.

## Data and model

| Input | Application |
|---|---|
| Copernicus GLO-30, EGM2008 | Surface elevations along the centreline at 20 m intervals, at stops and at the endpoints. Treat bridges, roofs and vegetation as possible contributions to the sampled surface. The planning rail profile places the nominal soffit 6 m above that surface, assumes 2 m from rail to soffit, limits the grade to 0.6% and keeps 140 m intervals level at stations. These are editable planning inputs. [Copernicus dataset and licence](https://copernicus-dem-30m.s3.amazonaws.com/readme.html) |
| ISRIC SoilGrids 2.0, 250 m | Use shallow and deep clay estimates and deep prediction quantiles to prioritise foundation-treatment allowances. Existing low/base/high ground sensitivities supply alternative bearing pressures, shaft lengths and proportions. Texture and moisture history carry no direct conversion to allowable pressure. Where the grid has no usable prediction the sample is left blank. [ISRIC SoilGrids documentation](https://docs.isric.org/globaldata/soilgrids/) |
| EC JRC/Google Global Surface Water 1.5, approximately 30 m | Sample historical occurrence for 1984–2024 on the centreline and retain the maximum within 100 m as an adjacent-water indicator. A pixel with zero occurrence records no historical detection at that pixel. Read the proximity values as screening evidence alongside the digital surface, particularly where a bridge or road may conceal water. [JRC data access](https://global-surface-water.appspot.com/download) |

The physical rail profile derives from the retained horizontal trace and sampled elevations. A centreline vertex locates the provisional Um Al Tubol stop at its earlier assumed chainage. Directional grades enter the existing time-stepped motion and power model. The resulting working days carry the same train, station calls, demand scenario and normal/degraded conditions into both power comparisons. The headway, terminal offset and platform length describe the case being priced. The route profiles are piecewise linear planning geometry.

The construction estimate uses the selected trial girder and its existing moving-load analysis. Site support quantities derive from the rail-level profile and the height of the cap above the sampled surface. The ground parameters are planning scenarios. A risk allowance considers shaft work and shallow footing enlargement, with treatment assignments prioritised by available water and texture evidence. The site costs identify the retained standard-scope allowances and show incremental site quantities so the same work enters the ledger once.

The cost record uses the existing low/base/high Iraqi material and contractor assumptions. The electrical rows estimate railway-side equipment, protection equipment scope, per-site AC tie-ins, routine upkeep and scheduled renewals. The model applies the existing design, test and programme allowances and the established cash schedule once. The cash rows identify exclusions, such as extraordinary network reinforcement, unlocated property works, taxation and financing. The 30-year values are discounted costs before fares. The annual cash series shows fares and public funding separately. [Earlier buyer ledger and scope](audit-production-guide.md)

## Reproduce, inspect and vary

The small [sampled layers file](site-layers.json) contains positions, source URLs, versions, raster hashes, units and attribution. The standard study runs offline from that file. The [GeoJSON](site-study.geojson) carries the alignment, stations and samples in WGS84, with the vertical datum and height fields recorded separately. The [CSV](site-study-profile.csv) works in a spreadsheet or GIS, and the [cash and assumptions JSON](site-study.json) identifies the evaluated alignment, site allowances, missing values and operating outcomes.

From the repository root:

```sh
./osr design railway site-study --check
./osr design railway site-study --output build/airport-gis-review
./osr design railway site-study --clearance-m 7 --grade-pct 0.5 --output build/airport-gis-alt
```

To regenerate the raster samples, install or use the repository's rasterio environment. Run the sampler with cached tiles or request the same published tiles. The cached rasters occupy about 113 MB. Review source changes before replacing a published sample.

```sh
python3 -m cities.Baghdad.engineering.simulation.site_layers --download --check
./osr design railway site-study --publish
```

Use the normal and outage trip totals to judge the proposed service before comparing the estimates. The study supports planning and budget comparison. The decision record retains the underlying operating holds for braking, utility protection and other fitted equipment.
