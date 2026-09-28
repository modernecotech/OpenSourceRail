import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    'example_city_scenario', ROOT / 'deployment/example-city/scenario.py'
)
SCENARIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCENARIO)


class ExampleCityScenarioTests(unittest.TestCase):
    def test_engineering_manifest_uses_generated_city_revision(self):
        source = {'city': 'samawah', 'asset_id': 'SAM-ST-001'}
        bound = SCENARIO.bind_engineering_manifest(
            source, {'city': 'samawah', 'engineering_revision': 'twin-current'}
        )

        self.assertEqual(bound['engineering_revision'], 'twin-current')
        self.assertNotIn('engineering_revision', source)

    def test_stale_pinned_revision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'pins stale revision'):
            SCENARIO.bind_engineering_manifest(
                {'city': 'samawah', 'engineering_revision': 'twin-old'},
                {'city': 'samawah', 'engineering_revision': 'twin-current'},
            )

    def test_manifest_cannot_bind_to_another_city(self):
        with self.assertRaisesRegex(ValueError, 'does not match package city'):
            SCENARIO.bind_engineering_manifest(
                {'city': 'samawah'},
                {'city': 'mosul', 'engineering_revision': 'twin-current'},
            )


if __name__ == '__main__':
    unittest.main()
