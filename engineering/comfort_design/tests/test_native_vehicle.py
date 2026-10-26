import json
from pathlib import Path
import pytest

from engineering.comfort_design import native_vehicle as n


def test_native_aggregate_uses_parallel_axis_not_a_uniform_equipment_box():
    boxes=[dict(id=str(i),mass_kg=1.,volume_m3=1.,cg_m=[x,0.,0.],
                inertia_kg_m2=[[1/6,0,0],[0,1/6,0],[0,0,1/6]]) for i,x in enumerate((-2.,2.))]
    result=n._aggregate(boxes)
    assert result['mass_kg']==2 and result['cg_m']==[0,0,0]
    assert result['inertia_kg_m2'][0][0]==pytest.approx(1/3)
    assert result['inertia_kg_m2'][1][1]==pytest.approx(8+1/3)


def test_verifier_refuses_another_vehicle_before_using_native_receipt(tmp_path):
    (tmp_path/'manifest.json').write_text(json.dumps(dict(candidate_id='other',body_candidate_id='other')))
    with pytest.raises(ValueError,match='another candidate'):
        n.verify_export(tmp_path,dict(candidate_id='expected',body_candidate_id='body'))


def test_native_groups_keep_different_material_densities_separate():
    assert n._group(dict(id='module/03/copper',density_kg_m3=8960.))!=n._group(dict(id='module/03/magnet',density_kg_m3=7600.))
    assert n._group(dict(id='module/03/a',density_kg_m3=7600.))!=n._group(dict(id='module/04/a',density_kg_m3=7600.))


def test_compound_properties_are_integrated_from_reopened_solids():
    class Matrix:
        def __getattr__(self,name):return 1e15/6 if name in ('A11','A22','A33') else 0.
    class Solid:
        Volume=1e9
        MatrixOfInertia=Matrix()
        def __init__(self,x):self.CenterOfMass=(x,0.,0.)
    class Compound:
        Solids=[Solid(-2000.),Solid(2000.)]
        # Deliberately no CenterOfMass or MatrixOfInertia on the compound.
    result=n._native_properties(Compound(),1.)
    assert result['mass_kg']==pytest.approx(2.)
    assert result['cg_m']==pytest.approx([0.,0.,0.])
    assert result['inertia_kg_m2'][1][1]==pytest.approx(8+1/3)
