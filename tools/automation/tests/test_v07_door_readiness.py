"""The Workbench door hold must fail closed on stale or mixed inputs."""
import json
from pathlib import Path
import tempfile
import unittest

from engineering.development_baseline.door_readiness import PACKET, summary


ROOT = Path(__file__).resolve().parents[3]
SOURCES = (
    PACKET,
    'docs/design-engine/v07-execution/door-interface-handoff.json',
    'docs/design-engine/v07-execution/door-route-request.json',
    'tools/automation/v07_door_pack_preflight.py',
)


class DoorReadinessTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for source in SOURCES:
            target = self.root / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / source).read_bytes())

    def test_current_packet_exposes_only_holds(self):
        value = summary(self.root)
        self.assertEqual(value['unnamed_part_document_count'], 74)
        self.assertEqual(value['unnamed_assembly_document_count'], 3)
        self.assertEqual(value['purchased_pieces_per_opening'], 597)
        self.assertFalse(value['pack_ready'])
        self.assertFalse(value['native_erp_admitted'])
        self.assertFalse(value['physical_accepted'])

    def test_changed_source_or_packet_is_held(self):
        route = self.root / SOURCES[2]
        route.write_bytes(route.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            summary(self.root)
        route.write_bytes((ROOT / SOURCES[2]).read_bytes())
        packet = self.root / PACKET
        value = json.loads(packet.read_bytes())
        value['pack_ready'] = True
        packet.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'source changed'):
            summary(self.root)

    def test_changed_generator_is_held(self):
        generator = self.root / SOURCES[3]
        generator.write_bytes(generator.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            summary(self.root)


if __name__ == '__main__':
    unittest.main()
