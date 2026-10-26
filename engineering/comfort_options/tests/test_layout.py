"""Regression/integrity tests for the explicit seated-comfort alternative."""
from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest

from engineering.comfort_options import layout


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[3]
        cls.rows = layout.family(root=cls.root)
        cls.primary = layout.primary_options(root=cls.root)['maximum_seating_door_bays']
        cls.benches = layout.make_layout(root=cls.root, vestibule_length_m=2.4,
                                         wheelchair_location='outer-ends')

    def test_family_is_bounded_reproducible_and_preserves_failed_controls(self):
        self.assertEqual(72, len(self.rows))
        self.assertEqual(self.rows, layout.family(root=self.root))
        self.assertEqual(72, len({r['layout_id'] for r in self.rows}))
        self.assertEqual(50, sum(r['engineering_screen']=='pass' for r in self.rows))
        self.assertEqual(22, sum(r['engineering_screen']=='fail' for r in self.rows))
        for row in self.rows:
            self.assertTrue(layout.validate_layout(row, root=self.root))

    def test_capacity_follows_fitted_seating_and_counts_wheelchair_users(self):
        r = self.primary
        self.assertEqual((48, 0, 48), (r['transverse_seats'], r['bench_seats'], r['seats_total']))
        self.assertEqual(50, r['passenger_limit'])
        self.assertEqual(50, r['geometrically_placed_passengers'])
        self.assertEqual(3750., r['payload_kg'])
        self.assertEqual(0, r['standing_passengers'])
        self.assertIsNone(r['wheelchair_device_additional_mass_kg'])
        self.assertEqual(1., r['seated_or_wheelchair_share'])

    def test_one_side_two_doors_preserves_two_active_platform_doors(self):
        baseline = self.rows[0]
        self.assertEqual((4,2,False), (baseline['doors_total'], baseline['active_doors_per_platform'], baseline['one_side']))
        self.assertEqual((2,2,True), (self.primary['doors_total'], self.primary['active_doors_per_platform'], self.primary['one_side']))
        self.assertEqual(0, baseline['bench_seats'])
        self.assertTrue(baseline['comfort_claims']['bench_omissions'])
        self.assertIn('Platform compatibility', ' '.join(self.primary['unknown']))

    def test_seat_module_uses_inner_width_and_negative_control_is_retained(self):
        r = self.primary; box = r['geometry']['clear_envelope']
        self.assertAlmostEqual(2.5606, box['y1_m']-box['y0_m'])
        self.assertAlmostEqual(.0306, (box['y1_m']-box['y0_m'])-(4*.47+.65))
        wide = next(x for x in self.rows if x['input_parameters']['seating_hypothesis']['seat_width_m']==.48)
        self.assertEqual('fail', wide['engineering_screen'])
        self.assertTrue(wide['necessary_definition_checks']['out_of_bounds'])
        dense = dict(layout.SEAT_OPTIONS[0], id='dense-negative-control', pitch_m=.65)
        rejected = layout.make_layout(seat_option=dense, root=self.root)
        self.assertGreater(rejected['seats_total'], r['seats_total'])
        self.assertIn('row-pitch-below-declared-800mm-comfort-screen', rejected['failure_reasons'])

    def test_occupants_posts_and_furniture_access_paths_do_not_overlap(self):
        for r in self.rows:
            if r['engineering_screen']=='pass':
                for values in r['necessary_definition_checks'].values():
                    self.assertEqual([], values)
                for route in r['geometry']['access_path_graph']['assigned_bay_routes']:
                    self.assertTrue(route['rectangle_union_connected'])
                    self.assertFalse(route['swept_route_approved'])
        self.assertFalse(self.primary['comfort_claims']['full_car_width_wheelchair_through_route'])

    def test_two_blanked_original_apertures_count_even_with_new_boarding_doors(self):
        for r in self.rows:
            stock = r['infill_stock']
            if r['one_side']:
                self.assertEqual(2, stock['blanked_original_openings'])
                self.assertAlmostEqual(5.88, stock['area_m2'])
                self.assertAlmostEqual(67.62, stock['total_mass_kg'])
                self.assertEqual(r['doors_total']-2, stock['new_openings'])
                self.assertEqual(0., stock['cut_material_removal_credit_kg'])
                self.assertTrue(stock['retained_original_opening_frames'])
            else:
                self.assertEqual(0., stock['total_mass_kg'])
            self.assertIsNone(stock['installed_mass_kg'])

    def test_benches_and_fixtures_are_material_stock_not_zero_mass(self):
        stock = self.benches['seating_stock']
        self.assertAlmostEqual(math.fsum(p['mass_kg'] for p in stock['stock_parts']), stock['total_mass_kg'])
        benches = [p for p in stock['stock_parts'] if p['id'].startswith('wall-bench-seat/')]
        self.assertEqual(4, len(benches))
        self.assertEqual([6,6,6,24], [p['quantity'] for p in benches])
        self.assertGreater(sum(p['mass_kg'] for p in benches), 0)
        self.assertIsNone(stock['installed_mass_kg'])
        self.assertEqual((36,6,44), (self.benches['transverse_seats'], self.benches['bench_seats'],self.benches['passenger_limit']))

    def test_seat_stock_resolves_within_interior_budget_without_tare_credit(self):
        for r in self.rows:
            budget = r['seating_budget']
            self.assertEqual(800., budget['retained_interior_allowance_kg'])
            self.assertAlmostEqual(800., budget['identified_seating_stock_kg']+budget['retained_unlocated_remainder_kg'])
            self.assertEqual(0., budget['known_stock_excess_kg'])
            self.assertEqual(0., budget['mass_delta_kg'])
            self.assertTrue(all(budget['source_chain_sha_matches'].values()))
            self.assertIsNone(r['installed_tare_kg'])

    def test_demand_controls_cannot_turn_unplaced_people_into_comfort(self):
        for r in self.rows:
            self.assertEqual([80,100,120], [c['proposed_passenger_limit'] for c in r['proposal_demand_controls']])
            self.assertTrue(all(c['engineering_screen']=='fail' for c in r['proposal_demand_controls']))
        r = layout.make_layout(standing_passengers=100, root=self.root)
        self.assertEqual('fail', r['engineering_screen'])
        self.assertIn('insufficient-nonoverlapping-standing-slots', r['failure_reasons'])
        self.assertLess(r['geometrically_placed_passengers'], r['passenger_limit'])

    def test_overcrowding_and_aw3_remain_distinct_from_proposed_cap(self):
        r = self.primary; overload = r['overload_sensitivity']
        self.assertEqual(4., overload['research_crowd_density_persons_m2'])
        self.assertGreater(overload['geometric_crowd_passengers'], r['passenger_limit'])
        self.assertEqual((160,12000.), (overload['retained_AW3_passengers'], overload['retained_AW3_payload_kg']))
        self.assertFalse(overload['service_limit_is_enforced'])
        self.assertFalse(overload['structural_load_reduction_authorised'])

    def test_operating_capacity_change_does_not_invent_new_physical_geometry(self):
        zero = self.primary
        four = layout.make_layout(standing_passengers=4, vestibule_length_m=1.5,
                                  wheelchair_location='best-fit', root=self.root)
        self.assertEqual(zero['physical_geometry_id'], four['physical_geometry_id'])
        self.assertNotEqual(zero['layout_id'], four['layout_id'])
        self.assertEqual(54, four['passenger_limit'])
        self.assertEqual('pass', four['engineering_screen'])

    def test_default_preserves_requested_door_benches_and_zero_standing(self):
        r=layout.make_layout(root=self.root)
        self.assertEqual((40,4,2,0,46), (r['transverse_seats'],r['bench_seats'],r['wheelchair_places'],r['standing_passengers'],r['passenger_limit']))
        self.assertEqual('benches-first',r['input_parameters']['wheelchair_location'])
        self.assertEqual('pass',r['engineering_screen'])
        options=layout.primary_options(root=self.root)
        self.assertEqual([46,50,44],[r['passenger_limit'] for r in options.values()])

    def test_refined_offsets_and_wc_arrangements_preserve_failed_trials(self):
        r = self.primary
        self.assertEqual('opposite-door', r['geometry']['wheelchair_location'])
        self.assertEqual({'outer-ends','adjacent-doors','opposite-door'},
                         {p['wheelchair_location'] for p in r['packing_trials']})
        adjacent = next(p for p in r['packing_trials'] if p['wheelchair_location']=='adjacent-doors')
        self.assertTrue(adjacent['packing_violations'])
        self.assertTrue(any(trial['row_origins_tested']>1 for p in r['packing_trials'] for trial in p['row_offset_search']))
        self.assertEqual(0, r['bench_seats'])
        self.assertTrue(any('Wheelchair users' in item['reason'] for item in r['comfort_claims']['bench_omissions']))

    def test_svg_explains_capacity_and_hypotheses(self):
        from xml.etree import ElementTree
        drawing=layout.render_svg(self.primary)
        ElementTree.fromstring(drawing)
        self.assertIn('48 seats +2 wheelchair users +0 standing',drawing)
        self.assertIn('remain unapproved',drawing)

    def test_every_result_rebuild_rejects_tampering_or_mixed_identity(self):
        for path in [('passenger_limit',), ('seating_stock','total_mass_kg'),
                     ('engineering_accepted',), ('physical_geometry_id',)]:
            changed = deepcopy(self.primary); node = changed
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = 'tampered'
            with self.assertRaisesRegex(ValueError, 'differs'):
                layout.validate_layout(changed, root=self.root)

    def test_stale_ancestor_allocation_is_rejected_before_budget_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in layout.SOURCE_FILES:
                target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((self.root/name).read_bytes())
            target = root/layout.SOURCE_FILES[0]
            target.write_text(target.read_text()+'\n# changed source\n')
            with self.assertRaisesRegex(ValueError, 'source chain differs'):
                layout.family(root=root)

    def test_sources_and_acceptance_flags_are_explicit(self):
        for r in self.rows:
            self.assertEqual('hold', r['physical_acceptance'])
            self.assertTrue(all(r[key] is False for key in layout.FALSE_FLAGS))
            self.assertIn('engineering/comfort_options/layout.py', r['source_sha256'])
            self.assertEqual(24.+r['doors_total'], r['glazing']['total_area_m2'])
            self.assertEqual(2*r['doors_total'], r['glazing']['door_leaf_count'])


if __name__ == '__main__':
    unittest.main()
