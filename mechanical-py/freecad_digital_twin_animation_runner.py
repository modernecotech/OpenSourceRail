"""FreeCAD GUI entry point for the repository digital-twin animation."""

from __future__ import annotations

import runpy
import sys
import traceback
from pathlib import Path


SCRIPT = Path(__file__).parent / "src" / "osr_mech" / "freecad_digital_twin_animation.py"
sys.path.insert(0, str(SCRIPT.parents[1]))
sys.argv = [str(SCRIPT)]

try:
    runpy.run_path(str(SCRIPT), run_name="__main__")
except SystemExit:
    raise
except Exception:
    traceback.print_exc()
    sys.exit(1)
