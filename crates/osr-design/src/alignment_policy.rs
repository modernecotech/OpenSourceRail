//! Explicit project civil policy; never modifies survey/environment rasters.
use anyhow::{ensure, Result};
use osr_routing::civil::{
    civil_segments_from_classes, elevated_curve_cost_multiplier, elevated_product_for_geometry,
    CivilClass, CivilSegment,
};
use osr_routing::raster::Grid;
use serde::Deserialize;
use std::path::Path;

/// A water endpoint is moved onto its bank before station/civil quantities are
/// generated. Closed rings keep every edge and rotate their chainage origin.
#[cfg(test)]
pub fn bank_route_ends(
    lines: &mut [osr_routing::topology::Line],
    grid: &Grid,
) -> Result<Vec<serde_json::Value>> {
    bank_route_ends_with_limit(lines, grid, 600.0)
}

pub fn bank_route_ends_with_limit(
    lines: &mut [osr_routing::topology::Line],
    grid: &Grid,
    maximum_crop_m: f64,
) -> Result<Vec<serde_json::Value>> {
    use osr_routing::topology::LineShape;
    let mut changes = Vec::new();
    for line in lines {
        if line.cells.len() < 2 {
            continue;
        }
        if matches!(line.shape, LineShape::Ring) && line.cells.first() == line.cells.last() {
            if grid.excludes_station_for_water(line.cells[0].0, line.cells[0].1) {
                let unique = line.cells.len() - 1;
                let first = line.cells[..unique]
                    .iter()
                    .position(|&(r, c)| !grid.excludes_station_for_water(r, c))
                    .ok_or_else(|| {
                        anyhow::anyhow!("{} ring has no dry platform origin", line.name)
                    })?;
                let from = line.cells[0];
                line.cells.pop();
                line.cells.rotate_left(first);
                line.cells.push(line.cells[0]);
                changes.push(serde_json::json!({"kind":"ring-chainage-origin-on-bank","line":line.name,"from_cell":from,"to_cell":line.cells[0],"geometry_changed":false}));
            }
            continue;
        }
        for at_start in [true, false] {
            let original = if at_start {
                line.cells[0]
            } else {
                *line.cells.last().unwrap()
            };
            if !grid.excludes_station_for_water(original.0, original.1) {
                continue;
            }
            let ordered: Vec<_> = if at_start {
                line.cells.clone()
            } else {
                line.cells.iter().rev().copied().collect()
            };
            let mut removed_m = 0.0;
            let mut found = None;
            for i in 1..ordered.len() {
                removed_m += (ordered[i].0 as f64 - ordered[i - 1].0 as f64)
                    .hypot(ordered[i].1 as f64 - ordered[i - 1].1 as f64)
                    * grid.reference.cell_m;
                if removed_m > maximum_crop_m {
                    break;
                }
                if !grid.excludes_station_for_water(ordered[i].0, ordered[i].1) {
                    found = Some(i);
                    break;
                }
            }
            let index = found.ok_or_else(|| {
                anyhow::anyhow!(
                    "{} water endpoint has no bank within {:.0} m; review alignment",
                    line.name,
                    maximum_crop_m
                )
            })?;
            ensure!(
                line.cells.len() - index >= 2,
                "bank crop would remove the complete line"
            );
            if at_start {
                line.cells.drain(..index);
            } else {
                line.cells.truncate(line.cells.len() - index);
            }
            changes.push(serde_json::json!({"kind":"radial-end-crop-on-bank","line":line.name,"at_start":at_start,"from_cell":original,"to_cell":ordered[index],"removed_route_m":removed_m,"basis":"Remove the unserved water tail before calculating stations, route, fleet and civil quantities; bank stability and access remain project releases."}));
        }
    }
    Ok(changes)
}

/// Keep platforms off the independent water mask without bending the track.
/// The final layout validator still checks spacing and interchange envelopes.
#[cfg(test)]
pub fn relocate_water_platforms(
    stations: &mut [osr_routing::station::Station],
    lines: &[osr_routing::topology::Line],
    grid: &Grid,
) -> Result<Vec<serde_json::Value>> {
    relocate_water_platforms_with_limit(stations, lines, grid, 700.0)
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BankPlatforms {
    maximum_relocation_m: f64,
    basis: String,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BankRouteEnds {
    maximum_crop_m: f64,
    basis: String,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct BankPolicy {
    schema_version: u32,
    platforms: BankPlatforms,
    route_ends: Option<BankRouteEnds>,
}
fn bank_policy(directory: &Path) -> Result<Option<BankPolicy>> {
    let path = directory.join("station-bank-policy.toml");
    if !path.is_file() {
        return Ok(None);
    }
    let policy: BankPolicy = toml::from_str(&std::fs::read_to_string(path)?)?;
    ensure!(
        policy.schema_version == 1
            && policy.platforms.maximum_relocation_m.is_finite()
            && (700.0..=1500.0).contains(&policy.platforms.maximum_relocation_m)
            && !policy.platforms.basis.trim().is_empty(),
        "bank policy requires schema 1, a 700–1500 m bounded relocation and a project basis"
    );
    if let Some(ends) = &policy.route_ends {
        ensure!(
            ends.maximum_crop_m.is_finite()
                && (600.0..=5000.0).contains(&ends.maximum_crop_m)
                && !ends.basis.trim().is_empty(),
            "endpoint crop requires a 600–5000 m bound and a project basis"
        );
    }
    Ok(Some(policy))
}
pub fn bank_shift_limit(directory: &Path) -> Result<f64> {
    Ok(bank_policy(directory)?.map_or(700.0, |p| p.platforms.maximum_relocation_m))
}
pub fn bank_endpoint_limit(directory: &Path) -> Result<f64> {
    Ok(bank_policy(directory)?
        .and_then(|p| p.route_ends)
        .map_or(600.0, |p| p.maximum_crop_m))
}

pub fn relocate_water_platforms_with_limit(
    stations: &mut [osr_routing::station::Station],
    lines: &[osr_routing::topology::Line],
    grid: &Grid,
    maximum_shift_m: f64,
) -> Result<Vec<serde_json::Value>> {
    type Candidate = (f64, f64, usize, usize); // shift, chainage, row, col
    let candidates = |station: &osr_routing::station::Station| -> Result<Vec<Candidate>> {
        if station.mandatory_crossing {
            ensure!(
                !grid.excludes_station_for_water(station.row, station.col),
                "Mandatory crossing platform is wet; review alignment"
            );
            return Ok(vec![(0.0, station.s_m, station.row, station.col)]);
        }
        let line = lines
            .iter()
            .find(|l| l.name == station.line_name)
            .ok_or_else(|| anyhow::anyhow!("water platform has no corridor"))?;
        let mut chainage = 0.0;
        let mut route = Vec::new();
        for (i, &(row, col)) in line.cells.iter().enumerate() {
            if i > 0 {
                let (pr, pc) = line.cells[i - 1];
                chainage +=
                    (row as f64 - pr as f64).hypot(col as f64 - pc as f64) * grid.reference.cell_m;
            }
            route.push((chainage, row, col));
        }
        let endpoint = station.s_m < 1.0 || (chainage - station.s_m).abs() < 1.0;
        let mut result: Vec<_> = route
            .into_iter()
            .filter_map(|(s, r, c)| {
                let shift = (s - station.s_m).abs();
                (shift <= maximum_shift_m
                    && (!endpoint || shift < 1.0)
                    && (!station.mandatory_crossing || shift < 1.0)
                    && !grid.excludes_station_for_water(r, c))
                .then_some((shift, s, r, c))
            })
            .collect();
        result.sort_by(|a, b| a.0.total_cmp(&b.0).then_with(|| a.1.total_cmp(&b.1)));
        ensure!(
            !result.is_empty(),
            "{} platform at {:.1} m has no dry corridor cell within {:.0} m; review alignment",
            station.line_name,
            station.s_m,
            maximum_shift_m
        );
        Ok(result)
    };
    let mut groups = std::collections::BTreeMap::<u32, Vec<usize>>::new();
    for (i, s) in stations.iter().enumerate() {
        if let Some(group) = s.junction_group {
            groups.entry(group).or_default().push(i);
        }
    }
    let mut selected = std::collections::BTreeMap::<usize, Candidate>::new();
    for (group, indices) in groups {
        if !indices
            .iter()
            .any(|&i| grid.excludes_station_for_water(stations[i].row, stations[i].col))
        {
            continue;
        }
        let choices: Vec<_> = indices
            .iter()
            .map(|&i| candidates(&stations[i]))
            .collect::<Result<_>>()?;
        // Multi-change complexes can contain two distinct transfers along
        // the same line. Preserve each existing cross-line walking leg,
        // rather than inventing a 600 m diameter for the entire complex.
        let mut required = vec![vec![false; indices.len()]; indices.len()];
        let distance = |a: usize, b: usize| {
            (stations[indices[a]].row as f64 - stations[indices[b]].row as f64)
                .hypot(stations[indices[a]].col as f64 - stations[indices[b]].col as f64)
                * grid.reference.cell_m
        };
        for a in 0..indices.len() {
            for b in 0..indices.len() {
                required[a][b] = stations[indices[a]].line_name != stations[indices[b]].line_name
                    && distance(a, b) <= 600.0;
            }
        }
        for a in 0..indices.len() {
            if !required[a].iter().any(|&edge| edge) {
                if let Some(b) = (0..indices.len())
                    .filter(|&b| stations[indices[a]].line_name != stations[indices[b]].line_name)
                    .min_by(|&b, &c| distance(a, b).total_cmp(&distance(a, c)))
                {
                    required[a][b] = true;
                    required[b][a] = true;
                }
            }
        }
        let mut best: Option<(f64, Vec<(usize, Candidate)>)> = None;
        // Evaluate each bank point as a fixed anchor. Choose the nearest
        // compatible point on each other corridor; fail closed if none fits.
        // Every required cross-line walking leg stays within 600 m.
        for (anchor_index, anchor_choices) in choices.iter().enumerate() {
            for &anchor in anchor_choices {
                let mut assignment = vec![(indices[anchor_index], anchor)];
                for (j, other_choices) in choices.iter().enumerate() {
                    if j == anchor_index {
                        continue;
                    }
                    if let Some(&candidate) = other_choices.iter().find(|&&(_, _, r, c)| {
                        assignment.iter().all(|&(i, (_, _, ar, ac))| {
                            !required[j][indices.iter().position(|&other| other == i).unwrap()]
                                || (r as f64 - ar as f64).hypot(c as f64 - ac as f64)
                                    * grid.reference.cell_m
                                    <= 600.0
                        })
                    }) {
                        assignment.push((indices[j], candidate));
                    } else {
                        break;
                    }
                }
                if assignment.len() == indices.len() {
                    let shift = assignment.iter().map(|(_, c)| c.0).sum::<f64>();
                    if best.as_ref().is_none_or(|(cost, _)| shift < *cost) {
                        best = Some((shift, assignment));
                    }
                }
            }
        }
        let (_, assignment) = best.ok_or_else(|| anyhow::anyhow!(
            "junction group {group} has no common dry bank within the declared search and 600 m transfer envelope; review alignment; members: {}",
            indices.iter().enumerate().map(|(j,&i)| format!("{}@({},{}) {:.1} m, nearest dry candidates {:?}",
                stations[i].line_name,stations[i].row,stations[i].col,stations[i].s_m,
                choices[j].iter().take(3).collect::<Vec<_>>())).collect::<Vec<_>>().join("; ")))?;
        selected.extend(assignment);
    }
    for (i, station) in stations.iter().enumerate() {
        if !selected.contains_key(&i) && grid.excludes_station_for_water(station.row, station.col) {
            selected.insert(i, candidates(station)?[0]);
        }
    }
    let mut changes = Vec::new();
    for (i, (_, new_chainage, row, col)) in selected {
        let station = &mut stations[i];
        if station.row == row && station.col == col && (station.s_m - new_chainage).abs() < 1e-6 {
            continue;
        }
        changes.push(serde_json::json!({"line": station.line_name, "junction_group": station.junction_group,
            "from_cell": [station.row, station.col], "to_cell": [row, col], "from_chainage_m": station.s_m,
            "to_chainage_m": new_chainage, "maximum_shift_m": maximum_shift_m,
            "basis": "dry bank point on the existing corridor within the declared bounded search; existing cross-line transfer legs jointly remain within 600 m; station footprint, bank stability and access remain project releases"}));
        station.row = row;
        station.col = col;
        (station.lat, station.lon) = grid.reference.rc_to_latlon(row, col);
        station.s_m = new_chainage;
        station.demand = grid.demand_at(row, col);
    }
    Ok(changes)
}

/// Fit an ordinary neighbouring stop after a bank move, retaining protected
/// endpoints and interchange positions and the 1.2 km spacing requirement.
pub fn fit_bank_neighbours(
    stations: &mut [osr_routing::station::Station],
    lines: &[osr_routing::topology::Line],
    grid: &Grid,
) -> Result<Vec<serde_json::Value>> {
    let mut changes = Vec::new();
    for line in lines {
        let mut indices: Vec<_> = stations
            .iter()
            .enumerate()
            .filter(|(_, s)| s.line_name == line.name)
            .map(|(i, _)| i)
            .collect();
        indices.sort_by(|&a, &b| stations[a].s_m.total_cmp(&stations[b].s_m));
        let mut route = Vec::new();
        let mut sm = 0.0;
        for (i, &(r, c)) in line.cells.iter().enumerate() {
            if i > 0 {
                let (pr, pc) = line.cells[i - 1];
                sm += (r as f64 - pr as f64).hypot(c as f64 - pc as f64) * grid.reference.cell_m;
            }
            route.push((sm, r, c));
        }
        for position in 0..indices.len().saturating_sub(1) {
            let (a, b) = (indices[position], indices[position + 1]);
            if stations[b].s_m - stations[a].s_m >= 1200.0 {
                continue;
            }
            let movable = |i: usize| {
                stations[i].junction_group.is_none()
                    && stations[i].s_m > 1.0
                    && sm - stations[i].s_m > 1.0
            };
            let index = if movable(a) {
                a
            } else if movable(b) {
                b
            } else {
                continue;
            };
            let old = stations[index].clone();
            let mut candidates: Vec<_> = route
                .iter()
                .copied()
                .filter(|&(s, r, c)| {
                    (s - old.s_m).abs() <= 700.0
                        && !grid.excludes_station_for_water(r, c)
                        && indices.iter().all(|&other| {
                            other == index || (s - stations[other].s_m).abs() >= 1200.0
                        })
                })
                .collect();
            candidates.sort_by(|a, b| {
                (a.0 - old.s_m)
                    .abs()
                    .total_cmp(&(b.0 - old.s_m).abs())
                    .then_with(|| a.0.total_cmp(&b.0))
            });
            if let Some(&(s, r, c)) = candidates.first() {
                let target = &mut stations[index];
                target.row = r;
                target.col = c;
                target.s_m = s;
                (target.lat, target.lon) = grid.reference.rc_to_latlon(r, c);
                target.demand = grid.demand_at(r, c);
                changes.push(serde_json::json!({"kind":"ordinary-neighbour-spacing-fit","line":line.name,"from_cell":[old.row,old.col],"to_cell":[r,c],"from_chainage_m":old.s_m,"to_chainage_m":s,"basis":"Keep bank interchange and endpoints fixed; move an ordinary stop on the same dry corridor within 700 m to preserve minimum spacing. Footprint and access require project release."}));
            }
        }
    }
    Ok(changes)
}

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
            let runs = line["core_runs"]
                .as_array()
                .ok_or_else(|| anyhow::anyhow!("Missing core runs"))?;
            // A retained raster fragment has no analytical radius certificate.
            // Keep its raster curvature and special-product gates after elevating.
            if runs.is_empty()
                || runs.iter().any(|run| {
                    run["geometry_basis"]
                        .as_str()
                        .is_some_and(|basis| basis != "analytical-tangents-and-circular-fillets")
                })
            {
                continue;
            }
            let radius = runs
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
                    if let Some(&radius) = self.analytical_radius.get(line_name) {
                        segment.minimum_curve_radius_m = radius.is_finite().then_some(radius);
                        segment.viaduct_product =
                            Some(elevated_product_for_geometry(radius, 25.0, true));
                        segment.elevated_cost_multiplier = elevated_curve_cost_multiplier(radius);
                    }
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
    fn bank_deviation_needs_a_bounded_project_basis() {
        let directory =
            std::env::temp_dir().join(format!("osr-bank-policy-{}", std::process::id()));
        std::fs::create_dir_all(&directory).unwrap();
        assert_eq!(bank_shift_limit(&directory).unwrap(), 700.0);
        let path = directory.join("station-bank-policy.toml");
        std::fs::write(&path,"schema_version=1\n[platforms]\nmaximum_relocation_m=1200.0\nbasis=\"wide mapped river; bank survey pending\"\n").unwrap();
        assert_eq!(bank_shift_limit(&directory).unwrap(), 1200.0);
        std::fs::write(
            &path,
            "schema_version=1\n[platforms]\nmaximum_relocation_m=1501.0\nbasis=\"too broad\"\n",
        )
        .unwrap();
        assert!(bank_shift_limit(&directory).is_err());
        std::fs::write(
            &path,
            "schema_version=1\n[platforms]\nmaximum_relocation_m=1200.0\nbasis=\"\"\n",
        )
        .unwrap();
        assert!(bank_shift_limit(&directory).is_err());
        std::fs::remove_dir_all(directory).unwrap();
    }
    #[test]
    fn water_platform_moves_on_corridor_and_unbounded_crossing_is_rejected() {
        use osr_routing::{
            raster::GridRef,
            station::Station,
            topology::{Line, LineShape},
        };
        let mut grid = Grid {
            reference: GridRef {
                height: 1,
                width: 5,
                cell_m: 100.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_north: 1.0,
                bbox_west: 0.0,
                bbox_east: 5.0,
                m_per_deg_lat: 100.0,
                m_per_deg_lon: 100.0,
            },
            cost: vec![1.0; 5],
            demand: vec![1.0; 5],
            buildability: vec![1; 5],
            water: Some(vec![0, 100, 100, 0, 0]),
            elevation_m: None,
            terrain_slope_percent: None,
        };
        let mut stations = vec![Station {
            mandatory_crossing: false,
            row: 0,
            col: 1,
            lat: 0.5,
            lon: 1.5,
            anchor_id: None,
            anchor_kind: None,
            anchor_name: None,
            line_name: "L".into(),
            s_m: 100.0,
            demand: 1.0,
            junction_group: None,
        }];
        let lines = vec![Line {
            name: "L".into(),
            shape: LineShape::Radial,
            cells: (0..5).map(|c| (0, c)).collect(),
            anchor_ids: vec![],
        }];
        let original = lines[0].cells.clone();
        let changes = relocate_water_platforms(&mut stations, &lines, &grid).unwrap();
        assert_eq!(changes.len(), 1);
        assert_eq!(
            (stations[0].row, stations[0].col, stations[0].s_m),
            (0, 0, 0.0)
        );
        assert_eq!(lines[0].cells, original);
        assert!(relocate_water_platforms(&mut stations, &lines, &grid)
            .unwrap()
            .is_empty());
        stations[0].col = 1;
        stations[0].s_m = 100.0;
        grid.water = Some(vec![100; 5]);
        assert!(relocate_water_platforms(&mut stations, &lines, &grid).is_err());
    }
    #[test]
    fn interchange_bank_selection_keeps_members_together_and_rejects_separated_shores() {
        use osr_routing::{
            raster::GridRef,
            station::Station,
            topology::{Line, LineShape},
        };
        let mut grid = Grid {
            reference: GridRef {
                height: 2,
                width: 20,
                cell_m: 100.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_north: 2.0,
                bbox_west: 0.0,
                bbox_east: 20.0,
                m_per_deg_lat: 100.0,
                m_per_deg_lon: 100.0,
            },
            cost: vec![1.0; 40],
            demand: vec![1.0; 40],
            buildability: vec![1; 40],
            water: Some(
                (0..40)
                    .map(|i| {
                        if (i < 20 && (5..=12).contains(&i))
                            || (i >= 20 && (8..=15).contains(&(i - 20)))
                        {
                            100
                        } else {
                            0
                        }
                    })
                    .collect(),
            ),
            elevation_m: None,
            terrain_slope_percent: None,
        };
        let lines: Vec<_> = (0..2)
            .map(|r| Line {
                name: format!("L{r}"),
                shape: LineShape::Radial,
                cells: (0..20).map(|c| (r, c)).collect(),
                anchor_ids: vec![],
            })
            .collect();
        let original: Vec<_> = [8, 12]
            .into_iter()
            .enumerate()
            .map(|(r, c)| {
                let (lat, lon) = grid.reference.rc_to_latlon(r, c);
                Station {
                    row: r,
                    col: c,
                    lat,
                    lon,
                    anchor_id: None,
                    anchor_kind: None,
                    anchor_name: None,
                    line_name: format!("L{r}"),
                    s_m: c as f64 * 100.0,
                    demand: 1.0,
                    junction_group: Some(0),
                    mandatory_crossing: false,
                }
            })
            .collect();
        let mut stations = original.clone();
        let changes =
            relocate_water_platforms_with_limit(&mut stations, &lines, &grid, 500.0).unwrap();
        assert_eq!(changes.len(), 2);
        assert!(stations
            .iter()
            .all(|s| !grid.excludes_station_for_water(s.row, s.col)));
        let separation = (stations[0].row as f64 - stations[1].row as f64)
            .hypot(stations[0].col as f64 - stations[1].col as f64)
            * 100.0;
        assert!(separation <= 600.0);
        assert_eq!(
            stations
                .iter()
                .zip(&original)
                .map(|(a, b)| (a.s_m - b.s_m).abs())
                .sum::<f64>(),
            900.0
        );
        assert!(
            relocate_water_platforms_with_limit(&mut stations, &lines, &grid, 500.0)
                .unwrap()
                .is_empty()
        );
        grid.water = Some(
            (0..40)
                .map(|i| if i <= 2 || i >= 37 { 0 } else { 100 })
                .collect(),
        );
        let mut separated = original;
        assert!(relocate_water_platforms_with_limit(&mut separated, &lines, &grid, 700.0).is_err());
        assert_eq!(separated[0].col, 8); // no partial mutation on failure
        assert_eq!(separated[1].col, 12);
        // One multi-change ID can cover two distinct walking transfers.
        // Moving a wet platform must preserve its transfer partner without
        // pulling a distant, already dry transfer onto the same bank point.
        grid.water = Some((0..40).map(|i| if i == 2 { 100 } else { 0 }).collect());
        let mut multi = vec![
            separated[0].clone(),
            separated[1].clone(),
            separated[0].clone(),
            separated[1].clone(),
        ];
        for (station, col) in multi.iter_mut().zip([2, 2, 15, 15]) {
            station.col = col;
            station.s_m = col as f64 * 100.0;
            (station.lat, station.lon) = grid.reference.rc_to_latlon(station.row, col);
        }
        let moves = relocate_water_platforms_with_limit(&mut multi, &lines, &grid, 500.0).unwrap();
        assert_eq!(moves.len(), 1);
        assert_eq!(multi[2].col, 15);
        assert_eq!(multi[3].col, 15);
        assert!(multi
            .iter()
            .all(|s| !grid.excludes_station_for_water(s.row, s.col)));
    }
    #[test]
    fn bank_endpoints_remove_unserved_tails_and_closed_rings_preserve_edges() {
        use osr_routing::{
            raster::GridRef,
            topology::{Line, LineShape},
        };
        let mut grid = Grid {
            reference: GridRef {
                height: 1,
                width: 5,
                cell_m: 100.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_north: 1.0,
                bbox_west: 0.0,
                bbox_east: 5.0,
                m_per_deg_lat: 100.0,
                m_per_deg_lon: 100.0,
            },
            cost: vec![1.0; 5],
            demand: vec![1.0; 5],
            buildability: vec![1; 5],
            water: Some(vec![100, 100, 0, 0, 100]),
            elevation_m: None,
            terrain_slope_percent: None,
        };
        let mut radial = vec![Line {
            name: "radial".into(),
            shape: LineShape::Radial,
            cells: (0..5).map(|c| (0, c)).collect(),
            anchor_ids: vec![],
        }];
        let changes = bank_route_ends(&mut radial, &grid).unwrap();
        assert_eq!(radial[0].cells, vec![(0, 2), (0, 3)]);
        assert_eq!(changes.len(), 2);
        assert_eq!(changes[0]["removed_route_m"], 200.0);
        assert_eq!(changes[1]["removed_route_m"], 100.0);
        let original = vec![(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 0)];
        let mut ring = vec![Line {
            name: "ring".into(),
            shape: LineShape::Ring,
            cells: original.clone(),
            anchor_ids: vec![],
        }];
        bank_route_ends(&mut ring, &grid).unwrap();
        assert_eq!(ring[0].cells.first(), ring[0].cells.last());
        let edges = |cells: &[(usize, usize)]| {
            let mut e = cells.windows(2).map(|p| (p[0], p[1])).collect::<Vec<_>>();
            e.sort();
            e
        };
        assert_eq!(edges(&ring[0].cells), edges(&original));
        assert_eq!(ring[0].cells[0], (0, 2));
        grid.water = Some(vec![100; 5]);
        assert!(bank_route_ends(&mut ring, &grid).is_err());
    }
    #[test]
    fn bank_fit_preserves_interchange_and_endpoint_and_moves_only_ordinary_neighbour() {
        use osr_routing::{
            raster::GridRef,
            station::Station,
            topology::{Line, LineShape},
        };
        let grid = Grid {
            reference: GridRef {
                height: 1,
                width: 61,
                cell_m: 100.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_north: 1.0,
                bbox_west: 0.0,
                bbox_east: 61.0,
                m_per_deg_lat: 100.0,
                m_per_deg_lon: 100.0,
            },
            cost: vec![1.0; 61],
            demand: vec![1.0; 61],
            buildability: vec![1; 61],
            water: None,
            elevation_m: None,
            terrain_slope_percent: None,
        };
        let make = |col, group| Station {
            row: 0,
            col,
            lat: 0.5,
            lon: col as f64 + 0.5,
            anchor_id: None,
            anchor_kind: None,
            anchor_name: None,
            line_name: "L".into(),
            s_m: col as f64 * 100.0,
            demand: 1.0,
            junction_group: group,
            mandatory_crossing: false,
        };
        let mut stations = vec![
            make(0, None),
            make(17, None),
            make(28, Some(0)),
            make(60, None),
        ];
        let lines = vec![Line {
            name: "L".into(),
            shape: LineShape::Radial,
            cells: (0..61).map(|c| (0, c)).collect(),
            anchor_ids: vec![],
        }];
        let changes = fit_bank_neighbours(&mut stations, &lines, &grid).unwrap();
        assert_eq!(changes.len(), 1);
        assert_eq!(
            stations.iter().map(|s| s.s_m).collect::<Vec<_>>(),
            vec![0.0, 1600.0, 2800.0, 6000.0]
        );
        assert_eq!(stations[2].junction_group, Some(0));
        assert_eq!(stations[1].col, 16);
    }
    #[test]
    fn retained_raster_run_does_not_acquire_an_analytical_radius() {
        let directory =
            std::env::temp_dir().join(format!("osr-policy-review-{}", std::process::id()));
        std::fs::create_dir_all(directory.join("engineering/alignment")).unwrap();
        std::fs::write(
            directory.join("alignment-policy.toml"),
            "[core]\nsouth=0.0\nnorth=1.0\nwest=0.0\neast=1.0\n",
        )
        .unwrap();
        std::fs::write(directory.join("engineering/alignment/core-realignment.json"),
            r#"{"lines":[{"line":"retained","core_runs":[{"geometry_basis":"retained-raster-requires-geometry-review","controls":[]}]},{"line":"detoured","core_runs":[{"geometry_basis":"superseded-by-water-constrained-route-requires-geometry-review","controls":[],"superseded_analytical_controls":[{"radius_m":1000.0}]}]},{"line":"arc","core_runs":[{"controls":[{"radius_m":1000.0}]}]}]}"#).unwrap();
        let policy = Policy::load(&directory).unwrap().unwrap();
        assert!(!policy.analytical_radius.contains_key("retained"));
        assert!(!policy.analytical_radius.contains_key("detoured"));
        assert_eq!(policy.analytical_radius["arc"], 1000.0);
        std::fs::remove_dir_all(directory).unwrap();
    }
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
