//! Explicit no-storage adjacent-line research domain, never a railway admission.
use super::*;
#[path = "fleet_frame.rs"]
mod frame;
pub use frame::{EntryFrame, FrameApplication, FrameCaseBinding, FrameGeometry};

/// Private proof from REAL immutable outer specs, never zero scratch stores.
pub(crate) struct InactiveRecordingPermit {
    exported_cases: Vec<Vec<u8>>,
}
impl InactiveRecordingPermit {
    pub(crate) fn allows(&self, c: &Case) -> bool {
        serde_json::to_vec(c).is_ok_and(|raw| self.exported_cases.contains(&raw))
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GeometryBinding {
    pub project_candidate_id: String,
    pub alignment_candidate_id: String,
    pub alignment_evaluation_id: String,
    pub route_manifest_id: String,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DirectedRoute {
    pub id: String,
    pub from_station_id: String,
    pub to_station_id: String,
    pub distance_m: f64,
    pub geometry_record_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub entry_frame: Option<EntryFrame>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResearchNetwork {
    pub schema: String,
    pub position_reference: String,
    pub route_resource_model: String,
    pub geometry_binding: GeometryBinding,
    pub station_order: Vec<String>,
    pub routes: Vec<DirectedRoute>,
}
#[derive(Debug, Clone, Serialize)]
pub struct NetworkPosition {
    pub station_offset_m: Option<f64>,
    pub route_id: Option<String>,
    pub route_position_m: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub native_route_position_m: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub frame_context_id: Option<String>,
}
#[derive(Debug, Clone, Serialize)]
pub struct NetworkDiagnostics {
    pub schema: &'static str,
    pub position_reference: String,
    pub route_resource_model: String,
    pub geometry_binding: GeometryBinding,
    pub routes: Vec<DirectedRoute>,
    pub storage_disabled: bool,
    pub signed_through_entry_supported: bool,
    pub geometry_verified: bool,
    pub shared_feed_capacity_verified: bool,
    pub limitations: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub affine_entry_contract_enabled: Option<bool>,
}
fn hash(s: &str) -> bool {
    s.len() == 64 && s.bytes().all(|c| c.is_ascii_hexdigit())
}
fn inactive_station(s: &Station, distance: f64) -> bool {
    let inactive = |q: &crate::cycle::Transfer| {
        nonneg(q.start_m)
            && pos(q.end_m)
            && q.start_m < q.end_m
            && q.end_m <= distance
            && q.max_force_n == 0.
            && q.max_power_w == 0.
    };
    s.initial_energy_j == 0.
        && s.store.capacity_j == 0.
        && pos(s.store.capture_efficiency)
        && s.store.capture_efficiency <= 1.
        && pos(s.store.release_efficiency)
        && s.store.release_efficiency <= 1.
        && s.store.leakage_per_s == 0.
        && s.reset.duration_s == 0.
        && s.reset.grid_energy_j == 0.
        && s.reset.grid_power_w == 0.
        && inactive(&s.release)
        && s.capture_stages.len() <= 16
        && s.capture_stages.iter().all(inactive)
}
impl ResearchNetwork {
    pub(super) fn validate(&self, c: &FleetCase) -> Result<(), String> {
        let binding = &self.geometry_binding;
        if self.schema != "osr-no-storage-adjacent-network/1"
            || self.position_reference != "signed-station-order-offset/1"
            || self.route_resource_model != "dedicated-directed-double-track-blocks/1"
            || binding.project_candidate_id != c.candidate_id
            || [
                &binding.project_candidate_id,
                &binding.alignment_candidate_id,
                &binding.alignment_evaluation_id,
                &binding.route_manifest_id,
            ]
            .iter()
            .any(|s| !hash(s))
            || !(2..=8).contains(&c.stations.len())
            || self.station_order.len() != c.stations.len()
            || self.routes.is_empty()
            || self.routes.len() > 2 * (c.stations.len() - 1)
        {
            return Err("Explicit no-storage2..8station adjacent research network, signed position convention, dedicated directed blocks and exact geometry/project bindings required".into());
        }
        let station_ids: HashSet<_> = c.stations.iter().map(|s| &s.id).collect();
        let ordered: HashSet<_> = self.station_order.iter().collect();
        if station_ids.len() != c.stations.len()
            || ordered != station_ids
            || self.station_order.iter().any(|s| s.is_empty())
        {
            return Err(
                "Unique station IDs and a complete unambiguous station order required".into(),
            );
        }
        let mut ids = HashSet::new();
        let mut pairs = HashSet::new();
        for r in &self.routes {
            let a = self
                .station_order
                .iter()
                .position(|s| s == &r.from_station_id);
            let b = self
                .station_order
                .iter()
                .position(|s| s == &r.to_station_id);
            if r.id.is_empty()
                || !ids.insert(&r.id)
                || !pairs.insert((&r.from_station_id, &r.to_station_id))
                || a.zip(b).is_none_or(|(a, b)| a.abs_diff(b) != 1)
                || !pos(r.distance_m)
                || !hash(&r.geometry_record_id)
            {
                return Err("Unique directed adjacent route IDs/pairs, positive exact distances and geometry record identities required".into());
            }
        }
        for s in &c.stations {
            let distance = self
                .routes
                .iter()
                .filter(|r| r.from_station_id == s.id || r.to_station_id == s.id)
                .map(|r| r.distance_m)
                .fold(f64::INFINITY, f64::min);
            if !distance.is_finite() || !inactive_station(s, distance) {
                return Err("Network mode rejects active storage, capture, release, leakage and reset equipment; all transfer placeholders must be inactive and within incident route domains".into());
            }
        }
        for d in &c.departures {
            let r = d
                .route_id
                .as_ref()
                .and_then(|id| self.routes.iter().find(|r| &r.id == id));
            if r.is_none_or(|r| {
                r.from_station_id != d.departure_station_id
                    || r.to_station_id != d.arrival_station_id
            }) {
                return Err("Every network departure must name its exact directed route, stations and unchanged journey distance".into());
            }
            let r = r.unwrap();
            match (&r.entry_frame, &d.frame_binding) {
                (Some(f), Some(b)) => f.validate(r, &self.geometry_binding, d, b)?,
                (None, None) => {
                    if r.distance_m != d.journey.distance_m {
                        return Err("Every network departure must name its exact directed route, stations and unchanged journey distance".into());
                    }
                    if d.journey
                        .control
                        .as_ref()
                        .and_then(|p| p.research_v2.as_ref())
                        .is_some_and(|v| v.berth_target_m != r.distance_m)
                    {
                        return Err("No-frame network berth target must equal the physical route endpoint; an early stop is not arrival at the next station".into());
                    }
                }
                _ => return Err(
                    "Both fixed route frame and per-departure compiled Case binding are required"
                        .into(),
                ),
            }
        }
        Ok(())
    }
    pub(super) fn inactive_permit(&self, c: &FleetCase) -> Result<InactiveRecordingPermit, String> {
        if c.network
            .as_ref()
            .is_none_or(|n| serde_json::to_vec(n).ok() != serde_json::to_vec(self).ok())
        {
            return Err(
                "Inactive recorder proof must bind the exact immutable outer network definition"
                    .into(),
            );
        }
        self.validate(c)?;
        let mut exported_cases = vec![];
        for d in &c.departures {
            if d.frame_binding.is_some() {
                exported_cases.push(serde_json::to_vec(&d.journey).map_err(|e| e.to_string())?);
            }
        }
        if exported_cases.is_empty() {
            return Err("Inactive recorder permission requires an explicitly framed, validated outer no-storage network".into());
        }
        Ok(InactiveRecordingPermit { exported_cases })
    }
    pub(super) fn indices(&self, c: &FleetCase, d: &Departure) -> (usize, usize, usize, f64) {
        let route = self
            .routes
            .iter()
            .position(|r| Some(&r.id) == d.route_id.as_ref())
            .unwrap();
        let r = &self.routes[route];
        let dep = c
            .stations
            .iter()
            .position(|s| s.id == r.from_station_id)
            .unwrap();
        let arr = c
            .stations
            .iter()
            .position(|s| s.id == r.to_station_id)
            .unwrap();
        let a = self
            .station_order
            .iter()
            .position(|s| s == &r.from_station_id)
            .unwrap();
        let b = self
            .station_order
            .iter()
            .position(|s| s == &r.to_station_id)
            .unwrap();
        (dep, arr, route, if b > a { 1. } else { -1. })
    }
    pub(super) fn diagnostics(&self) -> NetworkDiagnostics {
        NetworkDiagnostics {
            schema: "osr-no-storage-network-result/1",
            position_reference: self.position_reference.clone(),
            route_resource_model: self.route_resource_model.clone(),
            geometry_binding: self.geometry_binding.clone(),
            routes: self.routes.clone(), storage_disabled: true,
            signed_through_entry_supported: false, geometry_verified: false,
            shared_feed_capacity_verified: false,
            affine_entry_contract_enabled: self.routes.iter().any(|r|r.entry_frame.is_some()).then_some(true),
            limitations: vec![
                "Explicit geometry identities are provenance references, not native geometry verification or candidate admission".into(),
                "Each directed adjacent route is an assumed exclusive double-track block; shared single-track, platform, switch and finite-train conflicts are unsupported".into(),
                "All recorded motion assumes independently available full grid feed; shared supply capacity and line-level interfaces remain external held obligations".into(),
                if self.routes.iter().any(|r|r.entry_frame.is_some()) {
                    "Fixed affine entry uses declared geometry/envelope/feed context and unchanged physical target/authority; native validation checks projection, not source authentication or physical admission".into()
                } else {
                    "Signed station offsets are retained. Negative outgoing entry is held until a physically bound coordinate-rebase/entry-domain interface exists; no train is teleported to a nominal berth".into()
                },
                "Arrival, dwell and terminal turnaround are causal time budgets, not protected service or demonstrated station occupation/manoeuvres".into(),
            ],
        }
    }
}
