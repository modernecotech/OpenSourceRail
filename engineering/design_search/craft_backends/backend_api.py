"""A bounded common CAD/analysis/delivery interface for civil research.

Provider preference chooses an implementation for an explicit research task.
It does not admit a geometry to a safety evaluator or select a railway baseline.
Other retained tool routes remain registered at their existing specialist APIs.
"""
from copy import deepcopy
from pathlib import Path
from engineering.station_rail.common import identity
from . import native
from .cases import FLAGS

PRODUCER='engineering/design_search/craft_backends/backend_api.py'


class CapabilityHold(ValueError):
    """An unsupported interface is unknown, not a failed physical design."""


def registry():
    providers={
        'solidcraft':dict(role='CAD',operations=['generate','revise','validate_geometry','export'],
            execution='Implemented canonical polygon-prism civil adapter',
            preference='Opt-in preference for this civil research workflow only',
            independent_check='freecad',pin=native.pin('solidcraft')),
        'fieldcraft':dict(role='mechanical-analysis',operations=['prepare','mesh','solve','verify_results'],
            execution='Bounded uncracked isotropic civil fixture; geometry/load/mesh admission required',
            preference='Opt-in experimental numerical comparison',independent_check='calculix',pin=native.pin('fieldcraft')),
        'freecad':dict(role='CAD',operations=['independent_STEP_geometry_check'],
            execution='Retained existing CAD workers and exact reference import',preference='Existing development default'),
        'calculix':dict(role='mechanical-analysis',operations=['independent_solid_solve'],
            execution='Retained source-bound structural workers',preference='Existing structural default'),
        'gmsh_getdp':dict(role='electromagnetics',operations=['existing_specialist_evaluators'],
            execution='Retained; no FieldCraft electromagnetic substitution'),
        'gmsh_opencascade':dict(role='mechanical-meshing',operations=['import_STEP','conformal_tet10_mesh'],
            execution='Retained compiled mesher where direct FieldCraft meshing is unsupported'),
        'ifcopenshell':dict(role='BIM',operations=['existing_IFC_export_and_verification'],
            execution='Retained specialist adapter; not replaced by CAD export'),
        'chrono':dict(role='multibody-dynamics',operations=['existing_specialist_research'],
            execution='Retained; static component comparisons do not replace train dynamics'),
        'sumo':dict(role='transport-operations',operations=['existing_network_simulation'],
            execution='Retained; no CAD/CAE substitution'),
    }
    value=dict(schema='osr-engineering-backend-registry/1',providers=providers,
        default_cad='freecad',default_structural='calculix',
        interfaces_are_not_generic_admission=True,**FLAGS)
    value['registry_id']=identity(value);return value


class CivilCAD:
    provider='solidcraft'

    def generate(self,candidate,output,**kwargs):
        from . import viaduct_cad
        return viaduct_cad.generate(candidate,output,**kwargs)

    def revise(self,candidate,changes,*,reason,root=None):
        from . import viaduct_cases
        root=viaduct_cases.ROOT if root is None else root
        viaduct_cases.validate(candidate,root=root)
        if (not isinstance(changes,dict) or not changes or set(changes)-{'family','profile'}
                or not isinstance(reason,str) or not reason.strip()):
            raise CapabilityHold('This compiler requires a named family/profile revision and reason; arbitrary shapes need another adapter')
        next_case=viaduct_cases.build(changes.get('family',candidate['family']),changes.get('profile',candidate['profile']),root=root)
        if next_case['candidate_id']==candidate['candidate_id']:
            raise ValueError('A physical revision must change the physical candidate')
        record=dict(schema='osr-backend-physical-revision/1',parent_candidate_id=candidate['candidate_id'],
            candidate_id=next_case['candidate_id'],changes=deepcopy(changes),reason=reason,
            physical_selection_changed=False,**FLAGS)
        record['revision_id']=identity(record)
        return dict(candidate=next_case,ancestry=record)

    def validate_geometry(self,candidate,output=None,*,root=None):
        from . import viaduct_cases, viaduct_admission
        root=viaduct_cases.ROOT if root is None else root
        viaduct_cases.validate(candidate,root=root)
        if output is None:
            return dict(candidate_id=candidate['candidate_id'],definition_valid=True,
                native_geometry_checked=False,native_evaluation_admitted=False,**FLAGS)
        return viaduct_admission.verify(output,candidate,root=root)

    def export(self,candidate,output,*,root=None):
        from . import viaduct_admission
        verification=viaduct_admission.verify(output,candidate,root=root)
        import json
        row=json.loads((Path(output)/'manifest.json').read_bytes())['cases'][candidate['case_id']]
        if (row.get('execution')!='completed' or row.get('diagnostic',{}).get('comparison_passed') is not True
                or row.get('exact_step',{}).get('comparison_passed') is not True):
            raise CapabilityHold('Requested case has no passing exact native geometry comparison; retain it as failed/unknown evidence')
        folder=Path(output)/candidate['case_id']/'generate'
        value=dict(schema='osr-backend-CAD-artifacts/1',candidate_id=candidate['candidate_id'],
            component_geometry_id=candidate['component_geometry_id'],
            cad_result_id=verification['source_result_id'],cad_verification_id=verification['verification_id'],
            step_path=str(folder/'assembly.step'),step_sha256=native.digest(folder/'assembly.step'),
            native_path=str(folder/'assembly.sc'),native_sha256=native.digest(folder/'assembly.sc'),
            units=dict(STEP='mm',native_geometry='mm',source='m'),**FLAGS)
        value['artifact_record_id']=identity(value);return value


class CivilAnalysis:
    provider='fieldcraft'

    def prepare(self,candidate,cad_output,load_case='crowd_control',*,root=None):
        from . import viaduct_fem
        artifact=CivilCAD().export(candidate,cad_output,root=root)
        options={} if root is None else dict(root=root)
        return viaduct_fem.prepare(candidate,artifact,load_case,**options)

    def _admit(self,request,root=None):
        from . import viaduct_fem,viaduct_cases,viaduct_admission
        root=viaduct_fem.ROOT if root is None else root
        viaduct_admission._unreleased(request)
        if request.get('input_id')!=identity({k:v for k,v in request.items() if k!='input_id'}):
            raise ValueError('Numerical input seal differs')
        physical=request['physical_definition']
        case=viaduct_cases.build(physical['family'],physical['profile'],root=root)
        if request!=viaduct_fem.prepare(case,request['cad_artifact'],request['load_case']['name'],root=root):
            raise ValueError('Numerical input is not the canonical supported request')

    def mesh(self,request,controls,output,*,root=None,**kwargs):
        from . import viaduct_fem
        self._admit(request,root)
        return viaduct_fem.mesh(request,controls,output,**kwargs)

    def solve(self,request,model,output,*,root=None):
        from . import viaduct_fem,viaduct_admission
        # Check identities before reading files or dispatching any worker.
        viaduct_admission._unreleased(model)
        if model.get('mesh_id')!=identity({k:v for k,v in model.items() if k!='mesh_id'}):
            raise ValueError('Numerical mesh seal differs')
        if any(model.get(k)!=request.get(k) for k in ('candidate_id','component_geometry_id','input_id')):
            raise ValueError('Mixed numerical mesh candidate or input')
        self._admit(request,root)
        return viaduct_fem.solve(request,model,output)

    def verify_results(self,request,output,*,root=None,verification_python=None):
        import json
        from . import viaduct_replay,viaduct_workflow
        root=viaduct_workflow.ROOT if root is None else root
        output=Path(output)
        if request!=json.loads((output/'input.json').read_bytes()):raise ValueError('Requested numerical input differs')
        verification=viaduct_replay.invoke('analysis',output,python=verification_python,root=root)
        result=json.loads((output/'result.json').read_bytes())
        return dict(verification=verification,summary=viaduct_workflow.numerical_summary(result,output))

    def revise_resources(self,request,original_output,output,*,memory_mb=3072):
        from . import viaduct_fem_resource
        return viaduct_fem_resource.revisionrun(request,original_output,output,memory_mb=memory_mb)


class CivilDelivery:
    def _record(self,candidate,context,root):
        from . import viaduct_cases, viaduct_delivery
        root=viaduct_cases.ROOT if root is None else root
        viaduct_cases.validate(candidate,root=root)
        return viaduct_delivery.build(candidate['physical_definition'],context,root=root)

    def calculate_materials(self,candidate,context=None,*,root=None):
        value=self._record(candidate,context,root)
        return dict(nominal_stock=value['nominal_stock'],mass_accounts=value['mass_accounts'],
            candidate_id=value['candidate_id'],delivery_evaluation_id=value['delivery_evaluation_id'])

    def generate_processes(self,candidate,context=None,*,root=None):
        return self._record(candidate,context,root)['process_route']

    def estimate_costs(self,candidate,context=None,*,root=None):
        return self._record(candidate,context,root)['cost']

    def export_business_records(self,candidate,context=None,*,root=None):
        return self._record(candidate,context,root)['business_draft']
