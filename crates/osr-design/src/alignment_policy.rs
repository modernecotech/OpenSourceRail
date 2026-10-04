//! Explicit project civil policy; never modifies survey/environment rasters.
use anyhow::{ensure, Result};
use osr_routing::civil::{
    civil_segments_from_classes, elevated_curve_cost_multiplier, elevated_product_for_geometry,
    CivilClass, CivilSegment,
};
use osr_routing::raster::Grid;
use serde::Deserialize;
use std::path::Path;

#[derive(Deserialize)]
pub struct Core {
    south: f64,
    west: f64,
    north: f64,
    east: f64,
}
#[derive(Deserialize)]
pub struct Policy {
    core: Core,
    #[serde(skip)]
    analytical_radius: std::collections::BTreeMap<String, f64>,
}
impl Policy {
    pub fn load(directory: &Path) -> Result<Option<Self>> {
        let path = directory.join("alignment-policy.toml");
        if !path.is_file() {
            return Ok(None);
        }
        let mut policy: Self = toml::from_str(&std::fs::read_to_string(path)?)?;
        let c = &policy.core;
        ensure!(
            [c.south, c.north, c.west, c.east]
                .iter()
                .all(|v| v.is_finite())
                && c.south < c.north
                && c.west < c.east,
            "Invalid core alignment boundary"
        );
        let report: serde_json::Value = serde_json::from_slice(&std::fs::read(
            directory.join("engineering/alignment/core-realignment.json"),
        )?)?;
        for line in report["lines"]
            .as_array()
            .ok_or_else(|| anyhow::anyhow!("Missing analytical alignment controls"))?
        {
            let radius = line["core_runs"]
                .as_array()
                .unwrap()
                .iter()
                .flat_map(|run| run["controls"].as_array().unwrap())
                .filter_map(|control| control["radius_m"].as_f64())
                .fold(f64::INFINITY, f64::min);
            ensure!(
                radius >= 300.0,
                "Core curve needs reviewed special geometry"
            );
            policy
                .analytical_radius
                .insert(line["line"].as_str().unwrap().to_string(), radius);
        }
        Ok(Some(policy))
    }
    fn contains(&self, lat: f64, lon: f64) -> bool {
        let c = &self.core;
        lat >= c.south && lat <= c.north && lon >= c.west && lon <= c.east
    }
    pub fn classify(
        &self,
        line_name: &str,
        grid: &Grid,
        cells: &[(usize, usize)],
        original: &[CivilSegment],
    ) -> Vec<CivilSegment> {
        let mut classes = vec![CivilClass::AtGrade; cells.len()];
        for segment in original {
            classes[segment.from_idx..=segment.to_idx].fill(segment.class);
        }
        for (i, &(row, col)) in cells.iter().enumerate() {
            let (lat, lon) = grid.reference.rc_to_latlon(row, col);
            if self.contains(lat, lon) {
                classes[i] = if grid.is_water(row, col) || classes[i] == CivilClass::Bridge {
                    CivilClass::Bridge
                } else {
                    CivilClass::Elevated
                };
            }
        }
        // Split at the controlled area boundary, keeping actual outer raster
        // curvature. Core radii come from the analytic arcs, not 20 m raster
        // quantisation that otherwise turns a straight diagonal into a bend.
        let core: Vec<bool> = cells
            .iter()
            .map(|&(r, c)| {
                let (lat, lon) = grid.reference.rc_to_latlon(r, c);
                self.contains(lat, lon)
            })
            .collect();
        let mut output = Vec::new();
        let mut start = 0;
        while start < cells.len() {
            let mut end = start + 1;
            while end < cells.len() && core[end] == core[start] {
                end += 1;
            }
            // The prior run owns the boundary edge exactly once.
            let mut part =
                civil_segments_from_classes(grid, &cells[start..end], &classes[start..end]);
            if end < cells.len() {
                let (a, b) = (cells[end - 1], cells[end]);
                let boundary_m = ((a.0 as f64 - b.0 as f64).hypot(a.1 as f64 - b.1 as f64))
                    * grid.reference.cell_m;
                part.last_mut().expect("nonempty run").length_m += boundary_m;
            }
            for segment in &mut part {
                segment.from_idx += start;
                segment.to_idx += start;
                if core[start] && segment.class == CivilClass::Elevated {
                    let radius = *self
                        .analytical_radius
                        .get(line_name)
                        .expect("line has analytical controls");
                    segment.minimum_curve_radius_m = radius.is_finite().then_some(radius);
                    segment.viaduct_product =
                        Some(elevated_product_for_geometry(radius, 25.0, true));
                    segment.elevated_cost_multiplier = elevated_curve_cost_multiplier(radius);
                }
            }
            output.extend(part);
            start = end;
        }
        output
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn core_policy_preserves_water_outer_classes_and_total_chainage() {
        use osr_routing::raster::GridRef;
        let grid = Grid {
            reference: GridRef {
                height: 1,
                width: 7,
                cell_m: 20.0,
                lat0: 0.0,
                bbox_south: -1.0,
                bbox_north: 1.0,
                bbox_west: 0.0,
                bbox_east: 7.0,
                m_per_deg_lat: 20.0,
                m_per_deg_lon: 20.0,
            },
            cost: vec![1.0; 7],
            demand: vec![1.0; 7],
            buildability: vec![1; 7],
            water: Some(vec![0, 0, 0, 1, 0, 0, 0]),
            elevation_m: None,
            terrain_slope_percent: None,
        };
        let cells: Vec<_> = (0..7).map(|c| (0, c)).collect();
        let original = civil_segments_from_classes(&grid, &cells, &[CivilClass::AtGrade; 7]);
        let policy = Policy {
            core: Core {
                south: 0.0,
                north: 1.0,
                west: 2.0,
                east: 5.0,
            },
            analytical_radius: [("line-1".into(), f64::INFINITY)].into(),
        };
        let result = policy.classify("line-1", &grid, &cells, &original);
        assert!((result.iter().map(|s| s.length_m).sum::<f64>() - 120.0).abs() < 1e-9);
        assert_eq!(result.first().unwrap().class, CivilClass::AtGrade);
        assert_eq!(result.last().unwrap().class, CivilClass::AtGrade);
        assert!(result.iter().any(|s| s.class == CivilClass::Bridge));
        let elevated: Vec<_> = result
            .iter()
            .filter(|s| s.class == CivilClass::Elevated)
            .collect();
        assert!(!elevated.is_empty());
        assert!(elevated
            .iter()
            .all(|s| s.minimum_curve_radius_m.is_none() && s.elevated_cost_multiplier == 1.0));
    }
    #[test]
    fn boundary_is_inclusive_and_outskirts_are_excluded() {
        let p = Policy {
            core: Core {
                south: 33.22,
                north: 33.42,
                west: 44.28,
                east: 44.53,
            },
            analytical_radius: Default::default(),
        };
        assert!(p.contains(33.22, 44.28));
        assert!(p.contains(33.32, 44.4));
        assert!(!p.contains(33.219, 44.4));
        assert!(!p.contains(33.32, 44.531));
    }
}
