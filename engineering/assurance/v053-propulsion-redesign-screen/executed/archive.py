"""Freeze ignored research inventory and human-readable limitations."""
from hashlib import sha256
import json
from pathlib import Path
from engineering.ferrite_maglev import candidate_magnetics as m
OUT=m.ROOT/'build/propulsion-redesign-screen'
if __name__=='__main__':
 result=json.loads((OUT/'results.json').read_bytes());assert result['source_sha256']==m.sources()
 text='''# Isolated propulsion redesign screen — not adopted

The canonical a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd candidate and every production source stayed unchanged. This folder contains process-local input hypotheses only. All design/manufacturing/physical/adoption flags remain false.

The bounded screen executed21 coupons across9 initial geometry/temperature cases and selected refinements. Two additional256×64 requests were correctly refused by the existing grid-domain guard; they remain unknown/execution-error records. Their valid replacements use256×48. No failed or unknown record was discarded.

## Why the canonical variants fail

- Halbach: refined local opposing PM field rises426→464kA/m; demagnetisation margins already−82→−121kA/m before armature loading.
- Rectangular shoes: fundamental field changes only0.18%, but local opposing PM field rises301→350kA/m. The192×48 zero-armature margin is−5.83kA/m; a stable fundamental does not validate local material survival.
- Round shoes: linear matrix residuals are tiny while the nonlinear secant mismatch remains5.42–5.55 and predicted steel fields43.8–72.3T. Those runs are not converged; none of their force estimates receives operating credit.

## Separate geometry hypotheses

Doubling source period from0.25m to0.5m while retaining40mm depth and1mm chamfers initially looked attractive. At0°C the margin after the declared maximum-current armature bound fell57.5→26.5→4.47→−9.43kA/m as the grid advanced64→128→192→256 longitudinal cells. The failed256 result invalidates earlier positive estimates preserved in results-prior192.json. The final primary operating entry therefore refuses that hypothesis.

One final physical-corner alternative uses0.5m period,40mm depth and8mm45° chamfers. Its exact new hypothesis identity is2ccec6df01771f2c57d582deb1f7a0dcf44d8ff2ff4f4b8ce56da01609bcfc6a. The finest256×48 mesh has1.953mm longitudinal cells and0.833mm depth cells:4.096 and9.6 cells across the8mm corner.

At0°C its128→256 results give0.08352→0.08382T fundamental and42.10→28.95kA/m demagnetisation margin after the declared1350A armature bound. At40°C the fine result is0.07800T with70.83kA/m margin. These are converged nonlinear coupons with positive sampled material checks; the local peak is still changing and a formal grid-convergence result is NOT established. No full0–80°C temperature-range or3D/hardware validation is claimed.

The chamfers remove an exact scalar0.0024576m³/12.288kg of PM stock across the two12m bands (2.56% of unchamfered PM stock). Fine cell removal is2.474%; coarse is2.734%. Revised native CAD, net assembly mass/inertia, retention and manufacturing are unissued. The1258.2144kg source-box mass remains an upper bound rather than a new installed-mass claim.

## Conditional40°C operating quantities

The final positive coupon geometry was used with the unchanged source harmonic/finite-overlap equations: one straight12m band, four independent5m groups, only1m overlap in each exterior group and5m in the middle groups. This is not a train/route or inverter/control simulation.

At1349A peak and20m/s, the conditional undamaged40°C map predicts10.092kN longitudinal force per car, equal239.95N side-normal terms (zero net lateral force at the symmetric pose), maximum41.90V back EMF and66.77V steady rotating-current voltage, below2400/sqrt(3)=1385.64V. Copper at80°C dissipates178.66kW across the four groups;10s adiabatic rise is3.90K/group. These numbers are model quantities with explicit unresolved field/material/system gates, not qualified operating capacity or evidence of low cost.

An exact1350A phasor evaluates to1350.0000000000002A and is correctly refused by the unchanged strict source current guard. That refusal is retained; the1349A sample is a distinct interior request, not a relaxed limit. Full input currents and guard outputs are in current-boundary-diagnostic.json.

No costs, localisation percentages, full vehicle mass, whole-train sharing, guideway response, propulsion/lift compatibility, force/current transient, cooling, route performance or hardware acceptance is inferred. In particular, this propulsion coupon does not resolve the canonical candidate's failed stationary return-rail/lift support.

## Files and replay

results.json is the latest roll-up. Historical results-prior*.json retain superseded intermediate states; they cannot override the latest failed/refined evidence. raw/ and inputs/ preserve each executed or refused request. prior-failures.json binds the untouched canonical evidence. All runners and completed logs are checksum-bound by manifest.json.
'''
 (OUT/'findings.md').write_text(text)
 (OUT/'reproduction.txt').write_text('''Run from repository root with the exact source_sha256 inventory in manifest.json. All writes remain in ignored build/propulsion-redesign-screen/.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/run.py > build/propulsion-redesign-screen/run.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/refine.py > build/propulsion-redesign-screen/refine.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/final-refine.py > build/propulsion-redesign-screen/final-refine.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/chamfer-refine.py > build/propulsion-redesign-screen/chamfer-refine.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/final-operating.py > build/propulsion-redesign-screen/final-operating.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/boundary-diagnostic.py > build/propulsion-redesign-screen/boundary-diagnostic.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=. tools/automation/osr-python build/propulsion-redesign-screen/archive.py
No production/canonical edits, no adoption, all release flags false.
''')
 files={p.relative_to(OUT).as_posix():sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts}
 flags=dict(design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False,canonical_adoption=False)
 manifest=dict(schema='osr-ignored-propulsion-redesign-receipt/1',source_sha256=result['source_sha256'],files_sha256=files,production_sources_unchanged=True,canonical_configuration_sha256=result['parent_configuration_sha256'],
    latest_result='results.json',findings='findings.md',historical_result_files_superseded=True,executed_coupons=sum(x['state']=='executed' for x in result['rows']),unknown_refused_requests=sum(x['state']!='executed' for x in result['rows']),**flags)
 (OUT/'manifest.json').write_bytes(m.encoded(manifest))
 assert manifest['source_sha256']==m.sources()
 for name,digest in files.items():assert sha256((OUT/name).read_bytes()).hexdigest()==digest
 print(json.dumps(dict(manifest_sha256=sha256((OUT/'manifest.json').read_bytes()).hexdigest(),files=len(files),executed_coupons=manifest['executed_coupons'],unknown_requests=manifest['unknown_refused_requests'],source_unchanged=True)))
