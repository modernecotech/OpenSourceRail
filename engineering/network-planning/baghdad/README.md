# Baghdad integrated network, foundations and assembly plan

**Coordinated design-development concept; field construction and operating adoption remain open.**

![Network interfaces and residential gaps](network-and-residential-review.png)

[Interactive line / support / junction viewer](network-foundation-viewer.html) lets reviewers zoom, select a line and inspect individual support packets and interface records offline.

One source-bound asset graph connects each line, actual span, shared support, beam, launcher front, junction interface, station complex and residential intervention. The current native timetable/finance remains a comparator; this package does not claim new operating service or accepted structural profiles.

The plan assigns **11,148 support-specific foundation packets**, **10,128 catalogue bay assemblies**, **422 specials** and **34 workfronts** sharing **18 configured launchers**. 16 fronts have preceding asset assignments; a front record creates no additional machine. Support packets have coordinates, chainage, adjacent spans, desktop-soil investigation references and required loads/tests. Pile type/count/depth, groundwater and bearing capacity remain unselected until field design.

| Line | Foundation packets | Catalogue bay assemblies | Special packages | Candidate infill |
|---|---:|---:|---:|---:|
| [line-1](line-1-construction-plan.md) | 836 | 700 | 29 | 6 |
| [line-2](line-2-construction-plan.md) | 1048 | 868 | 81 | 3 |
| [line-3](line-3-construction-plan.md) | 824 | 770 | 21 | 4 |
| [line-4](line-4-construction-plan.md) | 960 | 857 | 45 | 5 |
| [line-5](line-5-construction-plan.md) | 810 | 737 | 30 | 1 |
| [line-6](line-6-construction-plan.md) | 848 | 748 | 48 | 1 |
| [line-7](line-7-construction-plan.md) | 820 | 767 | 22 | 0 |
| [line-8](line-8-construction-plan.md) | 848 | 746 | 44 | 1 |
| [line-9](line-9-construction-plan.md) | 2241 | 2090 | 68 | 10 |
| [line-10](line-10-construction-plan.md) | 199 | 191 | 4 | 0 |
| [line-11](line-11-construction-plan.md) | 266 | 258 | 4 | 0 |
| [line-12](line-12-construction-plan.md) | 252 | 240 | 6 | 0 |
| [line-13](line-13-construction-plan.md) | 227 | 215 | 6 | 0 |
| [line-14](line-14-construction-plan.md) | 270 | 262 | 4 | 0 |
| [line-15](line-15-construction-plan.md) | 204 | 196 | 4 | 0 |
| [line-16](line-16-construction-plan.md) | 215 | 211 | 2 | 2 |
| [line-17](line-17-construction-plan.md) | 280 | 272 | 4 | 1 |

## Junction and overlap coordination

62 crossing/shared-corridor/self-crossing interfaces need explicit structural treatment. 0 original interchange groups exceed the 600 m full-diameter screen. The new bounded grouping prevents transitive long-distance complexes and preserves platform coordinates. It does not create a track switch, measured walking path or accepted vertical profile.

[Integrated geometry and complex register](network-integration.json) · [GIS junction/residential layer](junctions-and-residential-plan.geojson) · [Foundation coordinate conflicts](foundation-location-conflicts.json).

## Residential coverage and expansion

Retained 2020 population within 1 km station circles is **49.0%**. 34 population-ranked infill candidates give a conditional radial sensitivity of **56.6%**. **2,019,201** currently unserved retained residents are also over 1 km from sampled existing corridors; infill cannot close those gaps. 16 named/located priority areas therefore require branch/extension or funded feeder/access studies. Area circles can overlap and are never summed as unique residents.

These are native population-count and distance screens, not current census, surveyed walksheds, ridership or funded service. Candidate sites need water/footprint/property/access, station structure, timetable, fleet, energy and full installed cost review.

[Expansion corridor plans](expansion-corridors.json) provide 14 source-bound routes along the retained arterial graph, tied to existing station connections, with access gaps and proposed stopping sites. Compare rail branches with frequent feeders; traffic direction, bridge grades/loads, railway curvature and walk routes are unverified. The combined infill/feeder 500 m stop-circle sensitivity is 60.9%; the rail 1 km sensitivity is 66.0%. [Shared corridor edges](shared-expansion-corridor-edges.json) count overlapping candidate road segments once. No corridor is adopted or funded.

## Foundation and assembly execution

[Foundation register](foundation-register.csv.gz) has one row per unique proposed support. [Span assembly register](span-assembly-register.csv.gz) has identified component pairs and both foundation parents, actual line/run, unique front assignment, sequence and predecessor. [Launcher fronts](launcher-fronts.json) preserve disconnected runs and relocation gates. [Stage library](assembly-stage-library.json) defines foundation/column/cap/bearing, factory/delivery, first/second beam securing, advance and handover dependencies. Specials and junctions use their own design/erection chains.

Decode compressed CSV using `python -c "import gzip; print(gzip.open('foundation-register.csv.gz','rt').read())"`. Coordinates are interpolated from the retained planning route; desktop soil does not select a foundation, and no pile depth or allowable bearing value is invented.

[Complete per-line summary](line-assembly-summary.json) · [Wider catalogue audit](catalogue-audit.csv) · [Catalogue findings and provenance](catalogue-audit-summary.json).

[Companion data archive](Baghdad-Network-and-Foundation-Planning.zip) contains this planning package and new controlled inputs. The original Baghdad proposal archive retains the baseline city/engineering input evidence. Use both for the full planning review; the companion does not imply physical release.

Run `python tools/automation/integrated-network-plan.py`; `--check` validates source/output hashes. `--retain-context` creates the immutable retained OSM road/name input from the cached extraction. Native route and financial assumptions change only through a subsequent fully regenerated, validated adoption revision.
