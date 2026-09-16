"""Failure-oriented integration acceptance tests independent of live ERP/FUXA."""
import copy
import importlib.util
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import build_package, digest, ifc_guid
from osr_integration.store import Store
from osr_integration.server import deliver
from osr_integration.engineering import package as engineering_package, execution_proposal, ifc_overlay
from osr_integration.embedded import energy_measurements, operating_measurements
from osr_integration.fuxa import deployment_manifest, deployment_review, project, validate_deployment_review


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat()


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'db.sqlite')
        self.generic = json.loads((ROOT / 'deployment/supervision/config/generic.json').read_text())
        self.package = build_package(self.generic, {'city': 'samawah'}, [{'asset_type': 'station', 'asset_id': 'SAM-ST-001', 'name': 'Station'}], 'rev1')
        self.store.apply(self.package, 'engineer')

    def message(self, now, value=80, **extra):
        return dict(city='samawah', environment='simulation', asset_id='SAM-ST-001:charger', measurement='temperature_c', source_id='simulator', sequence=int(now), source_timestamp=iso(now), unit='degC', quality='valid', value=value, **extra)

    def test_existing_historian_schema_is_migrated_forward(self):
        legacy = Path(self.tmp.name) / 'legacy.sqlite'
        with sqlite3.connect(legacy) as db:
            db.executescript('''
                CREATE TABLE assets (scope TEXT PRIMARY KEY, city TEXT, environment TEXT, asset_id TEXT, package TEXT, body TEXT, state TEXT DEFAULT 'as-designed');
                CREATE TABLE alarms (key TEXT PRIMARY KEY, scope TEXT, rule TEXT, pending REAL, active INTEGER DEFAULT 0, incident TEXT, last_event REAL DEFAULT 0, occurrences INTEGER DEFAULT 0, case_id TEXT, erp_status TEXT, acknowledged_by TEXT);
            ''')
        migrated = Store(legacy)
        with migrated.connect() as db:
            asset_columns = {row['name'] for row in db.execute('PRAGMA table_info(assets)')}
            alarm_columns = {row['name'] for row in db.execute('PRAGMA table_info(alarms)')}
        self.assertIn('configuration_status', asset_columns)
        self.assertTrue({'acknowledged_at', 'acknowledged_occurrence'} <= alarm_columns)

    def fault(self):
        for now in [1000, 1003, 1006]: self.store.ingest(self.message(now), 'simulator', now)

    def test_deterministic_and_repeat_safe_package(self):
        self.assertFalse(self.store.apply(self.package, 'engineer')['created'])
        updated = copy.deepcopy(self.package); updated['engineering_revision'] = 'rev2'; updated['sha256'] = digest({k: v for k, v in updated.items() if k != 'sha256'})
        with self.assertRaises(ValueError): self.store.apply(updated, 'engineer')
        review = self.store.package_review(updated)
        self.assertEqual(review['status'], 'review-required')
        self.store.apply(updated, 'engineer', self.package['sha256'], review['sha256'])
        self.assertEqual(len(self.store.snapshot()['assets']), 4)
        self.assertEqual(len(ifc_guid('SAM-ST-001:charger')), 22)

    def test_change_review_traces_design_embedded_and_lifecycle_impact_without_cross_city_mutation(self):
        mosul = build_package(self.generic, {'city': 'mosul'}, [
            {'asset_type': 'station', 'asset_id': 'MOS-ST-001', 'name': 'Mosul station'}], 'mosul-rev1')
        self.store.apply(mosul, 'engineer')
        mosul_before = self.store.snapshot('mosul', 'simulation', now=1000)
        base = dict(city='samawah', environment='simulation', asset_id='SAM-ST-001:charger',
                    engineering_revision='rev1', references=['sha256:review-source'])
        self.store.evidence(dict(base, id='impact-design', kind='design-review'), 'engineer', 'engineer')
        self.store.evidence(dict(base, id='impact-execution', kind='execution-release'), 'reviewer', 'reviewer')
        self.store.evidence(dict(base, id='impact-install', kind='installation', serial='SER-1', batch='BAT-1'), 'engineer', 'engineer')

        updated = copy.deepcopy(self.package)
        updated['engineering_revision'] = 'rev2'
        charger = next(a for a in updated['equipment'] if a['equipment_type'] == 'charger')
        charger['engineering_revision'] = 'rev2'
        charger['measurements']['temperature_c']['max'] = 160
        charger['erp_project'] = 'MOSUL-UNRELATED-MUST-NOT-CHANGE-SAMAWAH'
        updated['sha256'] = digest({k: v for k, v in updated.items() if k != 'sha256'})

        review = self.store.package_review(updated)
        self.assertEqual(review['summary']['changed'], 1)
        self.assertEqual(review['summary']['installed_serials_affected'], 1)
        self.assertEqual(review['summary']['evidence_records_requiring_review'], 3)
        impact = review['equipment_changes'][0]
        self.assertEqual(impact['asset_id'], 'SAM-ST-001:charger')
        self.assertTrue({'design-definition', 'telemetry-contract', 'business-execution'} <= set(impact['categories']))
        self.assertIn('osr-energy-site', impact['dependencies']['source_crates'])
        self.assertEqual(impact['affected_records']['installations'][0]['serial'], 'SER-1')
        self.assertTrue(all(row['review_status'] == 'requires-review' for row in impact['affected_records']['evidence']))
        self.assertEqual(self.store.snapshot('mosul', 'simulation', now=1000), mosul_before)

        # New evidence after preview invalidates the review without changing either package.
        self.store.evidence(dict(base, id='impact-analysis', kind='analysis'), 'engineer', 'engineer')
        with self.assertRaisesRegex(ValueError, 'changed after review'):
            self.store.apply(updated, 'engineer', self.package['sha256'], review['sha256'])
        review = self.store.package_review(updated)
        self.store.apply(updated, 'engineer', self.package['sha256'], review['sha256'])
        self.assertEqual(self.store.snapshot('mosul', 'simulation', now=1000), mosul_before)

        removal = copy.deepcopy(updated)
        removal['engineering_revision'] = 'rev3'
        removal['equipment'] = [a for a in removal['equipment'] if a['equipment_type'] != 'charger']
        removal['sha256'] = digest({k: v for k, v in removal.items() if k != 'sha256'})
        blocked = self.store.package_review(removal)
        self.assertFalse(blocked['application']['automatic_apply_permitted'])
        self.assertIn('installed serial', ' '.join(blocked['application']['blockers']))

        # A pending controller request also prevents its command contract changing beneath it.
        command = dict(request_id='impact-command', city='samawah', environment='simulation',
                       asset_id='SAM-ST-001:facilities', command='set_lighting', parameters={'level': 75},
                       created_at=iso(1000), expires_at=iso(1020), required_conditions=['local_remote_enabled'])
        self.store.command(command, 'operator', True, 1000)
        command_change = copy.deepcopy(updated)
        command_change['engineering_revision'] = 'rev3'
        facilities = next(a for a in command_change['equipment'] if a['equipment_type'] == 'facilities')
        facilities['commands']['set_lighting']['max'] = 90
        command_change['sha256'] = digest({k: v for k, v in command_change.items() if k != 'sha256'})
        blocked = self.store.package_review(command_change)
        self.assertIn('pending', ' '.join(blocked['application']['blockers']))

    def test_wrong_source_units_and_replay(self):
        m = self.message(1000)
        with self.assertRaises(PermissionError): self.store.ingest(m, 'other', 1000)
        self.store.ingest(m, 'simulator', 1000)
        self.assertTrue(self.store.ingest(m, 'simulator', 1000)['duplicate'])
        m['value'] = 99
        with self.assertRaises(ValueError): self.store.ingest(m, 'simulator', 1000)
        m = self.message(1001); m['unit'] = 'K'
        with self.assertRaises(ValueError): self.store.ingest(m, 'simulator', 1001)
        m = self.message(1002); m['source_timestamp'] = iso(999)
        with self.assertRaisesRegex(ValueError, 'Out-of-order source timestamp'):
            self.store.ingest(m, 'simulator', 1002)
        with self.assertRaisesRegex(ValueError, 'Future timestamp'):
            self.store.ingest(self.message(1010), 'simulator', 1002)

    def test_alarm_delay_hysteresis_repeats_and_queue(self):
        self.fault()
        self.store.ingest(self.message(1008, 65), 'simulator', 1008)
        snap = self.store.snapshot(now=1008); alarm = next(a for a in snap['assets'] if a['equipment_type'] == 'charger')['alarms'][0]
        self.assertEqual(alarm['active'], 1); self.assertEqual(len(snap['outbox']), 1)
        self.store.ingest(self.message(1010, 59), 'simulator', 1010)
        self.assertEqual(len(self.store.snapshot()['outbox']), 2)
        # Alarm clears; case stays attached, maintenance is never auto-closed.
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT active FROM alarms').fetchone()[0], 0)

    def test_acknowledgement_is_immutable_and_bound_to_one_occurrence(self):
        self.fault()
        first = self.store.acknowledge('samawah', 'simulation', 'SAM-ST-001:charger',
                                       'cooling', 1, 'operator-a', 1007)
        self.assertTrue(first['created'])
        repeated = self.store.acknowledge('samawah', 'simulation', 'SAM-ST-001:charger',
                                          'cooling', 1, 'operator-b', 1008)
        self.assertFalse(repeated['created'])
        self.assertEqual(repeated['actor'], 'operator-a')
        # A repeat notification during the same active condition keeps the first acknowledgement.
        for now in [1307, 1310, 1313]:
            self.store.ingest(self.message(now), 'simulator', now)
        repeated = self.store.acknowledge('samawah', 'simulation', 'SAM-ST-001:charger',
                                          'cooling', 2, 'operator-b', 1314)
        self.assertFalse(repeated['created'])
        self.assertEqual(repeated['actor'], 'operator-a')
        self.store.ingest(self.message(1320, 40), 'simulator', 1320)
        for now in [1321, 1324, 1327]:
            self.store.ingest(self.message(now), 'simulator', now)
        alarm = next(a for a in self.store.snapshot(now=1327)['assets']
                     if a['equipment_type'] == 'charger')['alarms'][0]
        self.assertEqual(alarm['occurrences'], 3)
        self.assertIsNone(alarm['acknowledged_by'])
        with self.assertRaisesRegex(ValueError, 'occurrence changed'):
            self.store.acknowledge('samawah', 'simulation', 'SAM-ST-001:charger',
                                   'cooling', 2, 'operator-a', 1328)

    def test_gap_and_invalid_do_not_establish_persistence(self):
        self.store.ingest(self.message(1000), 'simulator', 1000)
        self.store.ingest(self.message(1100), 'simulator', 1100)
        self.assertEqual(self.store.snapshot()['outbox'], [])
        self.store.ingest(self.message(1103, 200), 'simulator', 1103)
        self.store.ingest(self.message(1106), 'simulator', 1106)
        self.assertEqual(self.store.snapshot()['outbox'], [])

    def test_stale_disconnected_and_nan(self):
        self.store.ingest(self.message(1000), 'simulator', 1000)
        def reading(t): return next(a for a in self.store.snapshot(now=t)['assets'] if a['equipment_type'] == 'charger')['readings']['temperature_c']
        self.assertEqual(reading(1011)['quality'], 'stale'); self.assertEqual(reading(1031)['quality'], 'disconnected')
        with self.assertRaises(ValueError): self.store.ingest(self.message(1001, float('nan')), 'simulator', 1001)

    def test_outage_retry_and_remote_idempotency_contract(self):
        self.fault(); config = {'url': 'http://erp', 'key': 'x', 'secret': 'y'}
        with patch('osr_integration.server.request_json', side_effect=OSError()): deliver(self.store, config, 1010)
        self.assertEqual(self.store.snapshot()['outbox'][0]['attempts'], 1)
        with patch('osr_integration.server.request_json', return_value={'message': {'issue': 'ISS-1', 'status': 'Open'}}): deliver(self.store, config, 1020)
        self.assertEqual(self.store.snapshot()['outbox'][0]['state'], 'delivered')
        restored = Store(self.store.path)
        self.assertEqual(restored.snapshot()['outbox'][0]['state'], 'delivered')

    def test_commands_expiry_permission_and_controller_result(self):
        m = dict(request_id='command1', city='samawah', environment='simulation', asset_id='SAM-ST-001:facilities', command='set_lighting', parameters={'level': 75}, created_at=iso(1000), expires_at=iso(1020), required_conditions=['local_remote_enabled'])
        self.assertEqual(self.store.command(m, 'viewer', False, 1000)['state'], 'rejected')
        m['request_id'] = 'command2'
        self.assertEqual(self.store.command(m, 'operator', True, 1000)['state'], 'requested')
        with self.assertRaises(PermissionError): self.store.controller_result('command2', 'other', 'accepted', '', 1001)
        self.store.controller_result('command2', 'simulator', 'accepted', 'local conditions checked', 1001)
        self.assertEqual(self.store.controller_result('command2', 'simulator', 'completed', 'measured level 75', 1002)['state'], 'completed')
        m['request_id'] = 'command3'; self.store.command(m, 'operator', True, 1000)
        self.assertEqual(self.store.controller_commands('simulator', 1030), [])

    def test_package_removal_retires_asset_and_fails_pending_command(self):
        command = dict(request_id='retire-command', city='samawah', environment='simulation',
                       asset_id='SAM-ST-001:facilities', command='set_lighting',
                       parameters={'level': 75}, created_at=iso(1000), expires_at=iso(1020),
                       required_conditions=['local_remote_enabled'])
        self.assertEqual(self.store.command(command, 'operator', True, 1000)['state'], 'requested')
        self.store.ingest(self.message(999, 50), 'simulator', 999)
        updated = copy.deepcopy(self.package)
        updated['engineering_revision'] = 'rev2'
        updated['equipment'] = [a for a in updated['equipment']
                                if a['equipment_type'] not in {'facilities', 'charger'}]
        for asset in updated['equipment']:
            asset['engineering_revision'] = 'rev2'
        updated['sha256'] = digest({k: v for k, v in updated.items() if k != 'sha256'})
        review = self.store.package_review(updated)
        self.store.apply(updated, 'engineer', self.package['sha256'], review['sha256'])
        retired = {a['equipment_type']: a for a in self.store.snapshot(now=1001)['assets']
                   if a['configuration_status'] == 'retired'}
        self.assertEqual(set(retired), {'facilities', 'charger'})
        self.assertEqual(retired['charger']['readings']['temperature_c']['quality'], 'disconnected')
        with self.assertRaisesRegex(ValueError, 'retired asset'):
            self.store.ingest(self.message(1001), 'simulator', 1001)
        with self.store.connect() as db:
            stored = db.execute('SELECT state,result FROM commands WHERE id=?',
                                ('retire-command',)).fetchone()
        self.assertEqual((stored['state'], stored['result']),
                         ('failed', 'asset retired by supervisory package'))
        self.assertEqual(self.store.controller_commands('simulator', 1001), [])

        # Reapplying an earlier reviewed package is a supported rollback.
        reactivated = copy.deepcopy(self.package)
        review = self.store.package_review(reactivated)
        self.store.apply(reactivated, 'engineer', updated['sha256'], review['sha256'])
        charger = next(a for a in self.store.snapshot(now=1001)['assets']
                       if a['equipment_type'] == 'charger')
        self.assertEqual(charger['configuration_status'], 'active')
        self.assertFalse(self.store.ingest(self.message(1001), 'simulator', 1001)['duplicate'])

    def test_package_rejects_invalid_alarm_and_command_contracts(self):
        for mutate in [
            lambda package: next(a for a in package['equipment'] if a['alarms'])['alarms'][0].update(measurement='missing'),
            lambda package: package.update(equipment=[dict(package['equipment'][0], commands=[])] + package['equipment'][1:]),
            lambda package: next(a for a in package['equipment'] if a['equipment_type'] == 'facilities')['commands']['set_lighting'].update(max_ttl_seconds=0),
            lambda package: next(a for a in package['equipment'] if a['equipment_type'] == 'facilities')['commands']['set_lighting'].update(required_conditions=[]),
        ]:
            invalid = copy.deepcopy(self.package)
            mutate(invalid)
            invalid['sha256'] = digest({k: v for k, v in invalid.items() if k != 'sha256'})
            with self.assertRaises(ValueError):
                self.store.apply(invalid, 'engineer')

    def test_outbox_preserves_incident_order_during_retry(self):
        self.fault()
        self.store.ingest(self.message(1010, 40), 'simulator', 1010)
        config = {'url': 'http://erp', 'key': 'x', 'secret': 'y'}
        with patch('osr_integration.server.request_json', side_effect=OSError()) as request:
            deliver(self.store, config, 1020)
            self.assertEqual(request.call_count, 1)
        with patch('osr_integration.server.request_json') as request:
            deliver(self.store, config, 1021)
            request.assert_not_called()

    def test_desktop_selected_object_resolves_to_city_asset(self):
        spec = importlib.util.spec_from_file_location('bridge', ROOT / 'tools/integration/desktop_bridge.py')
        bridge = importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)
        link = Path(self.tmp.name) / 'links.json'
        link.write_text(json.dumps({'city':'samawah','environment':'simulation','bindings':[{'asset_id':'SAM-ST-001:charger','ifc':['guid1'],'freecad':['cabinet'],'gis':['station1']}]}))
        for app, identity in [('ifc','guid1'),('freecad','cabinet'),('gis','station1')]:
            self.assertIn('selected_asset=SAM-ST-001%3Acharger', bridge.resolve(link, app, identity))
        with self.assertRaises(ValueError): bridge.resolve(link, 'ifc', 'missing')

    def test_evidence_validation_and_repeat_safe_review(self):
        base = dict(id='analysis-1', kind='analysis', city='samawah', environment='simulation',
                    asset_id='SAM-ST-001:charger', engineering_revision='rev1', references=['sha256:source'])
        for refs in ['not-an-array', [], [''], [123]]:
            with self.assertRaises(ValueError): self.store.evidence(dict(base, references=refs), 'engineer', 'engineer')
        with self.assertRaises(PermissionError): self.store.evidence(base, 'viewer', 'viewer')
        with self.assertRaises(ValueError): self.store.evidence(dict(base, engineering_revision='wrong'), 'engineer', 'engineer')
        with self.assertRaises(ValueError): self.store.evidence(dict(base, kind='commissioning-test', result='unknown'), 'inspector', 'inspector')
        self.assertTrue(self.store.evidence(base, 'engineer', 'engineer')['created'])
        self.assertFalse(self.store.evidence(base, 'engineer', 'engineer')['created'])
        with self.assertRaises(ValueError): self.store.evidence(dict(base, references=['changed']), 'engineer', 'engineer')

    def test_vehicle_templates_preserve_station_identity_and_source_bindings(self):
        assets = [{'asset_type':'station','asset_id':'SAM-ST-001','name':'Station'},
                  {'asset_type':'rolling-stock','asset_id':'SAM-RS-L1-001','name':'Vehicle'}]
        package = build_package(self.generic, {'city':'samawah'}, assets, 'rev1')
        self.assertEqual(len(package['equipment']), 8)
        vehicle = [a for a in package['equipment'] if a['parent_asset_id']=='SAM-RS-L1-001']
        self.assertEqual(len(vehicle), 4)
        self.assertTrue(all(a['commands']=={} and a['source_crates'] for a in vehicle))
        self.assertEqual({a['asset_id'] for a in package['equipment'] if a['parent_asset_id']=='SAM-ST-001'},
                         {a['asset_id'] for a in self.package['equipment']})
        with self.assertRaises(ValueError): build_package(self.generic, {'city':'samawah','sites':['unknown']}, assets, 'rev1')

    def test_embedded_projection_rejects_wrong_schema_environment_and_missing_values(self):
        frame = json.loads((ROOT / 'tests/fixtures/operating-bridge.json').read_text())
        values = operating_measurements(frame)
        self.assertEqual(values[('vehicle-bms','soc_pct')], 72)
        self.assertEqual(values[('vehicle-cbm','brake_remaining_pct')], 90)
        self.assertEqual(values[('vehicle-hvac','compressor_pct')], 100)
        frame['station']['lighting_enabled'][0] = False
        self.assertEqual(operating_measurements(frame)[('facilities','lighting_pct')], 0)
        for patch in [{'schema':'unknown'}, {'environment':'physical'}]:
            with self.assertRaises(ValueError): operating_measurements(dict(frame, **patch))
        del frame['bms']
        with self.assertRaises(KeyError): operating_measurements(frame)

    def test_controller_acknowledgement_retry_is_idempotent_and_owned(self):
        m = dict(request_id='retry1',city='samawah',environment='simulation',asset_id='SAM-ST-001:facilities',command='set_lighting',parameters={'level':75},created_at=iso(1000),expires_at=iso(1020),required_conditions=['local_remote_enabled'])
        self.store.command(m,'operator',True,1000)
        for _ in range(2): self.assertEqual(self.store.controller_result('retry1','simulator','accepted','checked',1001)['state'],'accepted')
        with self.assertRaises(PermissionError): self.store.controller_result('retry1','other','accepted','checked',1001)
        with self.assertRaises(ValueError): self.store.controller_result('retry1','simulator','accepted','changed',1001)
        self.store.controller_result('retry1','simulator','completed','done',1002)
        self.assertEqual(self.store.controller_result('retry1','simulator','completed','done',2000)['state'],'completed')

    def test_backup_restore(self):
        self.fault(); target = Path(self.tmp.name) / 'backup.sqlite'; self.store.backup(target)
        self.assertEqual(Store(target).snapshot(now=1006), self.store.snapshot(now=1006))

    def test_ifc_and_engineering_handoff(self):
        root = Path(self.tmp.name); gid = ifc_guid('asset'); (root/'model.ifc').write_text("#1=IFCBUILDINGELEMENTPROXY('" + gid + "',$,'test',$,$,$,$,$,$);")
        e = engineering_package(root, dict(city='samawah', asset_id='asset', engineering_revision='rev1', assumptions=['pilot'], artifacts=[dict(path='model.ifc', tool='bonsai', tool_version='test')]))
        self.assertEqual(e['artifacts'][0]['ifc_objects'][0]['global_id'], gid)
        self.assertEqual(ifc_overlay(e, [{'ifc_global_id': gid}])['bindings'][0]['ifc_global_id'], gid)
        with self.assertRaises(ValueError): execution_proposal(e, {})
        with self.assertRaises(ValueError): engineering_package(root, dict(city='x', asset_id='a', engineering_revision='r', assumptions=[], artifacts=[dict(path='../missing', tool='osr', tool_version='1')]))

    def test_lifecycle_independence_and_replacement(self):
        def evidence(kind, actor, role, **fields):
            return self.store.evidence(dict(id=kind+str(len(fields)), kind=kind, city='samawah', environment='simulation', asset_id='SAM-ST-001:charger', engineering_revision='rev1', references=['test-evidence'], **fields), actor, role)
        evidence('design-review', 'designer', 'engineer')
        evidence('execution-release', 'reviewer', 'reviewer')
        evidence('installation', 'installer', 'engineer', serial='S1', batch='B1')
        evidence('commissioning-test', 'inspector', 'inspector', result='pass')
        with self.assertRaises(ValueError): evidence('commissioning-release', 'inspector', 'reviewer', test_id='commissioning-test1')
        evidence('commissioning-release', 'reviewer', 'reviewer', test_id='commissioning-test1')
        self.assertEqual(len(self.store.affected(batch='B1')), 1)
        for kind, role in [('design-review','engineer'),('execution-release','reviewer')]:
            self.store.evidence(dict(id='battery-'+kind,kind=kind,city='samawah',environment='simulation',asset_id='SAM-ST-001:battery',engineering_revision='rev1',references=['test']),role,role)
        with self.assertRaises(ValueError):
            self.store.evidence(dict(id='duplicate-serial',kind='installation',city='samawah',environment='simulation',asset_id='SAM-ST-001:battery',engineering_revision='rev1',references=['test'],serial='S1'), 'engineer','engineer')

        evidence('installation', 'installer', 'engineer', serial='S2', batch='B2', replaces_serial='S1')
        self.assertIsNotNone(self.store.affected(serial='S1')[0]['removed'])

    def test_fuxa_preserves_ids_and_disables_writes(self):
        f = project([self.package]); self.assertEqual(len(f['devices']), 4)
        self.assertTrue(all('postTags' not in d['property'] for d in f['devices'].values()))
        self.assertTrue(any(k.endswith('__temperature_c_quality') for d in f['devices'].values() for k in d['tags']))

    def test_fuxa_import_review_lists_replacements_and_binds_projects(self):
        desired = project([self.package])
        current = copy.deepcopy(desired)
        removed_device = next(iter(current['devices']))
        del current['devices'][removed_device]
        current['devices']['operator-custom-device'] = {'id': 'operator-custom-device'}
        changed_view = current['hmi']['views'][0]['id']
        current['hmi']['views'][0]['name'] = 'Unreviewed live edit'
        current['hmi']['views'].append({'id': 'operator-custom-view', 'name': 'Local display'})
        current['charts'] = [{'id': 'operator-custom-chart'}]
        review = deployment_review({'data': current}, [self.package])
        self.assertEqual(review['schema'], 'osr-fuxa-import-review/1')
        self.assertIn(removed_device, review['devices']['added'])
        self.assertIn('operator-custom-device', review['devices']['removed'])
        self.assertIn(changed_view, review['views']['changed'])
        self.assertIn('operator-custom-view', review['views']['removed'])
        self.assertTrue(review['project_settings']['changed'])
        self.assertTrue(review['destructive_changes'])
        self.assertEqual(review['sha256'], digest({k: v for k, v in review.items() if k != 'sha256'}))
        self.assertEqual(validate_deployment_review({'data': current}, [self.package], review), review)
        stale = copy.deepcopy(current); stale['devices']['operator-custom-device']['name'] = 'Changed after preview'
        with self.assertRaises(ValueError): validate_deployment_review(stale, [self.package], review)
        manifest = deployment_manifest([self.package])
        self.assertEqual(manifest['packages'][0]['city'], 'samawah')
        self.assertEqual(manifest['reviewed_display_customisations'], [])
        with self.assertRaises(ValueError): deployment_manifest([self.package, self.package])

    def test_embedded_units(self):
        r = energy_measurements(dict(schema='osr-energy-site/1', pv_w=240000, to_pad_w=180000, battery_soc_ppt=720))
        self.assertEqual(r[('pv','power_kw')], 240); self.assertEqual(r[('battery','soc_pct')], 72)


if __name__ == '__main__': unittest.main()
