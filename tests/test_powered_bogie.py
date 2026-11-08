import json
import unittest
from copy import deepcopy
from math import fsum

from engineering.station_rail.common import identity
from engineering.powered_bogie import design,geometry


class PoweredBogieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=design.parent()
        cls.body=design.build(cls.parent)
        cls.report=geometry.evaluate(cls.body)

    def test_known_drive_mass_is_external_once_and_catalogue_stays_bounded(self):
        b=self.body
        self.assertEqual(len(b['external_drive_placements']),24)
        self.assertEqual(sum(r['mass_kg']['base'] for r in b['external_drive_placements']),9552.)
        self.assertTrue(all(not r['body_BOM_contains_mass'] for r in b['external_drive_placements']))
        self.assertFalse(any('motor-envelope' in p['id'] or 'gear-envelope' in p['id'] for p in b['parts']))
        self.assertEqual({r['driven_axle_index'] for r in b['external_drive_placements']},set(range(0,24,2)))
        catalogue=json.loads((design.ROOT/design.policy()['source_catalogue']).read_bytes())
        p=design.policy()['primary_evidence']
        self.assertEqual(p['motor_mass_kg'],catalogue['motor']['listed_mass_kg'])
        self.assertEqual(p['gear_mass_including_couplings_kg'],catalogue['gearbox']['listed_total_weight_including_couplings_kg'])
        self.assertFalse(self.report['supplier_and_profile_gates']['catalogue_matches_OSR_wear_domain'])
        self.assertFalse(self.report['supplier_and_profile_gates']['stricter_research_wear_limit_selected'])

    def test_counted_stock_delta_conserves_mass_reactions_and_BOP(self):
        for case in ('low','base','high'):
            delta=self.body['nominal_part_mass_kg'][case]-self.parent['nominal_part_mass_kg'][case]
            self.assertAlmostEqual(delta,self.body['change_set']['mass_delta_kg'][case],places=7)
            B=self.body['BOP_partition']
            self.assertGreater(B['remaining_unknown_external_reserve_kg'][case],0.)
            self.assertAlmostEqual(B['explicit_parts_already_in_body_kg'][case]+
                B['remaining_unknown_external_reserve_kg'][case],B['previous_external_reserve_kg'][case])
        for scenario in self.body['mass_scenarios']:
            self.assertLess(abs(scenario['force_residual_N']),1e-7)
            self.assertLess(abs(scenario['moment_residual_Nm']),1e-6)
            self.assertGreater(scenario['minimum_axle_force_N'],0.)
            self.assertGreater(scenario['inertia_about_CG_kg_m2'][2][2],0.)
        for p in self.body['parts']:
            self.assertEqual(sum(r['count'] for r in self.body['patterns'] if r['part_id']==p['id']),p['quantity_per_train'])

    def test_physical_and_evaluation_identity_ancestry_and_mixed_parent_rejected(self):
        b=self.body
        self.assertEqual(b['candidate_id'],identity(b['physical_definition']))
        self.assertEqual(b['evaluation_id'],identity({k:v for k,v in b.items() if k!='evaluation_id'}))
        self.assertEqual(b['parent_candidate_id'],self.parent['candidate_id'])
        bad=deepcopy(self.parent);bad['patterns'][0]['positions_m'][0][2]+=.1
        with self.assertRaises(ValueError):design.build(bad)
        with self.assertRaises(ValueError):design.build(self.parent,variant_id='shift-motor-until-fit')
        self.assertFalse(b['selected_reference_changed']);self.assertFalse(b['physical_accepted'])

    def test_RHS_void_is_not_solid_and_native_stock_preserves_volume(self):
        p=next(p for p in self.body['patterns'] if p['part_id']=='powered-bogie/side-rhs' and p['bogie_index']==0)
        walls=geometry.stock_boxes(p)
        self.assertEqual(len(walls),8)
        centre=p['positions_m'][0]
        self.assertFalse(any(geometry.intersects(geometry.box(centre,[.01,.01,.01]),w['bounds_m']) for w in walls))
        volume=fsum(__import__('math').prod(w['bounds_m'][1][i]-w['bounds_m'][0][i] for i in range(3)) for w in walls)
        self.assertAlmostEqual(volume,2*design._volume(p['geometry']['source_stock']))
        case=geometry.stock_case(self.body)
        self.assertGreater(case['expected']['part_count'],20)
        self.assertFalse(case['physical_accepted'])

    def test_continuous_bound_surrounds_all_samples_and_conflicts_stay_held(self):
        self.assertEqual(len(self.report['samples']),12)
        self.assertLessEqual(len(self.report['samples']),24)
        for r in self.report['drives']:
            swept=r['continuous_swept_outer_box_m']
            for sample in r['sample_boxes_m']:
                for i in range(3):
                    self.assertGreaterEqual(sample[0][i]+1e-10,swept[0][i])
                    self.assertLessEqual(sample[1][i]-1e-10,swept[1][i])
            self.assertGreater(len(r['required_space_conflicts']),0)
            self.assertIn('HOLD',r['actual_hardware_fit_status'])
        self.assertTrue(any(r['continuous_body_or_battery_holds'] for r in self.report['drives']))
        self.assertFalse(self.report['maintenance']['removal_path_verified'])
        self.assertFalse(self.report['supplier_fit_verified'])
        self.assertTrue(any(r['relative_frame_swept_holds'] for r in self.report['drives']))
        self.assertEqual(len(self.report['joins_and_services']['flexibility']),2)
        self.assertTrue(all(not r['route_and_terminal_clash_verified'] for r in self.report['joins_and_services']['flexibility']))

    def test_required_fixings_positive_cost_and_repair_are_explicit(self):
        counts=self.report['joins_and_services']['per_bogie']
        self.assertEqual(counts['motor_foot_M20_bolts']+counts['gear_torque_M20_bolts'],12)
        self.assertEqual(counts['gear_internal_bearings_in_310kg'],2)
        for part in self.body['parts']:
            if part['id'].startswith('powered-bogie/'):
                self.assertTrue(all(v>0 for v in part['mass_each_kg'].values()))
                self.assertTrue(all(v>0 for v in part['direct_cost_each_usd'].values()))
                self.assertTrue(part['maintenance_removal'])
                self.assertTrue(part['manufacturing'])
        self.assertGreater(len(self.report['maintenance']['tool_proposals']),0)
        self.assertTrue(self.report['maintenance']['requires_workshop_drop_table'])


if __name__=='__main__':unittest.main()
