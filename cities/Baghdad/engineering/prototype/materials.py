"""Compare body materials at equal service using a stated net installed mass sensitivity."""

from cities.Baghdad import airport_finance, airport_opening
from engineering.outline.baghdad_system import _id


def compare(article, service, inputs):
    case = article["opening"]
    bundle = case["bundle"]
    mass = case["power"]["vehicle"]["mass_t"]
    # A costing question for the supplier, independent of any particular panel lay-up.
    saving_per_car_t = 0.5
    study = dict(
        purpose="Unranked material and repair cost sensitivity",
        parent=article["candidate_id"],
        material_family="Aluminium structure with GFRP panels and metallic attachment inserts",
        assumed_net_installed_saving_t_per_car=saving_per_car_t,
        requirements=[
            "Same 700-place six-car service, openings, floor and bogie interfaces",
            "Document tooling, joints, fire behaviour, damage inspection, repair and spares",
        ],
    )
    option = airport_opening.calculate(
        inputs=inputs,
        service=service,
        size_feeder=True,
        vehicle_revision=_id(study),
        loaded_mass_t=mass - bundle["formation_cars"] * saving_per_car_t,
    )
    if (
        option["timetable_id"] != case["timetable_id"]
        or option["bundle"]["formation_cars"] != bundle["formation_cars"]
        or option["candidate_id"] == case["candidate_id"]
    ):
        raise ValueError("Material enquiry requires an independent option on the same service")
    cfg = inputs[0]
    finance = airport_finance.evaluate(option, cfg, cfg["service_plan"]["departures_per_hour_direction"])

    def row(opening, budget):
        return dict(
            candidate_id=opening["candidate_id"],
            mass_t=opening["power"]["vehicle"]["mass_t"],
            supply_sites=opening["bundle"]["grid_sites"],
            traction_mw=opening["power"]["traction"]["dc_input_rating_request_mw"],
            grid_gwh_per_year=opening["power"]["energy"]["annual_grid_gwh"],
            priced_30y_usd_m=budget["market_scenarios"]["central"]["priced_whole_life_30y_usd_m"],
        )

    steel = row(case, article["finance"])
    hybrid = row(option, finance)
    return dict(
        study=study,
        steel=steel,
        illustrative_hybrid=hybrid,
        service_id=service["evaluation_id"],
        electricity_only_30y_difference_usd_m=(
            case["iraq_operations"]["cases"]["central"]["electricity_usd_m"]
            - option["iraq_operations"]["cases"]["central"]["electricity_usd_m"]
        )
        * sum((1 + cfg["discount_rate_real"]) ** -year for year in range(1, 31)),
        additional_whole_life_cost_at_break_even_usd_m=steel["priced_30y_usd_m"] - hybrid["priced_30y_usd_m"],
        hybrid_installed_mass_verified_t=None,
        hybrid_supplier_price_usd_m=None,
        hybrid_selected=False,
    )
