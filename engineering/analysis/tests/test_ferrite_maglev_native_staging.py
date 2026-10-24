"""Transport-only fixtures: native execution itself is checked by root smoke."""
import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from engineering.factory_examples import native


def paths(script):
    tree=ast.parse(Path(script).read_text())
    call=next(node.value for node in tree.body if isinstance(node,ast.Expr)
              and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name)
              and node.value.func.id=='export_native')
    return Path(ast.literal_eval(call.args[0])),Path(ast.literal_eval(call.args[1]))


def complete_fixture(script, *, wrong_input=False):
    source,output=paths(script)
    output.mkdir(parents=True)
    files={'model.FCStd':b'transport-fixture-fcstd','model.step':b'transport-fixture-step'}
    for name,data in files.items():(output/name).write_bytes(data)
    receipt=dict(input_sha256='0'*64 if wrong_input else sha256(source.read_bytes()).hexdigest(),
                 fcstd_reopened=True,step_reopened=True,
                 files_sha256={name:sha256(data).hexdigest() for name,data in files.items()})
    (output/'native-cad.json').write_text(json.dumps(receipt))
    Path(script).with_name('completed').write_text('complete')
    return receipt


def test_flatpak_stages_both_paths_under_shared_repo_and_preserves_bytes(tmp_path,monkeypatch):
    root=tmp_path/'repository';root.mkdir()
    source=tmp_path/'private-input.json';source.write_bytes(b'{"parts":[]}\n')
    output=tmp_path/'private-output';seen={}
    monkeypatch.setattr(native.shutil,'which',lambda name:None)
    def run(command,**kwargs):
        assert command[0]=='flatpak'
        staged,target=paths(command[-1])
        assert staged.is_relative_to(root) and target.is_relative_to(root)
        assert staged!=source and target!=output
        assert staged.read_bytes()==source.read_bytes()
        seen.update(complete_fixture(command[-1]))
    monkeypatch.setattr(native.subprocess,'run',run)
    result=native.generate(source,output,root)
    assert result==seen==json.loads((output/'native-cad.json').read_text())
    assert result['input_sha256']==sha256(source.read_bytes()).hexdigest()
    assert all(sha256((output/name).read_bytes()).hexdigest()==expected for name,expected in result['files_sha256'].items())


def test_flatpak_refuses_stale_input_receipt_before_copying_package(tmp_path,monkeypatch):
    root=tmp_path/'repository';root.mkdir();source=tmp_path/'input';source.write_bytes(b'original')
    output=tmp_path/'private-output'
    monkeypatch.setattr(native.shutil,'which',lambda name:None)
    monkeypatch.setattr(native.subprocess,'run',lambda command,**kwargs:complete_fixture(command[-1],wrong_input=True))
    with pytest.raises(ValueError,match='input or reopen'):
        native.generate(source,output,root)
    assert not output.exists()


def test_direct_freecad_keeps_requested_paths(tmp_path,monkeypatch):
    root=tmp_path/'repository';root.mkdir();source=tmp_path/'input';source.write_bytes(b'original')
    output=tmp_path/'private-output'
    monkeypatch.setattr(native.shutil,'which',lambda name:'/usr/bin/FreeCADCmd' if name=='FreeCADCmd' else None)
    def run(command,**kwargs):
        assert command[0]=='/usr/bin/FreeCADCmd'
        assert paths(command[-1])==(source,output)
        complete_fixture(command[-1])
    monkeypatch.setattr(native.subprocess,'run',run)
    assert native.generate(source,output,root)['step_reopened']
