"""Independent deck/parser/process contracts; no native solves during unit tests."""
import importlib.util
import json
from math import fsum
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

spec=importlib.util.spec_from_file_location('osr_calculix_reference',
    Path(__file__).resolve().parents[1]/'engineering/design_search/craft_backends/calculix_reference.py')
ccx=importlib.util.module_from_spec(spec);spec.loader.exec_module(ccx)


def synthetic_dat(definition,scale=1.,reaction_scale=1.):
    """Synthetic format boundary fixture, never represented as native evidence."""
    u=[0.,0.,0.];u[definition['component']]=definition['theory_displacement_m']*scale
    force=[-f*reaction_scale/len(definition['root_nodes']) for f in definition['applied_N']]
    return '\n'.join(['displacements (vx,vy,vz) for set TIP and time 1.0', '',
        str(definition['tip_node'])+' '+' '.join(map(str,u)), '',
        # RF at a load is an external load, not a support reaction: ignore it.
        'forces (fx,fy,fz) for set TIP and time 1.0',
        str(definition['tip_node'])+' '+' '.join(map(str,definition['applied_N'])),
        'forces (fx,fy,fz) for set ROOT and time 1.0', '',
        *[str(n)+' '+' '.join(map(str,force)) for n in definition['root_nodes']]])


class IndependentDecks(unittest.TestCase):
    def test_matched_mesh_geometry_counts_and_tip(self):
        for divisions,nodes,elements in [((8,2,2),261,32),((16,4,4),1505,256)]:
            deck,definition=ccx.cantilever_deck(divisions)
            self.assertEqual(definition['units'],'m-kg-s-N-Pa')
            self.assertEqual(definition['node_count'],nodes)
            self.assertEqual(definition['element_count'],elements)
            self.assertEqual(definition['node_xyz_m'][str(definition['tip_node'])],[1.,.05,.05])
            self.assertIn('*ELEMENT,TYPE=C3D20,ELSET=SOLID',deck)
            self.assertNotIn('TYPE=C3D20R',deck)
            self.assertIn('70000000000,0',deck)
            self.assertEqual(len(definition['root_nodes']),21 if divisions[1]==2 else 65)
            lines=deck.split('*ELEMENT,TYPE=C3D20,ELSET=SOLID\n')[1].split('*NSET')[0].splitlines()
            self.assertEqual(len(lines),2*elements)
            for i in range(0,len(lines),2):
                conn=[int(v) for v in (lines[i]+lines[i+1]).split(',')]
                self.assertEqual(len(conn),21)
                self.assertEqual(len(set(conn[1:])),20)
                self.assertTrue(all(str(n) in definition['node_xyz_m'] for n in conn[1:]))

    def test_consistent_quadratic_face_force_and_moment(self):
        for divisions in [(8,2,2),(16,4,4)]:
            _,d=ccx.cantilever_deck(divisions)
            self.assertEqual(d['applied_N'],[0.,0.,-1000.])
            self.assertAlmostEqual(fsum(v[2] for v in d['tip_load_N'].values()),-1000.)
            self.assertTrue(any(v[2]>0 for v in d['tip_load_N'].values()))
            moment=[0.,0.,0.]
            for n,f in d['tip_load_N'].items():
                x,y,z=d['node_xyz_m'][n]
                self.assertEqual(x,1.)
                moment[0]+=y*f[2];moment[1]-=x*f[2]
            self.assertAlmostEqual(moment[0],-50.)
            self.assertAlmostEqual(moment[1],1000.)
            self.assertAlmostEqual(d['theory_displacement_m'],-.0005748571428571429)

    def test_bounded_predeclared_meshes_only(self):
        for divisions in [(8.,2,2),(True,2,2),(8,2),(64,8,8),(1,1,1),'8x2x2']:
            with self.subTest(divisions=divisions),self.assertRaises(ValueError):
                ccx.cantilever_deck(divisions)

    def test_axial_definition_and_root_only_output(self):
        deck,d=ccx.axial_deck()
        self.assertIn('TYPE=T3D2',deck)
        self.assertIn('0.0001',deck)
        self.assertIn('*NODE PRINT,NSET=TIP\nU',deck)
        self.assertIn('*NODE PRINT,NSET=ROOT\nRF',deck)
        self.assertAlmostEqual(d['theory_displacement_m'],4.285714285714286e-5)


class DatParsing(unittest.TestCase):
    def test_declared_tip_and_root_only(self):
        for factory in [ccx.cantilever_deck,ccx.axial_deck]:
            _,definition=factory()
            r=ccx.parse_dat(synthetic_dat(definition),definition)
            self.assertTrue(r['numerical_screen_passed'])
            self.assertAlmostEqual(r['relative_theory_error'],0.)
            self.assertAlmostEqual(r['force_equilibrium_relative_residual'],0.)
            self.assertTrue(all(r[k] is False for k in ccx.FLAGS))

    def test_native_format_d_exponents(self):
        _,d=ccx.axial_deck()
        text='displacements (vx,vy,vz) for set TIP and time 1.0\n2 4.285714D-05 0 0\nforces (fx,fy,fz) for set ROOT and time 1.0\n1 -1D3 0 0'
        r=ccx.parse_dat(text,d)
        self.assertEqual(r['reaction_N'],[-1000.,0.,0.])
        self.assertTrue(r['numerical_screen_passed'])

    def test_incomplete_nonfinite_duplicate_blocks_rejected(self):
        _,d=ccx.axial_deck();valid=synthetic_dat(d)
        for text in ['',valid.split('forces')[0],valid.replace('2 4.2857142857142856e-05','2 nan'),
                     valid+'\n1 -1000 0 0',valid.replace('set ROOT','set MISSING')]:
            with self.subTest(text=text),self.assertRaises(ValueError):
                ccx.parse_dat(text,d)

    def test_calculation_survives_failed_screen(self):
        _,d=ccx.axial_deck()
        for text in [synthetic_dat(d,scale=2),synthetic_dat(d,reaction_scale=.9)]:
            r=ccx.parse_dat(text,d)
            self.assertFalse(r['numerical_screen_passed'])
            self.assertFalse(r['engineering_accepted'])
            self.assertFalse(r['physical_accepted'])

    def test_parser_byte_budget(self):
        _,d=ccx.axial_deck()
        with self.assertRaises(ValueError):ccx.parse_dat(' '*((16*1024**2)+1),d)


class BoundedRunner(unittest.TestCase):
    def test_resource_request_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            for kw in [dict(timeout_s=121),dict(timeout_s=True),dict(memory_mb=2049),dict(memory_mb=127)]:
                with self.subTest(kw=kw),self.assertRaises(ValueError):ccx.run(out,**kw)
                self.assertFalse(out.exists())

    def test_nonempty_and_empty_existing_directories_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):ccx.run(tmp)
            marker=Path(tmp)/'user.txt';marker.write_text('preserve')
            with self.assertRaises(ValueError):ccx.run(tmp)
            self.assertEqual(marker.read_text(),'preserve')

    def test_missing_executables_produce_nonpromoting_hold(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(ccx.shutil,'which',return_value=None),patch.object(ccx.subprocess,'Popen') as process:
            out=Path(tmp)/'run';r=ccx.run(out)
            self.assertEqual(r['state'],'held');process.assert_not_called()
            self.assertEqual(r['cases'],{})
            self.assertEqual(json.loads((out/'result.json').read_text()),r)
            self.assertEqual(r['sources_sha256'][ccx.SOURCE],ccx._digest(ccx.__file__))
            self.assertTrue(all(r[k] is False for k in ccx.FLAGS))

    def test_failed_spawns_preserve_three_independent_requests(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(ccx.shutil,'which',return_value='/bin/true'),patch.object(ccx.subprocess,'Popen',side_effect=OSError('synthetic unavailable process')) as process:
            out=Path(tmp)/'run';r=ccx.run(out)
            self.assertEqual(process.call_count,3)
            self.assertEqual(r['state'],'failed')
            for name,row in r['cases'].items():
                self.assertEqual(row['state'],'failed')
                self.assertTrue((out/name/'control.inp').exists())
                self.assertTrue((out/name/'request.json').exists())
                self.assertTrue((out/name/'failure.json').exists())

    def test_timeout_preserves_partial_logs_and_kills_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'case';deck,d=ccx.axial_deck()
            process=MagicMock(pid=987654,returncode=-9)
            process.communicate.side_effect=[subprocess.TimeoutExpired('test',1),(b'partial stdout',b'partial stderr')]
            with patch.object(ccx.subprocess,'Popen',return_value=process),patch.object(ccx.os,'killpg') as kill:
                r=ccx._execute(folder,deck,d,{k:'/bin/true' for k in ('ccx','time','bwrap')},1,128)
            kill.assert_called_once_with(987654,ccx.signal.SIGKILL)
            self.assertEqual(r['state'],'interrupted')
            self.assertEqual((folder/'stdout.log').read_bytes(),b'partial stdout')
            self.assertEqual((folder/'stderr.log').read_bytes(),b'partial stderr')
            self.assertIn('control.inp',r['files_sha256'])
            self.assertFalse(r['physical_accepted'])


if __name__=='__main__':unittest.main()
