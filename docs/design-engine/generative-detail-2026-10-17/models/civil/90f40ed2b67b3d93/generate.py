import sys
from pathlib import Path
sys.path[:0]=['/home/hayder/Documents/OpenSourceRail', '/home/hayder/Documents/OpenSourceRail/design/component-catalogue/src']
from engineering.factory_examples.native import export_native
export_native('/home/hayder/Documents/OpenSourceRail/build/generative-design/detail-publication-2026-10-17/models/civil/90f40ed2b67b3d93/model.json','/home/hayder/Documents/OpenSourceRail/build/generative-design/detail-publication-2026-10-17/models/civil/90f40ed2b67b3d93')
Path('/home/hayder/Documents/OpenSourceRail/build/factory-examples-native/90f40ed2b67b3d93/completed').write_text('complete')
