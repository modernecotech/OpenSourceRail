"""Source-bound illustrated v0.6 reference reader; no hardware acceptance inferred."""
from pathlib import Path
from hashlib import sha256
import html,io,json
from . import ROOT,FLAGS
from .common import encoded,identity,digest
from .evaluation import IDS
OUTPUT='docs/design-engine/current'
RECEIPT='OpenSourceRail-Book.receipt.json'
ILLUSTRATIONS='docs/assets/v0.6/illustrations.json'

def _illustrations(root):
    return json.loads((Path(root)/ILLUSTRATIONS).read_bytes())['illustrations']

def _inputs(root):
    root=Path(root)
    names=['engineering/station_rail/reader.py','engineering/development_baseline/book.py','engineering/development-baseline.toml',
        'README.md','docs/ROADMAP.md','docs/ARCHITECTURE.md','docs/first-adoptable-product.md','docs/open-source-rail-overview.md',
        'deployment/erpnext/README.md','deployment/supervision/README.md',OUTPUT+'/summary.json',OUTPUT+'/cities.json',OUTPUT+'/comparison.json',
        'docs/design-engine/v06-physical-closure/summary.json','docs/design-engine/v06-optimisation/summary.json',
        'docs/design-engine/v06-architecture/summary.json','docs/design-engine/v06-architecture/native-index.json',
        'docs/design-engine/v06-adaptive-design/summary.json','docs/design-engine/v06-adaptive-design/requirement-policy.json',
        'docs/design-engine/generative-structure/summary.json','docs/design-engine/coupled-railway/summary.json',OUTPUT+'/vehicle-overview.svg',OUTPUT+'/service-profile.svg',OUTPUT+'/interface-section.svg']
    names += [ILLUSTRATIONS,*(image['file'] for image in _illustrations(root))]
    return {name:digest(root/name) for name in names}

def build(root=ROOT,output=None,check=False):
    from engineering.development_baseline import selection
    from engineering.development_baseline.entrypoint import read_packet
    root=Path(root).resolve();output=root/'OpenSourceRail-Book.pdf' if output is None else Path(output)
    selected=selection.load(root);summary,_=read_packet(root);source=_inputs(root);receipt=root/RECEIPT
    if receipt.is_file() and output.is_file():
        old=json.loads(receipt.read_bytes())
        if (old.get('schema')=='osr-current-reader/1' and old.get('source_sha256')==source
            and old.get('pdf_sha256')==digest(output) and old.get('development_default') is True
            and old.get('selection_id')==selected['selection_id']
            and all(old.get(k)==selected['vehicle'][k] for k in IDS[1:])
            and all(old.get(k) is v for k,v in FLAGS.items())
            and old.get('receipt_id')==identity({k:v for k,v in old.items() if k!='receipt_id'})):
            return dict(verified=True,cached=True,pages=old['pages'],selection_id=selected['selection_id'],**FLAGS)
    if check:raise ValueError('Current-design reader or receipt is missing/stale')
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    import cairosvg,matplotlib
    fonts=Path(matplotlib.get_data_path())/'fonts/ttf'
    for name,file in [('OSR','DejaVuSans.ttf'),('OSR-Bold','DejaVuSans-Bold.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('OSR',normal='OSR',bold='OSR-Bold',italic='OSR',boldItalic='OSR-Bold')
    styles=getSampleStyleSheet()
    for name,size,leading,color in [('Text',9.3,14,'#24354b'),('Cell',8,11,'#24354b'),('Heading',20,25,'#123a52'),('Title',30,35,'#123a52'),('Sub',11,15,'#16736d')]:
        styles.add(ParagraphStyle(name+'OSR',fontName='OSR-Bold' if name in ('Heading','Title','Sub') else 'OSR',fontSize=size,leading=leading,spaceAfter=10 if name!='Cell' else 0,textColor=colors.HexColor(color)))
    def clean(text):
        for c in ('\u2014','\u2013','\u2011','\u2212'):text=str(text).replace(c,'-')
        import re
        if not (re.fullmatch(r'[a-f0-9 ]{32,}',str(text)) or re.fullmatch(r'g\d+ / [a-f0-9]{10}',str(text))):
            text=re.sub(r'\b(give|and|at|The|is|of|by|from|to|for|cover|approximately|its|uses|with|within|over|a|A|about|including|limit)(?=\d)',r'\1 ',str(text))
            text=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',text)
            text=re.sub(r'%(?=[A-Za-z])','% ',text)
            text=re.sub(r'\b([A-Za-z]{2,})(?=\d)',lambda m:m.group(1) if m.group(1) in {'HP','GoA','Type','LM','SCiB','OSR'} else m.group(1)+' ',text)
            text=re.sub(r'(?<=[A-Za-z])([,;:])(?=\d)',r'\1 ',text)
        return html.escape(str(text))
    def p(text,style='Text'):return Paragraph(clean(text),styles[style+'OSR'])
    story=[]
    def para(text):story.append(p(text))
    def sub(text):story.append(Spacer(1,5));story.append(p(text,'Sub'))
    def page(text):story.append(PageBreak());story.append(p(text,'Heading'))
    def table(head,rows,widths):
        data=[[p(cell,'Cell') for cell in row] for row in [head,*rows]]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcecea')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f5f7')]),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,12))
    def figure(name,height,caption):
        raw=cairosvg.svg2png(url=str(root/OUTPUT/name),output_width=1500);im=Image(io.BytesIO(raw));w=min(490,height*im.imageWidth/im.imageHeight);h=w*im.imageHeight/im.imageWidth
        story.append(KeepTogether([Image(io.BytesIO(raw),width=w,height=h),Spacer(1,7),p(caption,'Cell'),Spacer(1,13)]))
    artwork=_illustrations(root)
    def illustration(index,height):
        item=artwork[index];im=Image(str(root/item['file']))
        w=min(490,height*im.imageWidth/im.imageHeight);h=w*im.imageHeight/im.imageWidth
        im.drawWidth=w;im.drawHeight=h
        story.append(KeepTogether([im,Spacer(1,7),p(item['title']+'. '+item['caption'],'Cell'),Spacer(1,13)]))
    m=summary['mass'];s=summary['service'];native=summary['native'];comp=json.loads((root/OUTPUT/'comparison.json').read_bytes());city=json.loads((root/OUTPUT/'cities.json').read_bytes())
    story += [Spacer(1,18),p('OpenSourceRail','Title'),p('v0.6 - Station-powered freewheeling rail','Heading')]
    para('Simple vehicles. Repeated civil works. Comfortable, frequent journeys.')
    para('Reference engineering and prototype design | 27 October 2026')
    illustration(0,275)
    para('Concept artwork illustrates the intended railway. Controlled geometry and engineering records govern dimensions and equipment; these images do not establish physical performance or qualification.')
    para('Six lightweight cars run on passive wheel bogies and conventional steel rails. Wayside linear-induction motors launch and receive the train through passive onboard aluminium secondaries. The train has no traction motors, traction battery or suspension magnets.')
    para('Selected for development, with explicit trade-offs. Physical operation, lowest whole-life cost, complete installed mass and manufacturing release remain unestablished.')
    page('The whole OpenSourceRail project')
    para('OpenSourceRail develops the railway and the open tools needed to plan, design, procure, manufacture, construct, commission, operate, maintain and renew it. The aim is to retain design authority, software, fabrication, integration and repair capability in-country. Changing the reference vehicle does not remove that wider remit.')
    table(['Connected product','Useful scope','Present boundary'],[
        ('Design and delivery platform','City inputs, candidate revisions, quantities, supplier enquiries, project and lifecycle evidence.','Research workflows and retained business/supervision software; complete current-family deployment integration remains open.'),
        ('Railway and manufacturing system','Vehicles, stations, civil works, material/process choices, tooling, assembly and repair.','Physical candidates and numerical methods; installed equipment, production data and qualification remain incomplete.'),
        ('Open GoA4 controls','Station-led dispatch, ATP, interlocking, supervision and independent fault response.','Rust research, simulation and method/formal checks; no live railway or operating release.')],[115,190,185])
    para('ERPNext and Frappe HR retain project, procurement, workforce, stock, manufacturing, quality and maintenance functions. FUXA and the gateway retain equipment observations, trends, alarms, history and review-linked lifecycle records. Real deployment needs legal entities, users, business masters, device bindings, permissions and reviewed imports.')
    para('The current engineering Workbench is read-only. The separate planning prototype supports local editing and exports over historical packets; its v0.6 compilation remains unconnected. Earlier native ERPNext/FUXA/Workbench exercises are maglev-era simulation evidence, not commissioned v0.6 installations.')
    para('A controlled first adoption can organise a workshop, depot or bounded planning pilot before a new train is physically qualified. A business case closure, cleared alarm, source hash or simulated inspection cannot accept manufactured hardware or authorise movement.')
    para('Start with README.md, docs/first-adoptable-product.md, docs/ARCHITECTURE.md and the deployment/erpnext/ and deployment/supervision/ guides. The v0.4 and v0.5 front pages remain linked at their exact historical commits.')
    page('Local capability, manufacture and affordability')
    para('The objective is a simple, repairable railway with low whole-life cost. Develop concrete precasting, structural fabrication, GFRP panels, winding, interiors, wiring, assembly, inspection and maintenance locally. Specialist components remain competitively sourced and must retain their actual origin.')
    table(['Decision','What the comparison must include'],[
        ('Vehicle and equipment','Complete installed mass, passenger comfort, accessible layout, joints, thermal/fire behaviour, supplier evidence and repair access.'),
        ('Civil construction','Rails/fastenings, beams, torsion, bearings, piers, foundations, drainage, containment, emergency access, transport and erection.'),
        ('Manufacturing','Purchased stock, cuts, scrap, EBOM/MBOM, moulds/extrusions, tooling, joining, assembly precedence, labour, inspection and maintenance.'),
        ('Service and economics','Capacity, protected headway, dwell, fleet, stations and power, construction, purchased energy, availability, maintenance and renewals.')],[125,365])
    para('A lighter body can reduce motor demand and civil loading, but a cheaper train can still require a more expensive station or guideway. The same candidate must carry its physical, operating and manufacturing consequences through the comparison. Unknown equipment and prices stay unknown.')
    para('Local content means origin-traced domestic value added. A distributor address does not establish where cells, semiconductors, bearings, materials or machinery were manufactured. Financing and foreign-currency requirements need supported procurement and programme assumptions, separately from physical resource cost.')
    para('Current candidate packages generate CAD/IFC stock, engineering and manufacturing records, assembly/procurement tasks and disabled ERPNext drafts. They are not submitted purchases, qualified shop instructions, an as-built operating twin or a complete priced construction/cashflow plan.')
    para('Earlier LM3 factory targets, the v0.4 localisation illustration and v0.5 city budgets remain historical scenarios. They do not establish v0.6 prices, savings or domestic-content percentages. All 266 city geographies remain inputs; new performance publication remains held.')
    para('Contributors can improve material/supplier evidence, complete assemblies, physical models, manufacturing and repair methods, controls, city data and tests. See CONTRIBUTING.md and GOVERNANCE.md. Software uses Apache 2.0, open physical designs CERN-OHL-S v2 and documentation CC-BY-SA 4.0, subject to the notices in LICENSE.md.')
    page('Passenger comfort and local assembly')
    para('Concept illustrations of the seated passenger experience and local manufacturing objective. Detailed equipment, accessible clearances and assembly sequences remain engineering work.')
    illustration(1,220)
    illustration(2,220)
    page('Precast construction and station propulsion')
    para('Concept illustrations connect repeated civil works with station-powered wheel rail. The LIM interface is schematic; motor clearances, supports and powered-section lengths follow the candidate engineering records.')
    illustration(3,220)
    illustration(4,220)
    page('1. Preserve the ethos; change the support')
    para('OpenSourceRail aims to reduce whole-life transport cost through repeated components, local manufacture, accessible repair and open engineering. v0.6 removes magnetic levitation and its continuous steel-facing assemblies. This does not remove the need to prove station-only propulsion, safe stopping or the cost of the complete railway.')
    figure('vehicle-overview.svg',125,'Generated counted stock geometry. Supplier reference assemblies and residual accounts are not complete installed geometry.')
    table(['Location','Reference architecture'],[
        ('Train','Six 17m aluminium/GFRP comfort cars; identical passive bogies, independent brakes, ATP, communications, service battery, HVAC and solar roof.'),
        ('Ordinary guideway','Conventional running rails and direct fastenings on precast concrete; box, twin-beam and U-beam alternatives.'),
        ('Stations','Finite LIM primary sections, inverters, power/charge equipment, reserved receiving berth and compact elevated platforms.'),
        ('Control','Existing station-led GoA4 architecture with continuous onboard ATP and independent mechanical braking. No mainline switches; depot exceptions only.')],[105,385])
    para('Each car retains 44 fixed seats plus two wheelchair places, zero planned standing and two doors on one side. Four-abreast seating and door-zone wall benches preserve the comfort choice. 276 people/train at 120s gives 8,280 passengers/hour/direction; this is capacity arithmetic, not a demonstrated protected headway.')
    para('The revised floor reference is1.0m above rail to clear conventional running gear. Platform access, one-sided doors, centre-platform compatibility, evacuation and passenger admission need physical verification. The160-person/car crowd case remains a structural and braking sensitivity.')
    page('2. Equipped vehicle and mass accounts')
    table(['Per car','Reference result','Meaning'],[
       ('Accounted tare',f"{m['accounted_tare_kg_per_car']/1000:.3f}t",'Materials, supplier references and unlocated accounts'),
       ('46-person normal load',f"{m['accounted_cap_loaded_kg_per_car']/1000:.3f}t",'75kg/person hypothesis'),
       ('160-person crowd control',f"{m['accounted_160_control_kg_per_car']/1000:.3f}t",'Not the intended normal capacity'),
       ('Located material',f"{m['located_material_kg']/1000:.3f}t",'Native geometry subset, not complete tare'),
       ('Installed tare / CG / inertia','Unknown','Residual stock and complete equipment placement unresolved')],[130,90,270])
    para('Twelve two-axle bogies give24axles and48wheels. Motors and gearboxes are absent. Suspension, bearings, disc brakes, WSP, parking and wheel odometry remain. The6,730kg/car bogie reference includes partial proposed material and a transparent supplier/detail residual.')
    para('The new body has concentrated bogie reactions at12.8m centres rather than distributed magnetic supports. Deep side sills and the retained roof longitudinal members provide the intended body load path. The isolated side-sill fixture fails its declared stiffness limit. Ideal whole-body chord coupling is a necessary upper bound; posts, joints, shear transfer, openings, torsion, fatigue and crash behaviour remain unqualified.')
    para('Inherited body/service residuals may overlap new battery and electrical equipment. No unsupported mass subtraction is made. This conservative account needs disaggregation before it becomes a definitive equipped mass. Split battery cassettes, connections and removal paths remain unresolved.')
    para('The revised roof proposes HP60 core and a white finish. Glass, doors, floor and seating retain source ancestry; plastics remain alternatives requiring impact, fire, optics, retention and repair evidence.')
    page('3. Station motor: requirements before claims')
    para('The reference is a double-sided LIM. Powered primaries and converters remain wayside; each train car carries a9m passive aluminium secondary with support and heat-spreading stock. Single-sided LIM and synchronous PM alternatives remain comparisons.')
    figure('interface-section.svg',235,'Reference projected interface. Nominal15mm side clearance is a design target, not a demonstrated dynamic motor gap.')
    table(['2km normal-load requirement','Calculated target'],[
       ('Launch acceleration / speed cap','0.4m/s2 /20m/s; ideal powered distance500m'),
       ('Shared winding library choice',f"{s['shared_winding_m']:.0f}m across launch and receipt"),
       ('Section addresses / independent branches',f"{int(s['shared_winding_m']/12.5)} per direction; at least2train current/phase branches"),
       ('Actual available thrust / voltage / current','Unknown; requires actual primary and moving-secondary field maps')],[255,235])
    para('The executed GetDP manufactured conductive-slab model converges against an exact imposed travelling-field solution. It verifies a numerical method. It omits the actual primary, steel, slots, finite-height current closure, motor ends and inverter circuit; conditional force is not available train thrust.')
    para('Moving suspension, wheel wear, alignment, fin expansion and unwanted motor normal forces must fit the same clearance envelope. Full entry, exit, sectional handoff and120-second repeated duty remain gates.')
    page('4. Reference motion and independent stopping')
    table(['Input/result','Reference'],[
       ('Route / load','2,000m, six normal-load cars; flat route and declared resistance'),
       ('Runtime',f"{s['prototype_runtime_s']:.3f}s analytical target"),
       ('Berth resource interval',f"{s['nominal_resource_interval_s']:.2f}s necessary screen;120s target unqualified"),
       ('Resistance','0.0025mg +50N/car +1.8v2 N/car hypothesis; not measured drag'),
       ('Motion evidence','Required force, energy and geometry; physical train journey not completed')],[180,310])
    figure('service-profile.svg',205,'Target acceleration, natural coasting and receiving brake profile. Prescribed kinematic acceleration does not prove motor capability.')
    para('Empty, normal and crowd-control1.5/2km cases are evaluated, with grade and headwind sensitivities. The longest retained adjacent city gap is approximately3km. Adverse uphill cases can stop before receipt; downhill cases can violate the unpowered speed cap. Failures stay visible instead of adding silent boosters.')
    para('Onboard mechanical service/emergency/parking brakes must work independently of station power. A0.05adhesion hypothesis on a2%downhill gives about700m stopping from20m/s including1 s response, with no regeneration or resistance credit. Actual wet/hot curves, WSP, brake channels and thermal duty remain unknown.')
    page('5. Service energy, solar and hot weather')
    para('The auxiliary pack is for HVAC, doors, lights, communications, ATP and emergency functions only. No wheel-drive connection exists. The82.8kWh reference uses75industrial Type3-20 modules,25series by3parallel, plus enclosure, cooling, conversion, protection and retention accounts:1,345kg/car. This is not a railway-qualified installed pack.')
    table(['Necessary energy/current check','Result and qualification boundary'],[
       ('35s station charge target','200kW/car;1.2MW/train before simultaneous traction and station services'),
       ('Normal hotel load','35kW/car declared reference; prototype repeated-energy bound passes'),
       ('Adverse hotel load','50kW/car requires extra charge time in the2km case'),
       ('Hot-weather battery','Catalogue module ambient upper limit45C;50C surroundings require a proven cooled enclosure'),
       ('Ageing/reserve','80%end-of-life and90%hot-capacity hypotheses; SOC window20%-90%'),
       ('Solar','Flush roof PV retained; no unproven energy yield credited to make service pass')],[175,315])
    para('Catalogue voltage and continuous-current bounds do not establish charge acceptance versus SOC, temperature or life. A missed charge, stranded train and independently protected essential reserve require dispatch and emergency-energy validation. Longer/hot legs can change terminal charging, fleet and service.')
    para('LIM secondary heating is exposed over several slip assumptions. Active-plate-only and full-aluminium heat-capacity bounds differ; actual thermal conductance, repeated-duty cooling and receiving losses are unknown. A large calculated force obtained with imposed field can carry unacceptable secondary heat.')
    para('HVAC delivered cooling and COP at50C remain unknown. Passenger ventilation, solar gain, stationary heat rejection, redundancy, roof hot strength and durable reflective coating must close together.')
    page('6. Three civil alternatives and construction')
    para('Conventional rails replace continuous magnetic facings. Compare a closed box, two narrow beams with gauge-control diaphragms, and a U-section. Lower concrete area alone does not establish the least-cost guideway: torsion, rail support, foundations, containment, maintenance and erection matter.')
    c=comp['selected_civil_reference']
    table([f"Selected {c['span_m']:.0f}m crowd-sized box",'Counted quantity'],[
       ('Concrete',f"{c['concrete_m3']:.3f}m3"),
       ('Running rails',f"{c['running_rail_kg']/1000:.3f}t"),
       ('Steel incl. preliminary rebar/tendons',f"{c['counted_steel_kg']/1000:.3f}t"),
       ('Actual installed cost','Unknown')],[285,205])
    para('The selected reference is20m with26prestressing strands sized to the crowd load. The same fixed beam/tendons are checked at empty, normal and crowd loads; three families across four spans retain their separate comparisons. It is a necessary longitudinal screen, not an installed-cost winner.')
    para('Moving axle-load envelopes are calculated at each longitudinal section. Each section receives its own critical train position; it does not reuse one global peak. Prestress, no-train and release stress checks and a conservative deflection envelope remain analytical screens.')
    para('Steel boundaries differ from v0.5: its21.627t/25m interface account excluded reinforcement/prestress, while the new total includes preliminary detailing. Neither includes complete piers, foundations, bearings, walkways, containment and station primaries. Concrete quantity can increase. No steel saving is converted directly to a dollar saving.')
    sub('Construction sequence')
    para('Survey and geotechnical investigation; foundations; piers/headstocks; bearings and temporary stability; precast lift; rails and gauge setting; station motor installation; survey, inspection and independent release. Actual ground, crane radius, labour, factory throughput and supplier lead times are required.')
    para('Same-candidate BOM, manufacturing, procurement, assembly and controls records are research drafts. Unknown prices, availability dates and material release are not replaced with zeros or unconstrained schedules.')
    page('7. Automation, faults and retained geography')
    para('Station-led GoA4 reserves route and receiving berth, proves configuration and train readiness, sequences launch equipment and supervises receipt. Independent onboard ATP continuously enforces authority. Stations never replace the train brake protection layer.')
    para('Actual Rust ATP/interlocking, TCMS, doors and SCADA regressions are retained. New configuration-bound wheel/station predicates exercise readiness faults and mechanical brake requests. Inputs are fixtures: they establish neither a physical brake curve nor a safety-qualified GoA4 product. Historical magnetic healthy-gap fixtures remain archived.')
    table(['Fault','Required independent response'],[
       ('Receiving drive or communications lost','Respect authority and independent stopping envelope; cut station thrust and command brakes where required'),
       ('Localisation/integrity uncertain or berth occupied','Restrict authority and stop; no blind timer-based launch'),
       ('Wet rail or brake channel loss','Qualified WSP and degraded brake floor; protect the larger stopping distance'),
       ('Off-zone stop','No autonomous restart; protected rail-compatible rescue/towing and evacuation plan'),
       ('Service power lost','Independent essential/brake supply and emergency ventilation; hot-weather endurance qualification')],[170,320])
    para(f"The {city['city_count']} city geographies and detailed maps are preserved. No v0.6 city performance packages are generated. A metadata-only scan covers17,268adjacent operating-stop gaps; the longest is2,999.931m in Faisalabad. Grades, sites, demand, transfers, power and prices remain city-specific.")
    para('City commands return an explicit evidence hold. Existing fleet, winding, cost and finance figures describe historical designs. They are not carried over as v0.6 results.')
    page('8. Equal service and the selection decision')
    table(['Candidate','Accounted/proxy tare','Normal comparison load'],[(r['name'],f"{r['accounted_tare_kg_per_car']/1000:.3f}t/car",f"{r['comparison_normal_loaded_kg_per_car']/1000:.3f}t/car") for r in comp['alternatives']],[220,135,135])
    para('All comparison profiles use276people/train,75kg/person,120 s headway,72 km/h cap and the same nominal acceleration/braking. Drag hypotheses remain architecture-specific and unmeasured. The v0.4 row is an optimistic arithmetic proxy from its16.5m LM3, with traction/battery categories removed before replacement service equipment; it is not a designed17m comfort vehicle.')
    para('v0.6 is selected for research and prototype development by user direction because wheel support removes the unresolved levitation system and continuous magnetic-facing assemblies. Its vehicle account is heavier than v0.5; station-only LIM, high platforms and rescue introduce costs. The selection deliberately records that trade-off.')
    para('Whole-life economic acceptance remains unknown. Vehicle and station prices, supply reinforcement, construction, maintenance, wheel/rail renewal, energy tariffs, reliability, fleet, staff and financing need equal-service source data. The current package does not demonstrate that v0.6 beats v0.5 or a simpler powered rail alternative.')
    sub('Release remains separate')
    para('A prototype package needs reviewed drawings, tolerances, joining, tooling, BOM, procurement, inspection and an instrumented test programme. Development adoption does not grant manufacturing, physical motion or operating release.')
    page('9. Evidence gaps and next work')
    table(['Gate','State','Required evidence'],[(g['gate'],g['state'],g['reason']) for g in summary['gates']],[110,55,325])
    page('10. Native motor, body and brake follow-up')
    followup=json.loads((root/'docs/design-engine/v06-physical-closure/summary.json').read_bytes());motor=followup['motor']
    para('The bounded follow-up adds18current-excited GetDP motor cases and24actual Chrono brake executions. These are component/reduced-model experiments, not a physically coupled launch-coast-arrival journey.')
    table(['Executed comparison','Result'],[
        ('Full12.5m primary and9m secondary',f"{motor['force_N_full_geometry_2D']/1000:.3f}kN/car versus{motor['required_force_N_per_car']/1000:.3f}kN required"),
        ('Peak steel field','2.240T exceeds declared1.3T linear-domain bound'),
        ('Bare primary copper and steel',f"{followup['motor_primary_bare_stock_kg_per_m']:.1f}kg/m, excluding cooling, supports and power equipment"),
        ('Full motor heat at tested point','52.1kW secondary plus43.6kW primary copper per engaged module')],[240,250])
    para('Successful zero-current, phase-reversal and energy checks do not repair the force deficit or out-of-domain steel. Winding regrouping can reduce an arithmetic voltage requirement at much higher converter current, but finite-overlap current sharing and thermal duty are unknown. Installed available force stays unknown.')
    rows=[]
    for case in followup['brake_cases']:
        if case['load']=='normal':rows.append((case['case'],'Cannot stop' if case['stop_distance_m'] is None else f"{case['stop_distance_m']:.1f}m"))
    table(['Normal-load braking from20m/s','5ms Chrono result'],rows,[300,190])
    para('Wet/downhill uses adhesion0.05 on a2%downgrade; lost channel retains four discs/car. Assumed pad friction, piston pressure and ideal instantaneous WSP are not qualified hardware. The crowd failed-channel case needs over3km. Fault detection, authority, route speed and protected overrun must use a validated degraded stopping envelope.')
    para('Independent body verification rejected native rotational beam equations and an overly rigid solid-section fixture. Rejected results remain recorded. Counted post connections and actual floor cutouts/collars add77.154kg/car before unknown joining hardware; they are an unadopted alternative. Native stock fit-up does not prove body strength, fatigue or complete assembly.')
    para('Counted wheel, axle and disc rotation adds1,770.387kg/car equivalent inertial mass, with no added static weight. It now feeds launch work, coasting and brake energy. Exact findings, benchmark dispositions and compact source-bound evidence are in docs/design-engine/v06-physical-closure/.')
    page('11. Failure-driven candidate generations')
    campaign=json.loads((root/'docs/design-engine/v06-optimisation/summary.json').read_bytes())
    para(f"The existing runner completed{campaign['generations']}generations and{len(campaign['candidates'])}physical wheel/LIM candidates. Code generated each revision from recorded failures; the reference geometry was not manually edited between trials.")
    rows=[]
    for c in campaign['candidates']:
        body=next((x for x in c['body_cases'] if x['case']=='normal-fine'),{})
        deflection='Unknown' if body.get('maximum_vertical_displacement_m') is None else f"{1000*body['maximum_vertical_displacement_m']:.1f}mm"
        rows.append((f"g{c['generation']} / {c['candidate_id'][:10]}",f"{c['mass_kg_per_car']/1000:.3f}t",deflection,c['motor_numerical_status']))
    table(['Generation /candidate','Accounted tare/car','Normal deflection','Motor validity'],rows,[145,100,115,130])
    research=next((c for c in campaign['candidates'] if c['candidate_id']==campaign['next_experiment']['selected_candidate_id']),None)
    if research:
        crowd=next((c for c in research['body_cases'] if c['case']=='crowd'),{})
        running=next((c for c in research['motor_cases'] if c['speed_m_s']==20),{})
        crowd_value=crowd.get('maximum_vertical_displacement_m');force_value=running.get('metrics',{}).get('force_N');required_value=research.get('motor_required_force_N')
        crowd_text='Unknown' if crowd_value is None else f'{1000*crowd_value:.1f}mm'
        force_text='Unknown' if force_value is None else f'{force_value/1000:.3f}kN'
        required_text='Unknown' if required_value is None else f'{required_value/1000:.3f}kN'
        para(f"The next experiment accounts for{research['mass_kg_per_car']/1000:.3f}t/car. Its crowd deflection is{crowd_text} against25.6mm. Required thrust is{required_text}/car; the conditional calculation is{force_text}. Invalid motor fields cannot establish available thrust or physical feasibility.")
    para('The lighter participating-panel branch remains laterally nonconverged. Its vertical values are diagnostic. Synthetic laminate/core constants and ideal clamp transfer are unqualified; invalid body results trigger model work rather than unsupported geometry revisions.')
    para('Valid frame failures generate deeper/thicker counted stock. Motor revisions change teeth, backiron and windings; matched fin/neck geometry, car mass, rotor energy, brakes and civil loads propagate together. The fixed linear-steel limit cannot be relaxed to manufacture a pass.')
    para('Exact dependency digests, source revisions and solver identities bind caches and restart. The Pareto comparison ranks diagnostic priority and counted quantities. Prices and complete installed equipment remain unknown; research selection cannot satisfy integrated acceptance.')
    para('Every candidate generates native FreeCAD/STEP, reopened IFC, material takeoff and draft assembly, QA, procurement and maintenance records for known stock. Unknown equipment has no placeholder solids. Position-dependent journeys, joint/fatigue checks, qualified brakes and complete mass/CG/inertia remain open.')
    para('Inspect docs/design-engine/v06-optimisation/ and ./osr design campaign create/run/compare/publish. Typed next tasks retain candidate and trigger IDs with bounded scope. The266city packages and prior physical evidence remain preserved.')
    page('12. Challenge the railway architecture')
    architecture=json.loads((root/'docs/design-engine/v06-architecture/summary.json').read_bytes())
    para(f"The umbrella research campaign executes{architecture['evaluation_cases']}analytical cases across{architecture['physical_definitions']}physical definitions and{architecture['generations']}generations. It preserves the selected v0.6 reference while testing different propulsion distribution, powered-track length, speed, formation and concrete sections.")
    table(['Family','Research arrangement'],[(r['family_id'],r['label']) for r in architecture['families']],[50,440])
    para('Required-force trajectories compare4/6/8cars,1.5/2/3km station spacing and43.2/57.6/72km/h caps on a6km comparison ring. New drive and recovery equipment remains unweighed. Changed station density changes access service. Protected headway, actual available thrust and complete installed costs remain unknown; no economic winner or physical journey is claimed.')
    para('Six-axis finite-area joint fixtures now check work, equilibrium, reciprocity and modal refinement. The counted whole-body alternative adds113.008kg/car of known stock. After a retained3GiB allocation failure, a separately recorded5GiB resource revision completes the finer mesh without changing physics or limits. The vertical mesh change is1.43%; normal deflection28.018mm exceeds the provisional25.6mm comparison. The new adaptive policy treats that comparison as advisory. Perfect bonds and ideal section transfer require physical calibration and local joint/strength/fatigue checks.')
    para('The nonlinear DC magnetic method reproduces a generic49-point material circuit and its independent coenergy-gradient force. It is not selected motor steel or a moving nonlinear LIM. Spatial entry/centre/exit controls remain linear. Full nonlinear moving thrust, losses, inverter and thermal maps are still needed before a motor can supply a physical journey.')
    para('Capability admission binds geometry, interfaces, evaluator, benchmark, source and validity domain. Unsupported configurations generate bounded implementation or measurement tasks. M1 component correlation, M2 passive-carriage launch/coast/stop and M3 integrated pilot plans require measured data, uncertainty and independent review; none is marked complete.')
    para('Inspect docs/design-engine/v06-architecture/. Run ./osr design architecture run/publish/verify. Exact-source caching and an interrupted-run receipt demonstrate restart. The Workbench exposes all seven families, and scheduled CI runs bounded joint and nonlinear magnetic method checks.')
    page('13. Adaptive design from broad requirements')
    adaptive=json.loads((root/'docs/design-engine/v06-adaptive-design/summary.json').read_bytes())
    para(f"The function-first generator declares{adaptive['variable_count']}extensible variables across{len(adaptive['domains'])}domains. Materials, honeycombs, layups, load paths, joints, support arrangements, propulsion, fitout, service and civil/construction methods can change under separately identified research configurations. Examples are seeds, not an exhaustive menu.")
    para('Mandatory functional and safety obligations remain. Quantitative hard limits need a justified interface/material/function basis. Initial dimensions, L/500-style deflection comparisons, speed and headway are explicitly revisable hypotheses or targets. Numerical-model limits stay separate: changing the old linear-steel field bound cannot create nonlinear physics.')
    table(['Native section experiment','Tare account/car','Normal bending','Stock change'],[(r['section'],f"{r['accounted_tare_kg_per_car']/1000:.3f}t",'Unconfirmed' if r['normal_vertical_displacement_m'] is None else f"{r['normal_vertical_displacement_m']*1000:.3f}mm",f"{r['mass_change_vs_previous_jointed_body_kg']:+.2f}kg") for r in adaptive['rows']],[160,115,115,100])
    para('Changes are relative to the previous finite-area jointed body:19.335t/car and28.018mm normal displacement. These are counted stock plus inherited accounts, not a complete installed vehicle mass. Normal coarse/fine and crowd runs use the actual new section stock and passenger loads. Both displacement trends are checked; each crowd result has only one mesh.')
    para('The600mm-deep,5mm-wall experiment redistributes stock: about48kg/car less material and19.793mm normal bending. A500mm-deep alternative retains more underbody space. These model observations motivate further design work; local buckling, strength, joints, fatigue, flexible modes, swept clearances and physical correlation remain unknown.')
    para('Actual revised mass propagates to axle reactions, inertia-aware1.5/2/3km propulsion/energy demand and crowd-sized concrete alternatives. Available motor performance and complete installed cost remain unknown. Improving a provisional target does not establish safe operation.')
    para('The planner diagnoses physical failures, advisory targets, numerical/model problems and missing evidence separately. Repeated unsuccessful local changes escalate toward new load paths or architecture. Pending work survives invocation budgets. Exact native physics can be reused under a new policy context without changing its original receipt or pretending a new solve occurred.')
    para('Inspect docs/design-engine/v06-adaptive-design/ and ./osr design adaptive plan/run/publish/verify. The Workbench exposes the variables and native comparisons; the current reference and city geography remain unchanged. The search continues through its explicit frontier rather than declaring that one failed comparison ends the design.')
    page('14. Generate a different structure')
    generative=json.loads((root/'docs/design-engine/generative-structure/summary.json').read_bytes())
    para(f"The new structural grammar executes {generative['initial_recipe_count']} initial recipes and {generative['rewrite_count']} physical rewrites. Shared productions combine aluminium or research GFRP members, skins, foam/honeycomb sandwich layers, rib arrangements, modular segments and integrated roof functions. New combinations do not require another predefined body mesh; unsupported primitives and physics still need development.")
    table(['Executed stage','Result','Evidence boundary'],[
        ('Generated candidates',str(generative['candidate_count']),'Actual stock, apertures, material and joining definitions'),
        ('Native CAD exports',str(generative['CAD_case_count']),'FreeCAD and STEP reopen with matching stock volumes'),
        ('Axial design calculations',str(generative['native_design_case_count']),'Independent stiffness, equilibrium and energy checks'),
        ('Complete body qualification','Unknown','Shell, joints, buckling, modes, fatigue and correlation remain open')],[145,70,275])
    para('The initial pin-jointed rectangular underfloor has 49 mechanisms. Diagnosis generates a new triangulated load path below the passenger openings, regenerates its stock and loads, and reruns it. The child has zero mechanisms; two native axial subdivisions agree with the independent matrix solution. Its approximately 30.35 mm displacement belongs to an underfloor-only hypothesis, not the previous whole-body model. No L/500 acceptance claim follows.')
    para('A separate rewrite integrates roof, solar-mount and cable/drain functions into fewer declared manufactured groups. About 44 kg of nominal stock is removed, but equivalent performance, installed hardware, manufacture, sealing and repair remain unproven. A third rewrite changes rib positions. Material search and typed interfaces hold missing hot/wet, directional, capacity and process evidence explicitly.')
    para('Gross untrimmed stock includes unresolved node overlaps and joint cuts. Known-stock CG and inertia can be calculated; complete installed mass properties and prices cannot. Source-bound equipment accounts remain unlocated. New stock propagates to the same candidate\'s motion demand and civil screens, not a validated force-motion-thermal journey.')
    para('A failed tripod constraint input was preserved, the writer repaired, and four fresh independent fixtures passed. Numerical model repair is distinct from physical redesign. OpenMDAO, pymoo and Dakota were not executed for this comparison. Native FreeCAD and CalculiX performed the CAD and axial work. Inspect docs/design-engine/generative-structure/ or run ./osr design generative plan/run/publish/verify.')
    page('15. One coordinated railway experiment')
    coupled=json.loads((root/'docs/design-engine/coupled-railway/summary.json').read_bytes())
    para(f"The new coordinator connects architecture, adaptive revision proposals, physical bodies, installed inventory, interfaces, propulsion demand, braking, civil loads, manufacture and economic coverage. It starts with five structural recipes and retains {coupled['body_count']} body definitions after physical revisions. {coupled['evaluated_bundle_count']} railway bundles produce {coupled['downstream_stage_count']} linked stage records under the same six-car comfort/service comparison.")
    para('A body change assigns new physical identities and automatically invalidates dependent evaluations. New structural evidence also changes the case context even if geometry is unchanged. Exact native input, candidate, load, mesh, model source, executable and resources are checked before reuse. Stable experiment identity is separate from invocation and cache counters; pending tasks survive bounded runs.')
    table(['Shared calculation','Current evidence boundary'],[
        ('Inventory and manufacturing','Actual stock, cuts/blanks, joints, assembly operations and source-bound quote coverage. Unlocated equipment and unknown hardware stay explicit.'),
        ('Architecture and motor','Seven families and two primary-iron definitions. Changed bodies feed required force and powered-track quantities; available operating thrust is unknown.'),
        ('Braking and civil','Actual accounted mass, wheel rotational inertia, nine brake hypotheses and three crowd-loaded precast alternatives. No proven protection floor or complete site design.'),
        ('Economics and delivery','Scoped Pareto alternatives, matching BOM/assembly, disabled ERP research drafts and reopened IFC body stock. Installed costs and release remain unknown.')],[120,370])
    para('Wheel-traction and alternative-secondary configurations remove the retained passive-secondary account. Replacement drive/store/secondary equipment remains unweighed, with no zero-mass substitution. The physical-definition projection contains the actual new body, roof/material stock and selected equipment instead of stale reference-car fields.')
    para('No candidate has a complete installed mass, CG, inertia, purchased energy or whole-life cost. The forward journey refuses unavailable or invalid force maps. These are connected research alternatives; the selected v0.6 reference and all 266 city performance packages are unchanged.')
    para('Inspect docs/design-engine/coupled-railway/ or run ./osr design railway plan/run/publish/verify. GitHub Actions is enabled; the workflow requires engineering and browser contracts, with expensive native methods scheduled separately. A passing software check is distinct from physical qualification.')
    page('16. Three-dimensional bodies and transient fields')
    para('The generated metal frame and stressed-skin alternatives add counted floor/roof load paths, aperture frames, finite shared-face joints and roof services. Independent native fixtures check bending/shear refinement, intact-face transfer and orthotropic constitutive patches. Density-only or axial-only GFRP data receives no shell stiffness credit.')
    para('The first baseline grid created 152,004 cells and exceeded5GiB while factoring; no structural verdict followed. Aligned floor/roof profiles reduced coarse cells to about44,000-47,000 with essentially neutral stock mass and fewer extrusion families. Original inputs, failed logs and source bytes are retained. Computational budgets do not become railway acceptance limits.')
    completed=[r for r in coupled['body_rows'] if r['response']['native_cases']]
    mm=lambda value:'Unknown' if value is None else f'{value*1000:.3f}mm'
    table(['New solid model','Normal','Finer','Extra finer'],[(r['label'].replace('_',' '),mm(r['response']['normal_vertical_m']),mm(r['response']['fine_vertical_m']),mm(r['response']['extra_refined_vertical_m'])) for r in completed],[190,100,100,100])
    para('Normal/crowd incompatible-mode solid solves balance forces, moments and work/energy under intact-weld and lumped floor-load hypotheses. The frame\'s first refinement changed same-point deflection and energy materially, automatically triggering an unchanged-body0.425m experiment. Its remaining sensitivity stays open; nodal maxima are not a complete stress or whole-field convergence assessment. Torsion, through-thickness accuracy, local quadratic checks, joint/HAZ strength, fatigue, modes, thermal/fire and physical correlation remain necessary.')
    para(f"The new nonlinear transient magnetic kernel completed {coupled['magnetic_completed']} of {coupled['magnetic_method_cases']} bounded controls. Phase excitation, inverse H(B), net secondary current, Joule/mechanical work, stored energy and backward-Euler dissipation are explicit. Time refinement still changes thrust substantially. The short fixed conductor mask, generic steel and incomplete primary circuit/thermal/3D model cannot supply the actual20m/s operating map.")
    para('Actual launch-coast-arrival runs remain not-run. Required-force profiles, synthetic forward-method tests, native component calculations, independently reviewed engineering evidence and operating qualification remain separate. The next frontier requests model/equipment data and further numerical work without inventing a feasible or cheapest railway.')
    page('17. Reproduce and inspect')
    para('Use ./osr status, ./osr readiness, ./osr build, ./osr verify, ./osr test, ./osr book --check and ./osr workbench. ./osr sim baghdad reports its deliberate city-evaluation hold. ./osr legacy verify checks retained source/payload bytes at their recorded Git revisions.')
    para('The broader design-space comparison adds supplier-bound PET/PVC and directional honeycomb cores, aluminium/GFRP load paths, joints/inserts, motor topologies, glazing and HVAC leads. Run ./osr design space build/verify. Necessary bounds and component fixtures guide the next experiments; they do not establish a complete train or silently change the default.')
    para('The v0.5 archive preserves magnetic development evidence; its source and results are not overwritten to match a wheel-supported train. Historical numerical regeneration belongs in a separate checkout of the pinned revision.')
    sub('Repository records')
    for text in ('engineering/development-baseline.toml','engineering/station_rail/brief.toml','docs/design-engine/current/README.md','docs/design-engine/current/evaluation.json.gz','docs/design-engine/current/comparison.json','docs/design-engine/current/manifest.json','docs/design-engine/current/exports/manifest.json','docs/archives/v0.5-maglev/manifest.json'):
        para(text)
    sub('Physical and evaluation identities')
    for key in IDS:
        para(key.replace('_',' '));story.append(p(summary[key][:32]+' '+summary[key][32:],'Cell'));story.append(Spacer(1,8))
    para('Source receipts bind the exact files used. Native method convergence, analytical screening, independent review and authenticated physical acceptance remain separate levels of evidence.')
    def footer(c,doc):
        c.saveState();c.setFont('OSR',8);c.setFillColor(colors.HexColor('#537083'));c.drawString(48,27,'OpenSourceRail v0.6 | Research design - physical acceptance open');c.drawRightString(547,27,str(doc.page));c.restoreState()
    class StableCanvas(canvas.Canvas):
        def __init__(self,*args,**kwargs):kwargs['invariant']=1;super().__init__(*args,**kwargs)
    doc=SimpleDocTemplate(str(output),pagesize=(595.276,841.89),leftMargin=48,rightMargin=48,topMargin=43,bottomMargin=48,title='OpenSourceRail v0.6 - Station-powered freewheeling rail',author='OpenSourceRail')
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=StableCanvas)
    import subprocess,re
    info=subprocess.check_output(['pdfinfo',str(output)],text=True)
    found=re.search(r'^Pages:\s+(\d+)',info,re.MULTILINE)
    if found is None:raise ValueError('PDF page count could not be independently verified')
    pages=int(found.group(1))
    value=dict(schema='osr-current-reader/1',**{k:summary[k] for k in IDS},development_default=True,source_sha256=source,pdf_sha256=digest(output),pages=pages,**FLAGS)
    value['receipt_id']=identity(value);receipt.write_bytes(encoded(value))
    return dict(verified=True,cached=False,pages=pages,selection_id=selected['selection_id'],**FLAGS)
