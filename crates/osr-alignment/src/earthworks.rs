//! Earthworks quantities — cut / fill volumes + material take-off.
//!
//! Given a sampled alignment + terrain elevations at each station,
//! compute the earthworks required to build the formation:
//!
//! - **Cut**: volume removed where terrain is above the formation top.
//! - **Fill**: volume added where terrain is below the formation top.
//! - **Net**: cut − fill (positive = surplus material; negative = import).
//!
//! Plus the permanent-way materials that ship with the alignment:
//!
//! - **Rail tonnage** (two rails at the profile's linear mass per metre).
//! - **Sleeper count** (at the geometry preset's spacing).
//! - **Ballast volume** (from the track panel's ballast profile).
//! - **Concrete volume** (viaduct U-girder segments per elevated length).
//!
//! Output is a `EarthworksQuantities` document that plugs into the
//! cost-estimation pass (RFC 0003 §6) with real numbers instead of
//! the heuristics `osr-routing` uses at the solver stage.

use serde::{Deserialize, Serialize};

use crate::chainage::{sample_every, StationedPoint};
use crate::Alignment;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum CivilSection {
    /// Conventional ballasted track on graded formation.
    AtGrade,
    /// Elevated precast U-girder viaduct.
    Elevated,
    /// Short bridge over water / road — treated as elevated with the
    /// bridge class's U-girder.
    Bridge,
    /// Depot / yard formation — no viaduct, no cant.
    Depot,
}

impl CivilSection {
    pub fn is_elevated(self) -> bool {
        matches!(self, CivilSection::Elevated | CivilSection::Bridge)
    }
}

/// One sample at a single chainage.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct EarthworksSample {
    pub chainage_m: f64,
    pub formation_z_m: f64,
    pub terrain_z_m: f64,
    pub civil: CivilSection,
    /// Cut depth at this chainage, metres (0 if fill or elevated).
    pub cut_depth_m: f64,
    /// Fill depth at this chainage, metres (0 if cut or elevated).
    pub fill_depth_m: f64,
}

/// Aggregated earthworks quantities for an alignment.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct EarthworksQuantities {
    pub alignment_length_m: f64,
    pub sample_interval_m: f64,
    pub samples: Vec<EarthworksSample>,
    pub total_cut_m3: f64,
    pub total_fill_m3: f64,
    /// Net cut − fill. Positive means surplus spoil to truck off-site;
    /// negative means external fill is required.
    pub net_material_m3: f64,
    /// Elevated length: where CivilSection::Elevated or Bridge.
    pub elevated_length_m: f64,
    pub at_grade_length_m: f64,
    /// Approximate rail tonnage (two running rails × linear mass × length).
    pub rail_tonnes: f64,
    /// Approximate sleeper count (spacing × length).
    pub sleeper_count: u64,
    /// Ballast volume at ballasted sections (depot + at-grade).
    pub ballast_m3: f64,
    /// Concrete volume for elevated sections (U-girder cross-section × length).
    pub concrete_m3: f64,
}

/// Parameters bundling the permanent-way catalogue dimensions used
/// for take-off.
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct PermanentWayParams {
    /// Linear mass of one rail, kg/m (UIC 54E1 ≈ 54.77, 60E1 ≈ 60.21).
    pub rail_linear_mass_kg_per_m: f64,
    /// Sleeper spacing, metres (0.6 m standard metro, 0.65 urban tram).
    pub sleeper_spacing_m: f64,
    /// Ballast cross-section area per metre of track, m² (typ. 1.7 m²).
    pub ballast_cross_section_m2: f64,
    /// U-girder concrete cross-section area per metre, m² (typ. 2.1 m²).
    pub ugirder_cross_section_m2: f64,
    /// Typical formation width per at-grade track, metres.
    pub formation_width_m: f64,
}

impl Default for PermanentWayParams {
    fn default() -> Self {
        Self {
            rail_linear_mass_kg_per_m: 60.21, // UIC 60E1
            sleeper_spacing_m: 0.6,
            ballast_cross_section_m2: 1.7,
            ugirder_cross_section_m2: 2.1,
            formation_width_m: 6.0,
        }
    }
}

/// Callback: for a given (x_m, y_m), return the terrain elevation in
/// metres. Supplied by the deployment (from a DEM raster).
pub type TerrainSampler<'a> = &'a dyn Fn(f64, f64) -> f64;

/// Callback: for a given chainage, what civil section applies?
pub type CivilClassifier<'a> = &'a dyn Fn(f64) -> CivilSection;

/// Compute earthworks + material take-off for the alignment.
pub fn compute_quantities(
    alignment: &Alignment,
    sample_interval_m: f64,
    terrain_at: TerrainSampler<'_>,
    civil_at: CivilClassifier<'_>,
    params: PermanentWayParams,
) -> EarthworksQuantities {
    let stations: Vec<StationedPoint> = sample_every(alignment, sample_interval_m);
    let mut samples = Vec::with_capacity(stations.len());
    let mut cut_sum = 0.0;
    let mut fill_sum = 0.0;
    let mut elevated_len = 0.0;
    let mut at_grade_len = 0.0;

    for (i, sp) in stations.iter().enumerate() {
        let terrain_z = terrain_at(sp.x_m, sp.y_m);
        let civil = civil_at(sp.chainage_m);
        let mut cut = 0.0;
        let mut fill = 0.0;
        if !civil.is_elevated() {
            let delta = sp.z_m - terrain_z;
            if delta < 0.0 {
                // Formation below terrain — need to cut.
                cut = -delta;
            } else if delta > 0.0 {
                fill = delta;
            }
        }
        samples.push(EarthworksSample {
            chainage_m: sp.chainage_m,
            formation_z_m: sp.z_m,
            terrain_z_m: terrain_z,
            civil,
            cut_depth_m: cut,
            fill_depth_m: fill,
        });

        if i + 1 < stations.len() {
            let next = &stations[i + 1];
            let segment = (next.chainage_m - sp.chainage_m).max(0.0);
            if civil.is_elevated() {
                elevated_len += segment;
            } else {
                at_grade_len += segment;
                cut_sum += cut * params.formation_width_m * segment;
                fill_sum += fill * params.formation_width_m * segment;
            }
        }
    }

    let total_len = elevated_len + at_grade_len;
    let rail_tonnes = 2.0 * params.rail_linear_mass_kg_per_m * total_len / 1000.0;
    let sleeper_count = (total_len / params.sleeper_spacing_m).round() as u64;
    let ballast_m3 = params.ballast_cross_section_m2 * at_grade_len;
    let concrete_m3 = params.ugirder_cross_section_m2 * elevated_len;

    EarthworksQuantities {
        alignment_length_m: alignment.total_length_m(),
        sample_interval_m,
        samples,
        total_cut_m3: cut_sum,
        total_fill_m3: fill_sum,
        net_material_m3: cut_sum - fill_sum,
        elevated_length_m: elevated_len,
        at_grade_length_m: at_grade_len,
        rail_tonnes,
        sleeper_count,
        ballast_m3,
        concrete_m3,
    }
}

/// Emit a plaintext summary of the quantities — for the RFC 0003
/// cost-estimate table.
pub fn format_summary(q: &EarthworksQuantities) -> String {
    format!(
        "Alignment length:      {len:>10.1} m\n\
         At-grade:              {atg:>10.1} m\n\
         Elevated:              {elv:>10.1} m\n\
         Total cut:             {cut:>10.1} m³\n\
         Total fill:            {fil:>10.1} m³\n\
         Net (cut − fill):      {net:>10.1} m³   {dir}\n\
         Rail tonnage:          {rail:>10.2} t\n\
         Sleeper count:         {sl:>10}\n\
         Ballast:               {bal:>10.1} m³\n\
         Concrete (viaduct):    {con:>10.1} m³\n",
        len = q.alignment_length_m,
        atg = q.at_grade_length_m,
        elv = q.elevated_length_m,
        cut = q.total_cut_m3,
        fil = q.total_fill_m3,
        net = q.net_material_m3,
        dir = if q.net_material_m3 > 0.0 {
            "(surplus spoil → haul off-site)"
        } else if q.net_material_m3 < 0.0 {
            "(deficit → import fill)"
        } else {
            "(balanced)"
        },
        rail = q.rail_tonnes,
        sl = q.sleeper_count,
        bal = q.ballast_m3,
        con = q.concrete_m3,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::{HorizontalElement, VerticalElement};

    fn flat_alignment() -> Alignment {
        Alignment {
            line_slug: "test".into(),
            design_speed_kmh: 80.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Tangent {
                length_m: 1_000.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            }],
            vertical: vec![VerticalElement::Grade {
                length_m: 1_000.0,
                grade: 0.0,
                start_z_m: 10.0,
            }],
        }
    }

    #[test]
    fn terrain_matches_formation_gives_zero_earthworks() {
        let a = flat_alignment();
        let q = compute_quantities(
            &a,
            50.0,
            &|_x, _y| 10.0,
            &|_s| CivilSection::AtGrade,
            PermanentWayParams::default(),
        );
        assert_eq!(q.total_cut_m3, 0.0);
        assert_eq!(q.total_fill_m3, 0.0);
        assert_eq!(q.net_material_m3, 0.0);
    }

    #[test]
    fn terrain_above_formation_is_cut() {
        let a = flat_alignment();
        // Terrain uniformly 2 m above formation.
        let q = compute_quantities(
            &a,
            50.0,
            &|_x, _y| 12.0,
            &|_s| CivilSection::AtGrade,
            PermanentWayParams::default(),
        );
        assert!(q.total_cut_m3 > 0.0);
        assert_eq!(q.total_fill_m3, 0.0);
        // Cut volume ≈ 2 m × 6 m × 1000 m = 12 000 m³ (± interval rounding).
        assert!((q.total_cut_m3 - 12_000.0).abs() < 200.0, "{}", q.total_cut_m3);
    }

    #[test]
    fn elevated_skips_earthworks() {
        let a = flat_alignment();
        let q = compute_quantities(
            &a,
            50.0,
            &|_x, _y| 0.0, // terrain 10 m below formation
            &|_s| CivilSection::Elevated,
            PermanentWayParams::default(),
        );
        // No cut/fill on elevated — it's on viaduct.
        assert_eq!(q.total_cut_m3, 0.0);
        assert_eq!(q.total_fill_m3, 0.0);
        assert!(q.elevated_length_m > 900.0);
        assert!(q.concrete_m3 > 0.0);
    }

    #[test]
    fn rail_tonnage_scales_with_length() {
        let a = flat_alignment();
        let q = compute_quantities(
            &a,
            50.0,
            &|_x, _y| 10.0,
            &|_s| CivilSection::AtGrade,
            PermanentWayParams::default(),
        );
        // 1 km × 2 rails × 60.21 kg/m = ~120 tonnes.
        assert!((q.rail_tonnes - 120.42).abs() < 5.0, "{}", q.rail_tonnes);
    }
}
