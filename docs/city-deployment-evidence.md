# City soil inputs and deployment evidence

The catalogue now materialises the survey/civil readiness chain and native/SUMO
journey-time comparison for every city. Each city's `engineering/deployment/`
register identifies the remaining work, responsible function, closure evidence
and current result. The [catalogue index](../engineering/analysis/deployment-summary.md)
aggregates actual open gates. Generated documents do not count as received surveys,
completed construction or operating approval.

[City workforce and design development](city-workforce-design-development.md)
adds per-city organisation, skills/tasks, construction work profiles, joint and
finish maintenance, and climate-informed movement calculations.

## Soil inputs used for civil planning

The retained catalogue extraction covers **67,033 scope locations**: all
**10,215 station features** and **10,597 civil segments**, using 54,594 distinct
coordinates. Complete profiles exist at 64,805 locations; 2,228 have missing
values, spread across 126 cities. Repeated coordinates at shared scope boundaries
are sampled once and retained against each applicable station or segment.

[OpenLandMap soilDB](https://github.com/openlandmap/soildb) supplies shallow
pedological predictions, including uncertainty. The importer uses its published
2020–2022 mean, p16 and p84 layers at a common 120 m resolution, for clay, sand,
silt, fine-earth bulk density, organic carbon and pH. Depth intervals are 0–30,
30–60 and 60–100 cm. The nominal p16–p84 interval describes prediction uncertainty;
it is not an engineering characteristic value or a range of proven site conditions.

The [source lock](../engineering/data/soildb/sources.json) pins the upstream Git
revision and 54 layer URLs. The original [layer catalogue](../engineering/data/soildb/OpenLandMap_soildb_COGS.csv)
is retained with its hash. HTTP range requests read only relevant raster blocks.
Each city retains raw sampled values in engineering units, source ETags, raster
scales, nodata values, coordinate system and input/output hashes. The dataset is
attributed to Hengl et al., DOI 10.5194/essd-2025-336, under CC BY 4.0.

Sample locations include every station, each civil segment's ends and midpoint,
and additional locations with no more than 1 km of mapped route between them.
The route and station GIS layers determine locations; one city-centre value is
not extrapolated across the railway. Raster pixel size and route sample spacing
are separate quantities. Native raster pixels are sampled without smoothing or
nearest-valid-pixel substitution.

The upstream bulk-density filename encodes g/cm³ and its TIFF scale is 0.01,
while the catalogue unit column says kg/m³. The importer applies the TIFF scale
once, then multiplies by 1,000 to report kg/m³: raw 150 becomes 1,500 kg/m³.
Soil pH is scaled once to ordinary pH units. Nodata becomes an empty CSV value
and an explicit coverage flag. The source excludes deserts and permanent ice;
no-data can also occur locally within mapped cities.

Each city receives:

| File under `engineering/soil/` | Use |
|---|---|
| `samples.csv` | Location, chainage, depth, six properties and three statistics |
| `source-receipt.json` | Input and sample hashes, source URLs and raster metadata |
| `sample-locations.geojson` | GIS map with location-specific investigation triggers |
| `civil-investigation-plan.json` | Every station and civil segment mapped to samples and field work |
| `summary.json` and `README.md` | Coverage, units, triggers and modelling boundaries |

The civil plan prioritises plasticity/shrink-swell tests when the clay upper
prediction reaches 35%, moisture/erosion review when silt reaches 50%, granular
density/groundwater testing when sand reaches 70%, organic/compressibility tests
when organic carbon reaches 50 g/kg, and durability testing when the pH lower
prediction is below 5.5. These are transparent OSR investigation triggers, not
regulatory thresholds, soil hazard diagnoses or foundation selection rules.
High sand content alone does not establish liquefaction; clay content alone
does not establish swelling. Texture fractions remain independent predictions.

Bearing capacity, CBR, friction, cohesion, groundwater, contamination, sulfate/
chloride attack and deep stratigraphy are not supplied by these maps. Those
fields remain unknown. SoilDB values inform investigation locations and lab
scope; they do not manufacture boreholes or automatically resize foundations,
change excavation quantities or increase civil CAPEX.

The [Samawah soil report](../cities/catalogue/west-asia/Iraq/Samawah/engineering/soil/README.md)
and [deployment register](../cities/catalogue/west-asia/Iraq/Samawah/engineering/deployment/README.md)
show the complete handoff. The drainage/ground readiness report references the
soil summary and investigation-plan hashes while retaining its field-evidence gate.

## Other gaps repaired

- Survey/civil readiness and operations cross-checks were present for only two
  cities. They are now generated for the complete catalogue.
- Survey and alignment regeneration could overwrite received manifests. Existing
  receipt files are now preserved; their contents are still validated.
- Most retained simulation summaries lacked native reference timing fields.
  A separately generated, source-bound native kinematic report now supplies them.
  Its one-second execution extracts the reference calculation; it is explicitly
  not a full service or endurance replay.
- SUMO evidence is refreshed with current station dwell times before comparison.
  Missing or stale timing inputs cannot silently pass, and the comparison remains
  separate from conflict-aware capacity and operating acceptance.
- The provenance review exposed 264 full-service reports bound to older scenarios
  or validator inputs, with all 266 predating the current simulator binary.
  Current timing comparisons are separate from the full-service freshness gate;
  stale service acceptance is not carried forward.
  Samawah, Soroti and Sheikhupura have since passed fresh two-run nominal
  validation and all eight degraded cases each. The other 263 cities retain an
  explicit replay-refresh gate. Continuous two-day station/depot replay now
  passes in nine cities: Samawah, Uige, Quelimane, Edea, Bukavu, Soroti,
  Sheikhupura, Sumbawanga and Tartus.
- Soil, timing and deployment evidence is included in city package inventories
  and source-hash checks. Regeneration keeps these outputs connected to the inputs.

## Reproduce

```bash
# Fetch the pinned soil layers for the complete current catalogue.
.venv/bin/python engineering/analysis/city_soils.py --all --fetch --jobs 6

# Regenerate soil reports offline from retained, hash-checked samples.
.venv/bin/python engineering/analysis/city_soils.py --all

# Build native references, refresh civil gates and compare current SUMO evidence.
.venv/bin/python tools/automation/generate-deployment-evidence.py --all --reuse-sumo

# Rebuild the catalogue deployment summary.
.venv/bin/python engineering/analysis/city_deployment.py --all
```

For one changed city use `--design <city>/design.toml`; add `--fetch-soils` to
the deployment command when soil sample locations or source inputs have changed.
The normal city and full-package regeneration workflows include this step.
Existing receipt manifests survive regeneration. Newly required deliveries or
changed alignment scope appear as unresolved receipt checks until supplied.

Remaining site work includes survey/land/utilities, geotechnical investigation,
local hydrology, support and erection design, physical stabling and depot
layouts, installed-cost reconciliation and operator acceptance. Remaining
operating-model work includes the solar/storage replenishment duty and continuous
stabling evidence beyond the nine retained two-day replays. Per-city fleet
shortfalls remain explicit; neither interline transfers nor a default grid
upgrade is introduced to hide them.
