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
    error_log = SCRIPT.parents[4] / 'build/samawah-line-twin-error.log'
    error_log.parent.mkdir(parents=True, exist_ok=True)
    error_log.write_text(traceback.format_exc())
    traceback.print_exc()
    sys.exit(1)
