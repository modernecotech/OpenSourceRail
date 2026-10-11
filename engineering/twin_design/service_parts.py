"""Original routed service pieces; no supplier interfaces or ratings inferred."""
from osr_mech.automated_geometry import primitive_volume


def cylinder(identifier, x, y, z, radius, length, *, bore=None):
    p=dict(id=identifier,kind='tube' if bore else 'cylinder',centre_m=[x,y,z],radius_m=radius,length_m=length,axis='x')
    if bore:p['inner_radius_m']=bore
    return p


def install(car, inputs, add, allocated):
    x=car['centre_x_m'];e=inputs['electrical'];p=inputs['service_parts']
    if not 0<p['conductor_radius_m']<p['cable_radius_m']<.02:raise ValueError('invalid cable section')
    if not 0<p['pipe_inner_radius_m']<p['pipe_outer_radius_m']<.03:raise ValueError('invalid pipe section')
    if p['route_length_m']>e['tray_length_m']-.2:raise ValueError('service route exceeds tray')
    for name,y,part in [('hv',e['hv_tray_y_m'],'LM3-HV-P020'),('lv',e['lv_tray_y_m'],'LM3-CTRL-P040')]:
        length=p['route_length_m'];r=p['conductor_radius_m'];R=p['cable_radius_m']
        solids=[cylinder('equivalent-conductor',0,0,0,r,length),cylinder('insulation',0,0,0,R,length,bore=r)]
        mass=primitive_volume(solids[0])*p['conductor_density_kg_m3']+primitive_volume(solids[1])*p['insulation_density_kg_m3']
        ids=[add(car,name+'-routed-harness',part,'routed-equivalent-harness',dict(role='conductor-and-insulation',primitives=solids),
            [x,y,e['tray_z_m']+.025],1.,e['source_ids'],['hv-distribution'],mass=mass)]
        for sign in (-1,1):
            ids.append(add(car,name+'-connector-'+str(sign),part,'keyed-connector-reservation',
                dict(role='connector-reservation',primitives=[dict(id='body',kind='box',centre_m=[0,0,0],dimensions_m=[.06,.025,.025])]),
                [x+sign*(length/2+.035),y,e['tray_z_m']+.025],p['connector_density_kg_m3'],['harting-rail-guide'],['hv-distribution']))
        allocated[part][-1].extend(ids)
    ids=[];length=p['route_length_m'];R=p['pipe_outer_radius_m'];r=p['pipe_inner_radius_m']
    for sign in (-1,1):
        spec=dict(role='isolated-coolant-line',primitives=[cylinder('pipe-wall',0,0,0,R,length,bore=r)])
        ids.append(add(car,'coolant-line-'+str(sign),'LM3-HV-P030','coolant-pipe-wall',spec,
            [x,sign*.24,.98],p['pipe_density_kg_m3'],['liebherr-modules'],['batteries','hvac']))
        for end in (-1,1):
            spec=dict(role='replaceable-pipe-clamp',primitives=[cylinder('clamp',0,0,0,R+.004,.025,bore=R+.0005)])
            ids.append(add(car,f'coolant-clamp-{sign}-{end}','LM3-HV-P030','insulated-pipe-clamp',spec,
                [x+end*3.5,sign*.24,.98],p['clamp_density_kg_m3'],['liebherr-modules'],['batteries','hvac']))
    allocated.setdefault('LM3-HV-P030',[]).append(ids)
    d=inputs['doors'];ids=[];t=p['seal_section_m'];half=d['opening_width_m']/2+.06;top=d['opening_height_m']/2+.08;bottom=-d['opening_height_m']/2
    for side in (-1,1):
        for direction in (-1,1):
            spec=dict(role='replaceable-perimeter-weather-seal',primitives=[
                dict(id='top',kind='box',centre_m=[0,0,top],dimensions_m=[2*half+t,t,t]),
                dict(id='bottom',kind='box',centre_m=[0,0,bottom],dimensions_m=[2*half+t,t,t]),
                *[dict(id='side-'+str(sign),kind='box',centre_m=[sign*half,0,(top+bottom)/2],dimensions_m=[t,t,top-bottom-t]) for sign in (-1,1)]])
            ids.append(add(car,f'door-seal-{side}-{direction}','LM3-DOOR-P010','replaceable-weather-seal',spec,
                [x+direction*car['length_m']*d['longitudinal_fraction'],side*(d['lateral_m']+.09),d['centre_z_m']],
                p['seal_density_kg_m3'],['knorr-doors'],['doors','maintenance']))
    for group,identifier in zip(allocated['LM3-DOOR-P010'][-4:],ids):group.append(identifier)
