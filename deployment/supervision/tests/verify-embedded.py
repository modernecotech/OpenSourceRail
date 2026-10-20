"""Offline current maglev process-plan boundary and actual Rust replay check."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from services.integration.osr_integration.manufacturing import planning_process_status,factory_templates

plan=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/manufacturing.json'
status=planning_process_status(json.loads(plan.read_text()))
assert status['deployable_factory_methods']==[]
assert status['qualified'] is False and status['production_instruction_released'] is False
assert status['manufacturing_release'] is False and status['physical_release'] is False
try:
    factory_templates(json.loads(plan.read_text()))
except ValueError:
    pass
else:
    raise AssertionError('Planning routes became production methods')
replay=subprocess.run(['cargo','run','--locked','--quiet','-p','osr-maglev-control','--example','sbc_replay'],
    cwd=ROOT,capture_output=True,text=True,check=True)
frames=[line for line in replay.stdout.splitlines() if line.startswith('tick=')]
assert len(frames)==8
assert all('physical_output=false' in frame for frame in frames)
assert any('stop=true' in frame and 'traction=false' in frame for frame in frames)
print('PASS current process plan remains unqualified; actual eight-tick Rust replay has no physical outputs')
print('Live ERP/FUXA integration and hardware commissioning were not exercised.')
