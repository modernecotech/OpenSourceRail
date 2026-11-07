"""Generate a readable part catalogue and immutable same-candidate handoffs."""
from pathlib import Path
from hashlib import sha256
import gzip,html,json
from engineering.station_rail.common import digest,identity,encoded
from . import ROOT,FLAGS,catalogue

OUTPUT='docs/design-engine/vehicle-parts'
SOURCE='engineering/vehicle_parts/publication.py'


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('Fresh immutable output required: '+str(path))
    path.write_bytes(value if isinstance(value,bytes) else value.encode())


def _money(bounds):return ' / '.join('unknown' if bounds[k] is None else f"${bounds[k]:,.0f}" for k in catalogue.CASES)


def summary(value):
    return {k:value[k] for k in ('schema','candidate_id','parent_candidate_id','parent_selection_id','evaluation_id','bundle_id',
        'counted','nominal_mass_kg','direct_parts_process_usd','parent_account_comparison','design_stage','costing_policy',
        'electrical_checks','integration_policy','integrated_selection_id',*FLAGS)}


def assembly_plan(value):
    order=[('body/underframe','Fixture underframe and coupler/bogie hardpoints; establish car datums'),
        ('body/sideframe','Fit upper frame, door apertures and structural joints'),
        ('body/roof','Build roof panels and counted service mounting interfaces'),
        ('body/floor','Fit floor modules and maintain accessible service voids'),
        ('running/bogie-frame','Build and inspect bogie frames with wheelsets, axleboxes, suspension, brakes and local fittings'),
        ('body/underframe','Marry carbody to completed bogies using controlled lifting/supports'),
        ('services/battery','Install supported service racks, cooling and protected electrical distribution'),
        ('services/hvac','Install roof HVAC, ducts, drains and controlled roof interfaces; survey PV occupancy'),
        ('body/cladding','Fit body panels and accessible interior trim with identified bond/fastener schedules'),
        ('body/door-opening','Fit mechanical door operators/leaves, glazing, motors and independent monitoring'),
        ('body/chair','Fit chairs, wheelchair-space hardware, handholds and complete passenger access route'),
        ('services/lighting','Fit simple LED modules, protected branches and essential emergency fixtures'),
        ('services/control','Fit labelled control/safety/communication looms; verify independent braking/door interfaces'),
        ('running/intercar-coupler','Connect five mechanical couplers and separate gangways, air/electrical jumpers and essential lamps'),
        ('services/control','Controlled dimensional, insulation, leak, interlock and static function checks; retain defects'),
        ('running/bogie-brakes','Independent body/bogie/door/braking, dynamic and hot-weather validation before any release')]
    return dict(schema='osr-vehicle-manufacturing-assembly-plan/1',candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],
        operations=[dict(sequence=i+1,lead_assembly_id=a,operation=op,release='proposed-method; approved drawings/limits and test records pending') for i,(a,op) in enumerate(order)],
        subassembly_routes=value['assemblies'],fixture_and_tooling_requirements=[
            'Body datum jig, member cutting/drilling and qualified aluminium/steel joining stations',
            'Panel/core cutting, bond preparation/cure fixture and accessible joint inspection',
            'Bogie weld/boring fixture and independent dimensional/NDT/pressure/brake inspection',
            'Door operator alignment/travel rig and monitored obstruction/interlock test equipment',
            'Seating/glazing/gangway forming and controlled retention/adhesive application tooling',
            'Insulated electrical assembly/test station, approved crimp tools and qualified pressure/cooling circuit equipment',
            'Rated lifting/support stands, bogie lowering table and supported battery/module withdrawal tooling'],
        production_capacity_verified=False,tooling_capital_usd=None,person_hours_complete=None,
        reason='Part-level direct process allowances are present; final assembly hours, jig investment, yields, takt and qualified throughput need a factory route/capacity study',**FLAGS)


def business_draft(value):
    return dict(schema='osr-vehicle-manufacturing-business-draft/1',candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],
        disabled=1,transactions_performed=False,executable_work_order=False,
        items=[dict(item_code='OSR-PART-'+r['component_definition_id'][:16],part_id=r['id'],candidate_id=value['candidate_id'],
            component_definition_id=r['component_definition_id'],quantity_per_train=r['quantity_per_train'],
            material_id=r['material_id'],make_buy=r['make_buy'],stock=r['stock']) for r in value['parts']],
        gate='Engineering revision, supplier/process qualification, approved drawing/BOM and independent release required before controlled business import',**FLAGS)


def readme(value):
    count=value['counted'];mass=value['nominal_mass_kg']['known_leaf_subtotal'];cost=value['direct_parts_process_usd']['known_leaf_subtotal']
    rows=[]
    for a in value['assembly_summaries']:
        m=a['nominal_mass_kg']['known_leaf_subtotal']['base'];c=a['direct_parts_process_usd']['known_leaf_subtotal']['base']
        rows.append(f"| {a['name']} | {a['quantity_per_train']} | {a['unique_leaf_types']} | {m:,.1f} | ${c:,.0f} |")
    return f'''# Vehicle parts, manufacture and assembly

The six-car manufacturing proposal now contains **{count['unique_leaf_types']} named leaf-part types in {count['assembly_types']} assemblies**.
Each part identifies its material, quantity, stock dimensions or bought-component
envelope, manufacturing route, fixings/joining, proposed tolerance basis,
inspection and maintenance-removal method. This is a useful completed outline
breakdown; detailed released drawings and physical qualification remain later gates.

![Searchable catalogue with part quantities, materials and stock sketches](catalogue-preview.png)

**[Open the searchable part catalogue](index.html)** — select a subsystem, search a
part or material, and open its dimensional stock sketch, proposed route and checks.
[Machine-readable full bundle](manufacturing-bundle.json.gz) ·
[Materials](materials.json) · [Cut/stock schedule](stock-schedule.json) ·
[Assembly plan](assembly-plan.json) · [Downstream handoff](handoff.json) ·
[Disabled business draft](business-draft.json).

## What is counted

- **12 passive bogies, 24 wheelsets and 48 axleboxes:** frame members, wheel/axle forgings,
  bearings, seals, springs, dampers, emergency support, discs, calipers/actuators,
  local WSP equipment, guards, pins, bolts, washers and retainers.
- **Six car structures:** lower sills/bolsters, side/roof members, floor, sandwich-panel
  skins and cores, adhesive/weld allowances, repairable linings, roof layers,
  equipment brackets and individually counted attachment hardware.
- **264 fixed chairs and 12 wheelchair places:** seat shells, frames, cushion/fabric
  proposals and attachments; wheelchair places do not acquire extra seats.
- **12 one-sided door openings, 24 moving leaves and 110 panes:** mechanical belt/reducer,
  carriages, rollers, tracks, latches, manual release, closing-edge rubber, separate
  monitored sensor inserts, motors, controllers, switches, cable carriers, seals and fixings.
- **Five inter-car couplers and five separate passenger gangways:** drawgear and restraints,
  floor bridges, articulation/support elements, bellows, rubber/fabric frames, clamp strips,
  corners, fasteners, air hoses, electrical jumpers and essential lights. Two end/rescue
  couplings are also counted. Gangways do not replace load-bearing couplers or bogies.
- **Service systems:** simple LED lighting, battery modules/racks, separate terminal and
  coolant fittings, active pack cooling, auxiliary conversion, HVAC pressure components,
  ducts/drains, brake/suspension air, controls, cable routes, optional-interface passive
  aluminium secondary and the retained roof-PV research function.

The **{count['leaf_pieces_per_train']:,} expanded BOM units** include individual fasteners,
cut strips, consumable/charge allowances and bought subcomponents. They are a proposed
counted schedule, not a measured count of every internal semiconductor, cell or sealed
compressor part. Such bought-unit internals and delivery inclusions require supplier drawings.
Parent assembly weights, original vehicle category allowances and cells already inside
battery modules are not added again.

## Simple LED lighting

Each car has two 12 m rows made from **16 replaceable 1.5 m, 12 W LED modules**, plus four 6 W
vestibule lamps. Normal output demand is **216 W/car**; two separate 150 W drivers feed
four protected half-circuits. Four 3 W emergency fixtures/car and two 3 W fixtures/gangway
use independent essential feeds. No inter-car HV or low-voltage power buses are paralleled.

At the declared 90% driver efficiency, total train lighting input is approximately
**1.55 kW**. The 2.5 mm², 7.5 m half-route hypothesis gives about **0.292 V drop at 2.25 A**
with the stated 80°C copper model. This is necessary electrical sizing arithmetic;
illumination, glare, EMC, protection coordination, hot derating and emergency tests remain open.
The lighting estimate does not resize the retained 82.8 kWh/car service-energy hypothesis.

## Materials and local manufacture

Prefer repeatable cut/folded/extruded members, accessible positive fixings, replaceable
panel/door/light modules and controlled jigs. Each material has a proposed grade/form
and explicit qualification dependency. Examples include weldable aluminium frame sections,
5052-H32 folded service enclosures, structural steel bogie stock, wheel/axle/bearing
components requiring certification, composite panel skins/cores, railway glazing and fire/smoke-qualified elastomers.
A generic rubber or household diffuser is not evidence of railway fire performance.

The make/buy assignment distinguishes local fabrication, standard purchased hardware
and qualified bought equipment. It does not assume that a new local factory is automatically
cheaper: shared tooling, final assembly hours, production rate, yields and capital remain
explicitly outside this subtotal. No invented Chinese or repeat bulk discount is applied.
Current component quotations can replace individual allowance rows without changing the
physical geometry; their evidence and the resulting evaluation identity must change.

## Quantities and estimated direct cost

The six-car sum of declared stock masses and bounded component allowances is
**{mass['low']/1000:.2f} / {mass['base']/1000:.2f} / {mass['high']/1000:.2f} t** (low/base/high).
These are not verified installed masses, CGs or inertia. Gross stock and estimated bought
masses are labelled individually. The old 19.22 t/car category account is comparison-only;
the difference is not an established weight saving.

Declared direct part/process subtotals are **{_money(cost)}** across six cars.
They are engineering allowances, not quotations or a complete vehicle factory price.
Final car assembly/commissioning, shared plant/tooling, taxes/duties, delivery,
qualification, warranty and complete lifecycle costs remain outside the stated scope.
The low/base/high sums are bounding scenarios, not statistical confidence intervals.

| Assembly | Instances/train | Leaf types | Base scoped kg/train | Base direct parts/process USD/train |
|---|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

## Assemble and inspect

The [assembly plan](assembly-plan.json) starts with a datum-controlled underframe,
then the body frame, roof/floor, bogies, equipment, panels, doors/glazing, passenger
fitout and inter-car connections. Each subassembly has its own ordered operations,
identified part lists, tools, inspection and removal method. Stock sketches show
the declared blank or envelope; hole patterns, weld/bond geometry and mating fits
still need controlled manufacturing drawings. No part list grants manufacturing release.

Several interfaces were reconciled during the breakdown: body roof pads are flat
water/dielectric layers, while services owns distinct vibration mounts; electrical
door sensitive-edge inserts fit the separately counted body rubber profile. The
battery bill includes 72 series links/car, 150 external terminal fixings/car, 15 cold
plates/car, explicit headers/hoses/ports and active chilling. A radiator alone
cannot hold a 45°C module environment below a 50°C ambient.

## Formation and engineering handoff

This is a **new detail proposal**, descended from the current reference vehicle.
Its proposed 650 mm inter-car gap gives **105.25 m body-plus-gap length**, compared with
104.50 m at the parent 500 mm gap. End coupler projection, stopping tolerance and platform
margin are still unknown. The [handoff](handoff.json) carries this envelope and the same
candidate ID into inventory, interfaces, propulsion, braking, civil, manufacture and cost.
The current city fleet, platform and cost results are not silently overwritten.

Complete installed coordinates/CG/inertia, finite door/gangway/bogie motion, the service
pack's underfloor fit, roof occupancy and load paths require one installed CAD model.
Critical joints, fatigue, crash, wheel/rail dynamics, independent braking, fire/accessibility,
hot-weather duty and available propulsion need their appropriate analyses and evidence.
Neither candidate-specific propulsion nor manufacturing/operating release is selected here.

## Reproduce and revise

```bash
./osr design parts plan
./osr design parts build --output /path/to/private/fresh-parts-run
./osr design parts verify
```

Canonical editable source is [engineering/vehicle_parts](../../../engineering/vehicle_parts/).
Physical identity covers geometry, materials, counts, topology and mating contracts;
verification outcomes, prices and uncertainty remain evaluation context. All exported
items carry the same candidate and bundle. The business draft remains disabled and
performs no ERPNext, purchasing or control transactions.

Candidate: `{value['candidate_id']}`  
Bundle: `{value['bundle_id']}`
'''


def page(value,root=ROOT):
    payload=dict(candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],parts=value['parts'],materials=value['materials'],
        assemblies=value['assemblies'],technical_sources=value['technical_sources'],counted=value['counted'])
    template=(Path(root)/'engineering/vehicle_parts/catalogue.html').read_text()
    data=json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    return template.replace('/*CATALOGUE_DATA*/',data)


def artifacts(value,root=ROOT):
    stock=[dict(part_id=p['id'],candidate_id=value['candidate_id'],component_definition_id=p['component_definition_id'],
        quantity_per_train=p['quantity_per_train'],material_id=p['material_id'],stock=p['stock'],mass_basis=p['mass_basis'],
        note='Gross/nominal blank or envelope; no nesting yield, kerf optimisation or released hole/joint geometry') for p in value['parts']]
    result={'README.md':readme(value).encode(),'index.html':page(value,root).encode(),
        'catalogue.css':(Path(root)/'engineering/vehicle_parts/catalogue.css').read_bytes(),
        'catalogue.js':(Path(root)/'engineering/vehicle_parts/catalogue.js').read_bytes(),
        'summary.json':encoded(summary(value)),'manufacturing-bundle.json.gz':gzip.compress(encoded(value),mtime=0),
        'materials.json':encoded(dict(candidate_id=value['candidate_id'],materials=value['materials'],technical_sources=value['technical_sources'],**FLAGS)),
        'stock-schedule.json':encoded(dict(candidate_id=value['candidate_id'],rows=stock,**FLAGS)),
        'assembly-plan.json':encoded(assembly_plan(value)),'business-draft.json':encoded(business_draft(value)),
        'handoff.json':encoded(dict(candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],formation=value['integration_policy']['formation'],
            stages=value['downstream'],previous_baseline_results_inherited=False,**FLAGS))}


    assets=Path(root)/'engineering/vehicle_parts/assets'
    receipt=assets/'catalogue-preview.json'
    if receipt.is_file():
        capture=json.loads(receipt.read_bytes());png=assets/'catalogue-preview.png'
        if capture['candidate_id']!=value['candidate_id'] or capture['source_html_sha256']!=sha256(result['index.html']).hexdigest() or capture['png_sha256']!=digest(png):
            raise ValueError('Catalogue screenshot differs from actual current HTML/candidate')
        result['catalogue-preview.png']=png.read_bytes();result['catalogue-preview.json']=receipt.read_bytes()
    return result


def sources(value,root):
    names=[SOURCE,'engineering/vehicle_parts/catalogue.html','engineering/vehicle_parts/catalogue.css','engineering/vehicle_parts/catalogue.js','engineering/vehicle_parts/web_assets.py']
    names += [p.relative_to(root).as_posix() for p in (Path(root)/'engineering/vehicle_parts/assets').glob('*') if p.is_file()]
    return {**value['source_sha256'],**{n:digest(Path(root)/n) for n in names}}


def publish(root=ROOT,output=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if output.exists():raise ValueError('Fresh immutable publication output required')
    value=catalogue.build(root);output.mkdir(parents=True)
    files=artifacts(value,root)
    for name,raw in files.items():write(output/name,raw)
    m=dict(schema='osr-vehicle-parts-publication/1',candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],evaluation_id=value['evaluation_id'],
        source_sha256=sources(value,root),files_sha256={name:digest(output/name) for name in files},
        native_CAD_or_solver_executed=False,scope='Part definitions, stock/allowance arithmetic, proposed routes and same-candidate handoffs; no released installed CAD or physical acceptance',**FLAGS)
    m['manifest_id']=identity(m);write(output/'manifest.json',encoded(m));return verify(root,output)


def verify(root=ROOT,output=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if any(p.is_symlink() for p in (output,*output.parents)) or any(p.is_symlink() for p in output.rglob('*')):raise ValueError('Ordinary publication files required')
    m=json.loads((output/'manifest.json').read_bytes());catalogue._unreleased(m)
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Parts publication identity differs')
    names={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p!=output/'manifest.json'}
    if names!=m['files_sha256']:raise ValueError('Parts publication inventory differs')
    value=catalogue.build(root)
    if any(m[k]!=value[k] for k in ('candidate_id','bundle_id','evaluation_id')) or m['source_sha256']!=sources(value,root):raise ValueError('Parts publication source/candidate differs')
    files=artifacts(value,root)
    # gzip headers can vary across interpreters; verify canonical decompressed JSON.
    for name,raw in files.items():
        got=(output/name).read_bytes()
        if name.endswith('.gz'):
            if gzip.decompress(got)!=gzip.decompress(raw):raise ValueError('Parts bundle differs')
        elif got!=raw:raise ValueError('Parts artifact differs: '+name)
    return dict(verified=True,candidate_id=value['candidate_id'],bundle_id=value['bundle_id'],
        assemblies=value['counted']['assembly_types'],leaf_types=value['counted']['unique_leaf_types'],manifest_id=m['manifest_id'],native_execution=False,**FLAGS)
