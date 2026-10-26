# Broader v0.6 design space

OpenSourceRail seeks simple, affordable transport that can be manufactured and repaired locally. This bounded search uses material and architecture choices to respond to the failed wheel-rail campaign, while preserving its exact evidence and the comfort-first service brief.

**Research definitions and necessary bounds.** None of these new structural families inherits a validated full-body model, installed mass or physical acceptance. The [executed native campaign](../v06-optimisation/README.md) remains a separate source-bound result.

## What can change

| Domain | Design variables | Required consequence |
|---|---|---|
| Main body | Aluminium spaceframe; participating sandwich; hybrid integral panels; GFRP semi-monocoque | Regenerate load paths, aperture frames, bogie hardpoints and counted stock |
| Panels | PET/PVC foam; aluminium/aramid honeycomb; face material and plies; thickness; cell orientation; support pitch | Include core shear, directional properties, temperature, bondlines, edges and local reinforcement |
| Connections | Bonded flanges; bond plus bolts; potted inserts; welded nodes; clips with positive retention for removable panels | Count installation hardware and qualify peel, bearing, pullout, fatigue, cure and repair |
| Station motor | Return/tooth/slot dimensions; pitch; fin count/length; single/double LIM; passive reluctance; conductor, circuits, cooling and steel | New topologies require new native adapters; no multiplication of old force |
| Service | Explicit 57.6/43.2 km/h and acceleration/powered-zone alternatives alongside 72 km/h | New requirement identities; recompute trip time, dwell, headway, fleet and total infrastructure |
| Equipment | Coated polycarbonate glazing, retained seals and thermal movement; modular HVAC | Include mounting and hot-weather capacity; supplier sheet/module mass is not installed train mass |

## Executed necessary-bound comparison

| Generation / proposal | Architecture / core | Accounted comparison/car | Temperature bound | Full-body model |
|---|---|---|---|---|
| g0 / `611e3251a716` | aluminium_spaceframe / pvc_h80 | 19.225 t | fail at 80°C | held |
| g0 / `9aa1d31e2230` | participating_gfrp_sandwich / pet_t92_80 | 19.441 t | pass at 80°C | held |
| g0 / `3e7868a77053` | hybrid_integral_panels / al_5052_criii_31 | 19.526 t | pass at 80°C | held |
| g0 / `23ad1f98d8e7` | gfrp_semimonocoque / aramid_hrh10_48 | 19.490 t | pass at 80°C | held |
| g1 / `96a1c2c4730e` | participating_gfrp_sandwich / pet_t92_80 | 19.336 t | pass at 80°C | held |
| g1 / `87f4af0d932e` | participating_gfrp_sandwich / pvc_h80 | 19.329 t | fail at 80°C | held |
| g1 / `b55acf8b5afc` | participating_gfrp_sandwich / al_5052_criii_31 | 19.285 t | pass at 80°C | held |
| g1 / `29589e7cf4c4` | participating_gfrp_sandwich / aramid_hrh10_48 | 19.283 t | pass at 80°C | held |
| g2 / `7004c874d633` | participating_gfrp_sandwich / pet_t92_80 | 19.387 t | pass at 80°C | held |
| g2 / `25bd708ea93b` | participating_gfrp_sandwich / al_5052_criii_31 | 19.336 t | pass at 80°C | held |
| g2 / `e57c404f4a92` | participating_gfrp_sandwich / aramid_hrh10_48 | 19.334 t | pass at 80°C | held |

The 11 distinct structural proposals include a matched four-core comparison and follow-ups changing panel support pitch, joint layout and honeycomb orientation. Converging revision paths share one physical definition and retain both ancestries. Material removed and added, faces, edges, aperture frames, splice stock and hardpoint stock are counted. Some stock remains in component-local frames awaiting installation; missing washers, load spreaders, resin/repair allowances and prices remain explicit. These subtotals cannot rank a complete railway.

Supplier properties distinguish typical values, stated minima, source units, specimen thickness, cell axes and temperature claims. The 80°C core case is a research envelope, not a solved Baghdad roof temperature. Room-temperature shear values do not establish hot-load strength or fire approval. Honeycomb is not treated as isotropic foam.

The motor plan generates 12 distinct physical proposals. Only supported single-fin, copper-wound linear-material geometries can reach the existing adapter. Supplier magnetic polarisation checkpoints are not silently converted into an accepted nonlinear B–H law. Actual available thrust, repeated thermal duty and installed prices stay unknown.

## Validation before selection

The previous participating-body calculation remains laterally nonconverged. Diagnose boundary conditions, joint rotational restraint, mesh and load transfer before using a stronger material to mask a model defect. Small material and joint fixtures must pass their own analytical/reaction/mesh checks before new full-body comparisons.

Adhesive coupon shear is not a joint allowable, clip pullout classes are not a primary structural load path, and an unwelded alloy strength is not a welded-node strength. Attachment examples preserve unknown hardware masses. Glazing examples count sheet mass and thermal movement; pressure, retention, abrasion, cleaning, fire and emergency egress remain gates.

Native follow-up packages attached: **3**. Their immutable inputs, outputs, solver logs and manifests are retained in the indexed archive; detailed results remain conditional on each package's declared model and validity. A fixture pass is not full-train acceptance.

[Complete comparison](results.json.gz) · [Compact summary](summary.json) · [Primary-source catalogues](catalogues.json) · [Native results](native-results.json) · [Native follow-up index](native-index.json) · [Receipt](manifest.json)

```bash
./osr design space build
./osr design space verify
```

Choose architecture first, reject necessary failures cheaply, validate its evaluator, then size it with native workers. Integrated selection still requires the same equipped mass, joints, force maps, brakes, civil loads, full journey and equal-service cost. The selected development train and 266 city packages are unchanged.

## New native motor follow-up

Four centred 2D GetDP cases use the same normal-loaded car and counted rotational inertia: required launch thrust **11.758 kN/car**.

| Geometry | Conditional force at 20 m/s | Peak steel field at 20 m/s |
|---|---|---|
| deeper-return-and-teeth | 6.522 kN | 1.828 T |
| longer-pole-pitch | 2.542 kN | 2.126 T |

Both remain below required thrust and outside the retained 1.3 T linear-material domain. Energy balance and current-density checks do not establish an available installed force map. Native dispatch chose unchanged-fin geometries; the longer-fin proposal remains an interface task.

## Native sandwich method fixtures

**4/4** checks pass: separate L/W affine shear and two sandwich bending/shear meshes. The fixture uses published directional core values with explicitly synthetic unreported constitutive regularisation and reference metal faces. This is numerical method evidence, not measured material correlation or a complete body pass. Original refused shear decks remain archived at their historical source revision; the correction bounds numeric field width.


## Retained body-model diagnosis

The retained fine model has 128970 physical solid nodes in 1 connected component. The maximum lateral displacement occurs at node 66729. The 40 ideal clamp pads have rank 5: their two collinear transfer points leave one local rotation unconstrained. Connectivity alone therefore does not validate rotational restraint. This establishes a local model deficiency; its share of the full-body mode remains unresolved.

[Diagnosis and next unit-moment/eigenmode tasks](model-diagnosis.json) · [Exact retained input/displacement data](model-diagnosis-inputs.tar.gz)

## Primary-source starting points

[AIREX PET grade data](https://www.3accorematerials.com/uploads/pdf/TDS-AIREX-T92-E-01.2026-EMEA.pdf) · [DIAB PVC grade data](https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf) · [Hexcel directional honeycomb properties](https://www.hexcel.com/wp-content/uploads/2026/01/HexWebHoneycombAttributesandProperties.pdf) · [Hydro rail extrusions](https://www.hydro.com/gb/global/aluminium/products/extruded-profiles/aluminium-extrusions-in-use/modern-trains-and-rail/) · [Metawell corrugated panels](https://www.metawell.com/en/applications/rail-vehicles/) · [3M adhesive coupon conditions](https://multimedia.3m.com/mws/media/2534142O/3m-scotch-weld-epoxy-adhesive-dp490-technical-data-sheet.pdf)

The catalogues retain precise grades, revisions, source units and available byte hashes. Where byte retrieval was refused, the missing document hash stays explicit. Product certification or a supplier coupon does not release this train.
