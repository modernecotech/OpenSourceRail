# Full-train contact-domain verification

[Original six-car evidence](../../engineering/civil_exploration/examples/automated-parts-evidence.json)
· [independent profile replay](../../engineering/civil_exploration/examples/fulltrain-profile-domain-349cf69d.json)
· [original parts review provenance](../../engineering/civil_exploration/examples/automated-parts-history.json)
· [current parts compiler review](../../engineering/civil_exploration/examples/automated-parts-current-review.json)
· [timestep and guarded-run comparison](../../engineering/civil_exploration/examples/fulltrain-contact-domain-comparison.json)
· [current native/service evidence](../../engineering/civil_exploration/examples/automated-parts-current-evidence.json).

The first six-car run reported nonlinear non-convergence at 9.775 s. Independent
replay shows that the supplied wheel profile was already insufficient for the
computed contact footprint at **9.130 s**. A smaller timestep cannot establish
profile validity by itself, even if Newton iterations converge.

The affected contact is `train-A / car-6/bogie-2/axle-1 / side -1`. At the first
footprint exceedance:

| Quantity | Retained value |
|---|---:|
| Normal force | 43,776.549 N |
| Wheel contact coordinate | 56.064200 mm |
| Distance to supplied wheel-profile boundary | 3.935800 mm |
| Hertz lateral semi-axis | 3.944283 mm |
| Footprint beyond the declared boundary | 0.008483 mm |

The contact centre was inside the supplied table while part of its ellipse lay
outside it. Checking only the minimum-gap point therefore missed the first
domain violation. The original history contains 119 positive-load samples with
unsupported footprints. Subsequent reference-location substitution introduces
a discontinuous contact response; no forces beyond the supported footprint
are qualified by that history.

## Changed solver contract

The spatial adapter compares the full lateral semi-axis with both wheel and
rail profile margins. Using the full semi-axis in horizontal profile coordinates
is conservative for an inclined local tangent plane. This is a numerical domain
check, not an ISO resistance, derailment or wheel-profile acceptance criterion.

A Newton trial may temporarily use the reference tangent after an unsupported
profile lookup. The converged state must pass the actual profile, footprint,
joint-motion, patch-size and small-angle checks before any contact state is
committed or history sample emitted. An invalid converged state raises
`SpatialDomainError`; it is retained as `outside-model-domain` by the service
runner. Non-convergence remains a separate failure with residual, iteration
count and any final-trial domain violations.

The change prevents a substituted reference patch from entering a supposedly
valid history. It does not extend measured or supplied geometry, introduce an
unqualified flange model, or make the original train a qualified operating design.

## Reproduce the independent replay

```sh
tools/automation/osr-python tools/automation/audit-contact-profile-domain.py \
  --campaign build/engineering/reference-full-train-passage \
  --revision 349cf69d3cc0607924ac6671a59b7f851eff9395 \
  --output build/engineering/my-profile-domain-audit.json
```

The reader validates every retained campaign output hash and the recorded
solver sources against the producing commit, checks wheel identity/completeness
and ordered timestamps, then recomputes profile margins from the saved contact
coordinates and ellipse. It reports the first/worst unsupported footprint.
It does not infer a complete passage from a partial history or requalify the
old numerical environment. Reference-location fallback cannot be identified
unambiguously from the old coordinate fields alone.

Use the current service runner to generate fresh domain-checked evidence:

```sh
tools/automation/osr-python tools/automation/shared-service-envelope.py run \
  --model build/engineering/reference-parts-profile-guard/model.json \
  --config build/engineering/reference-parts-profile-guard/spatial_configuration.json \
  --output build/engineering/my-domain-checked-passage --cases empty-15mps
```

The original parts review and failed campaign remain bound to commit
`349cf69d3cc0607924ac6671a59b7f851eff9395`. The current compiler review is a separate
artifact; its source hashes do not rewrite the historical evidence.

## Required next physics evidence

Complete operating cases require supported new/worn wheel and rail profiles,
qualified treatment when flange or multiple contact occurs, and defensible
running-gear suspension/creep parameters. The current synthetic conicity,
bristle friction and equivalent suspension laws cannot supply that qualification.
Profile-domain rejection must remain an explicit constraint in optimisation and
calibration. Full-passage temporal/spatial convergence, railway acceptance and
physical holdouts remain open until the operating states stay inside a supported
contact domain or are assessed by an appropriately verified extended adapter.

## Fresh verification outcome

The preserved implementation was rerun with `dt=0.0025 s`, retaining the same
two deck elements per span and 2 m rail spacing. Its first unsupported footprint
also occurs at **9.130 s**; its later Newton failure occurs at 9.6775 s. The
normal force at the first boundary differs from the coarse replay by approximately
0.00376%. This diagnoses a profile-domain limit; it is not a complete-passage
time/mesh convergence result.

The retained pre-correction guarded run stops at **9.130 s** with `outside-model-domain` and
retains the last supported sample at **9.125 s**. Independent replay checks
**87,600 contacts across 1,825 supported samples**, with no unsupported footprint
in the committed history. The failed state is retained separately in the case
diagnostic. All three campaign receipts and the producing sources for the
archived timestep probe were checked before publication.

The focused suite passes **124 tests**, including contact-centre/ellipse boundary
cases, rejection before contact-state commitment, corrupt-history rejection,
service failure classification and retained-proof hash checks. No complete
six-car service passage or physical qualification is claimed.


## Steering correction and retained passage comparisons — 11 October 2026

The lateral rolling-reference velocity previously omitted steady wheel yaw.
The current small-rotation model projects body steering into the rolling direction,
while excluding the wheel spin coordinate. Independent rotation and Jacobian
checks exercise that term. The finite profile, patch-footprint, contact opening
and multiple-patch guards remain active.

With that correction, the 192-instance reference six-car train completed its
13.06 s passage at 15 m/s. The expanded 414-instance design also completed the
same passage. A cylindrical-profile verification benchmark completed separately;
it is not a supplier profile. Experimental convected-bristle runs still leave the
finite profile domain and are retained as rejected research cases.

Halving the reference time step from 0.005 to 0.0025 s changed maximum wheel
force from 44,123.906 to 44,128.648 N. Refining deck mesh 2 to 4 and rail step
2 to 1 m at the smaller time step changed peak carbody acceleration from
0.351569 to 0.247309 m/s². This substantial spatial change prevents a convergence
claim. Finer meshes and the broader load/speed/degradation matrix are separate
retained runs. Approved profiles, creep-law comparisons, suspension data and
physical contact/ride correlation are still required.
