# Airport route and demand

The mapped study covers **17.461 km** from the airport terminal area to Al Qadisiya. The earlier 12 km schematic falls **3.089 km** short of the sum of the great-circle distances through the five known centroids in stop order. That bound applies to those centroids. The location of Um Al Tubol was omitted from the bound. [Retained place sequence](../../maps/corridor-review.geojson) · [Earlier corridor study](SIMULATION.md)

| Stop | Study chainage (km) | Location basis |
| --- | ---: | --- |
| Baghdad Airport terminal | 0.000 | Passenger building centroid |
| Al Amiriya | 7.449 | Area centroid |
| Hay Al Aamil | 13.016 | Area centroid |
| Al Bayaa | 14.962 | Area centroid |
| Um Al Tubol | 16.212 | Assumed midpoint chainage within the Al Bayaa–Al Qadisiya review link |
| Al Qadisiya | 17.461 | Area centroid |

The study incorporates **6.725 km** of retained Airport Highway road geometry, with **10.736 km** of straight review connectors. Each connector has its endpoints and review reason in the alignment record and GeoJSON. The road sections provide a mapped horizontal reference. Survey the railway centreline, curve radii, levels, crossing clearances, station sites and accessible entrances before procuring against a station or pier location. The GeoJSON leaves Um Al Tubol without a point geometry. The vertical profile remains open. [Retained OpenStreetMap-derived road background](../../../catalogue/west-asia/Iraq/Baghdad/map-context.json.gz) · [Map background and attribution](../../maps/README.md)

## Journeys and station load

These central-demand comparisons use the same study alignment, a 35-second booked dwell and 18 daily service hours. The platform queue is the largest hourly origin flow in one direction multiplied by the headway. The busiest departure load is the equivalent maximum flow across any one rail leg. Capacity carryover, closing-time arrivals and uneven departures require the moving service replay.

| Headway (min) | Fixed annual journeys | Service-sensitive annual journeys | Service-sensitive busiest departure | Service-sensitive platform queue |
| ---: | ---: | ---: | ---: | ---: |
| 15 | 4,015,210 | 3,852,384 | 104.2 | 48.0 |
| 20 | 4,015,210 | 3,399,717 | 122.6 | 56.5 |
| 30 | 4,015,210 | 2,647,702 | 143.2 | 66.0 |

The fixed case carries forward all historical hourly OD values and uses the new chainages for passenger-km. The service-sensitive case weights each OD by the exponential of the change in generalised minutes relative to the 12 km, 15-minute central-access prior. The trial response is 0.025 per minute. The calculation includes booked ride time, expected first wait of half the headway, two walking paths, illustrative transfer friction at Al Amiriya and Al Bayaa, and an optional fare converted at the trial value of time. Walk and wait time carry twice the in-vehicle time weight. The central case allows 300 m at 1 m/s plus 60 seconds per path and applies an extra walking path, half a 15-minute connecting headway and five minutes of fixed friction to a 35% transfer share of relevant pairs.

At 15 minutes, the 100 m short-path case yields **6.20 million** annual journeys and the 600 m long-path case **1.37 million**. These distances define the sensitivity examples. Actual access and transfer paths require site evidence. Omitting transfer friction yields **4.64 million**. Raising the trial fare from zero to $0.50 at $3/hour yields **3.00 million**. These are uncalibrated responses to the stated changes. Local survey work needs to separate airport passengers, workers and other trips, record hourly directions and connections, measure walking and crossing time, and locate entrances.

## Reproduction and supplied records

Run from the repository root.

```sh
python3 -m unittest cities.Baghdad.engineering.simulation.test_airport_alignment_demand
python3 - <<'PY'
import json
from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand

alignment = airport_alignment.evaluate()
print(json.dumps(airport_alignment.geojson(alignment)))
for headway in (15, 20, 30):
    for mode in ("fixed", "service_sensitive"):
        demand = airport_demand.evaluate(alignment, headway_min=headway, mode=mode)
        print(headway, mode, demand["annual_all_journeys"], demand["evaluation_id"])
PY
```

The alignment ID binds the opening ancestry, trace, ordered stop positions and any supplied rail-level profile. The alignment record ID additionally binds the source files and assessment. The demand evaluation ID binds the alignment record, ordered stop IDs, headway, dwell, assumptions and full hourly matrices. The matrix dimensions are 24 Baghdad local hours × 6 origins × 6 destinations in the published Airport stop order.

Pass an optional JSON path as `survey` to `airport_alignment.evaluate`. Use schema `osr-baghdad-airport-survey-centreline/1` and supply `parent_candidate_id`, `crs` equal to `EPSG:4326`, `document`, `revision`, `verification_reference`, `geometry` as a GeoJSON LineString and `stops` as six ordered objects containing `id`, `vertex` and `coordinates`. Stop coordinates must match centreline vertices, including both endpoints. Compute `geometry_sha256` as `airport_alignment.identity({"geometry": geometry, "stops": stops})`. For vertices outside the retained Baghdad map bounds, include a `coverage_decision` with the same `geometry_sha256`, a source `document`, `review_reference` and `reason`. The record shows signed east and north offsets and great-circle distances from the five known centroids so reviewers can assess station relocations. Um Al Tubol has no centroid offset. The input file digest and verification reference travel with the record. Independent verification stays open.

Include an optional `vertical_profile` with the same `geometry_sha256`, the survey's vertical `datum` name or code and `elevations_m` containing one rail-level elevation per centreline vertex in order. The record returns cumulative horizontal `chainages_m`, rail-level `elevations_m` and one signed percent grade per adjacent pair in the Airport-00 to Airport-05 direction. Positive grade climbs in that direction. The default and a horizontal-only submission have no grade profile. The document and revision must cover the submitted levels. Verification of those levels and the vertical curves remains open.

The coupled motion calculation uses the signed local gradient at the train's position, up to 2% in either direction. At a vertical break it uses the grade ahead in the direction of travel. Yard moves use level track. The solver holds gradient for each 1–4 second motion step and reports the absolute accumulated work error from steps that cross vertical breaks. A scalar grade study on the same alignment needs the explicit `grade_basis="constant_sensitivity"` setting. The independent SUMO adapter supports the scalar study only.

Pass an optional JSON path as `observed` to `airport_demand.evaluate`. Use schema `osr-baghdad-airport-observed-od/2` and supply the matching `alignment_id`, ordered `stop_ids`, `timezone` equal to `Asia/Baghdad`, source `document`, inclusive ISO sample dates `sample_date_from` and `sample_date_to`, `observed_days`, `resolution` and `od`. Declare the sampled `service_offer` using the structure returned in `service_offer.observation_context` by a demand calculation for the same booked offer. This binds headway, dwell, formation, operating hours, booked speeds, turn allowance, fare, walking case and active transfer assumptions. A changed booked offer needs observations collected under the matching conditions. The v1 format predates the service declaration and needs an updated submission grounded in the source records. Terminal phasing and actual running conditions still need review against the source survey.

The count rows use `from`, `to`, `all` and `paying`, with local integer `hour` (0–23) for hourly resolution. Counts require finite model arithmetic. Vehicle and station capacity screens assess crowding separately. Hours and pairs absent from the file contribute zero counted journeys to the supplied sample. Daily counts retain their observed pair totals and use the historical hourly pattern for peak estimates. In observed mode the record annualises the observed daily mean over 365 days and records the sample dates and source digest. Seasonal representativeness and evidence review remain open.

For the coupled audit, pass `--observed` with the matching `--headway`, `--cars` and `--dwell-s` if the sample uses a dwell other than 35 seconds. The audit replays that one headway and uses the booked dwell in the door-exchange and cooling calculation. If the booked dwell falls short of the assisted door-exchange screen, a longer offer requires matching observations. The implied exchange uses peak queue and load inputs. Door-open cooling uses the unassisted exchange estimate capped by booked dwell.

## Independent working-day replay

Both cases use the corrected paired six-site layout, six steel cars at 146.136 t tare and 198.636 t peak, 35-second stops and a 40 °C auxiliary load case. The Airport study uses its historical planning capacity of 700 normal places per six-car train, equivalent to 2,800 and 1,400 places per hour per direction at 15 and 30 minutes. The separate v0.6 development reference uses 276 normal places per six-car train. The 15-minute case retains the 330-second terminal offset to expose the effect of shared terminal resources. The refined 30-minute case uses a 1,308-second offset and adds 210 seconds before the first and after the last empty positioning moves. [Airport study inputs](../../system.toml) · [v0.6 development reference](../../../../engineering/development-baseline.toml)

| Working-day check | 15 min, adverse | 30 min, refined |
| --- | ---: | ---: |
| Nominal shared-resource conflicts | 2 | 0 |
| Completed passenger trips | 103 / 144 | 72 / 72 |
| Completed positioning trips | 2 / 4 | 2 / 2 |
| Completed yard moves | 4 / 10 | 6 / 6 |
| Maximum coupled arrival delay (s) | 10,522 | 58 |
| Minimum collector voltage (V) | 1,491.3 | 1,492.3 |
| SUMO directional trips including positioning | 148 / 148 | 74 / 74 |
| SUMO completed stops | 740 | 370 |
| Largest absolute matched SUMO time difference (s) | 1,866 | 100 |
| Illustrative AC minimum voltage, nominal / weak (pu) | 0.9910 / 0.9573 | 0.9916 / 0.9585 |

SUMO uses separate trip vehicles and tracks for each direction. The coupled model also allocates shared throat and yard resources. The median matched SUMO running time is 10 seconds shorter in both cases. The 30-minute model carries 7,229 of 7,254 offered daily journeys. Grid connection data, feeder protection and equipment thermal ratings remain open. [Verification receipt](audit-verification.json)

Production receives the digested working-day summary and uses the recorded energy, served journeys, fleet and alignment in its partial estimate. The verifier reconciles booked annual kilometres using 458,873 passenger train-km, 12,746 empty positioning train-km and 548 yard train-km for the refined case. Its operated replay annualises to 472,167 train-km. The partial 15-minute day scales to 685,551 operated train-km against 944,151 booked for cost sensitivity. The replay verifies rejection when the energy total or digest changes after handoff.

```sh
.venv/bin/python -m cities.Baghdad.engineering.simulation.airport_audit_verify
.venv/bin/python -m cities.Baghdad.engineering.simulation.airport_audit_verify --replay --receipt build/corrected-airport-verification.json
```
