"""Replay two archived coupons in a reconstructed temporary original source tree."""
from hashlib import sha256
from pathlib import Path
import json,platform,sys
import numpy as np
import scipy
import run as original


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def main(archive):
    archive=Path(archive);rows=[]
    names=('resolved8mm-256-cold','resolved8mm-256-40')
    jobs=[]
    for name in names:
        expected=json.loads((archive/'executed/raw'/f'{name}.json').read_bytes())
        input_values=json.loads((archive/'executed/inputs'/f'{name}.json').read_bytes())
        if original.apply(expected['changes'])!=input_values:raise ValueError('archived actual changed input differs from original source plus declared changes')
        jobs.append(dict(id=name,changes=expected['changes'],**expected['grid']))
    fresh=original.batch(jobs)
    for actual in fresh:
        expected=json.loads((archive/'executed/raw'/f"{actual['id']}.json").read_bytes())
        # Geometry-volume annotation was added after the original coupon ran;
        # archive verify independently recalculates it from actual dimensions.
        expected.pop('physical_corner_alternative',None)
        expected.pop('elapsed_host_s');observed=dict(actual);observed.pop('elapsed_host_s')
        if expected!=observed:raise ValueError('exact selected numerical replay differs: '+actual['id'])
        rows.append(dict(id=actual['id'],coupon_sha256=sha256(canonical(actual['coupon'])).hexdigest(),
            complete_coupon_and_identity_exact_match=True,converged=actual['coupon']['converged'],
            margin_after_declared_current_bound_a_m=actual['demag_margin_after_declared_current_bound_a_m'],
            hypothesis_sha256=actual['hypothesis_sha256']))
    parent=original.m.definition()
    answer=dict(schema='osr-propulsion-selected-replay/1',source_sha256=original.m.sources(),parent_configuration_sha256=parent['configuration_sha256'],
        current_candidate_aw3_mass_kg_per_car=parent['mass_properties']['mass_kg'],cases=sorted(rows,key=lambda x:x['id']),
        ignored_elapsed_host_s_only=True,post_execution_geometry_annotation_independently_verified=True,
        python_version=platform.python_version(),numpy_version=np.__version__,scipy_version=scipy.__version__,
        design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False,configuration_adopted=False)
    original.write('replay-selected-results.json',answer)


if __name__=='__main__':main(sys.argv[1])
