# Mosul field-evidence brief

Deterministic pre-mobilisation requirements generated from the shared field-evidence template.
It issues the information request; it does not claim that field data or approvals exist.

- Brief status: **brief-issued-awaiting-signatures**
- Mobilisation authorized: **no**
- Field evidence accepted: **no**
- Horizontal CRS: EPSG:32638 candidate UTM zone 38N; survey authority to confirm or replace
- Vertical datum: `authority-to-confirm-before-mobilisation`
- Canonical requirements: `lib/templates/field-evidence.toml`

> The appointed survey authority, architect/engineer of record, operator and information manager approve this brief, responsibility matrix, CRS, vertical datum, accuracy schedule, access plan and data rights before field capture.

## Required packages

| ID | Dataset | Owner role | Delivery |
|---|---|---|---|
| `SUR-CTRL` | Primary and secondary survey control | appointed survey authority | RINEX plus field logs, adjustment report, coordinate schedule and signed control report |
| `SUR-TOPO` | Corridor and site topographic survey | survey delivery lead | GeoPackage 3D points/lines/polygons plus LandXML terrain and accepted PDF plans |
| `SUR-UTIL` | Above- and below-ground utilities | utility survey lead | GeoPackage 3D utility features, investigation records, photographs and confidence/quality attributes |
| `SUR-LAND` | Property, right-of-way and access constraints | client land and legal lead | GeoPackage boundaries/rights plus controlled title, consent and access register |
| `SUR-FLOOD` | Hydrology, flood and drainage evidence | drainage and flood lead | GeoPackage water/flood/outfall layers plus rainfall, level, model and authority records |
| `GEO-GI` | Ground investigation and laboratory testing | geotechnical engineer of record | AGS or equivalent structured logs, coordinates, samples/tests, factual report and interpretive design report |
| `OPS-WORKSHOP` | Existing workshop and depot capability audit | operator engineering lead | asset/capability register, measured layouts, utilities, photographs and gap assessment |
| `OPS-FLEET` | Existing fleet and operating interface audit | operator rolling-stock lead | fleet register, measured interface sheets, duty/condition records and migration constraints |
| `SUR-IMAGE` | Georeferenced photography and photogrammetry | reality-capture lead | source-image manifest and hashes, camera logs, GCP/check points, orthophoto/DSM and processing report |
| `SUR-SCAN` | Point-cloud and dimensional interface capture | reality-capture lead | E57/LAS/LAZ plus station setup, targets/control, registration and CloudCompare QA report |
| `INF-GOV` | Information ownership, security and acceptance | client information manager | responsibility matrix, naming/revision rules, common-data-environment plan, licence/consent register and acceptance record |

## Scope and acceptance

### `SUR-CTRL` — Primary and secondary survey control

Stable primary/secondary monuments covering every corridor, station, depot, bridge, energy site and construction compound.

**Provisional accuracy/quality requirement:** Primary control <=10 mm horizontal and <=15 mm vertical expanded uncertainty; interface control <=5 mm relative to accepted project control. Survey authority must approve or replace these project targets.

Acceptance evidence:

- approved projected CRS, epoch, units, geoid model and vertical datum
- instrument/antenna serials and calibration status
- redundant occupations and independent checks
- least-squares residuals, covariance/uncertainty and rejected-observation record
- signed monument descriptions and protection/inspection plan

### `SUR-TOPO` — Corridor and site topographic survey

Full corridor, station, depot, access, watercourse, road, structure, compound and lifting-route coverage with breaklines and feature coding.

**Provisional accuracy/quality requirement:** Hard-surface/detail points <=25 mm horizontal and <=20 mm vertical; general ground <=50 mm. Survey authority must approve class-by-feature targets and check density.

Acceptance evidence:

- feature code and layer dictionary
- check-point residual report
- coverage/void map and inaccessible-area register
- capture date/epoch and change notes
- signed completeness review against route limits

### `SUR-UTIL` — Above- and below-ground utilities

Electricity, telecoms, water, sewer, drainage, fuel, irrigation and unknown services within the works influence zone.

**Provisional accuracy/quality requirement:** Every feature carries horizontal/vertical uncertainty and detection/verification method; trial holes or records alone must not be silently treated as surveyed truth.

Acceptance evidence:

- records search and authority contacts
- detection method, equipment and calibration
- surface-feature correlation
- verification exposure/trial-hole schedule where design risk warrants
- unresolved and abandoned-service issue register

### `SUR-LAND` — Property, right-of-way and access constraints

Ownership, occupation, easements, road reserve, temporary access, compounds, lifting routes and acquisition constraints.

**Provisional accuracy/quality requirement:** Boundary geometry remains indicative until reconciled to authoritative records and verified by the competent land authority.

Acceptance evidence:

- authoritative source and retrieval date
- boundary/status confidence
- owner/occupier and consent state
- temporary/permanent requirement
- dispute and encroachment register

### `SUR-FLOOD` — Hydrology, flood and drainage evidence

Catchments, channels, historical levels, culverts, outfalls, tailwater, groundwater indicators and exceedance routes affecting the works.

**Provisional accuracy/quality requirement:** Levels use the accepted vertical datum; rainfall return periods and climate allowances require local authority confirmation.

Acceptance evidence:

- source dates and return periods
- surveyed channel/outfall/culvert levels
- historical event and community evidence
- blockage/tailwater assumptions
- authority-approved design storm and discharge constraints

### `GEO-GI` — Ground investigation and laboratory testing

Boreholes, CPTu, test pits, groundwater monitoring and laboratory programme zoned for at-grade, elevated, station, depot and energy works.

**Provisional accuracy/quality requirement:** Investigation spacing/depth and tests are risk-based and approved by the geotechnical engineer after desk study and walkover.

Acceptance evidence:

- desk study, walkover and conceptual ground model
- location/elevation tied to accepted control
- factual logs and chain of custody
- strength, settlement, corrosivity and groundwater parameters with uncertainty
- signed geotechnical design recommendations and residual risks

### `OPS-WORKSHOP` — Existing workshop and depot capability audit

Buildings, pits, cranes, lifting, machine tools, power, compressed air, fire systems, stores, access and workforce capability.

**Provisional accuracy/quality requirement:** Critical lifting, clearance and interface dimensions are measured to the tolerance required by the selected equipment supplier.

Acceptance evidence:

- asset identity, condition and certification
- measured capacity/clearance and utility availability
- repair/reuse/replace decision
- production and maintenance throughput
- operator-approved upgrade work packages

### `OPS-FLEET` — Existing fleet and operating interface audit

Existing vehicles, gauges, couplers, wheel/rail, depot interfaces, rescue, operating rules and reusable components relevant to the pilot.

**Provisional accuracy/quality requirement:** Safety and physical interfaces use independently checked measurements and controlled vehicle/configuration identity.

Acceptance evidence:

- vehicle/configuration and maintenance history
- measured gauge/coupler/wheel/depot interfaces
- operating duty and failure records
- rescue/recovery constraints
- signed compatibility and migration decisions

### `SUR-IMAGE` — Georeferenced photography and photogrammetry

Continuous corridor and detailed station/depot/structure/utility-context coverage, subject to permissions and privacy controls.

**Provisional accuracy/quality requirement:** Ground sampling distance and independent check-point limits are agreed by use case; neither EXIF position nor self-reported processing precision is acceptance evidence.

Acceptance evidence:

- capture plan, permissions and privacy controls
- camera/lens identity and calibration
- GCP versus independent check-point separation
- processing software/version/settings
- check-point residuals, voids, artefacts and obscuration map

### `SUR-SCAN` — Point-cloud and dimensional interface capture

Complex structures, station/depot interfaces, constrained utilities and clearance-critical areas selected by the design team.

**Provisional accuracy/quality requirement:** Registration RMS is reported but not used alone; independent control/check residuals and local interface comparisons govern acceptance.

Acceptance evidence:

- scanner identity/calibration and setup log
- target/control schedule
- registration method and residuals
- independent check points and cloud-to-cloud sections
- density, range, noise, void and movement/change register

### `INF-GOV` — Information ownership, security and acceptance

All raw and derived field information, personal/sensitive content, third-party records and authoritative project derivatives.

**Provisional accuracy/quality requirement:** Not applicable; this package governs provenance, access, revision, retention and authorized use.

Acceptance evidence:

- owner, producer, checker and accepting authority per dataset
- licence, reuse, publication and personal-data constraints
- file naming, metadata, revision and immutable hash rules
- backup, retention and access-control plan
- signed receipt/rejection/reissue workflow

## Data handling and handoff

Keep raw survey, imagery, scan, utility and personal data in access-controlled project storage; Git contains requirements, manifests, hashes, accepted summaries and non-sensitive derivatives only.

Complete [`survey-input-manifest.csv`](survey-input-manifest.csv) for every delivery.
Each accepted row must name the producer/checker, CRS and vertical datum, capture
date, controlled project-storage path, SHA-256 digest and acceptance state. RTKLIB
processing configurations/status/residual outputs, QGIS/CloudCompare/ODM settings
and signed review records accompany their respective source data.
