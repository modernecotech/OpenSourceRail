//! Fixed, declared route-to-native coordinates. No geometry or hash admission.
use super::*;

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FrameGeometry {
    pub project_candidate_id: String,
    pub body_candidate_id: String,
    pub body_evaluation_id: String,
    pub alignment_candidate_id: String,
    pub alignment_evaluation_id: String,
    pub station_candidate_id: String,
    pub station_evaluation_id: String,
    pub station_track_candidate_id: String,
    pub station_track_evaluation_id: String,
    pub operating_envelope_evaluation_id: String,
    pub feed_coverage_evaluation_id: String,
    pub drive_duty_evaluation_id: String,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EntryFrame {
    pub schema: String,
    pub context_id: String,
    pub train_reference: String,
    pub origin_route_m: f64,
    pub physical_route_distance_m: f64,
    pub physical_target_route_m: f64,
    pub physical_authority_route_m: f64,
    pub allowed_initial_route_interval_m: [f64; 2],
    pub station_track_reference_domain_m: [f64; 2],
    pub operating_envelope_reference_domain_m: [f64; 2],
    pub continuous_feed_reference_domain_m: [f64; 2],
    pub geometry: FrameGeometry,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FrameCaseBinding {
    pub frame_context_id: String,
    pub source_case_id: String,
    pub source_policy_id: String,
    pub compiled_case_id: String,
    pub compiled_policy_id: String,
    pub source_brake_start_route_m: f64,
    pub source_emergency_route_m: Option<f64>,
}
#[derive(Debug, Clone, Serialize)]
pub struct FrameApplication {
    pub frame_context_id: String,
    pub geometry: FrameGeometry,
    pub physical_route_distance_m: f64,
    pub origin_route_m: f64,
    pub direction: f64,
    pub physical_station_offset_m: f64,
    pub physical_initial_route_position_m: f64,
    pub native_initial_position_m: f64,
    pub source_case_id: String,
    pub source_policy_id: String,
    pub exported_case_id: String,
    pub exported_policy_id: String,
    pub execution_label: String,
    pub accepted_mechanical_steps: usize,
    pub case_fields_mutated: bool,
    pub canonical_hash_verified_by_native: bool,
    pub physical_geometry_verified: bool,
}
fn interval(x: &[f64; 2]) -> bool {
    x.iter().all(|v| v.is_finite()) && x[0] <= x[1]
}
impl EntryFrame {
    pub(in crate::fleet) fn native(&self, physical: f64) -> f64 {
        physical - self.origin_route_m
    }
    #[cfg(test)]
    fn physical(&self, native: f64) -> f64 {
        native + self.origin_route_m
    }
    pub(super) fn validate(
        &self,
        route: &DirectedRoute,
        network: &GeometryBinding,
        d: &Departure,
        binding: &FrameCaseBinding,
    ) -> Result<(), String> {
        let g = &self.geometry;
        let p = d
            .journey
            .control
            .as_ref()
            .ok_or("Framed feedback policy required")?;
        if self.schema != "osr-fixed-route-origin-entry/1"
            || self.train_reference != "formation-geometric-centre"
            || !hash(&self.context_id)
            || !self.origin_route_m.is_finite()
            || self.origin_route_m > 0.
            || self.physical_route_distance_m != route.distance_m
            || self.physical_target_route_m != route.distance_m
            || self.physical_authority_route_m != route.distance_m
            || !interval(&self.allowed_initial_route_interval_m)
            || self.allowed_initial_route_interval_m[0] < -d.journey.berth_tolerance_m
            || self.allowed_initial_route_interval_m[1] > d.journey.berth_tolerance_m
            || [
                &self.station_track_reference_domain_m,
                &self.operating_envelope_reference_domain_m,
                &self.continuous_feed_reference_domain_m,
            ]
            .iter()
            .any(|x| !interval(x) || x[0] > self.origin_route_m || x[1] < route.distance_m)
            || g.project_candidate_id != network.project_candidate_id
            || g.alignment_candidate_id != network.alignment_candidate_id
            || g.alignment_evaluation_id != network.alignment_evaluation_id
            || [
                &g.project_candidate_id,
                &g.body_candidate_id,
                &g.body_evaluation_id,
                &g.alignment_candidate_id,
                &g.alignment_evaluation_id,
                &g.station_candidate_id,
                &g.station_evaluation_id,
                &g.station_track_candidate_id,
                &g.station_track_evaluation_id,
                &g.operating_envelope_evaluation_id,
                &g.feed_coverage_evaluation_id,
                &g.drive_duty_evaluation_id,
            ]
            .iter()
            .any(|id| !hash(id))
        {
            return Err("Exact fixed-origin physical route/target/authority, unchanged berth interval and counted station-track/envelope/feed bindings required".into());
        }
        if binding.frame_context_id != self.context_id
            || binding.compiled_case_id != d.journey.id
            || binding.compiled_policy_id != p.policy_id
            || [
                &binding.frame_context_id,
                &binding.source_case_id,
                &binding.source_policy_id,
                &binding.compiled_case_id,
                &binding.compiled_policy_id,
            ]
            .iter()
            .any(|id| !hash(id))
            || binding.source_case_id == binding.compiled_case_id
            || binding.source_policy_id == binding.compiled_policy_id
        {
            return Err("New root-exported compiled Case/policy identities and exact frame binding required; canonical authentication remains external".into());
        }
        let end = self.native(route.distance_m);
        let source_brake = binding.source_brake_start_route_m;
        let emergency = binding.source_emergency_route_m;
        if !source_brake.is_finite()
            || source_brake < self.origin_route_m
            || source_brake > route.distance_m
            || emergency
                .is_some_and(|x| !x.is_finite() || x < self.origin_route_m || x > route.distance_m)
            || d.journey.distance_m != end
            || p.end_of_authority_m != end
            || d.journey.brake_start_m != self.native(source_brake)
            || d.journey.fault.emergency_at_m != emergency.map(|x| self.native(x))
            || p.research_v2
                .as_ref()
                .is_some_and(|v| v.berth_target_m != end)
        {
            return Err("Exported native target/authority/brake/fault coordinates must exactly project the physical frame; no authority extension or runtime mutation".into());
        }
        let drive = d
            .journey
            .drive
            .as_ref()
            .ok_or("Framed continuous source drive required")?;
        if drive.external_mass_kg != 0.
            || drive.external_resistance_n != 0.
            || drive.windows_m != vec![[0., end]]
            || self.native(self.allowed_initial_route_interval_m[0]) - 2. * p.position_error_bound_m
                < 0.
            || self.native(self.allowed_initial_route_interval_m[1]) + 2. * p.position_error_bound_m
                >= end
        {
            return Err("Counted continuous no-external-mass feed must cover the full entry/observation interval; max(0) truncation is not entry coverage".into());
        }
        Ok(())
    }
    pub(in crate::fleet) fn application(
        &self,
        d: &Departure,
        binding: &FrameCaseBinding,
        station_offset: f64,
        direction: f64,
        label: String,
    ) -> Result<FrameApplication, String> {
        let u = direction * station_offset;
        let x = self.native(u);
        let p = d
            .journey
            .control
            .as_ref()
            .ok_or("Framed feedback policy required")?;
        if !station_offset.is_finite()
            || !matches!(direction, -1. | 1.)
            || station_offset.abs() > d.journey.berth_tolerance_m
            || u < self.allowed_initial_route_interval_m[0]
            || u > self.allowed_initial_route_interval_m[1]
            || !x.is_finite()
            || x < 0.
            || x > d.journey.distance_m
            || x + p.position_bias_m - p.position_error_bound_m < 0.
            || x + p.position_bias_m + p.position_error_bound_m >= d.journey.distance_m
        {
            return Err("Actual signed station offset or complete biased observation interval is outside the declared physical/native entry coverage".into());
        }
        Ok(FrameApplication {
            frame_context_id: self.context_id.clone(),
            geometry: self.geometry.clone(),
            physical_route_distance_m: self.physical_route_distance_m,
            origin_route_m: self.origin_route_m,
            direction,
            physical_station_offset_m: station_offset,
            physical_initial_route_position_m: u,
            native_initial_position_m: x,
            source_case_id: binding.source_case_id.clone(),
            source_policy_id: binding.source_policy_id.clone(),
            exported_case_id: binding.compiled_case_id.clone(),
            exported_policy_id: binding.compiled_policy_id.clone(),
            execution_label: label,
            accepted_mechanical_steps: 0,
            case_fields_mutated: false,
            canonical_hash_verified_by_native: false,
            physical_geometry_verified: false,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn declaration() -> (ResearchNetwork, FleetCase, Departure, FrameCaseBinding) {
        let golden: serde_json::Value =
            serde_json::from_str(include_str!("../tests/data/fleet_legacy_control.json")).unwrap();
        let q: Request =
            serde_json::from_str(golden["request_raw_json"].as_str().unwrap()).unwrap();
        let mut c = q.cases[1].clone();
        let mut d = c.departures.remove(0);
        d.route_id = Some("AB".into());
        d.journey.id = "1".repeat(64);
        d.journey.distance_m = 1505.;
        d.journey.brake_start_m = 1505.;
        d.journey.drive.as_mut().unwrap().windows_m = vec![[0., 1505.]];
        let p = d.journey.control.as_mut().unwrap();
        p.policy_id = "2".repeat(64);
        p.end_of_authority_m = 1505.;
        let geometry = FrameGeometry {
            project_candidate_id: c.candidate_id.clone(),
            body_candidate_id: "3".repeat(64),
            body_evaluation_id: "4".repeat(64),
            alignment_candidate_id: "b".repeat(64),
            alignment_evaluation_id: "c".repeat(64),
            station_candidate_id: "5".repeat(64),
            station_evaluation_id: "6".repeat(64),
            station_track_candidate_id: "7".repeat(64),
            station_track_evaluation_id: "8".repeat(64),
            operating_envelope_evaluation_id: "9".repeat(64),
            feed_coverage_evaluation_id: "d".repeat(64),
            drive_duty_evaluation_id: "e".repeat(64),
        };
        let frame = EntryFrame {
            schema: "osr-fixed-route-origin-entry/1".into(),
            context_id: "f".repeat(64),
            train_reference: "formation-geometric-centre".into(),
            origin_route_m: -5.,
            physical_route_distance_m: 1500.,
            physical_target_route_m: 1500.,
            physical_authority_route_m: 1500.,
            allowed_initial_route_interval_m: [-2., 2.],
            station_track_reference_domain_m: [-5., 1500.],
            operating_envelope_reference_domain_m: [-5., 1500.],
            continuous_feed_reference_domain_m: [-5., 1500.],
            geometry,
        };
        let n = ResearchNetwork {
            schema: "osr-no-storage-adjacent-network/1".into(),
            position_reference: "signed-station-order-offset/1".into(),
            route_resource_model: "dedicated-directed-double-track-blocks/1".into(),
            geometry_binding: GeometryBinding {
                project_candidate_id: c.candidate_id.clone(),
                alignment_candidate_id: "b".repeat(64),
                alignment_evaluation_id: "c".repeat(64),
                route_manifest_id: "d".repeat(64),
            },
            station_order: vec!["A".into(), "B".into()],
            routes: vec![DirectedRoute {
                id: "AB".into(),
                from_station_id: "A".into(),
                to_station_id: "B".into(),
                distance_m: 1500.,
                geometry_record_id: "e".repeat(64),
                entry_frame: Some(frame),
            }],
        };
        let b = FrameCaseBinding {
            frame_context_id: "f".repeat(64),
            source_case_id: "3".repeat(64),
            source_policy_id: "4".repeat(64),
            compiled_case_id: d.journey.id.clone(),
            compiled_policy_id: d.journey.control.as_ref().unwrap().policy_id.clone(),
            source_brake_start_route_m: 1500.,
            source_emergency_route_m: None,
        };
        d.frame_binding = Some(b.clone());
        c.departures = vec![d.clone()];
        c.network = Some(n.clone());
        for s in &mut c.stations {
            s.store.leakage_per_s = 0.;
            s.reset.duration_s = 0.;
            s.reset.grid_energy_j = 0.;
            s.reset.grid_power_w = 0.;
        }
        (n, c, d, b)
    }
    #[test]
    fn pure_affine_projection_preserves_offset_and_reverse_direction() {
        let (n, _, d, b) = declaration();
        let r = &n.routes[0];
        let f = r.entry_frame.as_ref().unwrap();
        f.validate(r, &n.geometry_binding, &d, &b).unwrap();
        let a = f.application(&d, &b, -1.5, 1., "label".into()).unwrap();
        assert_eq!(a.native_initial_position_m, 3.5);
        assert_eq!(f.physical(a.native_initial_position_m), -1.5);
        assert_eq!(
            f.application(&d, &b, -1.5, -1., "reverse".into())
                .unwrap()
                .native_initial_position_m,
            6.5
        );
        assert!(!a.case_fields_mutated && !a.canonical_hash_verified_by_native);
    }
    #[test]
    fn pure_projection_rejects_missing_feed_stale_ids_and_displaced_targets() {
        let (n, _, d, b) = declaration();
        let mut r = n.routes[0].clone();
        r.entry_frame
            .as_mut()
            .unwrap()
            .continuous_feed_reference_domain_m = [0., 1500.];
        assert!(
            r.entry_frame
                .as_ref()
                .unwrap()
                .validate(&r, &n.geometry_binding, &d, &b)
                .is_err()
        );
        let r = &n.routes[0];
        let f = r.entry_frame.as_ref().unwrap();
        let mut stale = b.clone();
        stale.compiled_case_id = stale.source_case_id.clone();
        assert!(f.validate(r, &n.geometry_binding, &d, &stale).is_err());
        let mut d = d.clone();
        d.journey.control.as_mut().unwrap().end_of_authority_m += 1.;
        assert!(f.validate(r, &n.geometry_binding, &d, &b).is_err());
    }
    #[test]
    fn pure_outer_permission_never_uses_zero_inner_scratch_as_evidence() {
        let (n, mut c, d, _) = declaration();
        let permit = n.inactive_permit(&c).unwrap();
        assert!(permit.allows(&d.journey));
        let mut changed = d.journey.clone();
        changed.mass_kg += 1.;
        assert!(!permit.allows(&changed));
        c.stations[0].store.capacity_j = 1.;
        assert!(n.inactive_permit(&c).is_err());
    }
    #[test]
    fn pure_no_frame_v2_cannot_label_an_early_target_as_the_next_station() {
        let (mut n, mut c, mut d, _) = declaration();
        n.routes[0].entry_frame = None;
        d.frame_binding = None;
        d.journey.distance_m = 1500.;
        d.journey.control.as_mut().unwrap().research_v2 = Some(crate::ResearchFeedbackV2 {
            strategy: "held-docking-speed-governor/2".into(),
            berth_target_m: 1495.,
            brake_floor_n: 40000.,
            creep_speed_m_s: 0.2,
        });
        c.network = Some(n.clone());
        c.departures = vec![d];
        assert!(n.validate(&c).unwrap_err().contains("berth target"));
    }
}
