# Catalogue water and junction placement review

The [current audit](summary.json) checks all **266 cities** against retained,
independently sampled water evidence and their actual exported route geometry.
All checks pass. These are controlled planning examples; construction and
operating approvals remain open.

| Check | Previous revision | Current layouts |
|---|---:|---:|
| Cities with findings | 256 | 0 |
| Platform records in detected water cells | 249 | 0 |
| Missing grouped platforms at checked dry line junctions | 1,868 | 0 |
| Unapproved contiguous water runs above 1 km | 197 | 0 |

The [baseline audit](baseline.json) uses revision
`1fa30889464105bacfc634b87594866840575561` and the same retained water inputs.
Crossing counts are checks of pairs of lines, rather than unique station
complexes or passenger transfers.

Bukavu previously had four platform records in detected water cells, five
missed junction checks and two long lake crossings. Its regenerated example
has 21 platform records and none of those findings. Goma previously missed
two checked junctions; its 19 current platforms cover both, with no wet
platforms.

The shared pipeline restores complete OSM multipolygon geometry, including
island holes; samples ESA WorldCover 2021 permanent water on each controlled
20 m grid; excludes every detected water cell and unknown coverage from
platform sites; and checks between sparse route vertices. Short crossings are
priced bridge candidates. Longer water stretches require a retained shore
detour or an explicitly bounded change in endpoint scope.

Full-resolution GeoJSON preserves the actual centreline without display
offsets. Platform markers use actual coordinates. Shared route sections have
junctions at their entries and exits; each intermediate bend is not another
interchange. Native checks and a separate Shapely audit require grouped
platforms within 60 m of dry junctions at the controlled grid precision.

The changed layouts also require fresh full-day nominal and degraded software
screens and current fleet, depot, workforce and finance quantities. Kut,
Lubango and Khamis Mushait use costed two-cabinet station charging requirements.
Their actual reruns retain the 90% floor for ordinary degraded cases and
achieve minimum completion of 91.54%, 93.69% and 92.92%, respectively.
Khamis Mushait completes 89.69% during the ten-hour all-site grid outage,
above that exceptional case's unchanged 60% curtailment floor.
The requirements and release boundaries
are recorded in each city's `design-overrides.toml`; charging supplier,
electrical and thermal acceptance remain open.

Kinshasa’s enlarged 1,440-trainset example uses an actual local invocation of
the same source-bound native runner, with four independent case workers and
a larger wall-time allowance. Its execution receipt identifies the local
environment. All nominal/degraded durations, service floors and native output
hash checks are retained. The other 265 current executions are verified
GitHub outputs. The selected-city recovery workflow also allows additional
wall time for large networks. These are software planning results.

Planning capital retains the existing constructability multiplier for elevated
curves below 300 m radius. Restoring full geometry can materially raise that
cost screen. Realignment, survey and supplier quotations must validate it
before an investment decision; earlier capital and return headlines require
recalculation.

Endpoint changes in Douala, Zanzibar, Mwanza, Dar es Salaam and Tanga retain
city-specific bounds and reasons in their water-route policies and alignment
reports. Douala excludes the offshore end of one radial through a roughly
12 km water stretch. Recalculations use the shortened shore route. Recorded
shoreline backtracking remains an open geometry review, with its measured
excursion and the original 750 m threshold retained.

Each city publishes its land-cover samples, supplementary OSM water geometry,
combined mask, exact grid, buildability constraints and source receipt. The
receipt records actual source tile URLs and hashes, sampled windows and
retained input hashes. Checks recompute the mask from these retained inputs;
an empty legacy water relation is not treated as proof of dry land.

The historical 10 m classification comes from
[ESA WorldCover 2021 v200](https://esa-worldcover.org/en/data-access), class 80,
with four quarter-cell samples per 20 m planning cell. Attribution:
© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data
(2021) processed by ESA WorldCover consortium. Data licence: CC BY 4.0.

These checks do not establish current surveyed shorelines, platform footprints,
bank stability, transfer access or levels, property rights, bridge spans,
continuous curve geometry or physical rail–structure acceptance. Those remain
project releases even where the software planning checks pass.

Regenerate or verify with:

```sh
python tools/automation/refresh-city-water-evidence.py --check --jobs 4
python tools/automation/audit-city-geography.py
python tools/automation/audit-city-geography.py --check
```
