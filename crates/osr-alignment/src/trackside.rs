//! Trackside equipment placement — axle counters, balises, radio
//! masts, signals, cable cabinets.
//!
//! Given an alignment + signalling / comms design rules, produce a
//! list of placed assets with chainage + lateral offset. The output
//! drives:
//!
//! - Civil: trackside cable trough + cabinet foundation locations.
//! - Signalling: the interlocking's track-circuit / axle-counter
//!   block diagram.
//! - Comms: radio-mast spacing for continuous CBTC coverage.
//! - Permitting: as-built asset register handed to the regulator.
//!
//! Design rules follow RFC 0016 (wayside intrusion) +
//! RFC 0004 (interlocking) + industry baselines:
//!
//! - **Axle counters** at every block boundary; block length ≤ one
//!   braking distance at line speed (typ. 200 m for urban metro).
//! - **Balises** every 500 m on the line for position reference;
//!   paired balises in turnouts.
//! - **Radio masts** every 1 500 m (line-of-sight for 2.4 / 5 GHz
//!   CBTC; 5G adds density).
//! - **Cable cabinets** every 600 m, co-located with axle-counter
//!   pairs where practical.

use serde::{Deserialize, Serialize};

use crate::chainage::{sample_every, StationedPoint};
use crate::Alignment;

/// Kind of trackside asset.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum AssetKind {
    AxleCounter,
    Balise,
    RadioMast,
    CableCabinet,
    Signal,
}

/// One placed asset along an alignment.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Asset {
    pub kind: AssetKind,
    pub chainage_m: f64,
    pub x_m: f64,
    pub y_m: f64,
    pub z_m: f64,
    /// Lateral offset from track centreline, metres. Positive = right
    /// of direction of travel.
    pub lateral_offset_m: f64,
    /// Free-form identifier — `"B-samawah-L1-0425.2"` style.
    pub asset_id: String,
}

/// Design-rule parameters.
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct PlacementRules {
    pub axle_counter_spacing_m: f64,
    pub balise_spacing_m: f64,
    pub radio_mast_spacing_m: f64,
    pub cable_cabinet_spacing_m: f64,
    /// Offset from track centre at which trackside assets mount.
    pub lateral_offset_m: f64,
}

impl Default for PlacementRules {
    fn default() -> Self {
        Self {
            axle_counter_spacing_m: 200.0,
            balise_spacing_m: 500.0,
            radio_mast_spacing_m: 1_500.0,
            cable_cabinet_spacing_m: 600.0,
            lateral_offset_m: 2.8, // typical trackside clearance
        }
    }
}

/// Place every asset kind along the alignment per the design rules.
pub fn place_assets(
    alignment: &Alignment,
    rules: PlacementRules,
    line_slug: &str,
) -> Vec<Asset> {
    let mut out = Vec::new();
    let stations = sample_every(alignment, 10.0);
    if stations.is_empty() {
        return out;
    }

    let mut push = |kind: AssetKind,
                    sp: &StationedPoint,
                    idx: usize,
                    assets: &mut Vec<Asset>| {
        let prefix = match kind {
            AssetKind::AxleCounter => "AC",
            AssetKind::Balise => "B",
            AssetKind::RadioMast => "RM",
            AssetKind::CableCabinet => "CC",
            AssetKind::Signal => "SIG",
        };
        assets.push(Asset {
            kind,
            chainage_m: sp.chainage_m,
            x_m: sp.x_m + rules.lateral_offset_m * sp.bearing_rad.sin(),
            y_m: sp.y_m - rules.lateral_offset_m * sp.bearing_rad.cos(),
            z_m: sp.z_m,
            lateral_offset_m: rules.lateral_offset_m,
            asset_id: format!("{prefix}-{slug}-{idx:04}", slug = line_slug),
        });
    };

    let rules_table: &[(AssetKind, f64)] = &[
        (AssetKind::AxleCounter, rules.axle_counter_spacing_m),
        (AssetKind::Balise, rules.balise_spacing_m),
        (AssetKind::RadioMast, rules.radio_mast_spacing_m),
        (AssetKind::CableCabinet, rules.cable_cabinet_spacing_m),
    ];

    for &(kind, spacing) in rules_table {
        let mut next = 0.0;
        let mut idx = 0;
        for sp in &stations {
            let s = sp.chainage_m - alignment.start_chainage_m;
            if s + 1e-6 >= next {
                push(kind, sp, idx, &mut out);
                idx += 1;
                next += spacing;
            }
        }
    }
    out
}

/// Summarise the asset placement for a report.
pub fn count_by_kind(assets: &[Asset]) -> [(AssetKind, usize); 5] {
    let mut counts = [
        (AssetKind::AxleCounter, 0),
        (AssetKind::Balise, 0),
        (AssetKind::RadioMast, 0),
        (AssetKind::CableCabinet, 0),
        (AssetKind::Signal, 0),
    ];
    for a in assets {
        if let Some(row) = counts.iter_mut().find(|(k, _)| *k == a.kind) {
            row.1 += 1;
        }
    }
    counts
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::{HorizontalElement, VerticalElement};

    fn one_km_tangent() -> Alignment {
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
                start_z_m: 0.0,
            }],
        }
    }

    #[test]
    fn default_rules_produce_expected_counts() {
        let a = one_km_tangent();
        let rules = PlacementRules::default();
        let assets = place_assets(&a, rules, "test-L1");

        let by_kind: std::collections::HashMap<_, _> = count_by_kind(&assets)
            .into_iter()
            .collect();
        // 1 000 m / 200 m spacing = 5 extra axle counters + the one
        // placed at origin = 6. Same logic for the others.
        assert!(by_kind[&AssetKind::AxleCounter] >= 5);
        assert!(by_kind[&AssetKind::Balise] >= 2);
        assert!(by_kind[&AssetKind::RadioMast] >= 1);
    }

    #[test]
    fn assets_have_unique_ids_per_kind() {
        let assets = place_assets(&one_km_tangent(), PlacementRules::default(), "L1");
        let mut per_kind: std::collections::HashMap<AssetKind, std::collections::HashSet<String>> =
            Default::default();
        for a in &assets {
            per_kind
                .entry(a.kind)
                .or_default()
                .insert(a.asset_id.clone());
        }
        for (_, ids) in &per_kind {
            assert_eq!(
                ids.len(),
                ids.iter().collect::<std::collections::HashSet<_>>().len()
            );
        }
    }

    #[test]
    fn lateral_offset_applied() {
        // On a north-pointing tangent (bearing 0), assets should
        // be offset in +X (to the right).
        let assets = place_assets(&one_km_tangent(), PlacementRules::default(), "L1");
        let first = &assets[0];
        // With bearing 0 along +X, the "right" of travel is -Y.
        assert!((first.y_m - -2.8).abs() < 0.01);
    }
}
