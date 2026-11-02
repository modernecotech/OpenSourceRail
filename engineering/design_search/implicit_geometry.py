"""Bounded implicit gyroid-sheet research geometry, not an engineering design.

The smooth field is sampled at voxel centres. Binary VTK contains the exact
occupied cubes of that sampling, not a triangulated implicit surface, a CAD
solid, or proof of manufacturability. No physical railway is selected.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite, pi, prod
from pathlib import Path
import platform
import re

import numpy as np

from engineering.station_rail.common import digest, encoded, identity

PRODUCER = 'engineering/design_search/implicit_geometry.py'
MAX_VOXELS = 1_000_000
MAX_AXIS = 256
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, configuration_adopted=False)
ALLOWANCES = ('skin', 'interfaces_and_attachments', 'installation_and_protection')
HOLDS = ('Implicit surface and true minimum wall thickness unresolved by voxel centres',
         'Skin, interfaces, attachment, service access and installed mass unresolved or bounded separately',
         'Material grade and strength, manufacturing process, waste and inspection unresolved',
         'Load paths, torsion, buckling, fatigue, joints, fire and physical qualification unresolved',
         'No complete installed cost, station interface, site design or railway selection')
ENVIRONMENT_SCOPE = 'Observed runtime; exact replay still requires matching sampled bytes'


def _number(value, name, low, high):
    if type(value) not in (float, int) or not isfinite(value) or not low <= value <= high:
        raise ValueError('Finite bounded '+name+' required')
    return float(value)


def _triple(value, name, low, high):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError('Three '+name+' values required')
    return [_number(v, name, low, high) for v in value]


def _sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _material(value):
    if not isinstance(value, str) or re.fullmatch('[a-z][a-z0-9_-]{0,63}', value) is None:
        raise ValueError('Explicit material family identifier required')
    return value


def _physical(envelope_m, period_m, threshold, phase_rad, material_family):
    envelope = _triple(envelope_m, 'envelope (m)', .01, 20.)
    period = _number(period_m, 'period (m)', .005, 10.)
    if period > max(envelope)*4:
        raise ValueError('Period exceeds the bounded research envelope')
    return dict(schema='osr-implicit-gyroid-physical/1', kind='gyroid-sheet',
        equation='abs(sin(X)*cos(Y)+sin(Y)*cos(Z)+sin(Z)*cos(X)) <= threshold; X=2*pi*x/period+phase_x, likewise Y,Z',
        envelope_m=envelope, origin_m=[0., 0., 0.], period_m=period,
        threshold=_number(threshold, 'dimensionless threshold', .001, 3.),
        phase_rad=_triple(phase_rad, 'phase (rad)', -2*pi, 2*pi),
        material_family=_material(material_family),
        skin_interfaces_and_attachments_included=False)


def generate(envelope_m, period_m, threshold, *, material_family,
             phase_rad=(0., 0., 0.), parent_candidate_id=None):
    """Define an implicit volume. Grid and density are not physical identity."""
    if parent_candidate_id is not None and not _sha(parent_candidate_id):
        raise ValueError('Parent physical candidate identity must be SHA256 or absent')
    physical = _physical(envelope_m, period_m, threshold, phase_rad, material_family)
    result = dict(schema='osr-implicit-candidate/1', physical_definition=physical,
        candidate_id=identity(physical), parent_candidate_id=parent_candidate_id,
        declared_scope='Detached component research; not a complete beam or railway', **FLAGS)
    result['definition_id'] = identity(result)
    return result


def _candidate(value):
    if not isinstance(value, dict) or set(value) != {'schema','physical_definition','candidate_id',
            'parent_candidate_id','declared_scope','definition_id',*FLAGS}:
        raise ValueError('Exact implicit candidate required')
    if value['schema'] != 'osr-implicit-candidate/1' or any(value[k] is not False for k in FLAGS):
        raise ValueError('Research candidate cannot grant acceptance or selection')
    if value['definition_id'] != identity({k:v for k,v in value.items() if k != 'definition_id'}):
        raise ValueError('Candidate definition identity differs')
    p=value['physical_definition']
    if (not isinstance(p, dict) or set(p) != {'schema','kind','equation','envelope_m','origin_m','period_m',
            'threshold','phase_rad','material_family','skin_interfaces_and_attachments_included'}
            or p != _physical(p['envelope_m'], p['period_m'], p['threshold'], p['phase_rad'], p['material_family'])):
        raise ValueError('Implicit physical definition differs')
    if value['candidate_id'] != identity(p) or (value['parent_candidate_id'] is not None and not _sha(value['parent_candidate_id'])):
        raise ValueError('Candidate physical identity or ancestry differs')
    if value['declared_scope'] != 'Detached component research; not a complete beam or railway':
        raise ValueError('Research scope differs')
    return p


def _allowances(value):
    if value is None:
        return {key: None for key in ALLOWANCES}
    if not isinstance(value, dict) or set(value) != set(ALLOWANCES):
        raise ValueError('Each installation allowance must be unknown or positively bounded')
    result={}
    for key, bounds in value.items():
        if bounds is None:
            result[key]=None
            continue
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            raise ValueError('Allowances require low/high mass bounds or unknown')
        low=_number(bounds[0], 'allowance lower mass', .000001, 1e9)
        high=_number(bounds[1], 'allowance upper mass', low, 1e9)
        result[key]=[low,high]
    return result


def _grid(value):
    if (not isinstance(value,(list,tuple)) or len(value)!=3
            or any(type(n) is not int or not 2 <= n <= MAX_AXIS for n in value)
            or prod(value)>MAX_VOXELS):
        raise ValueError('Bounded three-axis integer voxel grid required')
    return list(value)


def _vtk_header(divisions, spacing):
    nx,ny,nz=divisions
    def n(x):return format(x,'.17g')
    return ('# vtk DataFile Version 3.0\nOpenSourceRail implicit centre-sampled research occupancy\n'
        'BINARY\nDATASET STRUCTURED_POINTS\n'
        f'DIMENSIONS {nx+1} {ny+1} {nz+1}\nORIGIN 0 0 0\n'
        f'SPACING {n(spacing[0])} {n(spacing[1])} {n(spacing[2])}\n'
        f'CELL_DATA {nx*ny*nz}\nSCALARS solid unsigned_char 1\nLOOKUP_TABLE default\n').encode('ascii')


def _environment():
    return dict(numpy=np.__version__,python=platform.python_version(),
        machine=platform.machine(),arithmetic='float64',scope=ENVIRONMENT_SCOPE)


def _recorded_environment(value):
    """Validate the sealed claimed environment, without attesting to its truth."""
    if not isinstance(value,dict) or set(value)!={'numpy','python','machine','arithmetic','scope'}:
        raise ValueError('Exact recorded numerical environment schema required')
    version=r'[0-9]+(?:\.[0-9]+){1,3}[A-Za-z0-9.+_-]{0,64}'
    if (not isinstance(value['numpy'],str) or re.fullmatch(version,value['numpy']) is None
            or not isinstance(value['python'],str) or re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.+_-]{0,64}',value['python']) is None
            or not isinstance(value['machine'],str) or re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',value['machine']) is None
            or value['arithmetic']!='float64' or value['scope']!=ENVIRONMENT_SCOPE):
        raise ValueError('Invalid recorded numerical environment')


def sample(candidate, divisions, *, density_kg_m3, minimum_feature_m,
           allowance_mass_kg=None):
    """Return source-bound voxel quantities and binary legacy VTK image data.

    VTK cell i,j,k uses x as its fastest index. The centre rule exactly
    specifies each occupied prism; a coarse occupancy is not exact implicit
    geometry. A Lipschitz-based interval bounds ideal continuous-field volume
    under exact arithmetic; it is not a structural or physical tolerance.
    """
    p=_candidate(candidate);dims=_grid(divisions)
    density=_number(density_kg_m3, 'material density (kg/m3)', .001, 100000.)
    feature=_number(minimum_feature_m, 'requested minimum feature (m)', .000001, min(p['envelope_m']))
    allowances=_allowances(allowance_mass_kg)
    spacing=[p['envelope_m'][i]/dims[i] for i in range(3)]
    if any(p['period_m']/h < 8-1e-12 for h in spacing):
        raise ValueError('At least eight voxel intervals per implicit period on every axis required')
    if any(feature/h < 3-1e-12 for h in spacing):
        raise ValueError('At least three voxel intervals per requested minimum feature on every axis required')
    k=2*pi/p['period_m']
    axes=[(np.arange(n,dtype=np.float64)+.5)*spacing[i]*k+p['phase_rad'][i] for i,n in enumerate(dims)]
    x,y,z=np.meshgrid(*axes,indexing='ij',sparse=True)
    field=np.sin(x)*np.cos(y)+np.sin(y)*np.cos(z)+np.sin(z)*np.cos(x)
    magnitude=np.abs(field);threshold=p['threshold']
    solid=magnitude<=threshold
    # Each dimensionless partial derivative is at most 2. Within a cell,
    # the centre-to-corner coordinate distances sum to half the spacings.
    field_variation=k*sum(spacing)
    definitely=magnitude+field_variation<=threshold
    possibly=magnitude-field_variation<=threshold
    data=solid.astype(np.uint8).tobytes(order='F')
    vtk=_vtk_header(dims,spacing)+data+b'\n'
    voxel_volume=prod(spacing);envelope_volume=prod(p['envelope_m'])
    count=int(np.count_nonzero(solid));low_count=int(np.count_nonzero(definitely));high_count=int(np.count_nonzero(possibly))
    sample_volume=count*voxel_volume
    result=dict(schema='osr-implicit-voxel-evaluation/1', candidate_id=candidate['candidate_id'],
        definition_id=candidate['definition_id'], source_sha256={PRODUCER:digest(Path(__file__)),
            'engineering/station_rail/common.py':digest(Path(__file__).resolve().parents[1]/'station_rail/common.py')},
        numerical_environment=_environment(),
        sampling=dict(method='centre sample; x-fastest VTK cell order',divisions=dims,origin_m=[0.,0.,0.],
            spacing_m=spacing,period_intervals_per_axis=[p['period_m']/h for h in spacing],
            requested_minimum_feature_m=feature,minimum_feature_intervals_per_axis=[feature/h for h in spacing],
            requested_feature_physically_proved=False,voxel_count=prod(dims)),
        material=dict(family=p['material_family'],density_kg_m3=density,density_is_assumption=True),
        geometry=dict(occupied_voxel_count=count,voxel_volume_m3=voxel_volume,
            envelope_volume_m3=envelope_volume,sampled_solid_volume_m3=sample_volume,
            sampled_solid_mass_kg=sample_volume*density,occupancy_sha256=sha256(data).hexdigest(),
            vtk_sha256=sha256(vtk).hexdigest(),
            ideal_arithmetic_implicit_volume_interval_m3=[low_count*voxel_volume,high_count*voxel_volume],
            ideal_arithmetic_field_variation_bound=field_variation,
            floating_point_roundoff_guaranteed=False,
            implicit_volume_interval_scope='Lipschitz enclosure under ideal exact arithmetic only; floating-point roundoff is not bounded',
            continuous_surface_qualified=False,physical_geometry_and_tolerance_qualified=False),
        allowance_mass_kg=allowances,complete_installed_mass_kg=None,complete_installed_cost=None,
        engineering_screen='unknown',manufacturing_process_qualified=False,
        evidence_maturity='calculated-voxel-research',holds=list(HOLDS),**FLAGS)
    result['evaluation_id']=identity(result)
    return result,vtk


def verify(candidate, result, vtk, *, expected_evaluation_id):
    """Replay exact content while retaining a separately bound original runtime.

    The caller must provide the original evaluation ID from a trusted external
    reference. Hashes cannot attest the actual runtime if an attacker controls
    both the record and its expected ID. This is analytical reproduction, not
    native-evaluator reuse or independent physical evidence.
    """
    if (not _sha(expected_evaluation_id) or not isinstance(result,dict)
            or result.get('evaluation_id') != expected_evaluation_id
            or expected_evaluation_id != identity({k:v for k,v in result.items() if k!='evaluation_id'})):
        raise ValueError('Externally expected evaluation identity differs')
    try:
        recorded_environment=result['numerical_environment']
        _recorded_environment(recorded_environment)
        sampling=result['sampling'];material=result['material']
        actual, payload=sample(candidate,sampling['divisions'],density_kg_m3=material['density_kg_m3'],
            minimum_feature_m=sampling['requested_minimum_feature_m'],allowance_mass_kg=result['allowance_mass_kg'])
        excluded=('numerical_environment','evaluation_id')
        original_content={k:v for k,v in result.items() if k not in excluded}
        replay_content={k:v for k,v in actual.items() if k not in excluded}
        if encoded(original_content)!=encoded(replay_content) or not isinstance(vtk,bytes) or vtk!=payload:
            raise ValueError('Voxel source, candidate, derived fields or payload differs')
    except (KeyError,TypeError) as error:
        raise ValueError('Malformed voxel evaluation record') from error
    return dict(verified=True,evaluation_id=expected_evaluation_id,replay_evaluation_id=actual['evaluation_id'],
        candidate_id=actual['candidate_id'],recorded_environment=deepcopy(recorded_environment),
        replay_environment=actual['numerical_environment'],environments_identical=recorded_environment==actual['numerical_environment'],
        expected_identity_from_caller=True,recorded_environment_independently_attested=False,native_evaluator_reuse=False,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,
        selected_reference_changed=False,configuration_adopted=False)
