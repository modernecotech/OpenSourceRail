# RFC 0009 — Track Design Standard

**Status:** Draft — planning only, no civil drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md)

## 1. Summary

OpenSourceRail commits to **four track-geometry presets**,
corresponding 1:1 to the rolling-stock families in
[RFC 0008](0008-rolling-stock-reference-design.md). Every line
in every deployment picks exactly one preset. Deviating from a
preset means stepping outside the project's tested envelope — the
simulator, the safety case, and the auto-gen pipeline all assume
one of these four.

| Preset | Gauge | Min radius | Max grade | Cant max | Rail profile | Compatible consists |
|---|---|---|---|---|---|---|
| `heritage-tram` | 1 000 mm | 25 m | 70 ‰ | 120 mm | Ri60 grooved | `tram-2car` |
| `standard-urban` | 1 435 mm | 90 m | 50 ‰ | 150 mm | UIC60 | `tram-2car`, `light-metro-3car` |
| `standard-metro` | 1 435 mm | 200 m | 35 ‰ | 160 mm | UIC60 | `light-metro-3car`, `metro-4car`, `metro-6car` |

> **No-tunnel invariant.** Per [RFC 0011](0011-civil-infrastructure-design-standard.md),
> every alignment is at-grade, elevated, or (at water crossings)
> bridge. The four presets above assume above-ground operation
> only; underground running is explicitly out of the project's
> upstream catalogue. Where a corridor cannot fit at-grade, the
> solver routes it elevated, never under.
| `mainline-mixed` | 1 435 mm | 400 m | 25 ‰ | 180 mm | UIC60E1 | `metro-4car`, `metro-6car` |

The presets already exist as a schema in
[`designs/templates/track-geometry.toml`](../../designs/templates/track-geometry.toml).
This RFC promotes them into a committed engineering envelope with
the civil rationale for every number.

## 2. Non-goals

- **Not a civil drawing standard.** Slab-track vs ballasted, fastener
  family, concrete sleeper geometry — all are per-deployment civil
  decisions, constrained by local material availability and by this
  RFC's envelope but not specified here.
- **Not an earthworks rulebook.** Cut/fill, drainage, embankment
  stability are owned by the deploying operator's civil team;
  this RFC specifies the *alignment* envelope they must respect.
- **Not a signalling-plan document.** Where signals / markers /
  balises physically go along the track is a deployment artefact
  — covered at a deployment level, not here.
- **Not a tunnel/bridge standard.** Those have their own envelopes
  (gauge clearance, ventilation, emergency egress) handled by
  `designs/templates/structures.toml` and a future structures RFC.
- **Not a standards body.** We reference EN 13848 (track geometry
  quality), UIC 505-1 (structure gauge), UIC 510 (wheel profile),
  UIC 720 (transition curves). We do not publish new ones.

## 3. Why four presets, not a continuum

A continuum of allowable geometry (pick your own radius, pick your
own grade) doesn't fit the project's "simple for countries to
implement" constraint. The sim's validation, the sensor-tuning
(odometry, hot-axle), the brake-curve coefficients, and the
station-archetype platform lengths are all calibrated against a
specific envelope. Going off-preset means redoing every one of
those calibrations at the deployment level.

Four presets cover the actual range of urban-rail deployments in
the target regions:

- `heritage-tram` fits retrofits of legacy metre-gauge European
  tram infrastructure (still common in some MENA and ex-French
  colonial networks).
- `standard-urban` is street-integrated light metro — the Samawah
  reference ([RFC 0003](0003-samawah-reference-deployment.md)).
- `standard-metro` is dedicated-ROW medium and large metro, the
  dominant deployment category worldwide.
- `mainline-mixed` is the edge case where the OSR-branded light
  metro shares track with existing heavy rail. Intentionally
  conservative — if you need this preset, you are outside the
  primary mission scope, and the envelope is deliberately close
  to a normal mainline spec to minimise surprises.

## 4. Gauge

**1 435 mm standard gauge** is the default for three of the four
presets. It is the only gauge for which off-the-shelf wheelsets,
rail profiles, switches, and fasteners are widely available from
multiple global suppliers and from domestic producers in MENA, sub-
Saharan Africa, South and Southeast Asia, and Latin America.

**1 000 mm metre gauge** is kept only for `heritage-tram` retrofit
work. Deploying a new metre-gauge corridor from scratch is
explicitly discouraged: the supplier base is thinner and the
lifetime maintenance burden higher. The preset is retained because
some legacy networks would otherwise need full gauge conversion to
adopt OpenSourceRail, which is a much larger CAPEX line than
deploying against their existing gauge.

**No Iberian gauge (1 668 mm), no Russian gauge (1 520 mm), no
narrow gauges under 1 000 mm.** Operators in those regions are
free to fork the project and add them; OpenSourceRail's upstream
envelope stays at 1 000 / 1 435.

## 5. Horizontal alignment

### 5.1 Minimum radius

| Preset | Min radius | Derivation |
|---|---|---|
| `heritage-tram` | 25 m | Ri60 grooved rail + `tram-2car` 2-axle bogie with small wheelbase (1.8 m) can negotiate 25 m at crawl speed (≤ 10 km/h) without excessive wheel-flange wear. |
| `standard-urban` | 90 m | UIC60 rail + `light-metro-3car` articulated bogie + 22 m/s max speed — radius comes from balanced-cant condition at 15 m/s through the curve (2/3 of max), 150 mm max cant. |
| `standard-metro` | 200 m | `metro-4car` + `metro-6car` consists are less forgiving; 200 m allows 25 m/s through a well-canted curve with unbalanced cant ≤ 60 mm (EN 13803-1 normal). |
| `mainline-mixed` | 400 m | Mainline conservative. Allows 33 m/s (120 km/h) at 180 mm cant. |

Transition curves (clothoid) are required at every curve-tangent
interface per UIC 720. Minimum transition length is
`L ≥ 0.5 × cant_mm × speed_m_s / 1000` (normal) — the auto-gen
solver already enforces this via the civil-class inference.

### 5.2 Maximum gradient

| Preset | Max grade | Derivation |
|---|---|---|
| `heritage-tram` | 70 ‰ (7 %) | Legacy tram constraint; `tram-2car` with 50 % powered wheelsets holds 7 % in dry + adhesion-limited rain with sanding. |
| `standard-urban` | 50 ‰ (5 %) | `light-metro-3car` at 50 % powered gives enough tractive effort; 5 % is the practical limit above which wheelslip becomes frequent in wet conditions. |
| `standard-metro` | 35 ‰ (3.5 %) | `metro-4car` / `metro-6car` fully-loaded (AW3) at 75–100 % powered axles; 3.5 % is the inflection where regenerative-braking downhill doesn't saturate the battery. |
| `mainline-mixed` | 25 ‰ (2.5 %) | Mainline conservative; allows a light-metro consist to operate on a corridor sometimes used by heavier stock. |

Gradient transitions (vertical curves) are not less than
`R_v ≥ 0.4 × v²` where v is design speed in m/s — standard UIC
metro practice, embedded in the auto-gen pipeline's civil-class
inference.

### 5.3 Cant (superelevation)

| Preset | Max cant | Rationale |
|---|---|---|
| `heritage-tram` | 120 mm | Street running limits cant — road surface either side of the tracks can't exceed a few degrees lateral slope. |
| `standard-urban` | 150 mm | Street-integrated with some dedicated ROW. |
| `standard-metro` | 160 mm | Dedicated ROW, standard metro number. |
| `mainline-mixed` | 180 mm | Mainline standard. |

Cant deficiency (unbalanced cant at design speed):
- Normal: ≤ 100 mm for `standard-urban`, ≤ 110 mm for `standard-metro`, ≤ 130 mm for `mainline-mixed`.
- Exceptional (with extra driver notice, slow orders): up to 150 mm.

### 5.4 Ruling speed

Per-preset `nominal_speed_mps` in the TOML is the design speed for
the alignment; actual line speed is constrained by the smallest
curve + grade + consist limit. This matches EN 13803-1 intent.

## 6. Vertical alignment

- Minimum crest/sag radius = `0.4 × v²` m with v in m/s.
- Vertical grades interpreted at station throats are limited to
  ≤ 2.5 ‰ regardless of preset — stopping on a grade is a
  long-tail fault that every operator tolerates badly.
- A grade is applied only in simple one-slope segments; compound
  grades are a civil-complexity red flag surfaced by the
  auto-gen's `quality.yaml`.

## 7. Track structure

### 7.1 Rail

| Preset | Profile | Mass | Notes |
|---|---|---|---|
| `heritage-tram` | Ri60 | 60 kg/m | Grooved, 180 mm deep groove for street embedment. |
| `standard-urban` | UIC60 (60E2) | 60 kg/m | Standard vignole; 260 Brinell grade. |
| `standard-metro` | UIC60 (60E2) | 60 kg/m | Same as urban; heavier profile unnecessary for 14 t axles. |
| `mainline-mixed` | UIC60E1 | 60 kg/m | Equivalent mass, different head geometry — better wear profile when shared with freight. |

### 7.2 Sleepers / slab

The preset envelope does **not** fix slab-track vs ballast — that
is deployment-specific. Constraints the presets do fix:

- Sleeper spacing: 600 mm typical, 550 mm in curves below 2×
  min radius for all ballasted presets.
- Fastener: Pandrol fastclip family or equivalent elastic-rail
  fastener; no rigid K-type fasteners (heavy maintenance).
- Slab-track option: only where the civil-class inference
  classifies the segment as elevated or tunnel (vibration-prone
  environments) — the operator may still choose ballasted in
  those segments.

### 7.3 Turnouts

| Preset | Typical turnout tangent | Divergent speed |
|---|---|---|
| `heritage-tram` | 1:5 (AKA "7°" typical) | 15 km/h |
| `standard-urban` | 1:9 | 40 km/h |
| `standard-metro` | 1:9 (station ends) / 1:14 (mainline crossovers) | 40 / 60 km/h |
| `mainline-mixed` | 1:14 / 1:18.5 | 60 / 80 km/h |

The `osr-wayside-points` software already handles any tangent;
this RFC pins the civil choice.

## 8. Structure gauge

All four presets respect **UIC 505-1 structure gauge**
(static envelope at 3.15 m wide × 4.32 m tall above top-of-rail),
with a dynamic outline adding ± 80 mm lateral and ± 50 mm
vertical for the design-maximum cant + sway. Per-consist
structure gauges come from [RFC 0008 §3.1](0008-rolling-stock-reference-design.md);
no family violates the static envelope.

## 9. Track geometry quality

Track geometry quality is measured and maintained per EN 13848:

| Indicator | Class QN1 (alert) | Class QN2 (immediate action) |
|---|---|---|
| Longitudinal level D1 | 6 mm | 10 mm |
| Alignment D1 | 5 mm | 7 mm |
| Cant | 15 mm | 20 mm |
| Twist (2 m base) | 4 mm/m | 7 mm/m |

Measurement cadence per preset:

| Preset | Recording-car cadence | Hand-measurement after each weather event |
|---|---|---|
| `heritage-tram` | 90 days | Yes (flood / dust storm) |
| `standard-urban` | 90 days | Yes |
| `standard-metro` | 60 days | Yes |
| `mainline-mixed` | 45 days | Yes |

A recording car is explicitly *not* required to be OpenSourceRail
hardware; any EN 13848-compliant recording trolley from the
commercial market is acceptable. The future
[`osr-track-geometry`](../../crates/) crate (not yet scaffolded)
will accept standard GPM/RECD data formats.

## 10. Self-consistency constraints

The auto-gen pipeline enforces the compatibility matrix from
RFC 0008 §4. Every preset declares `compatible_consists`; the
emitter picks a rolling-stock family first (by population band)
and then selects the tightest geometry preset that still lists
that family as compatible:

```text
  pop band         chosen family           chosen geometry preset
  ──────────────   ───────────────────     ─────────────────────────
  ≤ 300 k          tram-2car               heritage-tram OR standard-urban
  300 k … 1 M      light-metro-3car        standard-urban (Samawah)
  1 M … 3 M        metro-4car              standard-metro
  ≥ 3 M            metro-6car              standard-metro OR mainline-mixed
```

The emitter default for each band is the first entry in the
choice list; the per-deployment override is a single line in the
city recipe.

## 11. Pitfalls and decisions

- **We pick UIC60 over IRJ-equivalents.** Rail profile is where
  we take the standard path rather than the simple path —
  UIC60's global supply chain is well-stocked and second-source.
  A simpler lighter-profile would save mass but lose that
  supplier depth.
- **Ballasted vs slab is deferred.** Slab track has lower
  lifetime maintenance but 2–3× the initial CAPEX. The preset
  envelope stays neutral; the deployment recipe picks based on
  the operator's capital profile and local skills.
- **No mixed-gauge track.** Dual-gauge trackwork (1 000 + 1 435)
  is explicitly out of scope. Operators with that legacy have to
  choose one to extend.
- **No tilting rolling stock.** The rolling-stock families in
  [RFC 0008](0008-rolling-stock-reference-design.md) do not tilt;
  cant-deficiency limits are therefore conventional. If a future
  family adds tilting, the presets gain a `tilting_allowed`
  attribute and more permissive cant deficiency.
- **Maximum axle load is the consist, not the track.** Track is
  designed for ≥ 16 t axle load across every preset; the
  rolling stock stays under 14 t by design. This gives a future
  maintenance / utility vehicle a headroom to share the track.

## 12. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | Worked civil alignment for Samawah Line 1 + Line 2 references against `standard-urban`, with per-segment table + civil-class summary + compliance report at [`docs/civil/samawah/`](../civil/samawah/) (done 2026-04-22) | RFC 0003 |
| **v2** ✅ | Emitter enforces geometry/consist compatibility + emits `geometry` per line in auto-gen output (done 2026-04-22). **OSR-ALN alignment interchange format** at [`docs/civil/osr-aln-format.md`](../civil/osr-aln-format.md) — tool-agnostic TOML schema civil firms export to. | v0, RFC 0008 v2 |
| **v3** | Reference standard drawings (fastener, sleeper layout, turnout geometry) under CERN-OHL-S v2 | v1 |
| **v4** | `osr-track-geometry` crate that ingests EN 13848 recording data and feeds the CBM pipeline | v3 |
| **v5** | First-article track constructed and recorded at a pilot deployment | v1, v3 |

## 13. Relationship to existing work

- [`designs/templates/track-geometry.toml`](../../designs/templates/track-geometry.toml)
  — the Lego-block schema that this RFC ratifies.
- [`crates/osr-routing/src/civil.rs`](../../crates/osr-routing/src/civil.rs) —
  already classifies every 20 m cell as at-grade / elevated /
  bridge / bored tunnel; the civil inference respects minimum
  curve and max grade from the preset but uses hard-coded numbers
  today. Emitter v2 reads them from this RFC.
- [`crates/osr-design`](../../crates/osr-design/) — emits `geometry
  = "standard-urban"` as a hardcoded line attribute today; v2
  picks per §10 above.
- [`osr-sim`](../../crates/osr-sim/) — its `Section` type has
  `length_mm` and `max_speed_mps`; gradient and cant are
  unexposed today and land as v4 when the simulator gains a
  kinematic model beyond the current trapezoidal profile.

## 14. Open questions

1. **Should `standard-urban` allow steeper grades in short
   segments (say, 70 ‰ over < 100 m) for ramping to elevated
   structures?** Opens a per-segment override vs clean preset.
   Resolve with real Samawah alignment work.
2. **Metric vs imperial-historical gauge.** Does the mission
   scope ever need to support Cape gauge (1 067 mm) for southern
   Africa legacy? Revisit after the first sub-Saharan pilot.
3. **Slab-track cost model** — the per-site BOM comparison
   between ballast + slab + fastener + sleeper over 30 years. A
   planning-grade spreadsheet that the operator can localise
   would help — candidate output of v3.
4. **Expansion joints / CWR.** Continuously welded rail is the
   default; the RFC should commit on stress-free-temperature
   profile per climate band. Defer to a separate climate-adapter
   addendum.

## 15. Done criteria

- [x] Four presets committed with engineering rationale (§§3–7)
- [x] Gauge policy fixed (§4)
- [x] Horizontal + vertical alignment limits stated (§§5–6)
- [x] Rail / sleeper / turnout envelope named (§7)
- [x] Structure gauge named (§8)
- [x] Geometry-quality thresholds fixed (§9)
- [x] Rolling-stock ↔ geometry compatibility matrix (§10)
- [x] Pitfalls and alternatives explicit (§11)
- [x] Rollout ordered (§12)
- [x] Relationship to software + templates named (§13)

The next session picks up at **v2 — emitter compatibility**, a
single change in [`crates/osr-design/src/emit.rs`](../../crates/osr-design/src/emit.rs).
