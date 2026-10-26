"""Source-bound illustrated reader for the selected development default."""
from hashlib import sha256
from pathlib import Path
import html
import io
import json
import subprocess

from . import ROOT, OUTPUT, FLAGS
from . import selection

RECEIPT='OpenSourceRail-Book.receipt.json'


def _inputs(root):
    names=['engineering/development_baseline/book.py','engineering/development-baseline.toml',
           'README.md','docs/ROADMAP.md',OUTPUT+'/summary.json',OUTPUT+'/cities.json',
           OUTPUT+'/vehicle-overview.svg',OUTPUT+'/service-profile.svg',OUTPUT+'/interface-section.svg']
    return {n:sha256((root/n).read_bytes()).hexdigest() for n in names}


def build(root=ROOT,output=None,check=False):
    root=Path(root).resolve();output=root/'OpenSourceRail-Book.pdf' if output is None else Path(output)
    baseline=selection.load(root)
    # Authenticate current payloads before accepting them as reader sources.
    from .entrypoint import read_packet
    read_packet(root)
    sources=_inputs(root);receipt=root/RECEIPT
    current=None
    if output.is_file() and receipt.is_file():
        current=json.loads(receipt.read_bytes())
        if (current.get('schema')=='osr-current-reader/1' and current.get('selection_id')==baseline['selection_id']
            and current.get('development_default') is True
            and all(current.get(k)==baseline['vehicle'][k] for k in ('candidate_id','body_candidate_id','magnet_component_id'))
            and current.get('receipt_id')==selection.identity({k:v for k,v in current.items() if k!='receipt_id'})
            and current.get('source_sha256')==sources
            and current.get('pdf_sha256')==sha256(output.read_bytes()).hexdigest()
            and all(current.get(k) is v for k,v in FLAGS.items())):
            return dict(verified=True,cached=True,selection_id=baseline['selection_id'],pages=current['pages'],**FLAGS)
    if check:raise ValueError('Current-design reader or receipt is missing/stale')
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import cairosvg
    import matplotlib
    fonts=Path(matplotlib.get_data_path())/'fonts/ttf'
    for name,file in [('OSR','DejaVuSans.ttf'),('OSR-Bold','DejaVuSans-Bold.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('OSR',normal='OSR',bold='OSR-Bold',italic='OSR',boldItalic='OSR-Bold')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('BodyOSR',fontName='OSR',fontSize=9.3,leading=14,spaceAfter=9,textColor=colors.HexColor('#24354b')))
    styles.add(ParagraphStyle('CellOSR',parent=styles['BodyOSR'],fontSize=8,leading=11,spaceAfter=0))
    styles.add(ParagraphStyle('TitleOSR',fontName='OSR-Bold',fontSize=29,leading=35,spaceAfter=17,textColor=colors.HexColor('#123a52')))
    styles.add(ParagraphStyle('HeadOSR',fontName='OSR-Bold',fontSize=19,leading=24,spaceAfter=13,textColor=colors.HexColor('#123a52')))
    styles.add(ParagraphStyle('SubOSR',fontName='OSR-Bold',fontSize=11,leading=15,spaceBefore=9,spaceAfter=7,textColor=colors.HexColor('#16736d')))
    summary=json.loads((root/OUTPUT/'summary.json').read_bytes());index=json.loads((root/OUTPUT/'cities.json').read_bytes())
    for key in ('selection_id','candidate_id','body_candidate_id','magnet_component_id'):
        expected=baseline['selection_id'] if key=='selection_id' else baseline['vehicle'][key]
        if summary.get(key)!=expected or index.get(key)!=expected:raise ValueError('Reader input identity differs: '+key)
    if any(summary.get(k) is not v or index.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Reader acceptance state differs')
    def plain(s):
        return str(s).replace('\u2014',' - ').replace('\u2013','-').replace('\u2011','-').replace('\u2212','-')
    def p(s,style='BodyOSR'):return Paragraph(html.escape(plain(s)),styles[style])
    story=[]
    def para(s):story.append(p(s))
    def title(s):story.append(p(s,'HeadOSR'))
    def sub(s):story.append(p(s,'SubOSR'))
    def page(s):story.append(PageBreak());title(s)
    def table(headers,rows,widths):
        values=[[p(s,'CellOSR') for s in row] for row in [headers,*rows]]
        obj=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
        obj.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deeeec')),
            ('FONTNAME',(0,0),(-1,0),'OSR-Bold'),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#16736d')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f6f8')])]))
        story.append(obj);story.append(Spacer(1,12))
    def figure(name,height,caption):
        raw=cairosvg.svg2png(url=str(root/OUTPUT/name),output_width=1500)
        image=Image(io.BytesIO(raw));ratio=image.imageWidth/image.imageHeight
        w=min(490,height*ratio);h=w/ratio
        story.append(KeepTogether([Image(io.BytesIO(raw),width=w,height=h),Spacer(1,6),p(caption,'CellOSR'),Spacer(1,14)]))
    story += [Spacer(1,24),p('OpenSourceRail','TitleOSR'),p('Comfort-first development design','HeadOSR')]
    para('Simple vehicles. Repeated civil works. Frequent comfortable journeys.')
    para('Current repository design basis - 26 October 2026')
    figure('vehicle-overview.svg',205,'Exact selected material geometry; equipment and unlocated allocations are not a complete installed assembly.')
    para('Six 17 m cars, each with 44 seats plus two wheelchair places and no planned standing. All magnets and suspension controls remain onboard. A concrete beam with passive steel facings keeps the ordinary guideway simple; station winding groups provide launch and controlled arrival.')
    para('Selected for development. Stable physical operation, complete installed mass, manufacturing release and operating release have not been established.')
    sub('One configuration across the repository')
    para('The current selector, engineering dossier, 266 city calculations, delivery records, Workbench and this reader use the same physical identities. Historical evidence remains pinned to its actual source revision.')
    page('1. Ethos and system architecture')
    para('OpenSourceRail aims for low whole-life cost and useful passenger throughput through simple, repairable components and local manufacturing. The objective is a coherent railway, rather than the lightest individual part or an isolated passing simulation.')
    table(['Location','Selected approach'],[
        ('Train','Permanent magnets, fast support/guidance control, sensors, essential power, passenger services and independently retained equipment.'),
        ('Ordinary guideway','Repeated concrete beams and passive steel facings with attachment/alignment details; no permanent magnets or powered suspension equipment along ordinary spans.'),
        ('Stations','Finite launch/receiving windings, routed phase/current resources, passenger platforms and admission controls.'),
        ('Network','Fixed lines and transfers; explicit corridor, station, dwell, fleet and headway hypotheses.')],[120,370])
    para('Vehicle weight, support force, coil heating, cooling, structural deformation, guideway reactions, station propulsion and operating costs must close together. Numerical convergence alone is not feasibility.')
    sub('Comfort is an explicit service choice')
    para('The normal cap is 46 people per car: 44 fixed seats and two wheelchair places, with zero planned standing. This reduces normal passenger load and improves seating availability. Enforceable admission and compatible accessible stations are required; accidental/crowd-load and evacuation cases remain in verification.')
    para('Six cars carry 276 normal passengers. At a 120-second interval, 30 departures/hour give 8,280 passengers/hour/direction. The former 14,400 benchmark is not achieved by this seating policy. Mean waiting is 60 seconds only for regular, unsaturated service.')
    page('2. Vehicle, structure and mass')
    table(['Subsystem','Selected development basis'],[
        ('Body/frame','Aluminium extrusion frame with retained GFRP side/end structure. A fully redesigned aluminium-only body is not established.'),
        ('Floor','Aluminium skins/H80 core; selected counted floor stock 530.538 kg/car.'),
        ('Roof','1.2 mm aluminium skins, 45 mm H60 core and perimeter bearings on retained ribs; counted roof stock 495.369 kg/car. Added crossrail alternative was rejected for interference.'),
        ('Seats','20 paired benches plus four singles fit around retained structure; wall seating at door zones. Counted seat stock 258.294 kg within the retained interior account.'),
        ('Doors/windows','Two passenger doors on one side. Revised 61 mm door leaves; supplier operator reference remains unqualified. Retained laminated glass; plastic alternatives need retention, stiffness, optics and release evidence.'),
        ('Equipment','HVAC, batteries, wiring, controls, cooling, joints and protection must be located and weighed. Envelopes and accounting allocations are not invented material solids.')],[105,385])
    m=summary['mass']
    table(['Mass per car','kg','Meaning'],[
        ('Accounted tare',f"{m['accounted_tare_kg_per_car']:,.3f}",'Material, references and retained allocations'),
        ('46-person capped load',f"{m['accounted_cap_loaded_kg_per_car']:,.3f}",'75 kg/person declared hypothesis'),
        ('160-person control',f"{m['accounted_160_control_kg_per_car']:,.3f}",'Retained load sensitivity, not the normal capacity'),
        ('Complete installed tare/CG/inertia','Unknown','No complete installed mass properties claimed')],[145,95,250])
    para('Native CAD/STEP export and reopen established 20,776 material primitives and 10,198.351 kg of defined material. That is a material subset, not the complete equipped tare. Full joined-body structure, modes, fatigue and swept assembly/maintenance clearances remain open.')
    page('3. Suspension, gap and control')
    para('The selected onboard NdFeB Halbach assembly improves local force per kilogram relative to earlier ferrite research. It does not yet provide an accepted installed multiaxis force/current/temperature map, controllable equilibrium or stable hover.')
    figure('interface-section.svg',255,'Matched selected civil interface. The 12 mm coupon drawing gap is a reference pose, not an operating gap or boarding-height datum.')
    para('The lighter car has excess upward force at the retained 12 mm zero-current sample. Wider-gap samples require a different relative vehicle/facing position. Useful lift, lateral/rotational response, control current authority, temperature, damping and platform height must be solved together.')
    para('A smaller payload reduces required support force, but it does not by itself stabilize attractive magnetic suspension. Full-load reserve, force derivatives, fast control, essential power and mechanical retention remain necessary.')
    para('Electropermanent magnets may offer slow load trimming; they remain a separate research option. Fast stabilization, fault response and capture cannot be assumed from retained magnetic state or a scalar lift sample.')
    page('4. Service and finite station resources')
    table(['Input/result','Selected hypothesis or calculation'],[
        ('Headway / dwell','120 s target / 35 s'),('Launch cap / station spacing','20 m/s (72 km/h) / 2,000 m prototype'),
        ('Acceleration / deceleration','0.4 / 0.6 m/s2, flat route'),('Resistance','1,000 N/car + 1.8 v2 N/car; not measured drag'),
        ('Runtime / arrival before braking','151.930 s / approximately 14.266 m/s'),
        ('Station shared winding','800 m across launch and receipt; not 800 m for each separately'),
        ('Sections / independent resources','64 addresses/direction at 12.5 m; at least two concurrent train phase/current branches/direction'),
        ('Nominal resource interval','79.504 s; approximately 40.496 s below the 120 s target, not a safe-headway qualification')],[155,335])
    figure('service-profile.svg',195,'Analytical acceleration, drag-dependent coasting and braking for the selected accounted mass. This is not a physically levitating trip.')
    para('The winding library is 350/450/600/800/900/1,000 m. Each retained route leg selects its shortest full-engagement option. Terminal motors, overlapping intervals, phase handoff, actual voltage/current/thermal limits and safe stopping remain unqualified. The earlier 54 km/h/450 m prototype is an explicitly named comparison.')
    page('5. Baghdad and all-city recalculation')
    bag=next(r for r in index['cities'] if r['slug']=='baghdad');t=bag['totals']
    table(['Baghdad retained-stop proposal','Current result'],[
        ('Fixed lines / added passenger stops','14 / 0'),('Active + spare + cold reserve','791 + 101 + 14'),
        ('Trainsets / cars','906 / 5,436'),('Directional station winding','390,500 m'),
        ('Library counts','331 x 800 m; 133 x 900 m; 6 x 1,000 m'),('Motor interval overlaps','4; handoff/resource qualification open'),
        ('Mainline powered union coverage','Approximately 36.743%'),('Actual CAPEX / OPEX / finance','Unknown for this matched configuration')],[230,260])
    para('Fleet is recalculated from actual analytical coast/brake legs, retained terminal-time hypotheses, 35-second dwell, a 120-second interval, 12% rounded-up spares and one cold reserve per line. This is a planning requirement, not a vehicle purchase commitment.')
    para('All 266 city geographies and stops are retained. The same six-car comfort vehicle replaces older city-specific formations in current calculations. Geography and underlying map assets remain available; this migration does not regenerate or erase city basemaps.')
    para('Cities with unreachable coasting legs or no passing station-library option retain explicit failures and unknown complete totals. An unavailable total is not zero. Actual auxiliary loads, terminal energy, conversion losses and installed prices remain unqualified.')
    table(['Catalogue summary','Cities'],[(k,str(v)) for k,v in index['summary'].items() if k.startswith('cities_')],[360,130])
    page('6. Civil, electrical and thermal closure')
    para('The new interface uses passive steel facings under a 2.26 m-wide envelope. It requires counted spreaders, supports, attachments and brake/capture load paths beyond the older narrow box. A conservative prototype counts approximately 865.1 tonnes of steel per directional kilometre, before remaining prestress, reinforcement, bearings, piers and foundations. This is a redesign input, not an optimized low-cost route.')
    para('Vehicle and magnetic reactions must drive moving-load envelopes, deflection, facing alignment, prestress, piers, foundations, transport and erection. Costs must include the complete installed route and construction sequence.')
    sub('Hot-weather duty is a gating issue')
    para('The selected roof core fails the retained unshaded 0.5 solar-absorptivity, 900 W/m2, 50 C case against its continuous 70 C limit. A measured durable reflective finish, shading or material change is required; its mass and cost cannot be silently omitted.')
    para('HVAC references do not establish delivered cooling capacity or COP at 50 C. Passenger ventilation, solar gains, compressor phases, redundancy, stationary hot-weather heat rejection, charging and essential-energy endurance remain open.')
    sub('Capture, braking and recovery')
    para('The retained eight-shoe undamped capture model exceeds stated energy/force/compression bounds in required drop cases. Larger alternatives require real geometry, mass and tested force/stroke data. Independent clamp-brake force and wet/hot friction are unqualified. A stopped train outside powered zones needs a real recovery system; a time-shifted trajectory does not create restart thrust.')
    page('7. What the software evidence demonstrates')
    para('Six actual Rust controls now execute against the newly selected 72 km/h analytical profile. Nominal, journal and fault cases check protection logic and retained authority. Their virtual healthy gaps and assumed braking floors are protocol inputs, not a magnetic or brake model of the selected train.')
    para('The native car material assembly is unchanged and independently verified from its portable source-bound archive. The selected IFC exports the counted civil shell, two steel facings and five HVAC contexts, with native geometry/identity checks; it is not a complete civil or vehicle BIM.')
    para('Earlier ideal-force Project Chrono journeys are method benchmarks. The physical milestone remains an empty and capped-load six-car train establishing verified hover, traversing finite launch equipment, coasting 1.5-2 km and arriving under measured force, electrical, thermal and braking limits, followed by fault cases.')
    sub('Current delivery records')
    para('The engineering BOM, manufacturing, procurement, assembly, civil and controls packages share selection, vehicle, body and magnet identities. Missing supplier quotes, tooling, labour, origin evidence, serials, availability dates, construction crews and releases remain unknown. These records are suitable for research and requests for evidence, not fabrication authorization.')
    sub('Reproducibility')
    para('Use ./osr status, ./osr build, ./osr verify, ./osr test and ./osr book --check. The Workbench reads the same selected packet. Unsupported physical jobs hold explicitly. ./osr legacy verify checks retained evidence at its actual Git revision; historical regeneration belongs in an isolated checkout.')
    page('8. Engineering-readiness register')
    table(['Gate','State','Remaining evidence'],[(g['gate'],g['state'].upper(),g['reason']) for g in summary['gates']],[105,70,315])
    page('9. Next experiments and source records')
    for heading,text in [
        ('Magnetics and control','Resolve equilibrium and multiaxis current/temperature maps for the exact installed geometry; confirm convergence, reserve, damping and essential-power faults.'),
        ('Complete equipped vehicle','Locate and weigh all installed stock; qualify doors, glazing, seats, roof finish, HVAC and support hardpoints; derive full CG/inertia and reduced structural modes.'),
        ('Retention and stopping','Revise and count capture hardware; test energy, force and stroke. Establish independent braking friction/thermal duty and recovery outside powered zones.'),
        ('Coupled demonstration','Use the same accepted component maps and vehicle mass/structure in stationary hover, launch/coast/arrival and fault simulations. Retain no-survivor and failed cases.'),
        ('Whole-system comparison','Reoptimize civil stock and station groups, realistic dwell and transfers, manufacturing resources and equal-service costs before selecting a construction plan.')]:
        sub(heading);para(text)
    sub('Traceable repository locations')
    for name in ['engineering/development-baseline.toml','docs/design-engine/current/README.md','docs/design-engine/current/manifest.json','docs/design-engine/current/cities.json','docs/design-engine/current/exports/manifest.json','docs/ROADMAP.md','docs/archives/pre-comfort-default/manifest.json']:
        para(name)
    para('Source revision for the retained physical dossier: 578ee3950b872bf30fbf9e4207b2bda85951bdd7. The current selector is a new development-selection event; it does not rewrite earlier scientific acceptance dispositions.')
    page('Appendix: current city planning coverage')
    para('Each row refers to the same six-car 46-person/car and 120-second development target. Trainsets are analytical requirements; unknown means one or more complete-route inputs fail. The screen is only the declared analytical coast/station comparison. Actual operating qualification and prices remain open.')
    rows=[]
    for r in index['cities']:
        x=r['totals'];fleet=x['total_trainsets'];w=x['total_direction_winding_m']
        rows.append([r.get('name',r['slug']),str(x['lines']), 'Unknown' if fleet is None else str(fleet),
                     'Unknown' if w is None else f'{w/1000:,.1f}',
                     'Conditional' if r['engineering_screen']=='conditional-analytical-survivor' else r['engineering_screen']])
    table(['City','Lines','Trainsets','Winding km','Screen'],rows,[190,45,65,85,105])
    pages=[]
    def decorate(c,doc):
        pages.append(doc.page);c.saveState();c.setFillColor(colors.HexColor('#506476'));c.setFont('OSR',7.5)
        c.drawString(45,25,'OpenSourceRail | Current development design | Physical release held')
        c.drawRightString(550,25,str(doc.page));c.setStrokeColor(colors.HexColor('#d1dfe4'));c.line(45,39,550,39)
        if doc.page>1:c.drawString(45,815,'COMFORT-NDFEB-120S-1  /  26 October 2026')
        c.restoreState()
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix('.tmp.pdf')
    doc=SimpleDocTemplate(str(temp),pagesize=(595.276,841.89),rightMargin=52.5,leftMargin=52.5,topMargin=48,bottomMargin=53,
        title='OpenSourceRail - Comfort-first development design',author='OpenSourceRail',subject='Current selected development configuration; physical qualification remains open')
    doc.build(story,onFirstPage=decorate,onLaterPages=decorate,canvasmaker=lambda *a,**kw:canvas.Canvas(*a,**dict(kw,invariant=1)))
    temp.replace(output)
    text=subprocess.check_output(['pdftotext',str(output),'-'],text=True)
    for marker in ('8,280','906','Unknown','capture-energy','120'):
        if marker not in text:raise ValueError('Reader text check missing '+marker)
    result=dict(schema='osr-current-reader/1',selection_id=baseline['selection_id'],
        candidate_id=baseline['vehicle']['candidate_id'],body_candidate_id=baseline['vehicle']['body_candidate_id'],
        magnet_component_id=baseline['vehicle']['magnet_component_id'],source_sha256=sources,
        pdf_sha256=sha256(output.read_bytes()).hexdigest(),pages=max(pages),
        rendering=dict(reportlab=__import__('reportlab').Version,cairosvg=cairosvg.__version__,
            font_sha256={name:sha256((fonts/name).read_bytes()).hexdigest() for name in ('DejaVuSans.ttf','DejaVuSans-Bold.ttf')}),
        development_default=True,evidence_scope='Source-bound current development reader; numerical/physical scope explicitly separated',**FLAGS)
    result['receipt_id']=selection.identity(result)
    receipt.write_bytes(selection.encoded(result))
    return dict(verified=True,cached=False,pages=result['pages'],selection_id=baseline['selection_id'],**FLAGS)
