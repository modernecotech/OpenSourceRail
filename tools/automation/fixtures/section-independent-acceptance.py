"""Independent section-input and closed-form checks, outside candidate worktrees."""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from engineering.generative_design.mechanical_detail import box_section, i_section


def reject(function, values):
    try:
        function(*values)
    except (ValueError, TypeError):
        return
    raise AssertionError(
        f"accepted invalid physical input: {function.__name__}{values}"
    )


for function, valid in (
    (i_section, [0.3, 0.6, 0.02, 0.012]),
    (box_section, [0.3, 0.6, 0.02]),
):
    for i in range(len(valid)):
        for invalid in (True, False, -1, 0, float("nan"), float("inf")):
            trial = list(valid)
            trial[i] = invalid
            reject(function, trial)

# Independent subtraction of rectangles, not implementation reference outputs.
i = i_section(0.3, 0.6, 0.02, 0.012)
b = box_section(0.3, 0.6, 0.02)
assert math.isclose(
    i["area_m2"], 0.3 * 0.6 - (0.3 - 0.012) * (0.6 - 2 * 0.02), rel_tol=1e-12
)
assert math.isclose(
    i["inertia_m4"],
    (0.3 * 0.6**3 - (0.3 - 0.012) * (0.6 - 2 * 0.02) ** 3) / 12,
    rel_tol=1e-12,
)
assert math.isclose(b["area_m2"], 0.3 * 0.6 - 0.26 * 0.56, rel_tol=1e-12)
assert math.isclose(
    b["inertia_m4"], (0.3 * 0.6**3 - 0.26 * 0.56**3) / 12, rel_tol=1e-12
)
reject(i_section, [0.3, 0.6, 0.3, 0.012])
reject(box_section, [0.3, 0.6, 0.2])
print("Independent dimensions, geometry and closed-form section checks passed")
