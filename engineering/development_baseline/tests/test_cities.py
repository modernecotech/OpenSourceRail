"""Current-city regressions, including formerly different formations and failures."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import math
import os
import tempfile
import unittest

from engineering.development_baseline import cities, selection


ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT','/home/hayder/Documents/OpenSourceRail')).resolve()


def line(distance=2000.):
    return dict(line='fixture-line',retained_length_m=distance,
        stations=[dict(id='a',s_m=0.,lat=0.,lon=0.),dict(id='b',s_m=distance,lat=0.,lon=.01)],
        duty=dict(arrival_events_per_circuit=[
            dict(origin_station='a',destination_station='b',distance_m=distance,terminal_loop_allowance=False),
            dict(origin_station='b',destination_station='a',distance_m=distance,terminal_loop_allowance=False)]))


class CurrentCities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=selection.load(ROOT)
        cls.baghdad=cities.evaluate_city('baghdad',cls.baseline,root=ROOT)
        cls.benguela=cities.evaluate_city('benguela',cls.baseline,root=ROOT)

    def test_baghdad_reproduces_selected_retained_stop_alternative(self):
        result=self.baghdad; reference=self.baseline['network_proposal']; t=result['totals']
        for key in ('total_trainsets','additional_line_stop_sites','total_direction_winding_m',
                    'peak_active_trainsets','station_library_counts','motor_overlap_count'):
            self.assertEqual(t[key],reference[key])
        self.assertEqual(t['total_trainsets'],906)
        self.assertEqual(t['additional_line_stop_sites'],0)
        self.assertEqual(t['total_direction_winding_m'],390500.)
        self.assertEqual(result['service']['normal_capacity_pphpd_arithmetic'],8280.)
        self.assertFalse(result['service']['retained_14400_pphpd_comparison_met'])

    def test_former_three_car_city_uses_six_car_comfort_default(self):
        result=self.benguela
        self.assertEqual(result['vehicle']['cars'],6)
        self.assertEqual(result['vehicle']['normal_people_per_train'],276)
        self.assertEqual(result['vehicle']['standing_passengers_per_car'],0)
        self.assertEqual(result['totals']['cars'],6*result['totals']['total_trainsets'])
        self.assertEqual(result['vehicle']['accounted_cap_loaded_kg_per_car'],
                         self.baseline['vehicle']['mass']['accounted_cap_loaded_kg_per_car'])
        self.assertEqual(result['service']['headway_s'],120.)
        self.assertNotIn('aw2_capacity_per_direction_hour',json.dumps(result))

    def test_rejects_non_six_car_defaults_and_mixed_candidate(self):
        bad=deepcopy(self.baseline);bad['selection']['vehicle']['cars']=3
        with self.assertRaises(ValueError):
            cities.evaluate_city('baghdad',bad,root=ROOT)
        bad=deepcopy(self.baseline);bad['vehicle']['candidate_id']='0'*64
        with self.assertRaisesRegex(ValueError,'identity differs'):
            cities.evaluate_city('baghdad',bad,root=ROOT)
        bad=deepcopy(self.baseline);bad['vehicle']['mass']['accounted_tare_kg_per_car']-=1000.
        with self.assertRaises(ValueError):
            cities.evaluate_city('baghdad',bad,root=ROOT)

    def test_mass_is_propagated_to_motion_energy_station_force_and_fleet(self):
        mass=self.baseline['vehicle']['mass']['accounted_cap_loaded_kg_per_car']
        a=cities._line(line(),self.baseline['selection'],mass)
        b=cities._line(line(),self.baseline['selection'],mass+1000.)
        # The same prescribed launch speed and distance have equal drag work;
        # added kinetic energy is independently calculable, without a second model.
        expected_per_circuit=2*6*.5*1000.*20.**2/3.6e6
        self.assertAlmostEqual(b['mainline_mechanical_launch_kWh_per_circuit']-
                               a['mainline_mechanical_launch_kWh_per_circuit'],expected_per_circuit,places=9)
        self.assertNotEqual(a['circuit_s'],b['circuit_s'])
        self.assertNotEqual(a['peak_required_train_mechanical_kW'],b['peak_required_train_mechanical_kW'])
        self.assertEqual(b['peak_trainsets'],math.ceil(b['circuit_s']/120.))

    def test_unreachable_leg_is_a_retained_failure_not_a_zero_quantity(self):
        mass=self.baseline['vehicle']['mass']['accounted_cap_loaded_kg_per_car']
        result=cities._line(line(100000.),self.baseline['selection'],mass)
        self.assertEqual(len(result['coast_failures']),2)
        self.assertFalse(result['all_mainline_events_reachable'])
        for key in ('total_trainsets','circuit_s','direction_winding_m',
                    'mainline_mechanical_launch_kWh_per_circuit'):
            self.assertIsNone(result[key])
        self.assertGreater(result['coast_failures'][0]['shortfall_m'],0.)

    def test_geometry_quantities_and_unknown_prices_do_not_inherit_legacy_claims(self):
        value=self.benguela
        q=value['quantities']; length=2*value['totals']['retained_route_length_m']
        self.assertAlmostEqual(q['mainline_counted_steel_stock_kg'],
                               length/q['reference_span_m']*q['counted_steel_stock_kg_per_reference_span'])
        self.assertAlmostEqual(q['counted_steel_stock_tonnes_per_direction_km'],865.0931778841239)
        self.assertIsNone(q['reinforcement_prestress_endblocks_bearings_mass_kg'])
        self.assertIsNone(value['costs']['complete_CAPEX_USD'])
        self.assertIsNone(value['costs']['price_quote_coverage_fraction'])
        self.assertIsNone(value['energy']['actual_operating_energy_kWh'])
        self.assertFalse(value['physical_accepted'])
        self.assertFalse(value['gates']['protected_120s_headway'])

    def test_rejects_civil_from_another_selected_interface(self):
        spec=self.baseline['selection']; source=spec['source_design']
        civil=deepcopy(cities._source_civil(str(ROOT),source,self.baseline['source_sha256'][source]))
        civil['complete_counted_steel_stock_kg_per_span']*=.5
        civil['civil_interface_id']=selection.identity({k:v for k,v in civil.items() if k!='civil_interface_id'})
        with self.assertRaisesRegex(ValueError,'civil interface differs'):
            cities.evaluate_city('benguela',self.baseline,root=ROOT,civil=civil)

    def test_publish_integrity_and_readme_preserve_existing_geography(self):
        descriptor=next(r for r in cities.catalogue(ROOT) if r['slug']=='benguela')
        citypath=ROOT/descriptor['path']
        names=('city.json','engineering/maglev/summary.json','engineering/maglev/network.svg')
        before={name:sha256((citypath/name).read_bytes()).hexdigest() for name in names}
        with tempfile.TemporaryDirectory() as tmp:
            value=cities.publish_city(citypath,self.baseline,output=tmp,root=ROOT,update_readme=True)
            output=Path(tmp)/descriptor['path']
            manifest=json.loads((output/'engineering/current/manifest.json').read_bytes())
            for name,digest in manifest['files_sha256'].items():
                self.assertEqual(sha256((output/'engineering/current'/name).read_bytes()).hexdigest(),digest)
            text=(output/'README.md').read_text()
            self.assertIn('engineering/maglev/network.svg',text)
            self.assertIn('Historical ferrite planning package',text)
            self.assertIn('Primary planning method](../../../../../docs/design-engine/current/README.md)',text)
            self.assertIn('physical operation is not yet established',text)
            self.assertEqual(manifest['candidate_id'],value['candidate_id'])
            self.assertFalse(value['physical_accepted'])
        self.assertEqual(before,{name:sha256((citypath/name).read_bytes()).hexdigest() for name in names})

    def test_missing_current_index_never_falls_back_to_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError,'has not been generated'):
                cities.read_catalogue(tmp)


if __name__=='__main__':
    unittest.main()
