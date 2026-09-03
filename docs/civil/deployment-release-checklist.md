# Civil And Station Deployment Release Checklist

Generated alignments and station packages are planning-grade until
site evidence replaces catalogue assumptions. This checklist defines
what a deployment partner must add before civil/station design freeze.

| Gate | Required evidence | Closure criterion |
|---|---|---|
| Survey-grade alignment | Topographic survey, utility survey, property boundary check, flood levels, and control points | Generated route geometry is replaced or confirmed by survey-grade alignment |
| Ground model | Geotechnical boreholes, groundwater, bearing capacity, corrosivity, and settlement risk | Foundations and at-grade sections are sized by local engineer |
| Structures check | Project issue of the [`viaduct-design-basis.md`](viaduct-design-basis.md), 12-axle load model, kinematic/egress study, per-span 3-D analysis, seismic/wind/fatigue checks, prestress/reinforcement, foundations, drainage, and independent check | Licensed structural/geotechnical engineers sign the selected catalogue variants or issue OSR-US/OSR-SP designs |
| Bearings and movement | Eight-bearing interior/four-bearing end schedule, fixed/guided/free axes, deck gaps, jacking, thermal/creep/shrinkage, and CWR bridge interaction | Responsible engineer and track engineer jointly release the movement schedule |
| Transport and erection | Permit-load route, transporter, lifting points, temporary bracing, crane/launcher reactions, wind limits, contingency landing, and first-article trial | Temporary-works designer, lifting appointed person, and structural engineer close hold point |
| Station fit | Platform length, access route, drainage, lighting, PSD/edge protection, emergency egress, accessibility audit | Station archetype matches local code and passenger flow |
| Energy site | Solar yield, grid interconnect, charger thermal study, battery/fire separation, utility approval | Station charging assumptions are replaced by site-specific design |
| Permits and stakeholders | Road closures, land access, environmental clearance, emergency-services access, operator acceptance | Permit register has owner, due date, and approval status |

For Samawah, this checklist closes the roadmap item for survey-grade
alignment replacement and deployment-specific assumptions.

Issue the project information request from the canonical
[`field-evidence.toml`](../../lib/templates/field-evidence.toml) template. The
[Samawah field-evidence brief](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/field-evidence-brief.md)
shows the required packages and provisional accuracy schedule. Its receipt
manifest is intentionally empty: only the appointed authorities can approve
the CRS, vertical datum, delivery and mobilisation. The linked
[control-processing report](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/control-processing-readiness.md)
then verifies receipt metadata and hashes, runs the frozen RTKLIB profile when
real inputs exist, and keeps technical screening separate from survey-authority
acceptance. The subsequent [ground-model gate](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/ground-model-readiness.md)
checks the master GeoPackage, DTM, orthophoto, registered point cloud,
independent residuals, processing reports and signed release without storing
raw imagery or scans in Git.
The following [surveyed-alignment gate](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/surveyed-alignment-readiness.md)
then requires one checked OSR-ALN, LandXML export and deterministic round-trip
report per line, plus exact platform reconciliation, yard/turnout/clearance
dispositions and a signed alignment-designer/survey/track/information-management
acceptance record. Planning GIS traces cannot satisfy it.
The subsequent [route/station-fit gate](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/route-station-fit-readiness.md)
requires hash-locked utility, property/access, flood/drainage, station access,
intercity/yard, road/traffic, compound/lifting and possession/staging evidence.
It reconciles every current line and station and rejects unresolved high or
critical issues before coordinated authority acceptance.
The [drainage/ground gate](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/drainage-ground-readiness.md)
then replays the project SWMM input, checks accepted rainfall/level provenance,
requires borehole-zoned foundation or ground-treatment schedules for every line
and station, and invokes OpenGeoSys evidence only when a reviewed groundwater/
coupling decision warrants it.
The [structural-release gate](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/survey/structural-release-readiness.md)
then binds every chainaged span, pier, abutment, foundation and special
structure to converged OpenSees/CalculiX evidence, load cases, fatigue/seismic/
wind/bearing results, closed independent-check comments and signed release.
