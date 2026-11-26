"""Render the illustrated operator briefing from the checked-in drawings and screen captures."""
import json
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import cairosvg
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
URL = "https://github.com/modernecotech/OpenSourceRail/blob/main/"
NETWORK = ROOT / "cities/Baghdad/straight-through-network.json"
OUTPUT = HERE / "OpenSourceRail-Operator-Brief.pdf"
sources = {Path(__file__).resolve(), NETWORK}
baghdad = json.loads(NETWORK.read_text())
civil, service = baghdad["civil"], baghdad["cost"]["service"]
quantities, crews, programme = civil["quantities"], civil["workforce"], civil["programme"]
base_cost = baghdad["cost"]["cost_cases"]["base"]
W, H = 960, 600
TEAL, INK, GRAY, PAPER, LINE, GOLD = "#00695F", "#143739", "#425B5E", "#FAF9F3", "#CAD6CF", "#A45522"
for family, file in [('Regular', 'DejaVuSans.ttf'), ('Bold', 'DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(family, file))
c = Canvas(str(OUTPUT), pagesize=(W, H), invariant=True,
           pageCompression=1)
c.setTitle("OpenSourceRail | Railway design and delivery for operators")
c.setAuthor("OpenSourceRail")
page = 0


def rect(x, top, w, h, colour):
    c.setFillColor(colors.HexColor(colour))
    c.rect(x, H-top-h, w, h, fill=1, stroke=0)


def line(x, y, text, size=13, font='Regular', colour=INK):
    c.setFillColor(colors.HexColor(colour))
    c.setFont(font, size)
    c.drawString(x, H-y, text)


def para(x, top, width, text, size=14, colour=GRAY):
    style = ParagraphStyle('body', fontName='Regular', fontSize=size, leading=size*1.43,
                           textColor=colors.HexColor(colour))
    block = Paragraph(text, style)
    _, height = block.wrap(width, H)
    assert top + height < H-36, text
    block.drawOn(c, x, H-top-height)
    return top + height


def start(section, title, subtitle):
    global page
    if page:
        c.showPage()
    page += 1
    rect(0, 0, W, H, PAPER)
    line(35, 30, 'OpenSourceRail', 14, 'Bold', TEAL)
    line(185, 30, section.upper(), 10, 'Bold', GRAY)
    rect(35, 42, 890, 1, LINE)
    line(35, 92, title, 32, 'Bold')
    para(36, 106, 883, subtitle, 13)
    rect(35, 560, 890, 1, LINE)
    line(35, 580, 'Railway design and delivery     /     Operator review     /     26 November 2026', 9, colour=GRAY)
    line(893, 580, f'{page:02d}', 10, 'Bold', TEAL)


def picture(path, x, top, w, h):
    image = (HERE / path).resolve()
    sources.add(image)
    if image.suffix == '.svg':
        image = BytesIO(cairosvg.svg2png(url=str(image), scale=1.5))
    reader = ImageReader(image)
    iw, ih = reader.getSize()
    scale = min(w/iw, h/ih)
    width, height = iw*scale, ih*scale
    c.drawImage(reader, x+(w-width)/2, H-top-h+(h-height)/2, width, height, mask='auto')


def link(label, path, x=35, y=545):
    line(x, y, label+'  ↗', 10, 'Bold', TEAL)
    target = path if path.startswith('https:') else URL + (HERE/path).resolve().relative_to(ROOT).as_posix()
    c.linkURL(target, (x, H-y-4, x+pdfmetrics.stringWidth(label+'  ↗','Bold',10), H-y+11),
              relative=0, thickness=0)


def point(x, top, width, title, text):
    line(x, top+14, title, 15, 'Bold')
    return para(x, top+22, width, text, 12.2)


def table(x, top, widths, labels, rows, row_h=38):
    for i, row in enumerate([labels, *rows]):
        y = top+i*row_h
        rect(x, y, sum(widths), row_h-1, TEAL if i==0 else ('#EBF0EB' if i%2 else '#F3F4EE'))
        left = x
        for j,(item,width) in enumerate(zip(row,widths,strict=True)):
            font = 'Bold' if (i==0 or j==0) else 'Regular'
            size = 11.4
            assert pdfmetrics.stringWidth(item,font,size) < width-12, item
            line(left+8, y+row_h/2+4, item,size,font,'#FFFFFF' if i==0 else INK)
            left += width


def two_column_figure(path, points):
    picture(path, 34, 155, 571, 363)
    y = 161
    for title, text in points:
        y = point(633, y, 282, title, text) + 18


start('Railway proposals', 'A railway an operator can inspect',
      'Review the train, the station and the organisation that will build, fund and run them.')
picture('../assets/assembly-animations/viaduct-placement.jpg', 33, 145, 584, 350)
point(643, 158, 267, 'Core reference', 'A 30 km elevated example joins vehicle, track, stations, manufacturing and operating cost on one design.')
point(643, 273, 267, 'Baghdad', 'A connected elevated network with Airport service, orbital routes and direct Tigris crossings. Civil and operating accounts use the mapped route.')
point(643, 388, 267, 'Decision for the owner', 'Choose a service to investigate, an interface to prototype and a local package to quote.')
link('Open the operator guide','README.md')
link('Download the offline kit and open START.html','https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/operator-review/OpenSourceRail-Operator-Kit.zip',315)
para(35,497,881,'Run the interactive screens in the offline kit or the local Workbench under Operator review. Other links open design records on GitHub.',11.0)
start('Service offer', 'Baghdad service and cost allowances',
      'The six-minute costing offer gives the fleet and grid budget. Local demand and verified train workings determine the operating plan.')
table(35,160,[490,400],['Planning quantity','Baghdad metropolitan'],[
    ['Distinct guideway and station sites', f"{quantities['unique_guideway_km']:,.2f} km / {quantities['station_sites']:,}"],
    ['Normal places per train','700'],
    ['Direction interval / offered places per hour', f"{service['directional_headway_s']/60:g} min / {service['nominal_places_per_hour_direction']:,.0f}"],
    ['Fleet including reserves', f"{service['fleet_trainsets']:,} sets"],
    ['Power collection','Protected conductor'],
    ['Base installed planning allowance', f"US${base_cost['installed_planning_usd_m']/1000:.2f} billion"],
    ['Base annual operation', f"US${base_cost['annual_operations_total_usd_m']/1000:.2f} billion"]],39)
para(37,492,862,'Confirm route geometry, accessibility, safe separation and peak power. Obtain contractor prices for river structures and special interfaces.',12.4)
link('Service, works and lifecycle costs','../../cities/Baghdad/STRAIGHT-THROUGH-DELIVERY.md')
start('Baghdad / location', 'One connected route and station plan',
      'The network joins two rings with cross-Tigris corridors and an Airport service.')
picture('../../cities/Baghdad/maps/baghdad-straight-through-network.png', 35, 138, 510, 401)
point(564,152,344,'Passenger access','Check housing-to-centre journeys, the Airport entrance and shared platforms. Survey street approaches, step-free transfer routes and egress.')
point(564,279,344,'Delivery packages','Set the working zones and access routes for support construction, terminal yards, station work, special crossings and the finished deck.')
point(564,403,344,'Network changes','Test rerouted or withdrawn lines against the same walk threshold, origin and destination samples, and scheduled train-km.')
link('Metropolitan alignment and passenger evidence','../../cities/Baghdad/STRAIGHT-THROUGH-NETWORK.md')
link('Alternative networks','../../cities/Baghdad/THREE-RING-STUDY.md',610)
start('Design / rolling stock','Inspect the bogie and carbody',
      'The design viewer links each selected component to the drawing or schedule behind it. Inspect a train at the station, then switch to a single assembly.')
picture('twins/core-bogie.png',35,150,430,224)
picture('twins/baghdad-steel-frame.png',488,150,437,224)
point(36,382,418,'Core powered bogie','The six-car train uses 24 driven axles and 12 independent brake modules. Price and instrument the reaction link, mounting pins and rail fastening. A simulated two-second brake delay extends the downhill stop from 333 m to 387 m.')
point(490,382,419,'Baghdad steel stock','Follow the body truss and two bogie frames through stock cuts, welding and access for repair. The 5.196 t subtotal covers these members only. Wheels, suspension, drives, joints and fitout require further installed mass evidence.')
link('Core brake and clearance rigs','../../engineering/interface_studies/REFERENCE-RIGS.md')
link('Baghdad mechanical drawings','../../cities/Baghdad/engineering/mechanical/vehicle/README.md',489)
start('Design / station and control', 'From the viaduct to the platform edge',
      'The Baghdad trial places the station deck on its own supports beside the track. Movement between these structures affects boarding.')
two_column_figure('../../cities/Baghdad/station-interface.svg',[
    ('Inspect the civil interface','The trial island is 125 m by 8 m. Recurring guideway uses 20 m U-girders on shared piers. Survey bearing seats, footing pressures and the platform edge under load.'),
    ('Exercise the boarding sequence','With the train at rest and both brake holds proved, the replay releases 24 platform-side doors. The other side stays locked. Loss of a holding proof trips protection.'),
    ('Before dispatch','The replay closes and proves all 48 doors, then checks drive take-up. The brake supplier and operator still need to demonstrate the handover and measure rollback under load on a gradient.')])
link('Station and viaduct sections','../../cities/Baghdad/engineering/mechanical/civil/LIVE-STOCK.md')
link('Wiring and boarding replay','../../cities/Baghdad/engineering/controls/README.md',633)
start('Operate / control room','An equipment alarm during service',
      'This screen replays the project gateway with fixture inputs. Staff can inspect observations, timestamps and alarms without sending commands to train equipment.')
two_column_figure('screens/section-alarm.png',[
    ('Control desk','Select the section trip and the stale observation. Establish which indications are current before briefing the duty controller.'),
    ('Field response','The operator’s rules allocate authority to isolate, prove dead, enter the work area and restore power. A screen acknowledgement records an operator action.'),
    ('Repair record','Match the equipment label, approved drawing, serial and software revision on the maintenance order. Record checks and handback before closing the defect.')])
link('Screen gallery and provenance','screens/README.md')
link('Gateway replay and setup guide','screens/README.md',633)
start('Operate / workshop', 'Passenger planning and repair history',
      'Use the passenger journey screen to inspect a proposed service and the workshop record to trace what happened to a part.')
picture('screens/passenger-journey.png',34,152,433,206)
picture('screens/erp-serial-history.png',487,149,438,225)
point(36,377,415,'A train through its working day','Use the journey display to inspect waiting, running, walking and interchange time. This screen demonstrates the controls on a mapped city. Baghdad has its own matched service runs.')
point(490,377,417,'A native ERPNext serial record','The existing historical pilot shows a repair and inspection trail. The new railway still needs its own asset register, installed serials, warranty records, staff permissions and signed maintenance tasks.')
link('Open the gallery and workshop screens','screens/README.md')
link('ERPNext and Frappe HR setup','../../deployment/erpnext/README.md',489)
start('Finance / public budget','Price the works and annual operation',
      'Use equal service and construction scope. The project cash profile depends on approved phasing, access, renewals and actual rates.')
table(35,160,[360,175,175,180],['US$ billion','Low','Base','High'],[
    [label, *(f"{baghdad['cost']['cost_cases'][case][key]/1000:.2f}" for case in ('low','base','high'))]
    for key,label in [('installed_planning_usd_m','Installed planning allowance'),
                      ('annual_operations_total_usd_m','Annual operation'),
                      ('whole_life_present_usd_m','30-year present cost')]],62)
point(36,429,416,'Funding needs','Build annual draws from the purchasable scope and dated opening phases. Model fare receipts, borrowing fees, currency and public-service obligations with dated local inputs.')
point(491,429,416,'Scope still open','Obtain prices for river crossings, special structures and site-specific access before relying on a total construction cash requirement.')
link('Matched base scope and lifecycle quantities','../../cities/Baghdad/STRAIGHT-THROUGH-DELIVERY.md')
start('Build / vehicle works','Lay out the assembly and repair shops',
      'Price a repeatable factory module against the modelled fleet orders. Frame fixtures, inspection points, bogie access and a separate repair road need space before the first car arrives.')
two_column_figure('delivery/vehicle-works.svg',[
    ('Core order','Five proposed lines complete 306 cars in the allotted production window. The first-car assembly allowance is 720 direct hours.'),
    ('Baghdad fleet',f'The metro costing offer covers {service["cars"]:,} cars. Set production rate, phased orders and test output from the agreed service opening sequence.'),
    ('Bidder return','Quote buildings, line equipment, test road, wheelset handling, QA, staffing and the right to repair. Witness a first car, a repeat car and a bogie exchange.')])
link('Dimensioned vehicle works plan','delivery/vehicle-works.svg')
link('Production and shift assumptions','delivery/README.md',633)
start('Build / viaduct','A terminal yard feeds each advancing front',
      'The open-line study uses two terminal yards, rail flatbeds and launching gantries. Ground and structural interfaces define which sites can use the method.')
two_column_figure('../../cities/Baghdad/engineering/mechanical/civil/rail-fed/terminal-yard.png',[
    ('Stock and storage','Recurring 20 m U-girders on shared piers. Each yard provides 16 moulds and 24 released-stock positions within a 216 × 164 m trial footprint.'),
    ('Yard and front availability',f"The network allowance uses {programme['active_launcher_pairs']} paired launcher crews, {programme['active_road_day_teams']} road teams and {programme['concurrent_yard_sites']} concurrent yards."),
    ('Release to site','Inspect each casting batch and bearing seat. Prove trailer, pick and temporary deck loads. Schedule starter and closure lifts and bridge works separately.')])
link('Current fabrication and erection basis','../../cities/Baghdad/engineering/mechanical/civil/LIVE-STOCK.md')
start('People / shift coverage','Staff production and operating duties',
      'The delivery record counts civil casting, haul and erection by route and role. Validate staff availability, qualification and pay against the programme.')
table(35,155,[550,335],['Construction resource','Paid hours'],[
    ['Casting, haul and erection', f"{crews['paid_deck_and_casting_hours']:,.0f}"],
    ['Rail-fed erection', f"{crews['paid_rail_fed_erection_hours']:,.0f}"],
    ['Road erection and haul', f"{crews['paid_road_erection_and_haul_hours']:,.0f}"],
    ['Casting yard', f"{crews['paid_casting_hours']:,.0f}"]],46)
point(36,421,420,'Roster the service','Test relief, maintenance, passenger assistance and emergency duties in the shift model. Reconcile any payroll counted in other cost accounts.')
point(490,421,420,'Verify competence','Witness lifting, inspection, welding, isolation and passenger protection. Record role, equipment, restrictions and renewal dates.')
link('Factory, shift and competence plan','delivery/README.md')
start('Delivery / buying terms','Use the design to improve competing offers',
      'Baghdad can buy from another supplier and still use the open railway to negotiate prices, domestic production, long-term repair rights and financing.')
picture('finance/supplier-returns.png',35,145,552,372)
point(608,148,311,'Issue the same package','Download the scope and drawings for one station, body, bogie, civil kilometre, crossing or cabinet. Ask each bidder for a delivered cash price and a separate financing offer.')
point(608,284,311,'Compare two station offers','In the illustration, B costs $250,000 less and documents $587,500 more Iraqi value. Both returns use the same first article. The remaining untraced origin stays visible.')
point(608,418,311,'Contract for local repair','Confirm the drawings, tooling, training, spares and warranty. Witness an independent repeat build or repair before releasing the agreed payment.')
link('Buyer comparison and supplier enquiries','../../cities/Baghdad/BUYER-COMPARISON.md')
start('Delivery / next decisions','The first twelve weeks',
      'Start when the sponsor appoints an operator and gives the team access to routes, records and suppliers. Each decision has a named owner and a tangible return.')
steps=[('Weeks 1–2','Sponsor + operator','Agree the service brief, decision owners and scope of the first opening.'),
       ('Weeks 2–6','Route + operations','Locate stations, survey access and junctions, test dwell, turnback and a failed train.'),
       ('Weeks 3–8','Engineering leads','Quote a bogie, body bay, station edge, beam seat and door/brake bench. Agree test limits.'),
       ('Weeks 5–10','Local works + procurement','Time a first article. Obtain prices, local value, repair rights and financing terms.'),
       ('Weeks 8–12','Owner + finance','Choose a surveyed opening and a funded trial. Name the party responsible for integration.')]
for i,(when,who,what) in enumerate(steps):
    y=157+i*65
    rect(35,y,890,63,'#ECF1EB' if i%2==0 else '#F4F4EF')
    line(49,y+25,when,13,'Bold',TEAL);line(184,y+25,who,13,'Bold')
    para(415,y+11,495,what,12.4)
para(36,498,880,'Passenger opening depends on as-built records, emergency and accessible-travel exercises, trained rosters and independent acceptance of measured performance.',11.8)
link('Full delivery plan and handover evidence','WORKPLAN.md')
c.save()
receipt = {
    "artifact": OUTPUT.relative_to(ROOT).as_posix(),
    "sha256": sha256(OUTPUT.read_bytes()).hexdigest(),
    "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
                      for path in sorted(sources)},
}
(HERE / "operator-brief.receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print(f'{page} pages')
