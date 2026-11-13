"""Portable custody and non-inheritance checks for the held city overlay."""

import gzip
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engineering.station_rail.common import identity
from engineering.v07_candidate_overlay import build_overlay


def sealed(value, key):
    value[key] = identity(value)
    return value


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ref = '1' * 64
        self.research = '2' * 64
        self.body = '3' * 64
        self.service = sealed({'headway_s': 200.0, 'total_trainsets': 4}, 'evaluation_id')
        self.services = [self.service] + [sealed({'headway_s': 200.0 + n,
            'total_trainsets': 4 + n}, 'evaluation_id') for n in range(1, 6)]
        self.study = sealed(dict(schema='osr-railway-closure-study/1',
            body_candidate_id=self.body,
            bundle={'candidate_id': self.research, 'evaluation_id': '4' * 64,
                    'installed_mass_evaluation_id': 'e' * 64,
                    'physical_definition': {'body_candidate_id': self.body}},
            service_plans=self.services,
            records=[{'experiment': 'nominal', 'enabled': True, 'service': s}
                     for s in self.services],
            source_sha256={'source': '5' * 64},
            integrated_selection=None, priced_cities_replaced=False,
            engineering_accepted=False, physical_accepted=False,
            manufacturing_release=False, operating_release=False,
            selected_reference_changed=False), 'study_id')
        self.proposal = sealed(dict(schema='osr-pilot-delivery-proposal/1',
            status='DRAFT', summary={'cost_scopes': 14},
            identities={'candidate_id': self.research, 'body_candidate_id': self.body,
                'study_id': self.study['study_id'], 'bundle_evaluation_id': '4' * 64,
                'service_evaluation_id': self.service['evaluation_id']},
            source_sha256={'source': '5' * 64}, engineering_accepted=False,
            physical_accepted=False, manufacturing_release=False,
            operating_release=False, selected_reference_changed=False,
            transactions_performed=False, automatic_order_release=False), 'proposal_id')
        self.ids = {side: dict(reference_candidate_ids={'candidate_id': self.ref},
            source_outline_evaluation_id='6' * 64, planning_seed_id='7' * 64,
            city_input_id=('8' if side == 'before' else '9') * 64,
            manifest_id=('a' if side == 'before' else 'b') * 64)
            for side in ('before', 'after')}
        self.report = sealed(dict(schema='osr-corridor-revision-comparison/1',
            reference_candidate_ids={'candidate_id': self.ref}, identities=self.ids,
            edit={'proposed_stop_id': 'merged-stop'},
            cost_scopes={f'scope-{n}': {'before': {'base': 1000}, 'after': {'base': 100}}
                         for n in range(14)},
            source_sha256={'historical': 'c' * 64}, engineering_accepted=False,
            physical_accepted=False, manufacturing_release=False,
            operating_release=False, selected_reference_changed=False), 'comparison_id')
        self.wrapper = dict(schema='osr-corridor-comparison-response/1', report=self.report)
        self._write_all()

    def _write(self, name, value, compressed=False):
        path = self.root / name
        data = json.dumps(value, sort_keys=True).encode()
        path.write_bytes(gzip.compress(data, mtime=0) if compressed else data)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def _write_all(self):
        self.comparison_path, self.comparison_sha256 = self._write('comparison.json', self.wrapper)
        milestone = dict(schema='osr-v07-samawah-milestone-record/1',
            comparison_id=self.report['comparison_id'], edit=self.report['edit'],
            identities=self.ids, reference_candidate_ids=self.report['reference_candidate_ids'],
            raw_evidence={'files': {'run-03/comparison.json': {'sha256': self.comparison_sha256}}})
        self.milestone_path, self.milestone_sha256 = self._write('milestone.json', milestone)
        self.study_path, self.study_sha256 = self._write('study.json.gz', self.study, True)
        self.proposal_path, self.proposal_sha256 = self._write('proposal.json.gz', self.proposal, True)

    def _build(self, **changes):
        args=dict(comparison_path=self.comparison_path, comparison_sha256=self.comparison_sha256,
            milestone_path=self.milestone_path, milestone_sha256=self.milestone_sha256,
            study_path=self.study_path, study_sha256=self.study_sha256,
            proposal_path=self.proposal_path, proposal_sha256=self.proposal_sha256,
            reference_candidate_id=self.ref, research_candidate_id=self.research,
            body_candidate_id=self.body, study_id=self.study['study_id'],
            service_evaluation_id=self.service['evaluation_id'])
        args.update(changes)
        return build_overlay(**args)

    def test_all_candidate_costs_and_service_remain_unknown(self):
        overlay = self._build()
        self.assertEqual(overlay['status'], 'HELD_RESEARCH')
        self.assertEqual(len(overlay['cost_scopes']), 14)
        self.assertTrue(all(value is None for scope in overlay['cost_scopes'].values()
                            for value in scope.values()))
        self.assertTrue(all(value is None for value in overlay['service'].values()))
        self.assertIsNone(overlay['installed_mass'])
        self.assertIsNone(overlay['civil_quantities'])
        self.assertIsNone(overlay['selected_candidate_id'])
        self.assertEqual(len(overlay['invalidated_stages']), 9)
        self.assertEqual(len(overlay['retained_nominal_service_evaluation_ids']), 6)
        self.assertEqual(overlay['overlay_id'], identity({k:v for k,v in overlay.items() if k!='overlay_id'}))

    def test_changed_bytes_and_candidate_links_refused(self):
        self.comparison_path.write_bytes(self.comparison_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self._build()
        self._write_all()
        with self.assertRaisesRegex(ValueError, 'identities disagree'):
            self._build(research_candidate_id='d' * 64)

    def test_browser_round_trip_seal_is_reported_without_promoting_values(self):
        self.report['cost_scopes']['scope-0']['before']['base'] = 9999
        self._write_all()
        overlay = self._build()
        self.assertFalse(overlay['historical_comparison_embedded_seal_verified'])
        self.assertIsNone(overlay['cost_scopes']['scope-0']['before'])

    def test_optional_current_source_verification(self):
        (self.root / 'source').write_bytes(b'source')
        source_hash = hashlib.sha256(b'source').hexdigest()
        self.study['source_sha256']['source'] = source_hash
        self.proposal['source_sha256']['source'] = source_hash
        self.study = sealed({k:v for k,v in self.study.items() if k!='study_id'}, 'study_id')
        self.proposal['identities']['study_id'] = self.study['study_id']
        self.proposal = sealed({k:v for k,v in self.proposal.items() if k!='proposal_id'}, 'proposal_id')
        self._write_all()
        self.assertTrue(self._build(source_root=self.root)['research_source_bindings_verified_against_current_checkout'])
        (self.root / 'source').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed source'):
            self._build(source_root=self.root)


if __name__ == '__main__':
    unittest.main()
