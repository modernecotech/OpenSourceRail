"""Manufacturing-planning identities, quantity ownership and business boundaries."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys
import unittest

from engineering.pilot_delivery import ROOT
from engineering.pilot_delivery.model import (compile_proposal, validate_proposal, seal, guard_draft,
                                              _external)


def read(relative):
    return json.loads(gzip.decompress((ROOT/relative).read_bytes()))


class PilotDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=read('docs/design-engine/reconciled-pilot/study.json.gz')
        cls.body=read('docs/design-engine/reconciled-pilot/vehicle/installation.json.gz')
        cls.service=next(r['service']['evaluation_id'] for r in cls.study['records']
            if r['experiment']=='nominal' and r['service']['headway_s']==200
            and r['service']['opposite_phase_s']==90)
        cls.proposal=compile_proposal(cls.study,cls.body,cls.service)

    def test_counted_parts_assemblies_materials_and_fleet_are_retained(self):
        p=self.proposal;s=p['summary']
        self.assertEqual(s['component_types'],650)
        self.assertEqual(s['occurrence_patterns'],len(self.body['patterns']))
        self.assertEqual(s['body_occurrences_per_train'],121318)
        self.assertEqual(s['body_occurrences_project'],4*121318)
        self.assertEqual(s['assembly_types'],40)
        self.assertEqual(s['cost_scopes'],14)
        self.assertEqual(p['assembly_routes'][0]['source_operations'],self.body['assembly_plans']['plans'][0]['source_assembly_steps'])
        self.assertEqual(p['items'][0]['stock'],self.body['parts'][0]['stock'])
        # Original source-component identity is retained separately from the whole railway.
        self.assertNotEqual(p['items'][0]['source_component_candidate_id'],p['identities']['candidate_id'])
        for c in ('low','base','high'):
            self.assertAlmostEqual(sum(i['counted_direct_parts_process_usd_per_train'][c] for i in p['items']),
                                   self.body['direct_parts_process_usd'][c],places=5)

    def test_unknowns_and_release_holds_are_visible(self):
        p=self.proposal
        self.assertIsNone(p['capacity']['validated_vehicle_person_h'])
        self.assertIsNone(p['capacity']['actual_crew_count'])
        self.assertIsNone(p['capacity']['calendar_duration_days'])
        self.assertFalse(p['manufacturing_drawings_complete'])
        self.assertFalse(p['qualified_factory_route'])
        self.assertTrue(all(i['capacity']['validated_person_h'] is None for i in p['items']))
        self.assertTrue(all(i['capacity']['provisional_person_h']['low']>0 for i in p['items']))
        self.assertTrue(all(i['provisional_person_h'] is None for i in p['external_inventory']))
        self.assertEqual(p['summary']['task_status_counts'],{'held':712,'ready-for-planning-review':723})
        self.assertTrue(all(t['holds'] for t in p['tasks'] if t['status']=='held'))
        self.assertTrue(all(i['serial_plan']['serial_number'] is None for i in p['items']))

    def test_obsolete_battery_route_is_retained_as_held_source_only(self):
        route=next(a for a in self.proposal['assembly_routes'] if a['id']=='services/battery')
        self.assertEqual(len(route['source_route_unresolved_part_ids']),17)
        current={p['id'] for p in self.proposal['items']}
        self.assertTrue(all(i in current for step in route['operations'] for i in step['part_ids']))
        self.assertTrue(any(step['unresolved_source_part_ids'] for step in route['operations']))
        task=next(t for t in self.proposal['tasks'] if t['id']=='hold/source-route/services/battery')
        self.assertEqual(task['status'],'held')

    def test_civil_and_external_quantity_ownership(self):
        p=self.proposal
        external={r['id']:r for r in p['external_inventory']}
        self.assertEqual(external['traction-motor']['quantity_project'],48)
        self.assertEqual(external['gearbox-including-couplings']['quantity_project'],48)
        self.assertFalse(external['auxiliary-DC-DC-partition']['additive_procurement'])
        self.assertFalse(external['auxiliary-DC-DC-partition']['additional_to_body'])
        self.assertAlmostEqual(external['conductor-protection-feeder']['quantity_project'],3598.226207006117)
        civil={r['id']:r for r in p['civil_requirements']}
        self.assertEqual(civil['beam/precast-segment']['quantity_project'],300)
        self.assertEqual(civil['support/footing']['quantity_project'],76)
        self.assertFalse(civil['beam/precast-segment']['additive_mass_or_cost_ledger'])
        self.assertIsNone(civil['beam/precast-segment']['validated_person_h'])
        self.assertIn('tower', ' '.join(p['construction_route']['erection_sequence']).lower())
        self.assertFalse(p['construction_route']['lifting']['verified_chart_available'])
        self.assertGreater(p['cost_views'][0]['installed_capital_usd']['base'],0)

    def test_identity_or_bundle_tampering_rejected_even_when_proposal_resealed(self):
        for section,key in (('items','candidate_id'),('assembly_routes','engineering_revision'),
                            ('civil_requirements','civil_evaluation_id'),('tasks','bundle_evaluation_id'),
                            ('occurrence_patterns','service_evaluation_id')):
            with self.subTest(section=section):
                p=deepcopy(self.proposal)
                # Deliberately detach the shared binding: deepcopy retains aliasing within the proposal.
                p[section][0]['identities']=dict(p[section][0]['identities'])
                p[section][0]['identities'][key]='0'*64
                p.pop('proposal_id');seal(p,'proposal_id')
                with self.assertRaisesRegex(ValueError,'Mixed'):
                    validate_proposal(p)

    def test_wrong_body_or_service_is_not_an_implicit_default(self):
        b=deepcopy(self.body);b['candidate_id']='0'*64;b.pop('evaluation_id');seal(b)
        with self.assertRaisesRegex(ValueError,'Body physical identity'):
            compile_proposal(self.study,b,self.service)
        with self.assertRaisesRegex(ValueError,'explicit nominal service'):
            compile_proposal(self.study,self.body,'0'*64)

    def test_mixed_civil_or_cost_evaluation_rejected(self):
        s=deepcopy(self.study)
        s['civil']['parts']['beam_instances']=152
        # A false record cannot be admitted merely by recomputing the outer study seal.
        s.pop('study_id');seal(s,'study_id')
        with self.assertRaisesRegex(ValueError,'Unsealed'):
            compile_proposal(s,self.body,self.service)
        s=deepcopy(self.study)
        r=next(r for r in s['records'] if r['experiment']=='nominal' and r['service']['evaluation_id']==self.service)
        r['cost']['civil_cost_evaluation_id']='0'*64
        s.pop('study_id');seal(s,'study_id')
        with self.assertRaisesRegex(ValueError,'Mixed civil'):
            compile_proposal(s,self.body,self.service)

    def test_no_automatic_approval_serial_acceptance_or_safety_commands(self):
        for payload in ({'automatic_order_release':True},{'manufacturing_release':True},
                        {'safety_command_request':{'command':'depart'}},
                        {'commands':{'movement_authority':'depart'}},
                        {'serial_number_assigned':True},{'status':'approved'},{'docstatus':1},
                        {'construction_release':True}):
            with self.subTest(payload=payload),self.assertRaises(ValueError):
                guard_draft(payload)
        p=deepcopy(self.proposal);p['automatic_order_release']=True
        p.pop('proposal_id');seal(p,'proposal_id')
        with self.assertRaisesRegex(ValueError,'release or safety'):
            validate_proposal(p)

    def test_existing_execution_adapter_refuses_unreviewed_mapping(self):
        sys.path.insert(0,str(ROOT/'services/integration'))
        from osr_integration.engineering import execution_proposal
        from osr_integration.config import digest
        evidence=dict(schema='osr-engineering-evidence/1',city='synthetic-pilot',
                      asset_id='research',engineering_revision=self.body['evaluation_id'],artifacts=[])
        evidence['sha256']=digest(evidence)
        mapping=deepcopy(self.proposal['execution_mapping_draft'])
        mapping['engineering_sha256']=evidence['sha256']
        with self.assertRaisesRegex(ValueError,'Reviewed conversion'):
            execution_proposal(evidence,mapping)
        # A review name alone cannot invent Item/drawing/inspection mappings.
        mapping['review_reference']='test-boundary-only'
        with self.assertRaisesRegex(ValueError,'Incomplete item mapping'):
            execution_proposal(evidence,mapping)

    def test_BOP_partition_requires_arithmetic_not_a_second_allowance(self):
        s=deepcopy(self.study);items=deepcopy(self.proposal['items'])
        selected=next(p for p in items if p['counted_pattern_mass_kg_per_train']['high']<100)
        selected['BOP_partition']=True
        partition=selected['counted_pattern_mass_kg_per_train']
        with self.assertRaisesRegex(ValueError,'explicit external'):
            _external(s,items,self.proposal['identities'],4)
        reserve=next(r for r in s['installed']['variant']['inventory'] if r['id']=='inverter-cooling-mounting-collector-reserve')
        gross=dict(reserve['mass_hypothesis_kg'])
        remainder={c:gross[c]-partition[c] for c in gross}
        reserve.update(previous_external_reserve_kg=gross,
            explicit_parts_already_in_body_kg=partition,remaining_unknown_external_reserve_kg=remainder,
            mass_hypothesis_kg=remainder)
        rows,_=_external(s,items,self.proposal['identities'],4)
        r=next(r for r in rows if r['id']==reserve['id'])
        self.assertEqual(r['remaining_unlocated_mass_kg_per_train'],remainder)
        reserve['remaining_unknown_external_reserve_kg']['base']+=1
        with self.assertRaisesRegex(ValueError,'gross minus'):
            _external(s,items,self.proposal['identities'],4)

    def test_no_store_control_compiles_without_invented_storage(self):
        s=read('docs/design-engine/reconciled-pilot-no-store/study.json.gz')
        b=read('docs/design-engine/reconciled-pilot-no-store/vehicle/installation.json.gz')
        service=next(r['service']['evaluation_id'] for r in s['records'] if r['experiment']=='nominal'
            and r['service']['headway_s']==200 and r['service']['opposite_phase_s']==90)
        p=compile_proposal(s,b,service)
        self.assertNotEqual(p['identities']['candidate_id'],self.proposal['identities']['candidate_id'])
        self.assertNotIn('capture-release-interface-reserve',{r['id'] for r in p['external_inventory']})
        self.assertEqual(len(p['items']),650)


if __name__=='__main__':
    unittest.main()
