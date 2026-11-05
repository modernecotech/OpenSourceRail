"""Protect source geometry and the boundary between proposals and engineering evidence."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import unittest
import tempfile
from engineering.visual_models import core, station

ROOT=Path(__file__).resolve().parents[3]


class ModelContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assemblies,cls.sources=core.collect(ROOT)
        cls.models={a['id']:a for a in cls.assemblies}
        cls.record=json.loads(gzip.decompress((ROOT/'docs/design-engine/current/evaluation.json.gz').read_bytes()))

    def test_source_car_parts_and_holes_survive_without_coordinate_changes(self):
        source={p['id']:p for p in self.record['vehicle']['geometry_parts']}
        actual={e['source_part_id']:e for e in self.models['vehicle-fabrication']['entities'] if 'source_part_id' in e}
        self.assertEqual(set(actual),set(source))
        for name,part in source.items():
            entity=actual[name]
            self.assertEqual(entity['at_m'],part['at_m'])
            self.assertEqual(entity.get('holes',[]),part.get('holes',[]))
            self.assertAlmostEqual(core.volume(entity),part['volume_m3'],places=9)
        self.assertAlmostEqual(sum(e['source_mass_kg'] for e in actual.values()),9131.798543,places=3)
        self.assertTrue(any(e.get('holes') for e in actual.values()))

    def test_station_absolute_routes_are_not_translated_twice(self):
        scene=station.Scene('test','Test','',{})
        scene.pipe('route',[(10.,-3.,1.),(12.,-3.,1.)],.02)
        lo,hi=core.bounds(scene.value['entities'][0])
        self.assertEqual(lo,[9.98,-3.02,.98])
        self.assertEqual(hi,[12.02,-2.98,1.02])
        for name in ('station-overview','arrestor-storage','launcher-booster'):
            for e in self.models[name]['entities']:
                if e['shape']=='pipe':self.assertEqual(e['at_m'],[0,0,0])

    def test_motion_source_and_scenario_are_bound(self):
        for name in (station.REFERENCE,station.EVALUATION,'engineering/station_energy/data/arrestor-scenario.json'):
            self.assertEqual(self.sources[name],core.digest(ROOT/name))
        source=json.loads((ROOT/station.REFERENCE).read_bytes())
        ctx=self.models['station-overview']['reference_context']
        self.assertEqual(ctx['source_publication_id'],source['publication_id'])
        self.assertEqual(ctx['reference_evaluation_id'],self.record['evaluation_id'])

    def test_concrete_is_disjoint_source_stock(self):
        for name in ('viaduct-crane','viaduct-gantry','precast-fabrication'):
            stock=[e for e in self.models[name]['entities'] if e['material']=='concrete' and e['basis']=='source-geometry']
            prefixes={e['id'].split('-beam-')[0] for e in stock}
            for prefix in prefixes:
                beam=[e for e in stock if e['id'].startswith(prefix+'-beam-')]
                self.assertEqual(len(beam),6)
                self.assertAlmostEqual(sum(core.volume(e) for e in beam),22.2816,places=7)
                for i,e in enumerate(beam):
                    a,b=core.bounds(e)
                    for f in beam[i+1:]:
                        c,d=core.bounds(f)
                        self.assertFalse(all(min(q,s)-max(p,r)>1e-8 for p,q,r,s in zip(a,b,c,d)))

    def test_visual_ids_are_repeatable_and_cannot_promote_release(self):
        for a in self.assemblies:
            self.assertEqual(core.validate(deepcopy(a))['visual_study_id'],a['visual_study_id'])
            for key in core.FLAGS:self.assertIs(a[key],False)
        bad=deepcopy(self.assemblies[0]);bad['physical_accepted']=True
        with self.assertRaisesRegex(ValueError,'cannot grant'):core.validate(bad)
        bad=deepcopy(self.assemblies[0]);bad['entities'][0]['manufacturing_release']=True
        with self.assertRaisesRegex(ValueError,'cannot promote'):core.validate(bad)

    def test_proposed_core_does_not_occupy_concrete(self):
        entities=self.models['precast-fabrication']['entities']
        concrete=[e for e in entities if e['material']=='concrete' and e['basis']=='source-geometry']
        cores=[e for e in entities if e['group']=='void-former']
        self.assertEqual(len(cores),4)
        for e in cores:
            a,b=core.bounds(e)
            for f in concrete:
                c,d=core.bounds(f)
                self.assertFalse(all(min(q,s)-max(p,r)>1e-8 for p,q,r,s in zip(a,b,c,d)))

    def test_proposed_bearing_seats_are_inside_stock_and_not_source_analysis(self):
        for name in ('viaduct-crane','viaduct-gantry'):
            a=self.models[name];bearings=[e for e in a['entities'] if e['group']=='bearings']
            self.assertEqual(len(bearings),8)
            for e in bearings:
                lo,hi=core.bounds(e)
                self.assertTrue(any(lo[0]>=x and hi[0]<=x+20 for x in (0,20)))
                self.assertAlmostEqual(hi[2],-1.592)
            self.assertEqual(a['metrics']['proposed_bearing_centre_spacing_m'],19.4)
            self.assertIs(a['metrics']['source_analytical_results_apply_to_proposed_bearing_layout'],False)

    def test_bad_source_geometry_and_zero_length_routes_are_rejected(self):
        bad=deepcopy(self.models['vehicle-fabrication']);e=next(e for e in bad['entities'] if 'source_volume_m3' in e)
        e['source_volume_m3']*=2
        with self.assertRaisesRegex(ValueError,'volume differs'):core.validate(bad)
        bad=deepcopy(self.models['arrestor-storage']);e=next(e for e in bad['entities'] if e['shape']=='pipe')
        e['path_m']=[e['path_m'][0]]*2
        with self.assertRaisesRegex(ValueError,'Nonzero route'):core.validate(bad)

    def test_published_native_exports_replay(self):
        from engineering.visual_models.publication import verify
        result=verify(ROOT/'docs/engineering-models',ROOT)
        self.assertEqual(result['assemblies'],8)
        self.assertFalse(result['physical_accepted'])

    def test_frozen_drawing_survives_other_evaluations_but_not_geometry_changes(self):
        from engineering.visual_models.publication import verify
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'docs/design-engine/current/evaluation.json.gz';p.parent.mkdir(parents=True)
            changed=deepcopy(self.record);changed['evaluation_id']='different-cost-or-evaluation-epoch'
            p.write_bytes(gzip.compress(core.encoded(changed),mtime=0))
            result=verify(ROOT/'docs/engineering-models',root)
            self.assertTrue(result['reference_geometry_current'])
            self.assertFalse(result['source_epoch_current'])
            changed['vehicle']['geometry_parts'][0]['at_m'][0]+=.1
            p.write_bytes(gzip.compress(core.encoded(changed),mtime=0))
            with self.assertRaisesRegex(ValueError,'physical stock differs'):
                verify(ROOT/'docs/engineering-models',root)


if __name__=='__main__':unittest.main()
