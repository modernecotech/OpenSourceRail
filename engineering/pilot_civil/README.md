# Candidate-bound pilot civil design

This executable outline compares the 20 m box, original folded plate and a
physical deeper/thicker folded revision for the same 1.5 km, double-track pilot.
It consumes sealed `osr-pilot-axle-loads/1` input: a whole-system candidate ID,
vehicle/mass evaluation IDs, named static full-axle forces and located CG.
Axle forces must conserve the supplied train mass. Added propulsion and recovery
hardware belongs in the caller's axle packet; it is never assumed weightless.

```python
from engineering.pilot_civil import evaluate, evaluate_portfolio
results = evaluate_portfolio(axle_packet)
result = evaluate(axle_packet, family='folded_plate', revision='thick-web')
```

```sh
.venv/bin/python -m engineering.pilot_civil --output /private/fresh-run \
  --axle-input /private/axle-input.json --upstream-root /exact/upstream/checkout
# Optional bounded fresh native work: add --native.
.venv/bin/python -m pytest -q tests/test_pilot_civil.py
```

The fallback without `--axle-input` is the original parts-linked 12-driven-axle
comparison and explicitly equal axle shares. It is not the newer located body.
Different train packets are different evaluations; their evidence is not inherited.

The model applies the declared dynamic factor once. It translates a complete
train through 501 positions, uses actual 0.35/19.65 m bearing lines, free overhangs,
pointwise bending envelopes, lateral loads and a closed-section torsion estimate.
Position-sampling allowances are gross-model sensitivity estimates, not a bridge
response guarantee. Gross deflection targets are advisory interface hypotheses.
Concrete cracking, fatigue, shear, bearing restraint, settlement and dynamic
amplification remain distinct unverified obligations.

Prestress is an explicit six-duct, grouped-strand proposal. Automatic strand
sizing includes its own dead weight. Final two-support transfer and service
stress hypotheses, loss assumptions and camber are retained. Temporary
prop-restrained secondary effects, end-zone bursting, tendon/bar clashes and
joint shear transfer are **not verified**. The folded layout uses narrower
bearings fitting its 700 mm bottom flange; copying the box layout is prohibited.

The assembled civil ID includes reinforcement stock, tendon geometry, the
2×10 m match-cast/2 mm epoxy joint proposal, bearings, pier and designed footing.
A changed soil hypothesis with fixed dimensions changes evaluation only; a
redesigned footing changes physical identity. The route has 150 beams, 76 shared
two-track bents and 600 bearings. Cost owners are disjoint, civil-only replacements
for existing civil owners. Positive reserves cover incomplete joint, duct, grout,
chair, fixing and access detail. Rates are explicit preliminary procurement and
manufacturing assumptions, not supplier observations or verified Chinese prices.

A located scene separates concrete/metal solids, equipment envelopes, bar/tendon
paths and quantity reserves. Its rail profile is an envelope, not a rail drawing.
Gross concrete includes occupied reinforcement/duct space, so CAD material
volumes must not be added to stock mass as installed mass. Final installed mass
remains unknown. The scene is a useful outline, not a fabrication drawing.

Construction includes cut stock, two-point/four-sling handling, a braced reusable
four-leg temporary tower, pad-pressure and Euler/yield screens, staged jointing,
post-tensioning and controlled tower removal. The nominal 60 t capacity **at
12 m radius** is a declared trial input, not a manufacturer crane chart. Original
box whole lifts exceed that trial control after rigging; all alternatives also
face the declared 35 t transport payload. Segmentation is an actual manufactured
revision with a priced joint and temporary works, not a weakened lifting limit.

Native mode runs at most two SolidCraft jobs, one independent FreeCAD STEP measurement and two mesh/dual-solver cases.
It uses the exact new CAD, candidate loads and fresh FieldCraft/CalculiX results;
no historical FEM result is inherited. Each process is single-thread requested,
2 GiB address-space limited, 60 CPU seconds maximum and 58 seconds wall timeout.
The mesh cap is 20,000 tetrahedra. Failed jobs and exact logs are retained.
A perfectly bonded gross continuum is not a segment-joint or prestress model.
The coordinator approved the third CAD invocation for that independent STEP measurement, with no engineering-limit change.

Every run preserves request, input, source hashes, selections, raw native logs,
resource records, failures and SHA-256 manifest. Source hashes before/after detect
drift; the coordinator itself is not an OS read-only source sandbox. Native
records describe actual Bubblewrap/Flatpak scope and observed outcome. All
selection is for the next experiment. No reference, safety, construction,
manufacturing or operating approval is granted.

## Rotation-free final-load verification

The original finite longitudinal support-patch trial remains reproducible. Its
fixed vertical displacement over a finite longitudinal width can transmit a
bending couple and is therefore different from the simply supported analytical
beam. `support_audit` recovers the actual support wrenches; it does not infer a
pin from a support's label.

A separate final-load experiment explicitly embeds transverse bearing lines at
the exact support axes and constrains vertical displacement only on those lines.
This releases the longitudinal bending rotation while retaining transverse
support intervals. It is a pin-compatible gross comparison, **not** a model of
finite elastomer stiffness, contact, unilateral lift-off or local bearing stress.
Legacy `prepare` defaults retain the finite-patch hypothesis; the new experiment
requests `support_mode='rotation-free-line'` explicitly.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1 \
.venv/bin/python -m engineering.pilot_civil.final_trial \
  --axle-input /private/exact-axle-input.json \
  --upstream-root /exact/upstream/checkout --output /private/fresh-final-run
```

The final trial recalculates the civil design from the fresh sealed axle input,
creates one new gross SolidCraft model, checks its STEP independently in FreeCAD,
and compares up to three meshes through both FieldCraft and CalculiX. The explicit
revised numerical budget permits 50,000 cells, 3 GiB and 75 CPU seconds per
process; an actual 73-second wall timeout keeps the POSIX CPU hard limit within
75 seconds. Meshing and CalculiX retain the existing stricter 2 GiB process cap.
The 5% displacement-refinement target remains unchanged. Eight rolling native
checkpoint slots bound scratch disk use; full commands and retained final bytes
are recorded. Conductor/support gravity is applied at its declared lateral
offset in both solvers, rather than being smeared into a centred reserve.

Comparison records distinguish Euler–Bernoulli response, an explicit gross-web
Timoshenko shear correction and the 3D readback at the same top-deck observation
point. Agreement or refinement does not establish the real segment joint,
prestressing, cracking, fatigue, bearing, ground or construction-stage response.
