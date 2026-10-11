"""Independent replay of retained contact footprints against supplied profiles."""
from __future__ import annotations
import gzip
import math
from pathlib import Path
from engineering.civil_exploration.wheel_contact import ProfilePair,profile_footprint
from osr_mech.engineering_definition import load_definition,fingerprint


def audit_history(model,configuration,path):
    contact=configuration['contact']
    profiles={side:ProfilePair(contact['wheel_profiles'][str(side)],contact['rail_profile'],
        contact['rolling_radius_m'],contact['effective_modulus_pa']) for side in (-1,1)}
    wheelsets={(r['bogie'],r['axle']) for r in model['instances'] if r['axle'] is not None}
    expected={(e['id'],f'{bogie}/axle-{axle}',side) for e in configuration['traffic'] for bogie,axle in wheelsets for side in (-1,1)}
    samples=checks=exceeded=0;first=None;last=None;worst=None;previous=-math.inf;affected=set()
    import json
    with gzip.open(path,'rt') as stream:
        for line in stream:
            sample=json.loads(line);t=sample['time_s']
            if type(t) not in (int,float) or not math.isfinite(t) or t<=previous:
                raise ValueError('strictly increasing finite contact history times required')
            previous=t;last=t;observed=set()
            for row in sample['contacts']:
                identity=(row['train'],row['wheelset'],row['side'])
                if identity not in expected or identity in observed:raise ValueError('unknown or duplicate wheel contact identity')
                observed.add(identity)
                N=row['normal_n']
                if type(N) not in (int,float) or not math.isfinite(N) or N<0:raise ValueError('finite nonnegative normal force required')
                p=profiles[row['side']];footprint=profile_footprint(row,row['patch'],p.wheel_range,p.rail_range)
                checks+=1
                if N>0 and not footprint['inside_supplied_profiles']:
                    exceeded+=1;affected.add(identity)
                    item=dict(time_s=t,train=row['train'],wheelset=row['wheelset'],side=row['side'],normal_n=N,
                        contact_y_m=row['contact_y_m'],wheel_y_m=row['wheel_y_m'],**footprint)
                    if first is None:first=item
                    if worst is None or item['minimum_clearance_m']<worst['minimum_clearance_m']:worst=item
            if observed!=expected:raise ValueError('every expected wheel contact must appear in every sample')
            samples+=1
    if not samples:raise ValueError('nonempty retained contact history required')
    return dict(schema='osr-contact-profile-domain-audit/1',hardware_definition_sha256=fingerprint(model),
        configuration_sha256=fingerprint(configuration),sample_count=samples,contact_check_count=checks,
        last_retained_time_s=last,footprint_exceedance_count=exceeded,first_footprint_exceedance=first,worst_footprint_exceedance=worst,
        affected_contacts=[dict(train=t,wheelset=w,side=s) for t,w,s in sorted(affected)],
        all_retained_footprints_inside_supplied_profiles=exceeded==0,
        complete_passage_verified=False,physical_validation=False,engineering_released=False,
        limitations=['replay checks the saved nominal contact coordinates and Hertz ellipse',
            'a reference-location fallback cannot be identified unambiguously from old coordinates alone',
            'no flange, multiple patch, rail-roll or measured-profile qualification'])
