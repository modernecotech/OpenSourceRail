"""Offline packet integrity and untrusted archive rejection, without solvers."""
import gzip
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/publish_powered_bogie_detail.py'
PACKET=ROOT/'docs/design-engine/powered-bogie-detail'
spec=importlib.util.spec_from_file_location('bogie_packet_publisher',SCRIPT)
publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)


class PoweredBogiePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.packet=self.root/'packet'
        shutil.copytree(PACKET,self.packet)

    def reseal_outer(self):
        path=self.packet/'packet.json';p=json.loads(path.read_bytes())
        p['files_sha256']['source-and-run.tar.gz']=publisher.digest(self.packet/'source-and-run.tar.gz')
        p.pop('evaluation_id');p['evaluation_id']=publisher.identity(p)
        path.write_bytes(publisher.encoded(p))

    def change_archive(self,transform):
        path=self.packet/'source-and-run.tar.gz'
        rows=[]
        with tarfile.open(path,'r:gz') as tar:
            for m in tar:
                rows.append((m.name,tar.extractfile(m).read()))
        rows=transform(rows)
        raw=io.BytesIO()
        with tarfile.open(fileobj=raw,mode='w') as tar:
            for name,data in rows:
                info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644
                tar.addfile(info,io.BytesIO(data))
        path.write_bytes(gzip.compress(raw.getvalue(),mtime=0));self.reseal_outer()

    def test_existing_packet_verifies_without_current_checkout_or_git(self):
        # Copy just the verifier beside an empty working directory. No
        # engineering package, Git repository or archived code is imported.
        script=self.root/'standalone.py';shutil.copyfile(SCRIPT,script)
        result=subprocess.run([sys.executable,str(script),'verify','--packet',str(self.packet)],
            cwd=self.root,check=True,text=True,capture_output=True)
        record=json.loads(result.stdout)
        self.assertEqual(record['status'],'verified')
        self.assertEqual(record['artifact_files'],14)
        self.assertEqual(record['archive_members'],55)
        self.assertFalse(record['archived_code_executed'])
        self.assertFalse(record['current_producer_or_Git_required'])

    def test_legacy_publish_arguments_remain_supported(self):
        value={'candidate_id':'candidate','evaluation_id':'evaluation','files_sha256':{}}
        with patch.object(publisher,'publish',return_value=value) as publish:
            with patch('sys.stdout',new=io.StringIO()):publisher.main(['input-run','output-folder'])
        publish.assert_called_once_with(Path('input-run'),Path('output-folder'))

    def test_packet_seal_and_artifact_tamper_are_rejected(self):
        path=self.packet/'packet.json';p=json.loads(path.read_bytes())
        p['body_types']+=1;path.write_bytes(publisher.encoded(p))
        with self.assertRaisesRegex(ValueError,'seal differs'):publisher.verify(self.packet)
        shutil.copyfile(PACKET/'packet.json',path)
        (self.packet/'geometry.json').write_bytes((self.packet/'geometry.json').read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'Artifact hash differs'):publisher.verify(self.packet)

    def test_complete_inventory_and_nonordinary_artifacts_are_rejected(self):
        extra=self.packet/'unrecorded.txt';extra.write_text('unrecorded')
        with self.assertRaisesRegex(ValueError,'inventory differs'):publisher.verify(self.packet)
        extra.unlink()
        asset=self.packet/'assembly.svg';asset.unlink();asset.symlink_to(PACKET/'assembly.svg')
        with self.assertRaisesRegex(ValueError,'ordinary file'):publisher.verify(self.packet)

    def test_archive_traversal_is_rejected_even_when_outer_seal_is_recomputed(self):
        self.change_archive(lambda rows:rows+[('run/../../escape.py',b'raise RuntimeError("never execute")')])
        with self.assertRaisesRegex(ValueError,'path escapes'):publisher.verify(self.packet)
        self.assertFalse((self.root/'escape.py').exists())

    def test_archived_source_and_run_content_cannot_hide_under_outer_resealing(self):
        name='source/engineering/powered_bogie/design.py'
        self.change_archive(lambda rows:[(n,d+b'\n# tamper' if n==name else d) for n,d in rows])
        with self.assertRaisesRegex(ValueError,'Archived source snapshot hash differs'):publisher.verify(self.packet)
        shutil.copyfile(PACKET/'source-and-run.tar.gz',self.packet/'source-and-run.tar.gz')
        self.reseal_outer()
        name='run/retained-frame-control/geometry.json'
        self.change_archive(lambda rows:[(n,d+b' ' if n==name else d) for n,d in rows])
        with self.assertRaisesRegex(ValueError,'Archived run file hash differs'):publisher.verify(self.packet)

    def test_duplicate_archive_member_and_bounded_decompression_rejected(self):
        self.change_archive(lambda rows:rows+[rows[0]])
        with self.assertRaisesRegex(ValueError,'Duplicate archive member'):publisher.verify(self.packet)
        shutil.copyfile(PACKET/'source-and-run.tar.gz',self.packet/'source-and-run.tar.gz')
        self.reseal_outer()
        with patch.object(publisher,'MAX_ARCHIVE_BYTES',128):
            with self.assertRaisesRegex(ValueError,'Decompressed data exceeds bounded'):publisher.verify(self.packet)


if __name__=='__main__':unittest.main()
