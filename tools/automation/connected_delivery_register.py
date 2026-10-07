"""Trace every outstanding review area to evidence; computation is not acceptance."""
import hashlib
from pathlib import Path

REQUIREMENTS=(
 ('R01','Ring/dispatch correctness','software-regression','bidirectional dispatch and distance regressions','operations engineer'),
 ('R02','Energy/timetable recovery','software-study','conflict-capable timetable, berth/depot access and measured multi-day recovery','operations authority'),
 ('R03','Launcher reassignment','software-study','surveyed additional ring access, foundation releases and lifting/relocation plans','construction manager'),
 ('R04','Span/pier layout','software-study','surveyed pier positions, station transitions and designed special spans','civil designer'),
 ('R05','Supplier production and logistics','external-evidence','product qualification, capacity slots, geographic delivery routes and contracts','procurement manager'),
 ('R06','Commercial quotations','external-evidence','dated preliminary/firm/contracted scope-matched quotations','commercial manager'),
 ('R07','Structural and lifting design','computed-screen','prestress/reinforcement, stages, bearings, restraints, strengths, charts and independent checks','structural authority'),
 ('R08','Station passenger/site acceptance','computed-screen','surveyed OD/demand, flow criteria, evacuation/rescue, lift-out throughput and accessible street routes','station designer'),
 ('R09','BMS commissioning','software-integration','pack-specific accepted electrical/thermal calibration and physical commissioning','battery commissioning authority'),
 ('R10','ERP construction execution','software-integration','live-company, crew, inspection, maintenance, permit, shift and transfer evidence','HR and project authority'),
 ('R11','Cost/finance adoption','partial-cash-sensitivity','complete scope-priced budget, verified embedded credit, finance terms and accepted openings/revenue','finance authority'),
 ('R12','Clean regeneration','software-regression','supported-runtime clean-checkout and content provenance checks','repository maintainer'),
 ('R13','Rolling-stock release','external-evidence','closed masses/drawings/configurations, structural/thermal qualification and first articles','rolling-stock authority'),
 ('R14','Control electronics release','external-evidence','exact hardware, harnesses, enclosures, power/thermal budgets, benches and fault injection','electronics authority'),
 ('R15','Redundant control','external-evidence','remaining protection pairs and independently proven physical separation','control systems authority'),
 ('R16','Operating acceptance','external-evidence','repeated missions, depots, full-day headway/energy and recovery acceptance','operating authority'),
 ('R17','ERP/FUXA production deployment','external-evidence','legal companies, production authentication, physical assets and real adapters','deployment authority'),
 ('R18','Workforce funding and competence','external-evidence','funded recruitment, named rosters, competence assessment and measured workloads','HR authority'),
 ('R19','Other city adoption','external-evidence','city-specific connected model, source inputs and operating validation','city sponsor'),
 ('R20','Governance and assurance','external-evidence','appointed accountable parties, mandates and accepted evidence gates','programme sponsor'),
)


def build_register(root,records):
    known={row[0] for row in REQUIREMENTS};seen=set();observed=[]
    for record in records:
        if record['id'] in seen or record['requirement_id'] not in known:raise ValueError('unknown/duplicate acceptance record')
        seen.add(record['id']);relative=Path(record['path'])
        path=(root/relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root.resolve()) or not path.is_file():raise ValueError('acceptance record must resolve inside the repository')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('acceptance evidence receipt drift')
        if not record.get('scope_revision') or not record.get('authority') or not record.get('independent_reviewer'):
            raise ValueError('acceptance record needs scope, authority and independent reviewer')
        observed.append({**record,'authority_verified_by_generator':False})
    rows=[dict(id=identity,area=area,implementation_status=status,required_evidence=evidence,responsible_role=role,
        appointed_person=None,acceptance_status='evidence-entered-authority-verification-required' if any(r['requirement_id']==identity for r in observed) else 'open-external-evidence',
        acceptance_records=[r['id'] for r in observed if r['requirement_id']==identity],physical_or_commercial_release=False)
        for identity,area,status,evidence,role in REQUIREMENTS]
    return dict(schema=1,requirements=rows,records=observed,all_review_areas_traced=True,
        software_implementation_is_not_evidence_acceptance=True,engineering_release=False,
        note='Implemented studies/contracts are distinct from completed physical tests, supplier commitments, appointments and authority acceptance.')
