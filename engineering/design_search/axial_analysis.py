"""Prepare one axial/pin graph once for rigidity and linear-reference checks.

The unchanged ``grammar_structure`` functions remain the independent oracle.
This adapter only reuses their assembled arrays and validated stock within one
assessment; it introduces no material law, domain extension or acceptance gate.
NumPy continues to execute the SVD and linear solve through its compiled engine.
"""
from __future__ import annotations

from copy import deepcopy

import numpy as np

from engineering.station_rail.common import identity
from . import grammar_structure

PRODUCER = "engineering/design_search/axial_analysis.py"


class PreparedAxial:
    """Private assembled state with defensive public diagnostic/stock outputs."""

    def __init__(self, graph):
        self.__system = grammar_structure._system(graph)
        self.__input_graph_id = identity(self.__system["graph"])
        self.__diagnostic = None

    @property
    def stock(self):
        """Validated member records; caller edits cannot alter the prepared solve."""
        return deepcopy(self.__system["stock"])

    def __diagnose(self):
        if self.__diagnostic is None:
            s = self.__system
            free = s["free"]
            A = s["B"][:, free]
            _, sv, vh = np.linalg.svd(A, full_matrices=True)
            tolerance = max(1e-11, (float(sv[0]) if len(sv) else 1.) * 1e-10)
            rank = int(sum(sv > tolerance))
            mechanisms = len(free) - rank
            null = vh[rank:].T
            projection = float(np.linalg.norm(null.T @ s["F"][free])) if mechanisms else 0.
            vectors = []
            for j in range(min(mechanisms, 6)):
                full = np.zeros(len(s["F"]))
                full[free] = null[:, j]
                i = int(np.argmax(abs(full)))
                vectors.append(dict(maximum_component_node=s["ids"][i // 3], dof=i % 3 + 1,
                                    normalised_vector=full.tolist()))
            unknown = [m["id"] for m in s["stock"] if m["stock_mass_kg"] is None]
            known = sum(m["stock_mass_kg"] for m in s["stock"] if m["stock_mass_kg"] is not None)
            self.__diagnostic = dict(
                physical_graph_id=grammar_structure._physical_id(s), input_graph_id=self.__input_graph_id,
                node_count=len(s["ids"]), member_count=len(s["stock"]), free_dofs=len(free),
                compatibility_rank=rank, mechanism_count=mechanisms, rank_tolerance=tolerance,
                singular_values=sv.tolist(), load_projection_onto_mechanisms_N=projection,
                mechanism_vectors=vectors, necessary_rigidity_screen="pass" if mechanisms == 0 else "fail",
                counted_member_stock_mass_kg=None if unknown else known,
                known_member_stock_subtotal_kg=known, unknown_density_member_ids=unknown,
                unknown_joint_hardware_mass_kg=None,
                minimum_member_length_to_max_section_dimension=min(
                    m["length_m"] / max(m["section"]["width_m"], m["section"]["height_m"]) for m in s["stock"]),
                short_member_ids=[m["id"] for m in s["stock"] if
                    m["length_m"] / max(m["section"]["width_m"], m["section"]["height_m"]) < 10],
                stock_scope="Gross untrimmed prismatic tube centreline lengths; joint/miter/cross-section-roll and complete installed mass unresolved",
                model_scope=grammar_structure.SCOPE, **grammar_structure.FLAGS)
        return self.__diagnostic

    def diagnose(self):
        """Return the oracle-equivalent necessary axial rigidity diagnostic."""
        return deepcopy(self.__diagnose())

    def linear_reference(self):
        """Solve the same small-displacement axial model without reassembly."""
        s = self.__system
        if self.__diagnose()["mechanism_count"]:
            raise ValueError("Necessary rigidity failure; no unique pin-graph solution")
        displacement = np.zeros(len(s["F"]))
        free = s["free"]
        if free:
            displacement[free] = np.linalg.solve(s["K"][np.ix_(free, free)], s["F"][free])
        reaction = s["K"] @ displacement - s["F"]
        axial = np.array([m["E_Pa"] * m["area_m2"] / m["length_m"] for m in s["stock"]]) * (s["B"] @ displacement)
        return dict(displacements_m={key: displacement[3*i:3*i+3].tolist() for i, key in enumerate(s["ids"])},
            reactions_N={key: reaction[3*i:3*i+3].tolist() for i, key in enumerate(s["ids"])},
            member_axial_forces_N={m["id"]: float(n) for m, n in zip(s["stock"], axial)},
            strain_energy_J=float(.5 * displacement @ s["K"] @ displacement),
            external_work_J=float(.5 * s["F"] @ displacement))


def prepare(graph):
    return PreparedAxial(graph)
