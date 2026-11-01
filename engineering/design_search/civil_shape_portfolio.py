"""Source-bound 20 m civil geometry competition and provisional delivery costs."""
import argparse
import gzip
from html import escape
import json
from math import ceil, isfinite
from pathlib import Path
import shutil
import tempfile
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import civil_shape_geometry as geometry
from . import model_cost, multifidelity, quality_diversity, search_backends

PRODUCER = "engineering/design_search/civil_shape_portfolio.py"
CAMPAIGN = "campaigns/civil-shape-competition.toml"
OUTPUT = "docs/design-engine/civil-shape-portfolio"
OBJECTIVES = ("nominal_stock_mass_kg", "scoped_installed_base_iqd", "factory_hours_base")
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
    manufacturing_release=False, operating_release=False, selected_reference_changed=False)


def specification(root=ROOT):
    spec = tomllib.loads((Path(root)/CAMPAIGN).read_text())
    if (spec.get("schema") != "osr-civil-shape-competition/1"
            or spec.get("purpose") != "next-experiment"
            or spec.get("reference_changes_allowed") is not False
            or tuple(spec.get("families", [])) != geometry.FAMILIES
            or tuple(spec.get("profiles", [])) != geometry.PROFILES
            or spec.get("maximum_candidates") != 18
            or spec.get("span_m") != 20 or spec.get("deck_width_m") != 2):
        raise ValueError("Explicit bounded, non-promoting 20 m civil competition required")
    a = model_cost.assumptions(root)
    if a["design_life_years"] != 30:
        raise ValueError("This competition's explicit renewal/disposal scenarios require a 30-year life")
    for key, expected in (("production", a["production_shifts_per_day"]),
            ("construction", a["civil_shifts_per_day"])):
        if spec[key]["shifts_per_day"] != expected or spec[key]["hours_per_shift"] != 8:
            raise ValueError("Civil competition must use the canonical two-shift production/construction basis")
    if spec["production"]["productive_utilisation"] != a["productive_utilisation"]:
        raise ValueError("Productive utilisation differs from the canonical cost scenario")
    for group in ("rates", "complexity"):
        for key, values in spec[group].items():
            if (not isinstance(values, list) or len(values) != 3
                    or any(type(v) not in (int,float) or not isfinite(v) or v <= 0 for v in values)):
                raise ValueError("Explicit positive low/base/high assumptions required: " + key)
            if key != "form_reuses" and values != sorted(values):
                raise ValueError("Ordered low/base/high assumptions required: " + key)
    return spec


def sources(root=ROOT):
    paths = [PRODUCER, CAMPAIGN, "engineering/design_search/civil_shape_geometry.py",
        "engineering/design_search/multifidelity.py", "engineering/design_search/quality_diversity.py",
        "engineering/design_search/search_backends.py", "engineering/design_search/requirements-search.txt",
        "engineering/station_rail/common.py"]
    return {**model_cost.sources(root), **{p:digest(Path(root)/p) for p in paths}}


def estimate(candidate, quantities, spec, assumptions):
    """Non-overlapping Class C cost lines; no structural capacity is assumed."""
    if candidate["candidate_id"] != quantities["candidate_id"]:
        raise ValueError("Civil geometry and quantity candidate identities differ")
    if quantities != geometry.quantities(candidate):
        raise ValueError("Civil quantity payload does not reproduce from its physical geometry")
    if assumptions["design_life_years"] != 30:
        raise ValueError("The competition renewal/disposal scenarios require a 30-year life")
    q = quantities; a = assumptions["assumptions"]; r = spec["rates"]
    b = assumptions["benchmark_rates_iqd"]; complexity = spec["complexity"][candidate["family"]]
    concrete = q["by_material"].get("research_concrete", {}).get("volume_m3", 0.)
    steel = q["by_material"].get("structural_steel", {}).get("mass_kg", 0.)
    contact = q["concrete_contact_surface_m2"]; steel_surface = q["steel_surface_m2"]
    rail_kg = 2 * 60.21 * candidate["span_m"]
    fastener_sets = 2 * (ceil(candidate["span_m"]/.6) + 1)
    costs = []; hours = []; schedules = []; lines = {}

    def line(key, i, value):
        if not isfinite(value) or value < 0:
            raise ValueError("Finite nonnegative civil estimate line required: " + key)
        lines.setdefault(key, {})[model_cost.CASES[i]] = round(value, 2)

    for i in range(3):
        sensitivity = a["material_rate_sensitivity"][i]
        rebar = concrete*a["concrete_rebar_kg_per_m3"][i]
        # Reserves remain explicitly unsized. Zero applies only to known absent
        # material in a generated section, never to unresolved installed items.
        prestress = concrete*r["prestress_reserve_kg_per_m3"][i]
        concrete_cost = concrete*((a["concrete_cement_t_per_m3"][i]*b["cement_iqd_per_t"]
            + a["concrete_aggregate_m3_per_m3"][i]*b["aggregate_iqd_per_m3"]
            + a["concrete_sand_m3_per_m3"][i]*b["sand_iqd_per_m3"])
            * (1+a["concrete_waste_fraction"][i]) + a["concrete_admixture_iqd_per_m3"][i])
        stock = steel*a["steel_iqd_per_kg"][i] + rebar*b["rebar_iqd_per_kg"]*sensitivity
        prestress_cost = prestress*a["prestress_iqd_per_kg"][i]
        factory_h = (concrete*r["concrete_labour_h_per_m3"][i]
            + complexity[i]*(contact*r["form_labour_h_per_m2"][i] + steel*r["steel_fabrication_h_per_kg"][i])
            + rebar*r["reinforcement_labour_h_per_kg"][i] + prestress*r["prestress_handling_h_per_kg"][i])
        wage = model_cost._shift_adjusted_wage(b["wage_skilled_iqd_per_h"]*a["wage_burden_multipliers"][i],
            2, a["second_shift_wage_premium"][i], a["third_shift_wage_premium"][i])
        labour = factory_h*wage
        machine = factory_h*r["machine_hours_per_factory_labour_hour"][i]*a["machine_rate_iqd_per_h"][i]
        qa = (contact+steel_surface)*r["inspection_iqd_per_m2"][i]
        tooling = contact*complexity[i]*r["form_tooling_iqd_per_m2"][i]/r["form_reuses"][i]
        coating = steel_surface*r["surface_coating_iqd_per_m2"][i]
        direct = concrete_cost+stock+prestress_cost+labour+machine+qa+tooling+coating
        overhead = direct*a["factory_overhead_fraction"][i]
        factory = direct+overhead
        rail_cost = rail_kg*a["rail_iqd_per_kg"][i] + fastener_sets*a["fastener_iqd_per_set"][i]
        counted_mass = q["total_nominal_stock_mass_kg"]+rebar+prestress+rail_kg+fastener_sets*8.
        transport = counted_mass/1000*assumptions["outbound_route_km"]*a["transport_iqd_per_tonne_km"][i]
        erection = a["erection_crane_iqd_per_shift"][i]/a["spans_per_crane_shift"][i]
        site = r["site_hours_per_span"][i]*wage
        support = r["site_support_foundation_bearings_allowance_iqd"][i]
        services = r["site_services_allowance_iqd"][i]
        delivered = factory+rail_cost+transport
        installed = delivered+erection+site+support+services
        discount = assumptions["real_discount_rate"]; years = assumptions["design_life_years"]
        annuity = sum((1+discount)**(-year) for year in range(1,years+1))
        life = (installed + installed*r["annual_maintenance_fraction_of_installed"][i]*annuity
            + installed*r["renewal_fraction_at_year_15"][i]/(1+discount)**15
            + installed*r["disposal_fraction_at_year_30"][i]/(1+discount)**30)
        for key, value in dict(concrete_recipe=concrete_cost, steel_and_reinforcement=stock,
                unsized_prestress_reserve=prestress_cost, factory_labour=labour, machine=machine,
                inspection=qa, tooling_amortisation=tooling, coating=coating, factory_overhead=overhead,
                rails_and_fastenings=rail_cost, transport=transport, erection=erection,
                site_labour=site, supports_foundations_and_bearings_reserve=support,
                site_services_reserve=services).items():
            line(key,i,value)
        costs.append(dict(case=model_cost.CASES[i], factory_gate_iqd=round(factory,2),
            delivered_iqd=round(delivered,2), scoped_installed_iqd=round(installed,2),
            scoped_lifecycle_npv_iqd=round(life,2), preliminary_reinforcement_kg=rebar,
            unsized_prestress_reserve_kg=prestress, accounted_delivery_mass_kg=counted_mass,
            factory_person_hours=factory_h))
        hours.append(factory_h)
        schedules.append(dict(case=model_cost.CASES[i],
            single_worker_equivalent_factory_days=factory_h/(2*8*spec["production"]["productive_utilisation"]),
            single_worker_equivalent_site_days=r["site_hours_per_span"][i]/(2*8)))
    return dict(schema="osr-civil-shape-class-c-estimate/1", candidate_id=candidate["candidate_id"],
        estimate_class="C", currency="IQD", assumption_id=assumptions["assumption_id"],
        competition_assumption_id=identity(spec), cases=costs, line_items_iqd=lines,
        factory_person_hours=dict(zip(model_cost.CASES,hours)), schedule=schedules,
        production_shifts_per_day=2, civil_shifts_per_day=2,
        quantity_basis="Exact nominal section-cell stock; surface contact is a formwork proxy, not a developed mould drawing. Rail/fixing accounts are shared explicit interface hypotheses.",
        scope="One research span including factory, amortised tooling, QA, rail accounts, delivery and erection. Supports/foundations/bearings, site services and prestress have explicit bounded reserves; this is not a complete installed BOM or city budget.",
        unresolved=["reinforcement/tendon and anchorage design", "shear connectors, bearings and installed connections",
            "site-specific foundations and erection access", "mould release, rebar access and concrete placement",
            "maintenance quantities and validated service lives", "actual parallel crews, machine precedence and curing schedule"],
        process_route=["prepare mould/steel stock", "form or fabricate candidate geometry", "place provisional reinforcement/prestress",
            "cast/cure or join steel/concrete", "inspect and protect surfaces", "deliver and lift", "install rail and inspect interfaces"],
        complete_installed_mass_kg=None, complete_installed_cost_iqd=None, **FLAGS)


def _calculate(root=ROOT):
    root=Path(root); spec=specification(root); epoch=sources(root); a=model_cost.assumptions(root)
    candidates=[]; rows=[]
    for family in spec["families"]:
        for profile in spec["profiles"]:
            candidate=geometry.generate(family,profile); q=geometry.quantities(candidate)
            if candidate["span_m"]!=spec["span_m"] or candidate["deck_width_m"]!=spec["deck_width_m"]:
                raise ValueError("Civil span interfaces differ from the competition")
            cost=estimate(candidate,q,spec,a)
            row=dict(candidate_id=candidate["candidate_id"],descriptor=dict(family=family),profile=profile,
                quantities=q,cost_estimate=cost,metrics=dict(nominal_stock_mass_kg=q["total_nominal_stock_mass_kg"],
                    scoped_installed_base_iqd=cost["cases"][1]["scoped_installed_iqd"],
                    factory_hours_base=cost["factory_person_hours"]["base"]),
                execution="completed",fidelity=0,numerical_validity="exact-cell-quantity-calculation",
                engineering_screen="unknown",evidence_maturity="provisional-geometry-and-cost",
                structural_analysis="not-run", complete_installed_mass_kg=None, **FLAGS)
            row["evaluation_id"]=identity(row); candidates.append(candidate); rows.append(row)
    if len({c["candidate_id"] for c in candidates})!=spec["maximum_candidates"]:
        raise ValueError("Distinct physical candidate coverage differs")
    archive=quality_diversity.archive(rows,OBJECTIVES,("family",))
    budget=spec["screening"]
    frontier=multifidelity.plan(rows,archive["retained_candidate_ids"],
        maximum_tasks=budget["maximum_stage_1_tasks"],runtime_s=budget["maximum_runtime_s_per_task"],
        memory_bytes=budget["maximum_memory_bytes_per_task"],source_sha256=epoch)
    value=dict(schema="osr-civil-shape-portfolio/1",source_sha256=epoch,specification=spec,
        candidate_count=len(rows),family_count=len(spec["families"]),evaluations=rows,
        archive=archive,frontier=frontier,integrated_selection=None,selected_candidate_id=None,
        geometry_scope="Exact polygon-prism cells; variable depth and load-following ribs are stepped physical hypotheses, not arbitrary organic discovery, validated BREP or topology optimisation.",
        **FLAGS)
    if epoch!=sources(root): raise ValueError("Civil portfolio sources changed during evaluation")
    value["portfolio_id"]=identity(value)
    return value,gzip.compress(encoded(candidates),mtime=0)


def _readme(value):
    lines=["# Civil shape design portfolio", "",
        f"The 20 m span competition generates {value['candidate_count']} physical candidates across {value['family_count']} families and three profiles. Every candidate has explicit material geometry, calculated stock quantities, a provisional production route and low/base/high Class C delivery and lifecycle scenarios. All share a 2 m deck envelope. No structural loads have been evaluated or railway alternative selected.", "",
        "| Family / profile | Nominal stock (t) | Factory hours (base) | Scoped installed estimate (IQD million, base) |", "|---|---:|---:|---:|"]
    for r in value["evaluations"]:
        m=r["metrics"]; lines.append(f"| {r['descriptor']['family']} / {r['profile']} | {m['nominal_stock_mass_kg']/1000:.2f} | {m['factory_hours_base']:.1f} | {m['scoped_installed_base_iqd']/1e6:.2f} |")
    lines += ["", "![Nominal midspan section geometry](sections.svg)", "", "Geometry and search", "",
        "The families use box sections, ribbed U sections, varying-depth boxes, sloped folded plates, steel/concrete assemblies and load-following stepped ribs. Their actual polygons and cells determine material volume, stock mass, centroids, geometric second moments and exposed surfaces. Stepped depth/rib geometry is not a smooth organic surface or an optimised stress trajectory. Nominal stock omits unresolved reinforcement, prestress, connectors, bearings and installed equipment; complete installed mass remains unknown.", "",
        "The descriptor-cell Pareto archive retains each family's partial-quantity alternatives. A separate cross-family front does not discard family diversity or establish feasibility. One cheap next-evaluator request per family is retained before expensive refinement. The frontier records resource budgets, source identities and required domain checks, and dispatches no native solvers.", "",
        "Cost and production basis", "",
        "Concrete uses the canonical dated Iraqi material/wage benchmarks. New forming, fabrication, tooling reuse, inspection, site-support, maintenance and renewal factors are explicit Class C assumptions in the versioned competition. Factory labour scales with concrete volume, contact surface, steel fabrication mass, reinforcement and unsized prestress reserves. Surface area is a tooling/contact proxy rather than a developed mould design. A single overhead uplift applies to the factory subtotal; transport, erection and site allowances are separate. Factory, delivered, scoped installed and lifecycle estimates have separate totals.", "",
        "Production and civil work each use two 8-hour shifts. The worker-equivalent durations are labour-capacity diagnostics; curing, parallel teams, machine precedence, crane radius/capacity, concrete access, reinforcement details and site conditions require further evaluation. Prestress and supports remain explicitly priced reserves without credited structural capacity. Low/base/high values are scenarios, not statistical confidence intervals. There is no complete installed BOM or validated service life.", "",
        "Reproduce", "", "```bash", "./osr design civil-portfolio plan", "./osr design civil-portfolio build", "./osr design civil-portfolio verify", "```", "",
        "Optional independent archive audit: install `engineering/design_search/requirements-search.txt`, then run `./osr design civil-portfolio audit-optimizers`. It uses pymoo nondominated sorting and separate pyribs single-objective categorical archives on the evaluated pool; it does not claim evolutionary generation or replace the multiobjective archive.", "",
        "[Physical definitions](candidates.json.gz) · [Evaluations, cost lines and frontier](result.json) · [Source receipt](manifest.json)", "",
        "All engineering, physical, manufacturing and operation approvals remain pending. The selected v0.6 reference is unchanged.", ""]
    return "\n".join(lines)


def _gallery(candidates):
    """A common-scale section view from the actual physical polygons."""
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1210" viewBox="0 0 1200 1210" role="img" aria-labelledby="title desc">',
        '<title id="title">20 m civil competition: nominal midspan sections</title>',
        '<desc id="desc">Eighteen generated section geometries, at a common scale. Grey is concrete; blue is steel. Stock only, no structural acceptance.</desc>',
        '<rect width="1200" height="1210" fill="#ffffff"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="20">Nominal midspan sections — common scale, stock geometry only</text>',
        '<text x="20" y="50" font-family="sans-serif" font-size="14">Grey: concrete · Blue: steel · Variable-depth/rib families use stepped prisms along the span</text>']
    for i,candidate in enumerate(candidates):
        x=20+(i%3)*400; y=75+(i//3)*188
        parts.append(f'<g id="candidate-{candidate["candidate_id"]}"><rect x="{x}" y="{y}" width="380" height="175" rx="8" fill="#f7f9fb" stroke="#ccd4dc"/>')
        parts.append(f'<text x="{x+12}" y="{y+22}" font-family="sans-serif" font-size="14">{escape(candidate["family"])} / {escape(candidate["profile"])}</text>')
        cell=next(cell for cell in candidate['cells'] if cell['x_start_m']<=10<cell['x_end_m'])
        for section in cell['sections']:
            points=' '.join(f'{x+190+75*a:.4f},{y+40-75*b:.4f}' for a,b in section['polygon_yz_m'])
            color='#758493' if section['material']=='research_concrete' else '#087da3'
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="#273846" stroke-width="0.7"/>')
        parts.append('</g>')
    return ('\n'.join(parts)+"\n</svg>\n").encode()


def _check(out):
    m=json.loads((out/"manifest.json").read_bytes())
    if m.get("manifest_id")!=identity({k:v for k,v in m.items() if k!="manifest_id"}):
        raise ValueError("Civil portfolio manifest identity differs")
    actual={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!="manifest.json"}
    if any(p.is_symlink() or p.is_dir() for p in out.iterdir()) or actual!=m.get("files_sha256"):
        raise ValueError("Civil portfolio payload differs")
    return m


def build(root=ROOT,output=None):
    root=Path(root); out=root/OUTPUT if output is None else Path(output); value,compressed=_calculate(root)
    out.parent.mkdir(parents=True,exist_ok=True); stage=Path(tempfile.mkdtemp(prefix=".civil-portfolio-",dir=out.parent))
    try:
        (stage/"result.json").write_bytes(encoded(value)); (stage/"candidates.json.gz").write_bytes(compressed)
        (stage/"README.md").write_text(_readme(value))
        (stage/"sections.svg").write_bytes(_gallery(json.loads(gzip.decompress(compressed))))
        m=dict(schema="osr-civil-shape-publication/1",source_sha256=value["source_sha256"],
            files_sha256={p.name:digest(p) for p in stage.iterdir()},portfolio_id=value["portfolio_id"],**FLAGS)
        m["manifest_id"]=identity(m); (stage/"manifest.json").write_bytes(encoded(m)); verify(root,stage)
        if out.exists():
            old=_check(out)
            if old==m:return verify(root,out)
            backup=root/"build/civil-shape-portfolio/replaced-publications"/old["manifest_id"]
            backup.parent.mkdir(parents=True,exist_ok=True)
            if backup.exists():raise ValueError("Prior civil portfolio already retained; inspect before replacement")
            shutil.move(out,backup)
        stage.rename(out)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root); out=root/OUTPUT if output is None else Path(output); m=_check(out)
    if m.get("schema")!="osr-civil-shape-publication/1" or m.get("source_sha256")!=sources(root):
        raise ValueError("Civil portfolio source epoch differs")
    expected,compressed=_calculate(root)
    if (json.loads((out/"result.json").read_bytes())!=expected or (out/"candidates.json.gz").read_bytes()!=compressed
            or (out/"README.md").read_text()!=_readme(expected) or m.get("portfolio_id")!=expected["portfolio_id"]
            or (out/"sections.svg").read_bytes()!=_gallery(json.loads(gzip.decompress(compressed)))
            or any(m.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError("Civil portfolio does not reproduce")
    return dict(verified=True,manifest_id=m["manifest_id"],portfolio_id=expected["portfolio_id"],
        candidate_count=expected["candidate_count"],family_count=expected["family_count"],
        next_evaluator_requests=len(expected["frontier"]["requests"]),**FLAGS)


def audit_optimizers(root=ROOT):
    """Write an immutable optional-library run separately from canonical outputs."""
    root=Path(root); verify(root); value=json.loads((root/OUTPUT/"result.json").read_bytes())
    audit=search_backends.audit(value["evaluations"],OBJECTIVES,("family",),seed=0)
    record=dict(schema="osr-civil-shape-optimizer-run/1",portfolio_id=value["portfolio_id"],
        source_sha256=sources(root),audit=audit,**FLAGS)
    record["run_id"]=identity(record)
    out=root/"build/civil-shape-portfolio/optimizer-audits"/(record["run_id"]+".json")
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and out.read_bytes()!=encoded(record):raise ValueError("Immutable optimizer run differs")
    if not out.exists():out.write_bytes(encoded(record))
    return dict(run_id=record["run_id"],path=out.relative_to(root).as_posix(),
        candidate_count=audit["candidate_count"],library_versions=audit["library_versions"],
        descriptor_cells=audit["reference_cell_count"],pymoo_matches=audit["pymoo"]["matches_reference_archive"],
        pyribs_coverage=audit["pyribs"]["all_observed_descriptor_cells_covered"],**FLAGS)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("action",choices=("plan","build","verify","audit-optimizers"))
    action=p.parse_args().action
    print(json.dumps({"plan":specification,"build":build,"verify":verify,"audit-optimizers":audit_optimizers}[action](),indent=2))
