"""FreeCAD GUI entry point for the Samawah Line 1 digital twin."""

from __future__ import annotations

import runpy
import sys
import traceback
from pathlib import Path


SCRIPT = Path(__file__).parent / "src" / "osr_mech" / "freecad_samawah_line_twin.py"
sys.path.insert(0, str(SCRIPT.parents[1]))
sys.argv = [str(SCRIPT)]

try:
    runpy.run_path(str(SCRIPT), run_name="__main__")
except SystemExit:
    raise
except Exception:
    traceback.print_exc()
    sys.exit(1)
