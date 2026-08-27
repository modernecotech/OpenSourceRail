# Rapid Implementation And Recycled Materials Review

This note reviews current public rail-infrastructure practice for faster
delivery of urban rail track and stations, with attention to recycled or
lower-carbon materials. It is intended to guide OSR civil and station
standards, not to replace local structural approval, geotechnical design,
or railway product acceptance.

> **Implementation status:** The core trackform and elevated-guideway
> recommendations in this review are incorporated into the parametric civil
> catalogue; station-material and circular-procurement extensions remain
> identified below. Its original 3/12/18 M USD per route-km assumptions are
> retained as calibration benchmarks; active CAD-indexed planning targets are
> generated in
> [`civil-cost-model.toml`](../../lib/templates/civil-cost-model.toml).

## Executive Takeaways

1. **Use ballastless urban track as the default, but keep it boring.**
   The strongest near-term pattern is continuous slipformed or precast
   ballastless slab track with adjustable direct-fixation rail fasteners.
   This fits urban corridors better than ballast, avoids tamping cycles and
   loose aggregate, and is cleaner around crossings and platforms. The speed
   gain comes from repeatable geometry, mechanised placement and fast rail
   adjustment, not from inventing a new trackform.

2. **Split the track kit into two approved production methods.**
   Use continuous slipform on long open, machine-accessible sections. Use
   transportable ST6 single-track panels in constrained, replaceable, utility,
   transition and short-possession zones. Local closure pours remain available
   where survey tolerance or interfaces make either repeated method unsuitable.

3. **Make elevated guideway a factory product, not a bridge project.**
   Low-cost elevated rail depends on a short span catalogue, single-column
   pier lines, transportable decked Pi20/Pi25 or special segmental spans, standard bearings,
   and repeatable erection. It should be used where it avoids demolition,
   severe junction conflicts, or tunnelling, but the model should not assume
   elevated is cheap where foundations, utilities, stations, or special spans
   dominate.

4. **Treat recycled plastic sleepers as a specialist tool, not the main
   running-track answer.**
   Recycled composite sleepers are now real railway products, with
   Network Rail approval and metro applications. They are most attractive
   for bridges, tunnels, turnouts, temporary works, depots, and brownfield
   repairs where timber would otherwise be used. For new OSR urban lines,
   the main at-grade track should remain ballastless slab/direct fixation.

5. **Stations can benefit immediately from modular construction.**
   Precast platform units, modular GRP/composite deck systems, recycled
   rubber platform blocks, and standardized station "kit of parts" design
   all have real market examples. OSR should keep the current station
   strategy: small number of repeatable platform/canopy/service modules,
   factory QA, minimal bespoke architecture.

6. **Recycled materials should be specified by performance class.**
   Good candidates now: recycled steel, recovered/recycled aggregate in
   non-critical concrete, low-carbon cement replacements, recycled rubber
   vibration mats, recycled rubber platform blocks, recycled plastic
   sleepers in non-slab applications, and recycled plastic access modules.
   Avoid mandating a material recipe where local standards or supply are
   immature.

7. **The procurement system matters as much as the material.**
   Circular material depots, material passports, batch traceability,
   pre-approved supplier lists, and standard test packs are what make
   recycled materials fast rather than risky.

## Track Technologies

| Technology | Readiness | Speed effect | Recycled / low-carbon potential | OSR recommendation |
|---|---|---|---|---|
| Precast ballastless slab panels | High | High where geometry is repetitive and survey control is strong | Use low-carbon concrete, recycled aggregate where approved, EAF/recycled steel reinforcement | Adopt as standard option for tangent and broad-curve urban sections |
| Cast-in-place direct-fixation slab/plinths | High | Medium; slower concrete work but flexible around utilities and tight geometry | Low-carbon concrete mixes, recycled aggregate in base layers | Adopt as fallback and station/turnout/default constrained-section option |
| Adjustable direct-fixation fasteners | High | High for tolerance recovery and maintenance | Rubber pads may include recycled content if certified | Adopt; require vertical/lateral adjustment and replaceable pads |
| Slab mats / embedded resilient blocks | High | Medium; adds material but reduces later vibration mitigation work | Recycled rubber can be used where tested | Adopt in vibration-sensitive streets, hospitals, schools, and bridges |
| Recycled composite sleepers | Medium-high | High for spot replacements and timber-substitute locations | High recycled plastic content | Use for bridges, depots, temporary panels, and turnouts where approved; not core OSR slab track |
| Recycled rubber underlay | Medium | Medium; can reduce maintenance on ballasted track, less central to slab track | High recycled tyre content | Watchlist for depots and transition zones |
| Geopolymer / rubberized concrete sleepers | Research / pilot | Low near-term for OSR because OSR is slab-first | High cement reduction and tyre-rubber reuse potential | Watchlist; pilot only after local code acceptance |

### Ballastless Slab Track

The market already offers several forms of ballastless track that align
with OSR's urban environment: prefabricated slabs, cast-in-place slabs,
and direct-fixation plinth systems. WEGH's Arianna system is a
prefabricated prestressed slab system for ballastless lines, and its EPD
describes the slabs being laid on a bedding slab to even out foundation
irregularities. SYSTRA and STRADAL describe a low-carbon ballastless slab
track that can use existing ballastless-track installation equipment,
including gantry cranes, to protect schedule.

OSR should not copy a proprietary system outright. It should define an
interface envelope:

- Standard slab panel widths, lift points, recesses, duct routes, and
  drainage interfaces.
- Rail seat spacing and baseplate anchor pattern.
- Tolerance stack: subbase, panel, grout/bedding, baseplate adjustment,
  rail weld geometry.
- Precast QA: compressive strength, dimensional survey, anchor pull-out,
  embedded conduit continuity, and batch traceability.

### Direct-Fixation Fasteners

Fast, accurate installation depends on adjustability. Pandrol's Fastclip
Baseplate is explicitly for ballastless applications on precast concrete,
direct-pour concrete, or steel structures, with quick vertical and
lateral adjustment. Pandrol's DRS baseplate is positioned for metro,
light rail, bridge, viaduct, tunnel, and slab-track use where vibration
reduction matters.

OSR should require:

- At least +/-10 mm lateral adjustment at rail-seat level where possible.
- Vertical shim range sufficient to recover slab tolerances without
  breaking out concrete.
- Replaceable pads and clips.
- Electrical insulation suitable for track circuits only if the local
  signalling design needs it; OSR's onboard-first design reduces this
  dependency but does not remove bonding/earthing requirements.

### Recycled Composite Sleepers

Network Rail's approval of recycled plastic composite sleepers, and
Sicut's product acceptance, show that recycled-plastic sleepers are no
longer purely experimental. Network Rail's public material also frames
the move as part of circular economy and hardwood replacement. Victoria's
Duratrack trials show the approval route can be narrower: low-speed
siding and yard applications first, then broader use as standards mature.

For OSR:

- Use composite sleepers for depot yards, temporary construction track,
  bridges where timber would otherwise be used, and brownfield pilots.
- Do not use recycled-plastic sleepers as the primary support for new
  urban running track, because OSR has moved to ballastless slab.
- Require product acceptance evidence for screw pull-out, thermal
  movement, creep, fire/smoke, UV, dynamic stiffness, and fastening
  compatibility.

## Elevated Guideway Technologies

| Technology | Readiness | Speed effect | Recycled / low-carbon potential | OSR recommendation |
|---|---|---|---|---|
| Rail-designed decked Pi20/Pi25 beams | Prototype design required; established bridge family | High on 20–25 m repetitive spans | Low-carbon concrete after early-strength, creep and bond trials; reusable long-line mould | Adopt as the OSR reference after structural prototype and first article; one ≤3 m, ≤75 t beam per track |
| Full-span precast U-girders | High | High on 20–30 m repetitive spans with wide/heavy transport access | Low-carbon concrete, EAF/recycled rebar, reusable moulds | Retain as an acoustic or project-specific special product |
| Precast segmental U/box guideway with launching gantry | High | Very high on long viaduct packages and constrained streets | Low-carbon concrete and recycled rebar; lower traffic disruption | Adopt for long continuous elevated packages or where crane access is poor; avoid for short isolated stubs |
| Single-column median piers / classified foundations | High | High; reduces excavation width and utility diversion | Low-carbon concrete and recycled rebar in substructure | Select spread, bored, driven or pile-group interface by geotechnical/access zone |
| Precast pier caps or pier-cap shells | Medium-high | High; removes complex formwork above traffic | Low-carbon concrete, reusable forms | Adopt as a standard option for viaduct and elevated-station piers |
| Steel modular special spans | High | High for road/rail crossings and emergency works | Recycled steel content can be high | Use only for special crossings; concrete remains the default for repetitive spans |
| UHPC / fibre-reinforced concrete viaduct elements | Medium | Medium; may extend spans or reduce section depth | Lower material volume but higher material and QA burden | Watchlist; use only where local supply and structural review support it |

### Preferred Elevated Kit

The lowest-cost elevated portions should use the same discipline as the
rest of OSR: one repeatable kit, many repetitions. SYSTRA's U-shaped metro
viaduct work is a useful benchmark: Dubai Metro used 58.7 km of elevated
guideway mainly formed from U-shape precast segmental superstructure, and
SYSTRA frames the U-shaped viaduct as rapid, economical, and material-
efficient. FHWA's accelerated bridge construction guidance points in the
same direction for bridge-like work: prefabricate structural elements
offsite or near-site, transport them in, and install rapidly to reduce
onsite time and disruption.

For OSR, the elevated kit should be:

- Pi20/Pi25 standard spans, with a controlled special-span
  variant for road, railway, river, and utility crossings.
- One 2.9 m decked Pi-beam per track, stems below the rails, with separate
  outer walkway/barrier cassettes and a small inner service closure.
- Single-column piers in a road median or other clear line, with no
  bespoke pier architecture.
- Standard elastomeric bearings, expansion joints, drainage scuppers,
  inspection walkway brackets, earthing/bonding points, and cable trays.
- Ballastless direct-fixation track on the deck, with adjustable
  baseplates to absorb casting and erection tolerances.
- No overhead catenary envelope where battery operation is retained; this
  reduces visual clutter and vertical clearance pressure, but does not
  remove evacuation, walkway, drainage, bonding, or maintenance access.

### Production Strategy

Elevated guideway becomes rapid only when foundations, precast production,
and erection are overlapped as separate work fronts:

1. **Early utility and geotechnical release:** fix the pier line before
   girder production. Foundation surprises erase the factory advantage.
2. **Near-site precast yard:** cast Pi-beams, pier caps, ST6 panels, platform edge
   units, parapets, cable troughs, and walkway modules close enough that
   trucking does not become the bottleneck. Surrey Langley SkyTrain is a
   current example of guideway segments being made in a dedicated precast
   facility and trucked to the route.
3. **Standard formwork battery:** one mould family with reusable steel
   forms, surveyed casting beds, embedded inserts, and barcode/batch
   traceability.
4. **Parallel erection:** foundations stay several spans ahead, pier
   construction follows, and the launcher or crane crew erects spans while
   track and systems follow behind.
5. **Use the right erection method:** mobile crawler cranes are simplest
   for short elevated packages with street access. Launching gantries make
   sense when the elevated package is long enough to amortize setup or when
   traffic/utility constraints prevent repeated crane closures. Freyssinet
   reports span-by-span launching gantry methods as a fast method for
   multi-span viaducts, while precast girder erection is simpler and can
   place a span per shift.

### Cost Rules

The retained $12.0M/route-km elevated benchmark, and the current
$9.748M/route-km design-derived target, describe a repetitive package rather
than a promise for every elevated metre. The target is
most plausible when the alignment has:

- Long runs of repeated 20-30 m spans.
- Median or public-land pier locations.
- Shallow-to-moderate foundations with no major utility diversion.
- At-grade or simple elevated stations, not stacked architectural
  structures.
- Few special spans, few skewed crossings, and no custom aesthetic deck.
- A local precast yard with enough repetition to amortize moulds,
  stressing beds, transport fixtures, and launching equipment.

The model should add risk or avoid elevated where:

- Soft ground, seismic demand, flood scour, or deep utilities dominate.
- The line needs many elevated stations close together.
- Special spans exceed the standard catalogue repeatedly.
- Curves are tight enough to force many unique segment geometries.
- The project asks for signature architecture, enclosed viaducts, or
  double-deck structures.

### Elevated Stations

Elevated stations can destroy the cost advantage if each one becomes a
custom building. The station should be designed as a widened guideway bay,
not as a separate bridge:

- Keep side platforms on a regular 30 m column grid where possible.
- Use repeated pier caps/portal frames rather than deep transfer
  structures.
- Put stairs, lifts, and services in bolt-on modules outside the guideway
  load path.
- Keep paid concourse and plant rooms compact; avoid full-width enclosed
  concourses unless climate, security, or fare control requires them.
- Use the same canopy bay, platform edge, screen-door interface, cable
  trench, and drainage details as at-grade stations.

### Recycled And Low-Carbon Content In Elevated Works

Use recycled and lower-carbon content where it does not compromise the
prestressed primary span:

- Use EAF/recycled-content steel for rebar, brackets, walkways, cable
  trays, and canopies where certified.
- Use GGBS, fly ash, limestone calcined clay, or other approved low-carbon
  cement blends in piers, pile caps, pier caps, and station modules.
- Keep prestressed Pi-beams and special U-girders conservative until the precast supplier can
  prove early strength, durability, shrinkage, creep, and tendon bond.
- Use recycled aggregate in non-prestressed substructure or backfill only
  where local standards allow.
- Use GRP/composite walkway grating, cable covers, and access panels where
  fire/smoke and UV ageing evidence exists.
- Crush rejected precast elements and demolition concrete into subbase or
  non-critical aggregate rather than sending them to landfill.

## Station Technologies

| Technology | Readiness | Speed effect | Recycled / low-carbon potential | OSR recommendation |
|---|---|---|---|---|
| Precast platform L-walls / slabs / TT units | High | High | Low-carbon concrete and recycled aggregate can be specified | Keep as primary station platform structure |
| Modular GRP/FRP deck systems | Medium-high | High; supplier claims major installation time savings | Recyclability varies; low weight reduces transport and plant | Use for light platforms, extensions, temporary stops, and low-load station elements |
| Recycled rubber modular platforms | Medium | High; manual-handled blocks reduce plant and possessions | Very high recycled tyre content | Pilot for halt platforms, temporary stations, and extensions; require fire/slip/drainage tests |
| Modular station kit-of-parts | High | High across programme; less useful for one-off showpiece stations | Compatible with timber, recycled steel, low-carbon concrete | Adopt as OSR default |
| Recycled plastic bus/platform access modules | Medium | High for temporary accessibility works | High recycled plastic content | Use for temporary or feeder stops, not primary heavy rail platforms without approval |
| Mass timber station buildings | Medium-high | Medium; fast above-platform assembly | Renewable, low embodied carbon | Watchlist for dry climates and non-critical buildings; fire/termite/moisture details matter |

### Modular Platform Systems

There is a mature market for precast railway platform elements. Moore
Concrete supplies front wall units, L-walls, edging units, slabs, and
copings for new platforms and platform extensions. HERING's modular
platform systems are designed around prefabricated foundations, slabs,
and substructure components, including variants suited to tight closure
times and lighter lifting equipment. Older modular platform research such
as StepSafe also supports the basic direction: a small number of factory
made components, simple foundations, and repeatable installation sequence.

OSR should keep the station platform as a product family:

- Halt: short precast edge beam + modular deck + minimal canopy.
- Standard: L-wall or TT slab modules + portal canopy + cable/service
  trench.
- Major/interchange: same modules repeated with larger foundations,
  more circulation width, and more MEP.

### Recycled Rubber And Composite Platforms

Arcadis and partners developed the Footprint Modular Platform using
100% recycled rubber blocks for platform walls. Arcadis reports a
typical 36 m platform extension can save about 25 tonnes of carbon and
that the blocks reduce heavy lifting needs. This is highly relevant to
fast extensions, temporary stations, and low-platform pilots.

The important caution is product acceptance. Rubber-block platforms need:

- Fire/smoke classification.
- Slip resistance when dusty, wet, oily, and hot.
- UV/heat ageing data for hot climates.
- Drainage and trapped-water details.
- Load tests for crowding, maintenance carts, and edge impact.
- A repair method for damaged blocks.

### GRP / FRP Platform Decks

Dura Composites reports GRP platform systems already installed across
rail stations and claims installation time can be cut by up to 65%.
These systems are useful where speed, corrosion resistance, and low
weight matter. They are less obviously circular than recycled rubber or
plastic systems unless the supplier can provide end-of-life takeback and
recycled-content evidence.

OSR should allow GRP decks as an option for:

- Temporary platforms.
- Footbridges and access ramps.
- Low-load platform extensions.
- Coastal/corrosive environments.

### Modular Station Design

Network Rail's HUB Station and station design guidance both point toward
kit-of-parts station design. The US FTA's Los Angeles modular station
case is older, but still useful: standardize boxes, ancillary rooms,
MEP, structural elements, circulation, and platform layouts while leaving
site-specific entrances and public realm flexible. Arup's modular station
handbook for Indian station redevelopment reaches the same conclusion for
live rail environments: standardize typical components, prebuild offsite,
and reduce redevelopment time.

For OSR, that means:

- One platform edge detail across all station archetypes.
- One canopy bay module with repeatable columns, purlins, PV rails, and
  drainage.
- One electrical/telecom cabinet family.
- One ramp/stair kit.
- One ticketing/gate plinth, even when fare policy changes.
- Common MEP service routes and quick-disconnect interfaces.

## Recycled And Lower-Carbon Materials

### Near-Term Approved Material Families

| Material | Where to use now | Notes |
|---|---|---|
| Recycled steel / EAF steel | Rails only with certified new rail supply; station steelwork, canopy frames, rebar | Reused rail should not become running rail without full traceability and ultrasonic/profile acceptance |
| Recovered ballast / aggregate | Subbase, drainage aggregate, non-critical concrete where standards allow | Less central to ballastless OSR, still useful in subbase and civil works |
| Recycled concrete aggregate | Platform foundations, non-prestressed slabs, drainage works | Use performance specs; keep prestressed slab track conservative until approved |
| GGBS / fly ash / limestone calcined clay / low-carbon cement blends | Precast station elements, platform foundations, track slabs where supplier can certify strength and durability | Local supply varies strongly |
| Recycled rubber | Vibration mats, platform blocks, temporary access surfaces | Check fire, heat, smoke, creep, and slip |
| Recycled plastic composites | Sleepers/bearers in approved applications, access modules, cable trough covers, temporary works | Check thermal expansion and fire/smoke |
| Reused station components | Canopy steel, cabinets, benches, cable trays, lighting poles | Needs material passport and condition grading |

### Circular Procurement

Network Rail, Deutsche Bahn, SNCF, UIC, and Victoria's Big Build all
point in the same direction: reuse and recycled content need a system,
not isolated experiments. OSR should build procurement around:

- A material passport for every major batch: steel, concrete, rubber,
  plastic, rail, fasteners, and PV/canopy components.
- A recovered-material hierarchy: reuse as-is, remanufacture, recycle
  into equal-grade infrastructure, then downcycle.
- Regional material depots near construction packages.
- Contractor tender scoring for recycled content, takeback, and embodied
  carbon, but only where standards allow the material.
- A local product-acceptance register, not one-off waivers.

## Implementation Recommendations For OSR

### Adopt Now

1. **At-grade urban trackform:** ballastless direct-fixation slab; the current
   CAD-indexed target is $2.584M/route-km against the retained $3.0M benchmark.
2. **Elevated guideway kit:** repeatable Pi20/Pi25 or special segmental guideway,
   single-column piers, standard bearings, standard drainage, and one
   erection playbook.
3. **Two at-grade construction methods:** continuous slipform for long open
   runs and ST6 single-track precast panels for constrained or replaceable
   zones.
4. **Adjustable baseplates:** required for all ballastless track to speed
   survey recovery and maintenance.
5. **Station kit-of-parts:** precast platform units, steel portal canopy,
   modular ramp/stair/cabinet/service trench.
6. **Circular procurement clauses:** require recycled-content disclosure,
   takeback options, and batch traceability.
7. **Recycled-material pilots:** rubber platform extension, composite
   sleepers in depot/temporary track, low-carbon concrete in non-critical
   station elements.

### Pilot Before Standard Use

- Recycled rubber modular platform walls for permanent passenger
  platforms.
- GRP platform decks in high heat and high footfall.
- Recycled aggregate in prestressed track slabs.
- Geopolymer or graphene-enhanced concrete sleepers/slabs.
- Recycled rubber slab mats under main running track.

### Avoid As Core Standard For Now

- Reused rail as new running rail without full certification.
- Fully bespoke station architecture per city.
- Uncertified plastic structural modules in fire-critical station areas.
- One proprietary slab-track system that prevents local fabrication.
- Heavy recycled-content requirements that local suppliers cannot certify.

## Design Recommendations And Status

1. **Implemented:** the civil catalogue includes the ballastless urban slab
   system with:
   - continuous-slipform and constrained ST6 variants,
   - direct-fixation fastener envelope,
   - slab mat option,
   - cable trough and drainage interfaces.

2. **Recommended extension:** add a modular platform kit with:
   - precast concrete base option,
   - recycled rubber extension option,
   - GRP deck option,
   - standard service trench and cabinet plinth.

3. **Implemented:** the rapid elevated guideway catalogue includes:
   - full-span Pi20/Pi25 and segmental-launch variants,
   - 20 m / 25 m standard spans,
   - controlled special-span interface,
   - single-column pier and pier-cap shell catalogue,
   - elevated-station widened-bay interface.

4. **Recommended extension:** add a procurement-release checklist covering:
   - recycled content certificate,
   - product acceptance certificate,
   - fire/smoke/slip/UV/thermal test pack,
   - repair method,
   - end-of-life takeback or recycling route.

5. Retain $3.0M/route-km as the at-grade calibration benchmark and treat the
   current $2.584M CAD-indexed value as an unquoted planning target. Recycled
   content can reduce embodied carbon and site time, but should not be assumed
   to reduce first cost until supplier pricing is proven.

6. Retain $12.0M/route-km as the elevated calibration benchmark and treat the
   current $9.748M CAD-indexed value as a repetitive-package planning target
   only. Short elevated stubs, soft-ground foundations, many elevated stations,
   or repeated special spans should carry a local risk premium.

## Source Links

- [Network Rail: HUB Station modular kit-of-parts](https://www.networkrail.co.uk/stories/designing-railway-stations-for-the-future/)
- [Network Rail Station Design Guidance](https://www.networkrail.co.uk/wp-content/uploads/2021/06/NR_GN_CIV_100_02_Station-Design.pdf)
- [FTA: Modular Station Design](https://www.transit.dot.gov/regulations-and-guidance/modular-station-design)
- [Arup: Design Handbook for Modular Railway Stations](https://www.arup.com/en-us/projects/design-handbook-for-modular-railway-stations/)
- [HERING: modular railway platform construction systems](https://www.hering-group.com/en/products-services/system-platforms/systems-for-new-platform-construction/)
- [HERING: low-carbon platform concrete and recycled aggregate](https://www.hering-group.com/en/products-services/system-platforms/with-co2-reduced-concrete/)
- [Moore Concrete: precast railway platform components](https://www.moore-concrete.com/products/concrete-platforms)
- [Dura Composites: GRP railway station platforms](https://middle-east.duracomposites.com/grp-products/grp-frp-railway-station-platforms/)
- [Arcadis: Footprint recycled-rubber modular platform](https://www.arcadis.com/en-gb/news/europe/united-kingdom/2022/7/arcadis-design-partner-for-innovative-rail-platform-system-that-lowers-carbon-footprint)
- [Arcadis project page: low-carbon rail platform](https://www.arcadis.com/en-us/projects/europe/united-kingdom/the-low-carbon-rail-platform-of-the-future)
- [Sicut: Network Rail approval for recycled plastic sleepers](https://sicut.com/network-rail-full-product-approval/)
- [Sicut: Network Rail hardwood replacement with composite sleepers](https://sicut.com/network-rail-composite-sleepers/)
- [Sustainability Victoria: Duratrack recycled plastic sleeper trials](https://www.sustainability.vic.gov.au/news/news-articles/recycled-plastic-composite-railway-sleepers-replace-timber-sleepers-for-low-speed-rail-applications)
- [Pandrol Fastclip Baseplate for ballastless track](https://www.pandrol.com/us/product/fastclip-baseplate/)
- [Pandrol DRS Baseplate for non-ballasted metro/light rail](https://www.pandrol.com/us/product/drs-baseplate/)
- [WEGH Arianna ballastless slab track system](https://www.weghgroup.com/en/concrete-elements-for-track-system/railway-track-system-slabs/)
- [EPD International: Arianna slab track EPD](https://www.environdec.com/library/epd4332)
- [SYSTRA and STRADAL low-carbon ballastless slab track](https://www.systra.com/en/news/a-low-carbon-new-generation-ballastless-track/)
- [FHWA: prefabricated bridge elements and accelerated bridge construction](https://www.fhwa.dot.gov/bridge/prefab/index.cfm)
- [Freyssinet: precast segmental erection methods](https://www.freyssinet.com/solution/build/bridge-deck-construction/precast-segmental-erection/)
- [SYSTRA: bridges and U-shaped viaducts](https://www.systra.com/en/markets/bridges-viaducts/)
- [SYSTRA: Dubai Metro U-shaped precast elevated guideway](https://www.systra.com/uk/project/dubai-metro-united-arab-emirates/)
- [TRID: Dubai Metro light rail viaducts superstructure](https://trid.trb.org/View/864938)
- [Surrey Langley SkyTrain: precast concrete facility](https://surreylangleyskytrain.gov.bc.ca/precast-concrete-facility/)
- [Surrey Langley SkyTrain: launching gantries](https://surreylangleyskytrain.gov.bc.ca/launching-gantries/)
- [MRTA Orange Line East: elevated structures and elevated stations](https://mrta-orangelineeast.com/en/structure)
- [ANM Riyadh Metro Line 3: 3,000 precast segments](https://www.anm-metro.com/3000-precast-segments/)
- [edilon)(sedra slab track mats](https://www.edilonsedra.com/system/tracklast/)
- [Network Rail: reducing waste and material reuse](https://www.networkrail.co.uk/sustainability/reducing-waste/)
- [Network Rail: Whitemoor recycling centre](https://www.networkrail.co.uk/stories/welcome-to-whitemoor-our-huge-recycling-centre/)
- [Deutsche Bahn: ballast recycling](https://nachhaltigkeit.deutschebahn.com/en/measures/recycling-ballast)
- [SNCF: ballast recycling](https://www.groupe-sncf.com/en/group/about-us/companies/sncf-reseau/ballast-recyclaging)
- [UIC circular economy programme](https://www.uic.org/sustainability/circular-economy/)
- [Victoria Big Build recycled materials resources](https://bigbuild.vic.gov.au/about/ecologiq/resources)
- [Victoria Big Build environment and Recycled First](https://bigbuild.vic.gov.au/about/environment)
- [Research: sustainable rubberized geopolymer concrete sleepers](https://www.sciencedirect.com/science/article/pii/S014102962501987X)
- [Research: reducing carbon footprint of railway sleepers using recycled plastics](https://www.frontiersin.org/journals/sustainability/articles/10.3389/frsus.2024.1460159/full)
