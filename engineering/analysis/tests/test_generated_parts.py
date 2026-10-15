"""Independent geometry/function invariants for finite native part families."""

from copy import deepcopy
import itertools
import math
import unittest

import numpy as np

from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.generated_parts import (
    compile_definition,
    defaults,
    screen_definition,
    validate_definition,
    variables,
)
from engineering.design_engine.generated_parts_native import (
    NativeFailure,
    read_results,
    write_deck,
)


class GeneratedPartsTests(unittest.TestCase):
    def test_all_twelve_designs_are_distinct_and_keep_fixed_functions(self):
        for family in ("mechanical-cleat", "civil-steel-beam"):
            specs = variables(family)
            keys = list(specs)
            models = [
                compile_definition(family, dict(zip(keys, values)))
                for values in itertools.product(*(specs[k]["choices"] for k in keys))
            ]
            self.assertEqual(len(models), 6)
            self.assertEqual(len({m["physical_definition_sha256"] for m in models}), 6)
            self.assertEqual(len({fingerprint(m["loads"]) for m in models}), 1)
            self.assertEqual(len({fingerprint(m["supports"]) for m in models}), 1)
            for model in models:
                self.assertIs(validate_definition(model), model)
                self.assertFalse(model["physical_validation"])
                self.assertFalse(model["production_released"])

    def test_holes_remove_exact_mass_and_shift_centre_away_from_attachment_end(self):
        model = compile_definition("mechanical-cleat")
        props = model["parts"][0]["properties"]
        removed = 2 * math.pi * 0.003**2 * 0.012
        outer = 0.2 * 0.05 * 0.012
        self.assertAlmostEqual(props["volume_m3"], outer - removed, places=16)
        self.assertAlmostEqual(props["mass_kg"], 7850 * (outer - removed), places=12)
        self.assertAlmostEqual(
            props["cg_m"][0],
            (outer * 0.1 - removed * 0.025) / (outer - removed),
            places=14,
        )
        self.assertGreater(props["cg_m"][0], 0.1)
        light = compile_definition("mechanical-cleat", dict(topology="lightened-web"))
        self.assertAlmostEqual(
            props["mass_kg"] - light["parts"][0]["properties"]["mass_kg"],
            7850 * math.pi * 0.008**2 * 0.012,
            places=12,
        )

    def test_rhs_integrals_match_independent_section_formula(self):
        model = compile_definition("civil-steel-beam")
        props = model["parts"][0]["properties"]
        b, h, t, length, density = 0.1, 0.14, 0.006, 1.5, 7850
        area = b * h - (b - 2 * t) * (h - 2 * t)
        section_i = (b * h**3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12
        self.assertAlmostEqual(props["mass_kg"], density * area * length, places=10)
        # About the member CG: integral x^2 + z^2, not just section inertia.
        self.assertAlmostEqual(
            props["inertia_tensor_kg_m2"][1][1],
            density * (area * length**3 / 12 + section_i * length),
            places=10,
        )
        np.testing.assert_allclose(props["cg_m"], [0.75, 0, 0], atol=1e-14)

    def test_fixed_load_or_material_cannot_be_rehashed_into_same_family(self):
        model = compile_definition("mechanical-cleat")
        model["loads"][0]["force_n"][2] = -1
        model["physical_definition_sha256"] = fingerprint(
            {k: v for k, v in model.items() if k != "physical_definition_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "fixed function"):
            validate_definition(model)

    def test_unknown_nonfinite_or_changed_scope_selection_is_rejected(self):
        for values in (
            {"span_m": 0.01},
            {"thickness_m": float("nan")},
            {"thickness_m": True},
            {"topology": "no-holes"},
        ):
            with self.assertRaises(ValueError):
                compile_definition("mechanical-cleat", values)

    def test_analytical_screen_does_not_create_native_or_physical_pass(self):
        result = screen_definition(compile_definition("mechanical-cleat"))
        for key in (
            "linear_service",
            "mesh_refinement",
            "load_equilibrium",
            "independent_benchmark",
        ):
            self.assertEqual(result["checks"][key]["state"], "not-run")
        self.assertEqual(result["checks"]["physical_correlation"]["state"], "unknown")
        self.assertIsNone(result["metrics"]["loaded_face_deflection_m"])

    def test_mesh_missing_root_or_nonconserving_traction_is_rejected(self):
        from pathlib import Path
        import tempfile

        model = compile_definition("mechanical-cleat")
        with tempfile.TemporaryDirectory() as tmp:
            for mesh in [
                dict(nodes={}, root_nodes=[], tip_weights={}),
                dict(nodes={"1": [0, 0, 0]}, root_nodes=[1], tip_weights={"2": 0.5}),
            ]:
                with self.assertRaises(NativeFailure):
                    write_deck(model, mesh, {}, Path(tmp) / "bad.inp")

    def test_truncated_stress_field_cannot_publish_peak_demand(self):
        from pathlib import Path
        import tempfile

        mesh = dict(
            nodes={"1": [0, 0, 0], "2": [1, 0, 0]},
            root_nodes=[1],
            tip_weights={"2": 1},
            element_ids=[1],
        )
        text = "displacements\n1 0 0 0\n2 0 0 -.001\nforces\n1 0 0 1\nstresses\n1 1 1 0 0 0 0 0\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "truncated.dat"
            path.write_text(text)
            with self.assertRaisesRegex(NativeFailure, "complete finite"):
                read_results(path, mesh, [0, 0, -1])


if __name__ == "__main__":
    unittest.main()
