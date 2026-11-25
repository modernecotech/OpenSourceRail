"""Keep the pathway selection and service accounting tied to the declared inputs."""

import unittest

from cities.Baghdad import residential_planning, residential_systems


class ResidentialPlanningTests(unittest.TestCase):
    def test_overall_access_cannot_mask_a_failing_central_destination(self):
        def case(km):
            return {"network": {"candidate_id": str(km), "topology": {"route_km": km}},
                    "actions": [], "housing_access": {}, "removed_route_km": 900 - km}

        def trips(access):
            return {"journeys": {"served_share_pct": 80., "elapsed_p90_min": 50.,
                                 "reachable_with_at_most_share_of_all_pct": {"1": 55.}},
                    "destinations": {"market": {"served_share_pct": access}}}

        options = {"grid_reference": case(900), "terminal-trims": case(870), "extended-feeder-trims": case(850)}
        results = {"grid_reference": trips(80), "terminal-trims": trips(79), "extended-feeder-trims": trips(76)}
        tolerances = dict(served_loss_pp=.5, one_change_loss_pp=.75, destination_loss_pp=1.5,
                          p90_increase_min=2, walking_loss_pp=.5)
        selected, audit = residential_planning.choose_layout(options, results, dict.fromkeys(options, 75.), tolerances)
        self.assertEqual(selected, "terminal-trims")
        self.assertEqual(audit["extended-feeder-trims"]["exceeded"], ["destination_loss_pp"])

    def test_running_km_count_both_directions_and_include_train_reserve(self):
        network = {"lines": {"A": {"one_way_km": 6., "station_ids": ["first", "last"],
                                    "station_chainage_km": {"first": 0., "last": 6.}, "loop": False}}}
        policy = dict(headway_s=360, operating_hours_per_day=18, turnaround_min=3,
                      spare_fraction=.15, nominal_sets_per_depot=80, nominal_depots_per_control_centre=3)
        vehicle = dict(cars_per_train=6, normal_places_per_train=700, service_days_per_year=365)
        result = residential_systems.service_quantities(network, policy, vehicle)
        self.assertEqual(result["running_train_km_day"], 2160)
        self.assertEqual(result["running_train_km_year"], 788400)
        self.assertGreater(result["fleet_trainsets"], result["active_trainsets"])
        self.assertEqual(result["cars"], 6 * result["fleet_trainsets"])
