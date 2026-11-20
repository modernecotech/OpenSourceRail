"""Render the illustrated operator briefing from the checked-in drawings and screen captures."""
import json
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
W, H = 960, 600
TEAL, INK, GRAY, PAPER, LINE, GOLD = "#00695F", "#143739", "#425B5E", "#FAF9F3", "#CAD6CF", "#A45522"
for family, file in [('Regular', 'DejaVuSans.ttf'), ('Bold', 'DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(family, file))
c = Canvas(str(HERE / "OpenSourceRail-Operator-Brief.pdf"), pagesize=(W, H), invariant=True,
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
    line(35, 580, 'Railway design and delivery     /     Operator review     /     20 November 2026', 9, colour=GRAY)
    line(893, 580, f'{page:02d}', 10, 'Bold', TEAL)


def picture(path, x, top, w, h):
    image = HERE / path
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
picture('twins/baghdad-station.png', 33, 145, 584, 350)
point(643, 158, 267, 'Core reference', 'A 30 km elevated example joins vehicle, track, stations, manufacturing and operating cost on one design.')
point(643, 273, 267, 'Baghdad', 'Seven historical corridors and an independent citywide proposal can each be priced by local and international teams.')
point(643, 388, 267, 'Decision for the owner', 'Choose a service to investigate, an interface to prototype and a local package to quote.')
link('Open the operator guide','README.md')
link('Download the offline kit and open START.html','https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/operator-review/OpenSourceRail-Operator-Kit.zip',315)
para(35,497,881,'Run the interactive screens in the offline kit or the local Workbench under Operator review. Other links open design records on GitHub.',11.0)
start('Service offer', 'Three railway choices',
      'Peak capacity is the number of places offered per hour in one direction. Paid journeys require a separate demand and fares study.')
table(35,160,[298,168,208,216],['Planning quantity','Core reference','Baghdad / seven corridors','Baghdad / citywide'],[
    ['Elevated route / budgeted stations','30 km / 12','148.2 km / 64','605.652 km / 280'],
    ['Normal places per train','276','700','700'],
    ['Peak interval / places per hour¹','120 s / 8,280','150 s / 16,800','150 s / 16,800'],
    ['Fleet including reserves','51 sets','242 sets','934 sets'],
    ['Power collection','1.5 kV DC overhead','Protected conductor','Protected conductor'],
    ['Installed capital, 2026 US$','1.025 billion','7.866 billion','31.018 billion'],
    ['Annual operations and maintenance','30.5 million','197.0 million','780.5 million']],35)
para(37,457,862,'¹ Per modelled service. Baghdad’s citywide plan assigns passenger paths to 555.553 km and reserves a further 50.099 km. The two Baghdad options are independent investment decisions.',12.4)
para(37,503,862,'The earlier v0.6 station-powered, passive-wheel train remains a separate development reference with its own tests.',11.5)
link('Core service and cost','../reference-v07/cost/README.md')
link('Baghdad service and cost','../../cities/Baghdad/COST-AND-DELIVERY.md',298)
start('Baghdad / location', 'Baghdad’s original seven corridors',
      'The Iraqi National Investment Commission published this map in February 2024. Its seven route lengths total 148.2 km.')
picture('../../cities/Baghdad/maps/Baghdad-148km.png',35,141,477,390)
point(535,152,375,'Read the original routes','Trace the pale pink airport approach from the west and the blue corridor towards Al Zafraniya in the southeast. The investment brief allows 64 stations. Entrances and platform sites require surveys.')
point(535,279,375,'What to survey first','Confirm the airport terminal entrance, accessible walks to Sadr City and Jadriya, disputed place names and river crossings. Agree a survey datum and chainage with the authority.')
point(535,397,375,'Procurement context','October Arabic interviews describe unsuccessful earlier offers and a new study. Late 2026 to early 2027 is a preparation window. The invitation date awaits an official notice.')
link('Original NIC map and table, page 4','https://mofa.gov.iq/paris/wp-content/uploads/sites/55/2024/02/Baghdad-PDF.pdf#page=4')
link('Arabic ministry workshop record','https://mop.gov.iq/archives/40342',541)
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
two_column_figure('twins/baghdad-boarding.png',[
    ('Inspect the civil interface','The trial island is 125 m by 8 m. The single-track beam is 10 m long. The design team must survey bearing seats, footing pressures and the platform edge under load.'),
    ('Exercise the boarding sequence','With the train at rest and both brake holds proved, the replay releases 24 platform-side doors. The other side stays locked. Loss of a holding proof trips protection.'),
    ('Before dispatch','The replay closes and proves all 48 doors, then checks drive take-up. The brake supplier and operator still need to demonstrate the handover and measure rollback under load on a gradient.')])
link('Station and viaduct sections','../../cities/Baghdad/engineering/mechanical/civil/README.md')
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
picture('screens/baghdad-service.png',34,152,433,206)
picture('screens/erp-serial-history.png',487,149,438,225)
point(36,377,415,'A train through its working day','Use the Baghdad diagram to follow a set through stops and a terminal turn. Inspect the platform and block conflicts at peak headway. The citywide mainline option diagrams all 14 routes by deferring five access sections.')
point(490,377,417,'A native ERPNext serial record','The existing historical pilot shows a repair and inspection trail. The new railway still needs its own asset register, installed serials, warranty records, staff permissions and signed maintenance tasks.')
link('Open the gallery and workshop screens','screens/README.md')
link('ERPNext and Frappe HR setup','../../deployment/erpnext/README.md',489)
start('Finance / public budget','How much cash does the operator need?',
      'The seven-corridor case below assumes 50% borrowing at 4% real, repaid over 20 years. Figures use constant 2026 US dollars.')
two_column_figure('finance/baghdad-funding.png',[
    ('Construction','The city borrows about $3.93bn. Construction interest of $322.5m is paid from budget. The largest annual buyer draw during works is $1.282bn.'),
    ('First full service year','Debt payments plus operating cost need $486.4m before receipts. With 100m paid journeys at $1 net each, the remaining requirement is $386.4m. Both fare inputs are illustrations.'),
    ('A different term sheet','At 7% real over 12 years, the same network needs $692.1m in its first full service year. Check fees, FX exposure and guarantees alongside the cash price.')])
link('How to use the funding calculator','README.md')
link('Annual debt and renewal schedules','../../cities/Baghdad/COST-AND-DELIVERY.md',634)
start('Build / vehicle works','Lay out the assembly and repair shops',
      'Price a repeatable factory module against the modelled fleet orders. Frame fixtures, inspection points, bogie access and a separate repair road need space before the first car arrives.')
two_column_figure('delivery/vehicle-works.svg',[
    ('Core order','Five proposed lines complete 306 cars in the allotted production window. The first-car assembly allowance is 720 direct hours.'),
    ('Baghdad seven corridors','Twelve lines at the trial rate have capacity for 1,464 cars against an order of 1,452. Losing one five-day production cycle across all twelve uses the margin.'),
    ('Bidder return','Quote buildings, line equipment, test road, wheelset handling, QA, staffing and the right to repair. Witness a first car, a repeat car and a bogie exchange.')])
link('Dimensioned vehicle works plan','delivery/vehicle-works.svg')
link('Production and shift assumptions','delivery/README.md',633)
start('Build / viaduct','A casting yard needs room to store beams',
      'Coordinate casting, release inspection, haulage and erection. Giving each activity a daily rate can obscure the space required between them.')
two_column_figure('delivery/precast-yard.svg',[
    ('Core reference','Two yards supply 6,000 beams. Each needs at least 440 pre-erection stock positions under the proposed dates. The illustrated 180-place yard needs at least 260 additional places per yard.'),
    ('Baghdad seven corridors','Six yards supply 29,640 beams. Balanced peak month-end stock needs 164 places per yard. Daily arrivals, blocked roads and rejected beams can raise that figure.'),
    ('Release to site','Identify each casting batch and bearing seat, approve lift and traffic plans, and confirm pier readiness before dispatch. Price overflow land and extra handling.')])
link('Dimensioned precast yard plan','delivery/precast-yard.svg')
link('Yard and workforce quantities','delivery/quantities.json',633)
start('People / training','Who will build and run the railway?',
      'Illustrative establishments cover the duties listed in the workforce plan. Agree wages, shifts, relief, contracted services and training costs with the employing operator.')
staff = json.loads((HERE/'delivery/quantities.json').read_text())['studies']
networks = ('core', 'first', 'metropolitan')
rosters = [staff[k]['workforce_scenarios']['goa4']['posts_fte'] for k in networks]
rows = [[label,*(f'{s[key]:,}' for s in rosters)] for label,key in [
    ('Scheduled staff onboard / GoA4','scheduled onboard staff'), ('Station duty and passenger assistance','station duty and passenger assistance'),
    ('Control centre','OCC control, traction, incidents and information'),('Rolling-stock technicians','depot rolling-stock technicians')]]
rows += [['GoA4 / all listed operating duties, FTE',*(f'{staff[k]["workforce_scenarios"]["goa4"]["total_fte"]:,}' for k in ('core','first','metropolitan'))],
         ['Peak day-shift build posts¹',*(f'{staff[k]["production_day_posts"]:,}' for k in ('core','first','metropolitan'))]]
table(35,154,[320,145,212,213],['Workforce measure','Core','Baghdad / seven corridors','Baghdad / citywide'],rows,31)
para(36,380,884,'¹ Positions across the listed vehicle, yard and erection activities. Build jobs overlap by package. Operating FTE use 1,720 rosterable hours per person-year, including relief in the establishment.',11.5)
point(36,424,420,'Recruit and teach','Start with local instructors, pilot crews and independent assessors. Budget classroom, simulator and mentored work before shadow rosters.')
point(490,424,420,'Authorise by demonstrated task','Witness assisted boarding, isolation and restoration, train recovery, welding and lifting. Record restrictions and renewal dates in the HR skills register.')
link('Roles, wages to quote and competence assessments','delivery/README.md')
start('People / shift coverage','Test a staffing and training budget',
      'Choose unattended service, supervised commissioning or onboard assistance. Price the duties and reconcile existing payroll before taking a scenario to the funding calculator.')
two_column_figure('delivery/workforce.png',[
    ('Staff the working day','The seven-corridor GoA4 case has 1,526 FTE. At an illustrative $24,000 loaded pay each, payroll is $36.624m. Subtract only documented or explicitly assumed payroll already in the operating allowances.'),
    ('Prepare local instructors','At 80 classroom and 80 supervised hours each, plan for 128 classes of up to 12 and 122,080 supervised learner-hours. Quote instructors, assessors and roster relief separately.'),
    ('Record qualification','The employing operator records signed role, equipment, restrictions and expiry against each employee. Link training and assessment to the duties allowed on the shift.')])
link('Workforce planner, inputs and hiring plan','delivery/README.md')
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
print(f'{page} pages')
