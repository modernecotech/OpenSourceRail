"""Independent system screens on retained, verified actuator observations."""
import math

ACTUAL_MODULE_UPWARD_LIMIT_N = 20_000.0


def actual_module_force(run):
    """A requested-force clamp cannot establish the actual-force envelope.

    The declared study limit equals the retained allocator's request ceiling.
    It is conservative bookkeeping for this experiment, not a qualified joint,
    magnet attachment or guidebeam resistance.
    """
    peak=run.get('extrema',{}).get('peak_module_force_n')
    known=type(peak) in (int,float) and math.isfinite(peak) and peak>=0
    passed=known and peak<=ACTUAL_MODULE_UPWARD_LIMIT_N
    return dict(state='passed' if passed else 'failed' if known else 'hold',
                passed=bool(passed),observed_peak_n=peak if known else None,
                limit_n=ACTUAL_MODULE_UPWARD_LIMIT_N,
                scope='Actual simulated upward module force;20kN declared study bound. Independent structural and attachment qualification remains open.')
