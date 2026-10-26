"""Load the explicit selection; never fall back silently to a legacy model."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import tomllib
from . import ROOT,INPUT,FLAGS

def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return sha256(encoded(v)).hexdigest()

def load(root=ROOT):
    root=Path(root).resolve();raw=(root/INPUT).read_bytes();v=tomllib.loads(raw.decode())
    if v.get('schema')!='osr-development-baseline-selection/1' or v.get('selected_for_development') is not True:
        raise ValueError('Explicit selected development baseline required')
    if v.get('family')!='comfort-ndfeb-station-powered':raise ValueError('Unsupported selected family')
    if any(v['acceptance'].get(k) is not val for k,val in FLAGS.items()):raise ValueError('Selection cannot grant qualification')
    manifest_path=root/v['source_manifest'];manifest=json.loads(manifest_path.read_bytes())
    if sha256(manifest_path.read_bytes()).hexdigest()!=v['source_manifest_sha256']:raise ValueError('Selected source publication changed')
    path=root/v['source_design']
    if sha256(path.read_bytes()).hexdigest()!=manifest['files_sha256'][path.name]:raise ValueError('Selected source design payload differs')
    source=json.loads(gzip.decompress(path.read_bytes()));car=source['vehicle']
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):
        expected=v['vehicle_candidate_id'] if key=='candidate_id' else v[key]
        if car[key]!=expected:raise ValueError('Selected physical '+key+' differs')
    network=next((r for r in source['whole_system_alternatives']['proposals'] if r['proposal_id']==v['network_proposal_id']),None)
    if network is None or network['launch_speed_m_s']!=v['service']['launch_speed_cap_m_s'] or network['maximum_station_spacing_m'] is not None:
        raise ValueError('Selected retained-stop network proposal differs')
    if (v['vehicle']['cars'],v['vehicle']['normal_passengers_per_car'],v['service']['headway_s'])!=(6,46,120.):
        raise ValueError('Default formation/capacity/headway contract differs')
    capacity=6*46*3600/120
    if v['service']['normal_capacity_pphpd_arithmetic']!=capacity:raise ValueError('Capacity arithmetic differs')
    bindings={INPUT:sha256(raw).hexdigest(),v['source_manifest']:sha256(manifest_path.read_bytes()).hexdigest(),
              v['source_design']:sha256(path.read_bytes()).hexdigest()}
    return dict(schema='osr-development-baseline/1',selection_id=identity(v),selection=v,
        vehicle=deepcopy(car),network_proposal=deepcopy(network),
        development_default=True,source_sha256=bindings,**FLAGS)
