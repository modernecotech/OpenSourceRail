# Baghdad integrated network, foundations and assembly plan

**Coordinated design-development concept; field construction and operating adoption remain open.**

![Network interfaces and residential gaps](network-and-residential-review.png)

[Interactive line / support / junction viewer](network-foundation-viewer.html) lets reviewers zoom, select a line and inspect individual support packets and interface records offline.

One source-bound asset graph connects each line, actual span, shared support, beam, launcher front, junction interface, station complex and residential intervention. The current native timetable/finance remains a comparator; this package does not claim new operating service or accepted structural profiles.

The plan assigns **10,985 support-specific foundation packets**, **9,973 catalogue bay assemblies**, **404 specials** and **28 workfronts** sharing **18 configured launchers**. 10 fronts have preceding asset assignments; a front record creates no additional machine. Support packets have coordinates, chainage, adjacent spans, desktop-soil investigation references and required loads/tests. Pile type/count/depth, groundwater and bearing capacity remain unselected until field design.

| Line | Foundation packets | Catalogue bay assemblies | Special packages | Candidate infill |
|---|---:|---:|---:|---:|
| [line-1](line-1-construction-plan.md) | 918 | 770 | 32 | 3 |
| [line-2](line-2-construction-plan.md) | 1165 | 988 | 76 | 3 |
| [line-3](line-3-construction-plan.md) | 932 | 863 | 29 | 4 |
| [line-4](line-4-construction-plan.md) | 1040 | 943 | 44 | 5 |
| [line-5](line-5-construction-plan.md) | 952 | 874 | 35 | 7 |
| [line-6](line-6-construction-plan.md) | 974 | 846 | 60 | 2 |
| [line-7](line-7-construction-plan.md) | 867 | 813 | 21 | 2 |
| [line-8](line-8-construction-plan.md) | 915 | 811 | 39 | 3 |
| [line-9](line-9-construction-plan.md) | 2423 | 2280 | 61 | 8 |
| [line-10](line-10-construction-plan.md) | 242 | 238 | 2 | 0 |
| [line-11](line-11-construction-plan.md) | 155 | 153 | 1 | 0 |
| [line-12](line-12-construction-plan.md) | 48 | 46 | 1 | 0 |
| [line-13](line-13-construction-plan.md) | 127 | 123 | 2 | 2 |
| [line-14](line-14-construction-plan.md) | 227 | 225 | 1 | 1 |

## Junction and overlap coordination

46 crossing/shared-corridor/self-crossing interfaces need explicit structural treatment. 0 original interchange groups exceed the 600 m full-diameter screen. The new bounded grouping prevents transitive long-distance complexes and preserves platform coordinates. It does not create a track switch, measured walking path or accepted vertical profile.

[Integrated geometry and complex register](network-integration.json) · [GIS junction/residential layer](junctions-and-residential-plan.geojson) · [Foundation coordinate conflicts](foundation-location-conflicts.json).

## Residential coverage and expansion

Retained 2020 population within 1 km station circles is **27.7%**. 40 population-ranked infill candidates give a conditional radial sensitivity of **45.7%**. **2,173,888** currently unserved retained residents are also over 1 km from sampled existing corridors; infill cannot close those gaps. 16 named/located priority areas therefore require branch/extension or funded feeder/access studies. Area circles can overlap and are never summed as unique residents.

These are native population-count and distance screens, not current census, surveyed walksheds, ridership or funded service. Candidate sites need water/footprint/property/access, station structure, timetable, fleet, energy and full installed cost review.

[Expansion corridor plans](expansion-corridors.json) provide 15 source-bound routes along the retained arterial graph, tied to existing station connections, with access gaps and proposed stopping sites. Compare rail branches with frequent feeders; traffic direction, bridge grades/loads, railway curvature and walk routes are unverified. The combined infill/feeder 500 m stop-circle sensitivity is 51.4%; the rail 1 km sensitivity is 58.8%. [Shared corridor edges](shared-expansion-corridor-edges.json) count overlapping candidate road segments once. No corridor is adopted or funded.

## Foundation and assembly execution

[Foundation register](foundation-register.csv.gz) has one row per unique proposed support. [Span assembly register](span-assembly-register.csv.gz) has identified component pairs and both foundation parents, actual line/run, unique front assignment, sequence and predecessor. [Launcher fronts](launcher-fronts.json) preserve disconnected runs and relocation gates. [Stage library](assembly-stage-library.json) defines foundation/column/cap/bearing, factory/delivery, first/second beam securing, advance and handover dependencies. Specials and junctions use their own design/erection chains.

Decode compressed CSV using `python -c "import gzip; print(gzip.open('foundation-register.csv.gz','rt').read())"`. Coordinates are interpolated from the retained planning route; desktop soil does not select a foundation, and no pile depth or allowable bearing value is invented.

[Complete per-line summary](line-assembly-summary.json) · [Wider catalogue audit](catalogue-audit.csv) · [Catalogue findings and provenance](catalogue-audit-summary.json).

[Companion data archive](Baghdad-Network-and-Foundation-Planning.zip) contains this planning package and new controlled inputs. The original Baghdad proposal archive retains the baseline city/engineering input evidence. Use both for the full planning review; the companion does not imply physical release.

Run `python tools/automation/integrated-network-plan.py`; `--check` validates source/output hashes. `--retain-context` creates the immutable retained OSM road/name input from the cached extraction. Native route and financial assumptions change only through a subsequent fully regenerated, validated adoption revision.
