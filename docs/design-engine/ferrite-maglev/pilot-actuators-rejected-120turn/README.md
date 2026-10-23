# Provisional electrical/magnetic/moving actuator composition

The retained ideal-force benchmark remains separate. This new execution integrates actual public Rust current controllers with independently solved RL windings, gap-dependent support flux and forces, moving-body/guideway states and local powered-group phase references. Copper heat, DC energy, current/voltage/temperature/phase screens and rejected cases are retained.

Nominal executed 1412/2000 moving frames; numerical feasibility False; failure FAULT 36:Some(Current).

Counted repair steel-wall-004/equal-copper-80t10mm2: 29,064.079kg/car AW3; 2000/2000 frames; numerical pass False; failure None; current screen False.
Counted repair steel-wall-004/equal-copper-100t8mm2: 29,064.079kg/car AW3; 2000/2000 frames; numerical pass False; failure None; current screen False.
Counted repair steel-wall-004/higher-copper-120t20mm2: 30,116.751kg/car AW3; 122807/140417 frames; numerical pass False; failure independent post-step physical gap outside envelope; current screen False.

Equal-copper rewinds preserve I²R and current density at equal ampere-turns; they cannot cure the thermal failure by relabelling a60A rating. The counted higher-copper candidate derives its680mm mean turn from280×200mm outer and120×80mm inner dimensions,120turns×20mm² in a70mm-deep pack; actual copper, resistance, pack fill and vehicle mass are recalculated. The detachable collector adds its separately derived106.01368kg/car of splice plates and bolts, with no cut-stock removal credit. Additional mount36kg/car and cooling120kg/car with an explicit3× continuous winding heat-rejection allocation are included. The3.75A/mm² baseline wire screen and separate60A drive screen remain unchanged. Coldplate flow/thermal resistance is an unqualified design requirement, and full-trip adiabatic temperature does not qualify continuous duty.

[Counted higher-copper packaging](candidate-bay.svg) · [Exact candidate bay definition](candidate-bay.json.gz). Existing26.4t hardpoint/civil acceptance is not inherited: the new gross load requires re-evaluation.

Each group uses a flux-weighted virtual phase reference. The full3degree mechanical/index allowance remains ADDITIONAL to actual car-relative phase and position, timestamp, stator-registration and thermal uncertainties. Worst-case magnitudes are summed against the unchanged5degree local limit. Seventy independently controlled5m groups per direction count140converters at a two-direction station; the actual12m band/17.5m pitch leaves5.5m between bands. Whole-train5degree spread is a distinct historical observation. The adverse index error also enters the physical field and its unwanted normal force.

Gap-field screens use an assumed25,000mm² pole area, while the winding inner aperture is9,600mm². No core neck/yoke area or validated flux split has been derived. A low gap B cannot establish core saturation acceptance; the magnetic geometry remains an explicit manufacturing/field-map hold. Updated body/beam gap poses are checked after every mechanical frame, including the final frame.

The nominal motion profile uses actual Baghdad line14 mainleg geometry, with runtime rounded upward to the1ms model clock; finance must use that exact profile hash. Rust current input power and heat are aggregate support/wayside values; they must not be added to a separate LSM loss budget as support-only energy. The RL energy identity covers frozen-geometry incremental current energy, not a complete measured PM/structure energy balance.

Assumed25,000mm² gap pole area versus9,600mm² winding aperture: pole shoe/core neck/yoke flux geometry and saturation remain unreconciled; gap-field pass does not close this hold
Support/LSM maps, shared PM flux, saturation/core/eddy losses and temperature qualification
Lateral/guidance dynamics and all omitted current circuits
Complete converter/DC/brake/cooling/electrical fault energy and physical timing
Whole equipped-body mass/CG/inertia and joined load paths remain unaccepted

No digital pass authorizes hardware, manufacturing or operation.
