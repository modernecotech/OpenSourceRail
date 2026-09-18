"""Whole-city contract sweep through native evaluators and the production historian.

This complements the selected live HTTP deployment; it is not a whole-network
real-time throughput or FUXA load claim.
"""
import json
import copy
import time
from datetime import datetime,timezone


def verify(h,supervisor,company,project):
    from osr_integration.config import digest
    from osr_integration.store import Store
    from osr_integration.manufacturing import factory_control_state,factory_measurements
    simulation=h.module('network_native_simulator','tools/automation/supervision-simulator.py')
    package=supervisor.city_package('samawah')
    for a in package['equipment']:a['company_id']=company;a['erp_project']=project
    package.pop('sha256');package['sha256']=digest(package)
    folder=h.OUTPUT/'full-network';folder.mkdir(parents=True,exist_ok=True)
    h.write(folder/'package.json',package)
    database=folder/'historian.sqlite3'
    if database.exists():raise ValueError('Whole-city fixture historian must start empty')
    store=Store(database);store.apply(package,'example-network-engineer')
    bridge=simulation.EmbeddedBridge();cache={};count=0;rejected=0
    factory=factory_control_state({},[a['manufacturing_method']['method_id'] for a in package['equipment'] if a.get('manufacturing_method')])
    try:
        for a in package['equipment']:
            if a.get('manufacturing_method'):values=factory_measurements(a,factory)
            else:
                key=a['site_id']
                if key not in cache:cache[key]=bridge.evaluate('network|'+key,75,{})
                values=cache[key]
            for name,m in a['measurements'].items():
                fixtures={'temperature_c':35,'energy_kwh':1200,'running_hours':40,'pump_running':0}
                value=values.get((a['equipment_type'],name),fixtures.get(name))
                if value is None:raise AssertionError('No native/declared fixture source for '+a['asset_id']+':'+name)
                for sample,expected in [(value,'valid'),(m['min']-1,'invalid'),(m['max']+1,'invalid'),(value,'valid')]:
                    try:
                        result=store.ingest(dict(city='samawah',environment='simulation',asset_id=a['asset_id'],measurement=name,
                            source_id='simulator',sequence=time.time_ns(),source_timestamp=datetime.now(timezone.utc).isoformat(),
                            value=sample,quality='valid',unit=m['unit']),'simulator')
                    except ValueError:
                        if expected!='invalid' or -1e12<=sample<=1e12:raise
                        rejected+=1;continue # Global numeric envelope rejects before historical ingestion.
                    if result['quality']!=expected:raise AssertionError('Invalid full-city contract: '+a['asset_id']+':'+name)
                count+=1
    finally:bridge.close()
    with store.connect() as db:
        actual=db.execute('SELECT COUNT(DISTINCT scope) AS assets,COUNT(*) AS readings FROM readings').fetchone()
    assert actual['assets']==len(package['equipment']) and actual['readings']==count*4-rejected
    future=time.time()+2*86400
    store.prune(now=future)
    with store.connect() as db:retained=db.execute('SELECT COUNT(*) FROM readings').fetchone()[0]
    assert retained==count*4-rejected
    changed=copy.deepcopy(package);changed['historian']['retention_days']=1
    changed.pop('sha256');changed['sha256']=digest(changed)
    review=store.package_review(changed)
    store.apply(changed,'example-network-engineer',package['sha256'],review['sha256'])
    store.prune(now=future)
    with store.connect() as db:remaining=db.execute('SELECT COUNT(*) FROM readings').fetchone()[0]
    assert remaining==count # The latest reading remains as explicitly aged/disconnected history.
    result=dict(passed=True,equipment=actual['assets'],measurements=count,boundary_and_native_samples=count*4,rejected_at_ingestion=rejected,native_site_evaluations=len(cache),
        retention={'clock_advanced_days':2,'before_days':7,'after_days':1,'before_rows':retained,'after_rows':remaining,'latest_preserved':True},
        observation='Native evaluator/fixture -> production historian; sequential contract sweep, not real-time network load',
        physical_acceptance=False,package_sha256=package['sha256'])
    h.write(folder/'report.json',result);return result
