"""A real counted child can enter planning without inheriting native journey proof."""
from math import fsum
import unittest

from engineering.powered_bogie.design import parent, build
from engineering.railway_closure import ROOT, FLAGS
from engineering.railway_closure.installed import integrate, axle_packet
from engineering.railway_closure.bundle import combine
from engineering.railway_closure.service import plan, brief
from engineering.railway_closure.cost import evaluate
from engineering.pilot_civil.design import evaluate as civil_evaluate
from engineering.pilot_delivery.model import compile_proposal, seal, validate_proposal


class ChildDeliveryAdmissionTests(unittest.TestCase):
    def test_actual_child_parts_replace_routes_and_BOP_once(self):
        body=build(parent())
        installed=integrate(body)
        civil=civil_evaluate(axle_packet(installed),family='folded_plate',revision='thick-web',upstream_root=ROOT)
        bundle=combine(installed,civil)
        service=plan(bundle['candidate_id'],{'A':188.2,'B':188.2},brief(),headway_s=200,phase_b_s=90,active_trainsets=3)
        cost=evaluate(body,installed,civil,service)
        # This fixture contains analytical bookkeeping only. No native journey,
        # physical evidence, measured process rate or released work is invented.
        study=dict(schema='osr-railway-closure-study/1',bundle=bundle,
            body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],
            installed=installed,civil=civil,records=[dict(experiment='nominal',service=service,cost=cost,
                request=dict(candidate_id=bundle['candidate_id']),result=dict(candidate_id=bundle['candidate_id']),energy=None)],
            source_sha256={},test_only=True,scope='Unit test bookkeeping fixture without native journey evidence',**FLAGS)
        seal(study,'study_id')
        proposal=compile_proposal(study,body,service['evaluation_id'])
        self.assertTrue(validate_proposal(proposal))
        self.assertEqual(proposal['summary']['component_types'],body['proposed_component_types'])
        self.assertEqual(proposal['summary']['component_types'],668)
        self.assertGreater(proposal['summary']['unknown_process_time_types'],0)
        self.assertIsNone(proposal['capacity']['provisional_vehicle_person_h'])
        self.assertGreater(proposal['capacity']['known_provisional_vehicle_person_h_subtotal']['base'],0)
        current={p['id'] for p in body['parts']}
        underframe=next(r for r in proposal['assembly_routes'] if r['id']=='body/underframe')
        self.assertEqual(underframe['occurrences_per_train'],len(body['assembly_occurrences']['body/underframe']))
        self.assertEqual(underframe['occurrences_per_train'],6)
        route=next(r for r in proposal['assembly_routes'] if r['id']=='research/powered-bogie')
        self.assertEqual(set(route['component_type_ids']),{p['id'] for p in body['parts'] if p['assembly_id']==route['id']})
        self.assertTrue(route['current_part_ids_needing_route_detail'])
        self.assertTrue(all(i in current for a in proposal['assembly_routes'] for op in a['operations'] for i in op['part_ids']))
        running=next(r for r in proposal['assembly_routes'] if r['id']=='running/bogie-frame')
        self.assertTrue(set(body['change_set']['removed_part_ids'])<=set(running['source_route_unresolved_part_ids']))
        source_routes={r['assembly_id']:r for r in body['assembly_plans']['plans']}
        self.assertEqual(running['source_operations'],source_routes[running['id']]['source_assembly_steps'])
        external={r['id']:r for r in proposal['external_inventory']}
        reserve=external['inverter-cooling-mounting-collector-reserve']
        for c in ('low','base','high'):
            counted=fsum(p['counted_pattern_mass_kg_per_train'][c] for p in proposal['items'] if p['BOP_partition'])
            self.assertAlmostEqual(counted,body['BOP_partition']['explicit_parts_already_in_body_kg'][c])
            self.assertAlmostEqual(reserve['remaining_unlocated_mass_kg_per_train'][c]+counted,
                                   body['BOP_partition']['previous_external_reserve_kg'][c])
        self.assertFalse(external['auxiliary-DC-DC-partition']['additive_procurement'])
        self.assertEqual(external['traction-motor']['quantity_project'],48)
        self.assertEqual(external['gearbox-including-couplings']['quantity_project'],48)
        self.assertFalse(proposal['manufacturing_release'])
        self.assertFalse(proposal['movement_authority'])
        self.assertFalse(proposal['physical_accepted'])


if __name__=='__main__':
    unittest.main()
