import sys
from pathlib import Path
sys.path[:0]=['/home/hayder/Documents/OpenSourceRail', '/home/hayder/Documents/OpenSourceRail/design/component-catalogue/src']
from engineering.factory_examples.native import export_native
export_native('/home/hayder/Documents/OpenSourceRail/build/generative-design/detail-final-2026-10-17/models/mechanical/f815d2a21de1144c/model.json','/home/hayder/Documents/OpenSourceRail/build/generative-design/detail-final-2026-10-17/models/mechanical/f815d2a21de1144c')
Path('/home/hayder/Documents/OpenSourceRail/build/factory-examples-native/f815d2a21de1144c/completed').write_text('complete')
