"""Workbench escaping, unknown stock, repeatable publication and local role APIs."""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

import pytest

from engineering.design_search import contracts, publication

ROOT=Path(__file__).resolve().parents[3]
PAYLOAD='</script><img src=x onerror="globalThis.hacked=true"><script>hacked=true</script>&\u2028'


def candidate():
    return contracts.make_candidate(requirement_revision='req-html',label=PAYLOAD,
        architecture={'guidebeam':{'section_id':'coupon','span_m':25.}},
        frames=[{'id':'vehicle','parent_id':None,'origin_m':[0.,0.,0.],
                 'rotation_matrix':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]}],
        materials=[{'id':'test','density_kg_m3':12.,'basis':'declared test material'}],
        geometry=[{'id':'block','kind':'box','frame_id':'vehicle','material_id':'test','size_m':[1.,1.,1.],'at_m':[0.,0.,0.]}],interfaces=[],
        installed_inventory=[{'id':'block','geometry_id':'block','scope':'vehicle-per-car','frame_id':'vehicle','quantity':1,
            'status':'known','unit_mass_kg':12.,'cg_m':[.5,.5,.5],'inertia_kg_m2':[[2.,0.,0.],[0.,2.,0.],[0.,0.,2.]],'basis':'exact cube'},
            {'id':'unweighed-pump','scope':'vehicle-per-car','frame_id':'vehicle','quantity':1,'status':'unknown','unit_mass_kg':None,
             'cg_m':None,'inertia_kg_m2':None,'basis':'installed pump not weighed'},
            {'id':'unweighed-anchors','scope':'guideway-per-span','frame_id':'vehicle','quantity':1,'status':'unknown','unit_mass_kg':None,
             'cg_m':None,'inertia_kg_m2':None,'basis':'installed anchors not designed'}])


@pytest.fixture
def comparison(monkeypatch):
    physical=candidate();request=contracts.make_evaluation_request(physical,evaluator_id='definition',evaluator_sources={'solver.py':'a'*64},purpose='next-experiment')
    result=contracts.make_result(request,execution_status='executed',numerical_status='converged',screen_status='unknown',maturity='definition',
        metrics={'known_vehicle_mass_kg':12.},constraints=[{'id':'inventory','state':'unknown','description':PAYLOAD}],diagnostics=[PAYLOAD])
    value=dict(campaign_id='b'*64,candidates=[physical],results=[result],confirmations=[],
        next_experiment={'status':'selected-for-next-experiment','selected_candidate_id':physical['candidate_id'],'policy':{'label':PAYLOAD}},
        integrated_baseline={'status':'no-eligible-candidate','selected_candidate_id':None,'rejections':{physical['candidate_id']:['unknown-installed-stock']}},
        qualification={'physical_accepted':False,'tasks_on_hold':576})
    monkeypatch.setattr(publication.campaign,'compare',lambda *args,**kwargs:deepcopy(value))
    monkeypatch.setattr(publication.campaign,'definition',lambda *args,**kwargs:{'campaign_id':value['campaign_id'],'schema':'test-immutable-campaign'})
    monkeypatch.setattr(publication.campaign,'source_epoch',lambda:{'publication.py':'c'*64})
    return value


class Scripts(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=False);self.scripts=[];self.active=None
    def handle_starttag(self,tag,attributes):
        if tag=='script':self.active=[dict(attributes),''];self.scripts.append(self.active)
    def handle_data(self,data):
        if self.active is not None:self.active[1]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.active=None


def test_summary_retains_unknown_mass_and_all_stock_scopes(comparison):
    value=publication.summary(comparison);row=value['candidates'][0]
    assert row['mass']['known_mass_subtotal_kg']==12.
    assert row['mass']['total_mass_kg'] is None
    assert row['mass']['cg_m'] is None
    assert set(row['inventory']['unknown_stock_ids'])=={'unweighed-pump','unweighed-anchors'}
    assert not row['inventory']['complete_installed_distribution']
    assert row['baseline_rejections']==['unknown-installed-stock']
    assert all(value[key] is False for key in contracts.FLAGS)


def test_malicious_html_stays_in_inert_escaped_json(comparison,tmp_path):
    publication.publish(comparison['campaign_id'],output=tmp_path)
    page=(tmp_path/'index.html').read_text();scripts=Scripts();scripts.feed(page)
    assert len(scripts.scripts)==2
    data=scripts.scripts[0]
    assert data[0]=={'id':'data','type':'application/json'}
    assert '<' not in data[1] and '&' not in data[1]
    decoded=json.loads(data[1]);assert decoded['candidates'][0]['label']==PAYLOAD
    assert decoded['candidates'][0]['evaluations'][0]['diagnostics']==[PAYLOAD]
    assert decoded['candidates'][0]['mass']['total_mass_kg'] is None
    assert '.innerHTML' not in scripts.scripts[1][1]
    assert '.textContent' in scripts.scripts[1][1]


def test_browser_script_renders_labels_as_text_without_html_execution(comparison,tmp_path):
    node=shutil.which('node')
    if node is None:pytest.skip('Node is optional for the DOM smoke test')
    publication.publish(comparison['campaign_id'],output=tmp_path)
    scripts=Scripts();scripts.feed((tmp_path/'index.html').read_text())
    driver=r'''
const input=JSON.parse(require('fs').readFileSync(0,'utf8')),vm=require('vm');
const created=[];
class Element{constructor(tag){this.tag=tag;this.children=[];this.value='';this._text='';created.push(this);}
append(child){this.children.push(child);}replaceChildren(){this.children=[];}
set textContent(value){this._text=String(value);}get textContent(){return this._text;}
set innerHTML(value){throw Error('Unsafe HTML rendering');}}
const elements={};for(const id of ['data','choice','candidate','disposition','policy','scope'])elements[id]=new Element(id);
elements.data.textContent=input.data;
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
vm.runInNewContext(input.script,{document,JSON},{timeout:1000});
if(elements.candidate.children.find(el=>el.tag==='h2').textContent!==input.payload)throw Error('Label not preserved as text');
if(created.some(el=>el.tag==='img'))throw Error('Untrusted image element created');
if(!elements.candidate.children.some(el=>el.tag==='pre'&&el.textContent.includes('unweighed-pump')))throw Error('Unknown inventory hidden');
process.stdout.write('safe-text-render');'''
    result=subprocess.run([node,'-e',driver],input=json.dumps({'script':scripts.scripts[1][1],'data':scripts.scripts[0][1],'payload':PAYLOAD}),
        text=True,capture_output=True,timeout=10,check=True)
    assert result.stdout=='safe-text-render'


def test_publication_is_deterministic_and_check_preserves_files(comparison,tmp_path):
    publication.publish(comparison['campaign_id'],output=tmp_path)
    before={path.name:path.read_bytes() for path in tmp_path.iterdir()}
    publication.publish(comparison['campaign_id'],output=tmp_path,check=True)
    publication.publish(comparison['campaign_id'],output=tmp_path)
    assert {path.name:path.read_bytes() for path in tmp_path.iterdir()}==before


@pytest.mark.parametrize('name',['index.html','README.md','comparison.json.gz','campaign.json','manifest.json'])
def test_publication_check_rejects_tampered_output(comparison,tmp_path,name):
    publication.publish(comparison['campaign_id'],output=tmp_path)
    path=tmp_path/name;path.write_bytes(path.read_bytes()+b'tampered')
    with pytest.raises(ValueError,match='stale candidate comparison'):publication.publish(comparison['campaign_id'],output=tmp_path,check=True)


def test_role_toml_schema_and_no_permission_or_model_overrides():
    # Official schema: https://learn.chatgpt.com/docs/agent-configuration/subagents
    project=tomllib.loads((ROOT/'.codex/config.toml').read_text())
    assert set(project)=={'agents'}
    assert project['agents']=={'max_concurrent_threads_per_session':3}
    names=set()
    for path in (ROOT/'.codex/agents').glob('*.toml'):
        role=tomllib.loads(path.read_text())
        assert set(role)=={'name','description','developer_instructions'}
        assert role['name']==path.stem and role['name'] not in names
        names.add(role['name'])
        assert isinstance(role['description'],str) and role['description'].strip()
        assert 'AGENTS.md' in role['developer_instructions']
    assert names=={'coordinator','magnetics','electrical','mechanical','civil','twin','service','verifier'}


def test_local_codex_config_validation_does_not_start_a_model():
    executable=shutil.which('codex')
    if executable is None:pytest.skip('Codex CLI is optional outside the authoring environment')
    value=subprocess.run([executable,'app-server','--strict-config','--print-startup-config'],cwd=ROOT,text=True,capture_output=True,timeout=20,check=True)
    parsed=json.loads(value.stdout)
    assert parsed.get('appServerVersion')
    assert 'configRequirements' in parsed


def test_cli_dispatches_without_running_models(comparison,tmp_path,monkeypatch,capsys):
    from engineering.design_search import __main__ as cli
    called=[]
    monkeypatch.setattr(cli.campaign,'create',lambda path,**kwargs:called.append((path,kwargs)) or {'created':True})
    assert cli.main(['campaign','create','spec.toml','--state',str(tmp_path)])==0
    assert called==[(Path('spec.toml'),{'state':tmp_path})]
    assert json.loads(capsys.readouterr().out)=={'created':True}


@pytest.mark.parametrize('arguments,expected',[
    (['design','campaign','create','campaign.toml'],['-m','engineering.design_search','campaign','create','campaign.toml']),
    (['design','campaign'],['tools/automation/ferrite-maglev-study.py','campaign']),
    (['design','campaign','--output','build/custom'],['tools/automation/ferrite-maglev-study.py','campaign','--output','build/custom']),
    (['design','status'],['tools/automation/ferrite-maglev-study.py','status']),
    (['twin','compile','candidate'],['-m','engineering.design_search','twin','compile','candidate']),
])
def test_launcher_preserves_legacy_and_new_routes(tmp_path,arguments,expected):
    launcher=tmp_path/'osr';shutil.copyfile(ROOT/'osr',launcher)
    runner=tmp_path/'tools/automation/osr-python';runner.parent.mkdir(parents=True)
    runner.write_text('#!'+sys.executable+'\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n');runner.chmod(0o755)
    value=subprocess.run(['bash',str(launcher),*arguments],text=True,capture_output=True,timeout=10,check=True)
    assert json.loads(value.stdout)==expected
