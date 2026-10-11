"""Serial-bound condition observations with independent installed/design identity."""
from copy import deepcopy
from engineering.industrialisation.common import artifact,finite,fingerprint,timestamp

DOMAINS={'wheel-radius':('m','wheel-contact'),'spring-stiffness':('N/m','suspension'),'bearing-stiffness':('N/m','civil-support'),'battery-capacity':('Ah','battery-duty'),'battery-resistance':('ohm','battery-duty'),'civil-crack-width':('m','civil-resistance')}


def bind(installed, observation, calibration,*,root):
    if observation['serial']!=installed['serial'] or observation['manufactured_revision']!=installed['manufactured_revision'] or observation['configuration_sha256']!=installed['configuration_sha256']:raise ValueError('observation targets another installed serial/revision/configuration')
    name=observation['quantity']
    if name not in DOMAINS or observation['unit']!=DOMAINS[name][0] or calibration['unit']!=observation['unit']:raise ValueError('condition/calibration quantity or unit mismatch')
    if observation['instrument_serial']!=calibration['instrument_serial'] or name!=calibration['quantity']:raise ValueError('calibration instrument or quantity mismatch')
    t=timestamp(observation['measured_at'])
    if not timestamp(calibration['valid_from'])<=t<=timestamp(calibration['valid_until']):raise ValueError('measurement outside calibration validity')
    finite(observation['value'],'condition value',0.);finite(observation['uncertainty'],'condition uncertainty',0.)
    uncertainty=finite(calibration['uncertainty'],'calibration uncertainty',0.)
    lo=finite(calibration['minimum'],'calibrated minimum');hi=finite(calibration['maximum'],'calibrated maximum')
    if not lo<hi or not lo<=observation['value']<=hi:raise ValueError('condition observation outside calibrated instrument range')
    if observation['uncertainty']<uncertainty:raise ValueError('observation understates calibration uncertainty')
    artifact(observation['evidence'],root,kind='measurement');artifact(calibration['evidence'],root,kind='calibration')
    result=deepcopy(installed);previous=result.get('condition',{});prior=previous.get(name)
    if prior and timestamp(prior['measured_at'])>=t:raise ValueError('condition observation is not newer')
    previous[name]=deepcopy(observation);result['condition']=previous;result['condition_revision_sha256']=fingerprint(previous)
    result['invalidated_analysis_domains']=sorted({DOMAINS[q][1] for q in previous})
    result['analysis_reexecution_required']=True;result['physical_correlation_accepted']=False
    return result
