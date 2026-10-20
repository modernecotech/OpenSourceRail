"""A routine regeneration must not replace controlled network intent."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("city_package_refresh", ROOT / "tools/automation/generate-city-packages-fast.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_existing_ring_layout_is_retained_unless_resynthesis_is_explicit(tmp_path, monkeypatch):
    city = tmp_path / "city"
    city.mkdir()
    design = city / "design.toml"
    original = '[city]\nslug="test"\n[[lines]]\nname="line-6"\nshape="ring"\n'
    design.write_text(original)
    raster = tmp_path / "rasters"
    raster.mkdir()
    (raster / "test.grid.json").write_text('{}')
    (city / "corridors.json").write_text('{}')  # deliberately unrelated cache
    monkeypatch.setattr(module, "RASTER_CACHE", raster)
    monkeypatch.setattr(module, "LOG_ROOT", tmp_path / "logs")
    monkeypatch.setattr(module, "source_artifacts", lambda *args: [design])
    commands = []
    monkeypatch.setattr(module, "run_logged", lambda command, *args, **kwargs: commands.append(command) or 0)
    result = module.prepare_city("test", design, {"country": "IQ"}, False, False)
    assert result["passed"]
    assert design.read_text() == original
    assert any("refresh-city-design-costs.py" in " ".join(cmd) for cmd in commands)
    assert not any(Path(cmd[0]).name == "osr-design" for cmd in commands)
    commands.clear()
    module.prepare_city("test", design, {"country": "IQ"}, False, False, True)
    assert any(Path(cmd[0]).name == "osr-design" for cmd in commands)


def _prepared_city(tmp_path, monkeypatch, slug, *, existing=True, policy=False):
    city = tmp_path / slug
    city.mkdir()
    design = city / "design.toml"
    if existing:
        design.write_text(f'[city]\nslug="{slug}"\n[[lines]]\nname="retained-ring"\nshape="ring"\n')
    if policy:
        (city / "alignment-policy.toml").write_text("[core]\n")
    raster = tmp_path / "rasters"
    raster.mkdir()
    (raster / f"{slug}.grid.json").write_text('{}')
    (city / "corridors.json").write_text('{}')
    monkeypatch.setattr(module, "RASTER_CACHE", raster)
    monkeypatch.setattr(module, "LOG_ROOT", tmp_path / "logs")
    monkeypatch.setattr(module, "source_artifacts", lambda *args: [design])
    commands = []

    def run(command, *args, **kwargs):
        commands.append(command)
        if Path(command[0]).name == "osr-design" and not design.exists():
            design.write_text(f'[city]\nslug="{slug}"\n')
        return 0

    monkeypatch.setattr(module, "run_logged", run)
    return design, commands


def test_default_refresh_preserves_baghdad_and_adopted_policy_layouts(tmp_path, monkeypatch):
    for slug in ("baghdad", "other-city"):
        case = tmp_path / slug
        case.mkdir()
        design, commands = _prepared_city(case, monkeypatch, slug, policy=True)
        original = design.read_bytes()
        result = module.prepare_city(slug, design, {"country": "IQ"}, False, False)
        assert result["passed"]
        assert result["layout_action"] == "retained-controlled-layout"
        assert design.read_bytes() == original
        assert not any("rework-" in " ".join(command) for command in commands)
        assert not any(Path(command[0]).name == "osr-design" for command in commands)


def test_planned_corridor_reuse_attaches_independent_water_before_native_stations(tmp_path, monkeypatch):
    import json
    design, commands = _prepared_city(tmp_path, monkeypatch, 'reuse-water')
    out=design.parent/'engineering/alignment';out.mkdir(parents=True)
    (design.parent/'corridors.json').write_text(json.dumps({'lines':[{'name':'retained-ring'}]}))
    (out/'core-realignment.json').write_text(json.dumps({'sources_sha256':{},'lines':[{'line':'retained-ring'}]}))
    (out/'residential-line-expansion.json').write_text(json.dumps({'sources_sha256':{},'city':'reuse-water','final_line_count':1}))
    result=module.prepare_city('reuse-water',design,{'country':'KE'},False,False,reuse_planned_corridors=True)
    assert result['passed']
    water=next(i for i,c in enumerate(commands) if 'generate-station-water-screen.py' in ' '.join(c) and '--prepare-grid' in c)
    native=next(i for i,c in enumerate(commands) if Path(c[0]).name=='osr-design')
    assert water<native


def test_selected_batch_preserves_full_catalogue_validation_coverage(tmp_path, monkeypatch):
    import sys
    paths={s:tmp_path/s/'design.toml' for s in ('first','second','untouched')}
    for path in paths.values():path.parent.mkdir();path.write_text('[city]\n')
    catalog=tmp_path/'catalog.toml'
    catalog.write_text(''.join(f'[[cities]]\nslug="{s}"\ncountry="KE"\n' for s in paths))
    monkeypatch.setattr(module,'CATALOG',catalog)
    monkeypatch.setattr(module,'SUMMARY_PATH',tmp_path/'package-summary.json')
    monkeypatch.setattr(module,'ENGINEERING_SUMMARY',tmp_path/'engineering.json')
    monkeypatch.setattr(module,'discover_designs',lambda:paths)
    monkeypatch.setattr(module,'engineering_results',lambda selected:(0,set(selected)))
    monkeypatch.setattr(module,'ignored_review_artifacts',lambda selected:{})
    monkeypatch.setattr(module,'finish_city',lambda slug,*args,**kwargs:dict(city=slug,passed=True,phase='complete-package'))
    commands=[]
    monkeypatch.setattr(module,'run_logged',lambda command,*args,**kwargs:commands.append(command) or 0)
    monkeypatch.setattr(sys,'argv',['generate-city-packages-fast.py','--only','first,second','--finish-only','--jobs','1'])
    assert module.main()==0
    checks=[c for c in commands if any(Path(p).name in {'validate-ring-interchanges.py','validate-station-clusters.py'} for p in c)]
    assert len(checks)==2
    assert all('--all' in c and '--design' not in c for c in checks)


def test_new_city_bootstraps_its_own_current_planner_by_default(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "new-city", existing=False)
    result = module.prepare_city("new-city", design, {"country": "FR"}, False, False)
    assert result["passed"]
    assert result["design_approach"] == "current-source-controlled-layout-v1"
    native = [i for i, command in enumerate(commands) if Path(command[0]).name == "osr-design"]
    current = [i for i, command in enumerate(commands) if "rework-city-alignment.py" in " ".join(command)]
    assert len(native) == 2
    assert native[0] < current[0] < current[-1] < native[1]
    correction=next(i for i, command in enumerate(commands) if 'correct-city-network.py' in ' '.join(command))
    assert current[-1] < correction < native[1]
    assert "--design-only" not in commands[native[0]]
    assert "--design-only" in commands[native[1]]
    assert not any("rework-baghdad-alignment.py" in " ".join(command) for command in commands)
    assert all(str(design) in command for command in (commands[i] for i in current))


def test_retained_layout_refresh_does_not_download_deleted_raster_cache(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, 'retained')
    (module.RASTER_CACHE / 'retained.grid.json').unlink()
    assert module.prepare_city('retained', design, {'country': 'IQ'}, False, False)['passed']
    assert not any('osr_osm.cli' in command or 'osr_geo.cli' in command for command in commands)
    assert not any(Path(command[0]).name == 'osr-design' for command in commands)


def test_explicit_baghdad_resynthesis_retains_its_controlled_planner(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "baghdad", policy=True)
    result = module.prepare_city("baghdad", design, {"country": "IQ"}, False, False, True)
    assert result["passed"]
    assert result["layout_action"] == "resynthesised"
    assert any("rework-baghdad-alignment.py" in " ".join(command) for command in commands)
    assert not any("rework-city-alignment.py" in " ".join(command) for command in commands)


def test_full_refresh_generates_design_status_before_package_manifest(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "test")
    result = module.finish_city("test", design, 1)
    assert result["passed"]
    status = next(i for i, command in enumerate(commands) if "generate-city-design-status.py" in " ".join(command))
    federation = next(i for i, command in enumerate(commands) if "generate-city-federation.py" in " ".join(command))
    manifest = next(i for i, command in enumerate(commands) if "generate-city-package-manifest.py" in " ".join(command))
    assert federation < status < manifest


def test_baghdad_proposal_is_rebuilt_after_final_package_manifest(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "baghdad")
    result = module.finish_city("baghdad", design, 1)
    assert result["passed"]
    manifest = next(i for i, command in enumerate(commands) if "generate-city-package-manifest.py" in " ".join(command))
    proposal = next(i for i, command in enumerate(commands) if "build-baghdad-proposal.py" in " ".join(command))
    assert manifest < proposal == len(commands) - 1
    commands.clear()
    assert module.finish_city("baghdad", design, 1, publish_proposal=False)["passed"]
    assert not any("build-baghdad-proposal.py" in " ".join(command) for command in commands)


def test_full_refresh_rechecks_retained_clearance_without_deleted_osm_cache(tmp_path, monkeypatch):
    import hashlib,json
    design, commands = _prepared_city(tmp_path, monkeypatch, 'retained')
    corridor=design.parent/'retained.corridor.geojson';corridor.write_bytes(b'controlled corridor')
    folder = design.parent/'engineering/clearance'
    folder.mkdir(parents=True)
    for name in ('building-footprints.json.gz','building-source.json','terrain-elevation.f32.gz','terrain-source.json'):
        (folder/name).write_bytes(b'retained')
    for name in ('building-source.json','terrain-source.json'):
        (folder/name).write_text(json.dumps(dict(corridor_sha256=hashlib.sha256(corridor.read_bytes()).hexdigest())))
    assert module.finish_city('retained', design, 1)['passed']
    command = next(c for c in commands if 'audit-viaduct-clearance.py' in ' '.join(c))
    assert '--retain-inputs' not in command and '--fetch-terrain' not in command
    commands.clear()
    corridor.write_bytes(b'changed alignment')
    assert module.finish_city('retained', design, 1)['passed']
    command = next(c for c in commands if 'audit-viaduct-clearance.py' in ' '.join(c))
    assert '--retain-inputs' in command and '--fetch-terrain' in command
    commands.clear()
    (folder/'terrain-source.json').unlink()
    assert module.finish_city('retained', design, 1)['passed']
    command = next(c for c in commands if 'audit-viaduct-clearance.py' in ' '.join(c))
    assert '--retain-inputs' in command and '--fetch-terrain' in command


def test_aggregate_publication_reseals_context_then_inventory_then_archives(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, 'baghdad')
    assert module.finalize_publication('baghdad', design)['passed']
    names = [Path(command[1]).name for command in commands]
    assert names == ['generate-city-package-manifest.py', 'publish-city-summary.py',
                     'generate-city-federation.py', 'generate-city-design-status.py',
                     'generate-city-package-manifest.py', 'build-baghdad-proposal.py']
    commands.clear()
    monkeypatch.setattr(module, 'run_logged', lambda command, *a, **k: commands.append(command) or 1)
    assert not module.finalize_publication('baghdad', design)['passed']
    assert len(commands) == 1  # Stale numerical evidence cannot be repaired by resealing text.


def test_reused_corrected_route_rejects_geometry_and_source_drift(tmp_path,monkeypatch):
    import hashlib,json,pytest
    monkeypatch.setattr(module,'REPO_ROOT',tmp_path)
    city=tmp_path/'city';out=city/'engineering/alignment';out.mkdir(parents=True)
    source=tmp_path/'retained-input';source.write_bytes(b'retained')
    routes=dict(lines=[dict(name='a',cells=[[0,0],[1,1]])])
    proof=dict(schema='osr-city-network-correction/1',candidate_sha256=hashlib.sha256((json.dumps(routes,sort_keys=True,indent=2)+'\n').encode()).hexdigest(),source_sha256={'retained-input':hashlib.sha256(source.read_bytes()).hexdigest()},engineering_release=False,physical_release=False)
    (out/'network-correction.json').write_text(json.dumps(proof))
    module.verify_network_correction(city,routes)
    with pytest.raises(ValueError,match='candidate identity'):
        module.verify_network_correction(city,dict(lines=[]))
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Stale corrected corridor source'):
        module.verify_network_correction(city,routes)
