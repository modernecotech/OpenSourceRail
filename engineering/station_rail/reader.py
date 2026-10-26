"""Source-bound illustrated v0.6 reference reader; no hardware acceptance inferred."""
from pathlib import Path
from hashlib import sha256
import html,io,json
from . import ROOT,FLAGS
from .common import encoded,identity,digest
from .evaluation import IDS
OUTPUT='docs/design-engine/current'
RECEIPT='OpenSourceRail-Book.receipt.json'

def _inputs(root):
    root=Path(root)
    names=['engineering/station_rail/reader.py','engineering/development_baseline/book.py','engineering/development-baseline.toml',
        'README.md','docs/ROADMAP.md',OUTPUT+'/summary.json',OUTPUT+'/cities.json',OUTPUT+'/comparison.json',
        'docs/design-engine/v06-physical-closure/summary.json',OUTPUT+'/vehicle-overview.svg',OUTPUT+'/service-profile.svg',OUTPUT+'/interface-section.svg']
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
        if not re.fullmatch(r'[a-f0-9 ]{32,}',str(text)):
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
    m=summary['mass'];s=summary['service'];native=summary['native'];comp=json.loads((root/OUTPUT/'comparison.json').read_bytes());city=json.loads((root/OUTPUT/'cities.json').read_bytes())
    story += [Spacer(1,18),p('OpenSourceRail','Title'),p('v0.6 - Station-powered freewheeling rail','Heading')]
    para('Simple vehicles. Repeated civil works. Comfortable, frequent journeys.')
    para('Reference engineering and prototype design | 26 October 2026')
    figure('vehicle-overview.svg',245,'Counted material proposal. Supplier reference assemblies and residual accounts are not complete installed geometry.')
    para('Six lightweight cars run on passive wheel bogies and conventional steel rails. Wayside linear-induction motors launch and receive the train through passive onboard aluminium secondaries. The train has no traction motors, traction battery or suspension magnets.')
    para('Selected for development, with explicit trade-offs. Physical operation, lowest whole-life cost, complete installed mass and manufacturing release remain unestablished.')
    page('1. Preserve the ethos; change the support')
    para('OpenSourceRail aims to reduce whole-life transport cost through repeated components, local manufacture, accessible repair and open engineering. v0.6 removes magnetic levitation and its continuous steel-facing assemblies. This does not remove the need to prove station-only propulsion, safe stopping or the cost of the complete railway.')
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
    page('11. Reproduce and inspect')
    para('Use ./osr status, ./osr readiness, ./osr build, ./osr verify, ./osr test, ./osr book --check and ./osr workbench. ./osr sim baghdad reports its deliberate city-evaluation hold. ./osr legacy verify checks retained source/payload bytes at their recorded Git revisions.')
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
