"""Same-model finer motor samples; explicitly below independent-domain confirmation."""
from pathlib import Path
from . import contracts as k,wheel_families,wheel_motor


def confirm(candidate,request,primary):
    car=wheel_families.materialize(candidate);params=wheel_families._parameters(candidate)
    native=primary['diagnostics'][0]['native'];required=native['required_force_N']
    fine=wheel_motor.evaluate(params['motor'],required,Path.cwd()/'native-refinement',confirmation=True)
    changes=[]
    for a,b in zip(native['cases'],fine['cases']):
        if 'metrics' not in a or 'metrics' not in b:continue
        changes.append(dict(speed_m_s=a['case']['speed_m_s'],force_relative_change=abs(b['metrics']['force_N']-a['metrics']['force_N'])/max(1.,abs(b['metrics']['force_N'])),
            peak_field_relative_change=abs(b['metrics']['maximum_steel_phasor_B_bound_T']-a['metrics']['maximum_steel_phasor_B_bound_T'])/max(.01,abs(b['metrics']['maximum_steel_phasor_B_bound_T']))))
    numerical=len(changes)==len(native['cases']) and all(c['force_relative_change']<.02 and c['peak_field_relative_change']<.05 for c in changes)
    domain=all(r.get('model_domain')=='within_linear_hypothesis' for r in fine['cases'])
    return k.make_result(request,execution_status='executed',numerical_status='converged' if numerical else 'nonconverged',
        screen_status='pass' if numerical and domain else 'fail',maturity='numerical-screen',
        metrics=dict(original_screen_status=primary['screen_status'],same_model_refinement_pass=numerical),
        constraints=[dict(id='same-model-field-and-force-refinement',state='pass' if numerical else 'fail'),dict(id='linear-material-domain',state='pass' if domain else 'fail')],
        diagnostics=[dict(scope='Same-model mesh comparison; not cross-solver, prototype or independent-domain qualification',changes=changes,native=fine)])
