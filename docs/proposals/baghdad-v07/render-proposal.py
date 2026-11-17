import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

root=Path.cwd()
base=root/'docs/proposals/baghdad-v07'
A=json.loads((base/'rfi-schematic.geojson').read_text())
B=json.loads((base/'concept-b-2035-map.geojson').read_text())
map_path=root/'tmp/pdfs/baghdad-two-concepts.png'
map_path.parent.mkdir(parents=True,exist_ok=True)
(root/'output/pdf').mkdir(parents=True,exist_ok=True)
navy='#123047'; teal='#007f86'; gold='#bf812d'; red='#bd4c42'; gray='#84939b'
fig,ax=plt.subplots(1,2,figsize=(12.8,5.4),dpi=175)
fig.patch.set_facecolor('#f8faf9')
ac={'Green':'#2a9d68','Red':'#c8464b','Blue':'#3974b9','Purple':'#8c59ac','Yellow':'#d09b20','White':'#616a70','Airport':'#e27432'}
for f in A['features']:
    g=f['geometry'];p=f['properties']
    if g['type']=='LineString':
        pts=g['coordinates'];ax[0].plot([z[0] for z in pts],[z[1] for z in pts],color=ac.get(p['line'],gray),lw=2.1,alpha=.82,label=p['line'])
    elif p.get('kind')!='rfi_named':
        x,y=g['coordinates'];ax[0].scatter([x],[y],s=24,c=red,zorder=6)
for f in B['features']:
    g=f['geometry'];p=f['properties']
    if g['type']=='LineString':
        pts=g['coordinates'];kind=p.get('concept','')
        color=red if kind.endswith('access-edit') else (teal if kind.endswith('infill-research') else '#748892')
        ax[1].plot([z[0] for z in pts],[z[1] for z in pts],color=color,lw=1.6 if color==red else (1.4 if color==teal else .85),alpha=.88 if color in (red,teal) else .48,zorder=3 if color in (red,teal) else 1)
    elif p.get('concept','').endswith('access-edit'):
        x,y=g['coordinates'];ax[1].scatter([x],[y],s=24,c=red,zorder=6)
    elif p.get('concept','').endswith('infill-research'):
        x,y=g['coordinates'];ax[1].scatter([x],[y],s=6,c=teal,zorder=5)
for a in ax:
    a.set_xlim(44.18,44.68);a.set_ylim(33.03,33.53);a.set_aspect(1.19)
    a.set_facecolor('#edf3f1');a.grid(color='white',lw=.8)
    a.tick_params(labelsize=7,colors='#5e7079')
    a.set_xlabel('Longitude east',fontsize=8,color=navy)
ax[0].set_title('A  |  148.2 km authority corridor concept',loc='left',fontsize=11,fontweight='bold',color=navy)
ax[1].set_title('B  |  605.65 km schematic programme',loc='left',fontsize=11,fontweight='bold',color=navy)
ax[0].legend(loc='upper left',fontsize=6.6,ncol=2,frameon=True,facecolor='white')
for a in ax:
    a.text(44.229,33.258,'AIRPORT',fontsize=7,color=red,fontweight='bold')
    a.text(44.46,33.404,'SADR',fontsize=7,color=red,fontweight='bold')
    a.text(44.387,33.273,'JADRIYA',fontsize=7,color=red,fontweight='bold')
fig.text(.5,.015,'Schematic place-centroid / generated research geometry only. No route, crossing, station, land or airport entry is surveyed.',ha='center',fontsize=8,color='#6b777b')
fig.tight_layout(rect=[0,.055,1,.90])
fig.savefig(map_path,bbox_inches='tight',facecolor=fig.get_facecolor())
plt.close(fig)

font='/usr/share/fonts/truetype/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',font));pdfmetrics.registerFont(TTFont('DejaVu-Bold',bold))
ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='TitleX',fontName='DejaVu-Bold',fontSize=23,leading=29,textColor=colors.HexColor(navy),spaceAfter=10))
ss.add(ParagraphStyle(name='H1X',fontName='DejaVu-Bold',fontSize=15,leading=20,textColor=colors.HexColor(navy),spaceBefore=8,spaceAfter=9))
ss.add(ParagraphStyle(name='H2X',fontName='DejaVu-Bold',fontSize=10.5,leading=14,textColor=colors.HexColor(teal),spaceBefore=8,spaceAfter=5))
ss.add(ParagraphStyle(name='BodyX',fontName='DejaVu',fontSize=8.7,leading=13.5,textColor=colors.HexColor('#263d48'),spaceAfter=6))
ss.add(ParagraphStyle(name='SmallX',fontName='DejaVu',fontSize=7.4,leading=11.2,textColor=colors.HexColor('#344a52'),spaceAfter=5))
ss.add(ParagraphStyle(name='THX',fontName='DejaVu-Bold',fontSize=7.4,leading=11.2,textColor=colors.white,spaceAfter=5))
ss.add(ParagraphStyle(name='NoteX',fontName='DejaVu',fontSize=7,leading=10.5,textColor=colors.HexColor('#5b6c73'),spaceAfter=5))
ss.add(ParagraphStyle(name='MetricX',fontName='DejaVu-Bold',fontSize=17,leading=21,textColor=colors.HexColor(navy),alignment=TA_CENTER))
ss.add(ParagraphStyle(name='MetricLabX',fontName='DejaVu',fontSize=8,leading=12,textColor=colors.HexColor('#5b6c73'),alignment=TA_CENTER))
P=lambda t,style='BodyX': Paragraph(t,ss[style])
W=180*mm
story=[]
def heading(t): story.append(P(t,'H1X'))
def sub(t): story.append(P(t,'H2X'))
def para(t,style='BodyX'): story.append(P(t,style))
def table(rows,widths=None,header=True):
    x=Table([[P(str(v),'THX' if header and ri==0 else 'SmallX') for v in row] for ri,row in enumerate(rows)],colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    x.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(navy)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#eef4f2')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,-1),(-1,-1),.3,colors.HexColor('#b8c8cc'))]))
    story.append(x);story.append(Spacer(1,5*mm))

story.append(Spacer(1,7*mm))
story.append(P('BAGHDAD URBAN RAIL','TitleX'))
para('Two concept proposal for Amanat Baghdad, commercial lenders and UKEF discussion', 'H1X')
para('OpenSourceRail v0.7 | 17 November 2026 | Engineering concept and funding discussion', 'BodyX')
story.append(Spacer(1,6*mm))
metric=Table([[P('148.2 km','MetricX'),P('500-800 km','MetricX'),P('2035','MetricX')],[P('Authority-aligned first programme','MetricLabX'),P('Metropolitan network vision','MetricLabX'),P('Planning horizon, subject to delivery proof','MetricLabX')]],colWidths=[60*mm]*3)
metric.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eaf2f0')),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#bbd1d0')),('INNERGRID',(0,0),(-1,-1),.3,colors.white),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]));story.append(metric)
story.append(Spacer(1,9*mm))
heading('Decision requested')
para('Mandate Concept A as the first detailed feasibility and procurement comparison, while safeguarding Concept B corridors in the same study with Amanat Baghdad and the National Investment Commission (NIC). Confirm concession rights, airport property and the public sponsor; use measured demand, walking access, ground/utility survey and complete service cost. This is a study and corridor-protection request, not construction debt or a physical design selection.')
heading('Two separate concepts')
table([['Concept A - first programme','Concept B - metropolitan programme'],['Seven RFI-named corridors, 148.2 km and 64 notional stations. Add a passenger-terminal entrance, three Sadr City access tests and two Jadriya access tests.','Existing 14-line, 513.34 km research map plus 3.11 km airport chord and six schematic infill corridors of 89.21 km, giving a 605.65 km minimum programme in the 500-800 km strategy.'],['US$18.0bn single planning envelope, including 20% contingency.','US$69.6bn single planning envelope, including 20% contingency.']],[90*mm,90*mm])
para('Both amounts are programme hypotheses, not tendered capital prices. Candidate identities, maps, rates and open engineering conditions are in the accompanying repository data.', 'NoteX')
story.append(PageBreak())
heading('Route and access proposal')
story.append(Image(str(map_path),width=178*mm,height=75*mm))
para('A maps only 37 RFI-named place points plus five access anchors; 15 named waypoints have no reliable coordinate. Its 64 station assets in the budget are an RFI allowance, not 64 mapped/approved sites. B combines generated research alignments, six focus edits and six infill corridors. No path is surveyed.', 'NoteX')
table([['A corridor','Nominal km','Principal named places / v0.7 intervention'],['Green','19','Allawi - Mansour - Bayaa - Saydiyya - Doura'],['Red','27.7','Allawi - Kadhimiya - Adhamiya - Mustansiriya - Maisaloun'],['Blue','22','Shaab - Waziriya - Tayaran - Andalus - Zuafaraniya; Sadr transfer'],['Purple','14.5','Tayaran - Hamza - 55/83 Squares - Ur - Shaab; three Sadr access tests'],['Yellow','30','Baladiyat - Maisaloun - Jadriya Square - Bayaa - Adan; two Jadriya anchors'],['White','23','Kadhimiya - Shulah - Gazaliya - Amiriya - Bayaa'],['Airport','12','Baghdad Airport passenger terminal - Amiriya - Aamil - Bayaa - Qadisiya']],[28*mm,24*mm,128*mm])
para('A needs owner confirmation of the Arabic/English Jadriya Square name and the exact terminal entrance. Airport security, land, accessible walks, Tigris crossings, grade and utilities remain route gates.', 'SmallX')
story.append(PageBreak())
heading('Concept B | network scale and 2035 test')
para('The research source declares 513.34 km, while its earlier cost dossier uses 494.43 km. Reconcile the length measures before using a unit cost. Line 5 needs at least a 3.11 km straight-line airport extension. Six proposed infill corridors add 89.21 km of schematic chord, bringing the minimum programme screen to 605.65 km. Actual route lengths may be longer after land, street and crossing surveys.')
table([['Area','Required candidate action','Evidence / next test'],['Airport terminal','Extend line 5 to a landside passenger-terminal entrance.','Agree property/security and accessible access; survey alignment.'],['Sadr City','Test two stops on/near line 10 and one on line 9; connect through services.','WorldPop radial screen adds about 445,500 modelled residents to the two OSM district areas if all three anchors work.'],['Jadriya','Test two anchors near lines 1 and 2, with a feasible connection or protected feeder.','WorldPop radial screen adds about 49,800 modelled residents in the 2 km study circle; crossing/utility access open.'],['Six infill routes','Add 89.21 km of Sadr, east-bank, Karkh, southwest and northern corridors with 61 stop anchors.','Radial screen rises to 4.59m of 8.60m; filtered OSM walking sensitivity only 2.13m; access unverified.'],['Five short lines','Retain lines 10-14 for now.','They total 34.36 km and 46 assumed trainsets but reach unique catchments; no savings booked.']],[32*mm,76*mm,72*mm])
sub('The 12 million-plus population case')
para('Use 12 million-plus metropolitan residents as a stress scenario for 2035, not a forecast. Agree the geographic boundary and reconcile Iraqi census, local WorldPop and UN population definitions. The present WorldPop 1 km radial screen reaches about 2.58m of 8.60m modelled residents (30%). It is not a walking-access, ridership or OD measure.')
sub('2035 delivery condition')
para('A 606 km completion in roughly nine years would require an average opening rate near 67 km/year after immediate start; actual construction would begin later and need a higher rate. Multiple simultaneous civil fronts, land and utility release, depots, grid, fleet, approvals and sustainable operating subsidy must be proven. Stage openings so every stage has a usable network.')
story.append(PageBreak())
heading('Capacity and physical railway')
para('The v0.6 development reference is a simple station-powered, passive-wheel six-car train with 276 normal places and no planned standing. It has no selected installed propulsion. Safety, accessibility, braking, rescue and passenger protection are compulsory for either concept.')
table([['Necessary-bound check','Result'],['RFI claim: 3.25 million passengers per day','The current six-car reference on seven lines at four-minute intervals, both directions and 18 hours offers at most 1,043,280 places/day, even with every train full all day.'],['Required design selection','Measured peak OD by direction and hour; choose formation, platform, dwell, headway, powered length, traction/braking duty, fleet, power and civil loads together.'],['Equal-service alternatives','Compare station-launch wheel support, powered-wheel research and any other admissible concept at the same service, recovery and whole-life scope. No research alternative silently changes the reference.']],[58*mm,122*mm])
sub('Buildability and local manufacture')
para('Size one complete car and repairable door module, then one standard viaduct span, pier, foundation and erection sequence against Baghdad soil, flood, river and utility conditions. Count installed joints, wiring, cooling, protection, access and spares. Use a 1.5-2 km demonstrator to measure propulsion, stopping, heat, recovery, vibration, maintenance and erection logistics before serial procurement.')
para('Publish a make/buy and local-value ledger by cost, fabrication hours, tooling, inspection, supplier capability and repairability. Public tables call these counted vehicle components and equipment/fitout allowance awaiting detailed placement. The latter remains a positive mass/cost provision.')
story.append(PageBreak())
heading('One capital figure per concept')
table([['Programme','Planning capital envelope','Basis'],['A: 148.2 km','US$18.0bn','14 scope quantities and rates plus 20% contingency; RFI civil mix, 64 stations and four depots.'],['B: 605.65 km schematic','US$69.6bn','Separate 14 scope model plus 20% contingency; 226 line-stop assets, 12 depots and civil classes provisionally priced.']],[58*mm,44*mm,78*mm])
para('The estimates include tunnels/portals, elevated and at-grade works, stations/access/evacuation, track, controls, station power/braking, grid interfaces, trainsets, depots, land/utilities/disruption, assurance, testing and rescue/tooling. The 2018 World Bank Bogotá and 2024 São Paulo appraisals are external comparators, not Iraq quotations. A public 2024 Baghdad programme report cites US$17.5bn; it does not validate our US$18.0bn point.')
sub('Financial case is a separate gate')
para('No defensible annual operating cost, 30-year life-cycle cost, fare revenue or debt-service coverage exists for either revised service yet. The earlier 14-line operating estimate belongs to another candidate. Do not use it to imply farebox bankability. Financing interest, UKEF premium, taxes, foreign exchange and full land settlement also need explicit treatment in the lender model.')
sub('UKEF and commercial banks')
para('UKEF Buyer Credit may support up to 85% of an eligible UK export contract, with at least 15% buyer direct payment and an acceptable bank. It does not finance 85% of either whole metro. Iraq country cover and indicative market appetite are not approval. Name the UK exporter, eligible content, Iraqi/local packages, sponsor equity, public support, EPC/O&amp;M contracts, term lenders, ESHR/land plan and debt-service model before an application.')
story.append(PageBreak())
heading('Mandate and next decisions')
table([['Gate','Evidence required to pass'],['1. Authority and rights','Amanat/NIC resolve concession status, sponsor, procurement route, land and airport operating agreement.'],['2. Surveyed route and demand','OD and accessible walking data, exact waypoints, river/soil/utility/flood surveys, stations, depots and population boundary.'],['3. Equal-service engineering','Full vehicle/propulsion/civil alternatives, demonstrator measurements, emergency cases, quantity and local manufacturing/repair ledger.'],['4. Bankable cost and finance','Supplier bids, staged annual cash flow, fare and public-payment obligation, UK-eligible packages, independent adviser, ESHR/land and lender terms.'],['5. Stage approval and opening','Only approve construction stages with an independently verified railway and funded accessible operation.']],[36*mm,144*mm])
sub('Selected sources')
for title,url in [
 ('NIC 2024 Baghdad Metro RFI - investpromo.gov.iq','https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf'),
 ('Iraqi Ministry of Planning - mop.gov.iq/archives/40342','https://mop.gov.iq/archives/40342'),
 ('UN urbanisation data - population.un.org/wup','https://population.un.org/wup/'),
 ('UKEF Buyer Credit - gov.uk/guidance/buyer-credit-facility','https://www.gov.uk/guidance/buyer-credit-facility'),
 ('UKEF Iraq cover - gov.uk/guidance/country-cover-policy-and-indicators','https://www.gov.uk/guidance/country-cover-policy-and-indicators'),
 ('World Bank São Paulo appraisal - documents1.worldbank.org','https://documents1.worldbank.org/curated/en/099022725110032757/pdf/BOSIB-0b1c6377-dcd4-470d-88ca-2342fc535d3e.pdf')]:
    para(f'<link href="{url}" color="#007f86">{title}</link>','SmallX')
para('Scope and evidence: OpenSourceRail docs/proposals/baghdad-v07/README.md, COST-AND-FINANCE.md, two candidate GeoJSON files and separate cost-ledger-a/b.json. Schematic geometry and modelled population are not surveyed design or measured ridership. Neither programme is physically accepted or approved by Amanat Baghdad, NIC, a lender or UKEF.', 'NoteX')

def decorate(c,doc):
    c.saveState(); w,h=doc.pagesize
    c.setStrokeColor(colors.HexColor(teal)); c.setLineWidth(.8);c.line(15*mm,h-15*mm,w-15*mm,h-15*mm)
    c.setFont('DejaVu',7);c.setFillColor(colors.HexColor('#617782'))
    c.drawString(15*mm,13*mm,'OpenSourceRail | Baghdad v0.7 engineering and finance concept | 17 Nov 2026')
    c.drawRightString(w-15*mm,13*mm,str(doc.page));c.restoreState()

out=root/'output/pdf/Baghdad-Metro-v0.7-Proposal.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(210*mm,297*mm),rightMargin=15*mm,leftMargin=15*mm,topMargin=20*mm,bottomMargin=20*mm,title='Baghdad urban rail v0.7 two-concept proposal',author='OpenSourceRail')
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
print(out, out.stat().st_size)
