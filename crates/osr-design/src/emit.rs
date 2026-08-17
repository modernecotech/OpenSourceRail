//! Emit design.toml + corridor.geojson + design-quality.yaml + stations.json.
//!
//! The design.toml we emit is a *superset-ready* document: every station
//! carries lat/lon + anchor metadata; every line carries its cell-space
//! polyline. The recipe in lib/recipes/city-to-design.toml then
//! layers in archetype / kit / profile selections when the Python
//! generator fuses this with the templates.
//!
//! This file never calls anyhow::Error types that would leak solver-side
//! state — all output is purely a projection of the bundle + lines.

use std::collections::BTreeMap;
use std::fs;
use std::io::Write;
use std::path::Path;
use std::sync::OnceLock;

use anyhow::Result;
use osr_routing::civil::{CivilClass, CivilSegment};
use osr_routing::raster::RasterBundle;
use osr_routing::station::Station;
use osr_routing::topology::{hub_cell, Line};
use serde::{Deserialize, Serialize};

#[allow(clippy::too_many_arguments)] // Stable emitter boundary mirrors artifact inputs.
pub fn write_all(
    out_dir: &Path,
    slug: &str,
    country: &str,
    climate: Option<&str>,
    profile: Option<&str>,
    population: u64,
    bundle: &RasterBundle,
    lines: &[Line],
    stations: &[Station],
    civil_per_line: &[Vec<CivilSegment>],
) -> Result<()> {
    // Take an owned, mutable copy of the civil mix so the
    // elevated-junction pass can splice 1 km Elevated sections in
    // around any all-at-grade interchange. Other emitters then read
    // the post-pass classification.
    let mut civil_mut: Vec<Vec<CivilSegment>> = civil_per_line.to_vec();
    let elevated_junctions = enforce_elevated_junctions(bundle, lines, stations, &mut civil_mut);
    eprintln!(
        "elevated-junction upgrades: {} junction(s) (${:.1} M / EUR {:.1} M premium)",
        elevated_junctions.len(),
        (elevated_junctions.len() as f64) * junction_premium_usd() / 1_000_000.0,
        (elevated_junctions.len() as f64) * junction_premium_eur() / 1_000_000.0
    );

    write_design_toml(
        out_dir,
        slug,
        country,
        climate,
        profile,
        population,
        bundle,
        lines,
        stations,
        &civil_mut,
        &elevated_junctions,
    )?;
    write_corridor_geojson(out_dir, slug, bundle, lines, stations)?;
    write_stations_json(out_dir, slug, stations)?;
    write_quality_yaml(out_dir, slug, bundle, lines, stations, &civil_mut)?;
    Ok(())
}

// ---- Elevated-junction enforcement -----------------------------------
//
// At every interchange where *all* crossing lines are AtGrade, one of
// the lines must lift to clear the others. This converts \xb1500 m
// (50 cells \xd7 20 m = 1 km total) of that line's civil class to
// Elevated. We pick the higher-numbered line as the one to lift, so the
// "primary" line stays at-grade where possible and the choice is stable
// across runs. If any line through the junction is already Elevated /
// Bridge, no upgrade is needed.

const JUNCTION_HALF_WINDOW_CELLS: usize = 25;

#[derive(Debug, Clone)]
pub(crate) struct ElevatedJunction {
    pub group_id: u32,
    pub elevated_line: String,
    pub lat: f64,
    pub lon: f64,
}

fn enforce_elevated_junctions(
    bundle: &RasterBundle,
    lines: &[Line],
    stations: &[Station],
    civil_per_line: &mut [Vec<CivilSegment>],
) -> Vec<ElevatedJunction> {
    use std::collections::BTreeMap;

    // Collect station indices by junction_group.
    let mut groups: BTreeMap<u32, Vec<usize>> = BTreeMap::new();
    for (i, s) in stations.iter().enumerate() {
        if let Some(g) = s.junction_group {
            groups.entry(g).or_default().push(i);
        }
    }

    let line_index: BTreeMap<&str, usize> = lines
        .iter()
        .enumerate()
        .map(|(i, l)| (l.name.as_str(), i))
        .collect();

    let mut out = Vec::new();
    for (gid, idxs) in &groups {
        // Distinct line names participating in this junction.
        let mut line_names: Vec<&str> = idxs
            .iter()
            .map(|&i| stations[i].line_name.as_str())
            .collect();
        line_names.sort();
        line_names.dedup();
        if line_names.len() < 2 {
            continue; // not actually a multi-line junction
        }

        // Centroid of the junction (already snapped — any station works).
        let lat = stations[idxs[0]].lat;
        let lon = stations[idxs[0]].lon;

        // For each line at the junction, find the civil class at the
        // closest cell. If any line is non-at-grade, no upgrade needed.
        let mut all_at_grade = true;
        for &lname in &line_names {
            let li = match line_index.get(lname) {
                Some(li) => *li,
                None => continue,
            };
            let line = &lines[li];
            let segs = &civil_per_line[li];
            let cell_idx = nearest_cell_idx_to_latlon(bundle, line, lat, lon);
            let class = class_at(segs, cell_idx);
            if class != CivilClass::AtGrade {
                all_at_grade = false;
                break;
            }
        }
        if !all_at_grade {
            continue;
        }

        // Pick the highest-numbered line at this junction to lift.
        let mut sorted_names = line_names.clone();
        sorted_names.sort();
        let lift_name = *sorted_names.last().unwrap();
        let lift_idx = line_index[lift_name];
        let lift_line = &lines[lift_idx];
        let centre_idx = nearest_cell_idx_to_latlon(bundle, lift_line, lat, lon);
        let half = JUNCTION_HALF_WINDOW_CELLS;
        let from_idx = centre_idx.saturating_sub(half);
        let to_idx = (centre_idx + half).min(lift_line.cells.len().saturating_sub(1));

        // Reclassify [from_idx, to_idx] inclusive on the lift line.
        let lift_segs = &mut civil_per_line[lift_idx];
        *lift_segs = reclass_window(
            bundle,
            lift_line,
            lift_segs,
            from_idx,
            to_idx,
            CivilClass::Elevated,
        );

        out.push(ElevatedJunction {
            group_id: *gid,
            elevated_line: lift_name.to_string(),
            lat,
            lon,
        });
    }
    out
}

/// Find the cell index along `line.cells` nearest to (lat, lon).
fn nearest_cell_idx_to_latlon(bundle: &RasterBundle, line: &Line, lat: f64, lon: f64) -> usize {
    let mut best_idx = 0;
    let mut best_d2 = f64::INFINITY;
    for (i, &(r, c)) in line.cells.iter().enumerate() {
        let (clat, clon) = bundle.grid.reference.rc_to_latlon(r, c);
        let dlat = clat - lat;
        let dlon = clon - lon;
        let d2 = dlat * dlat + dlon * dlon;
        if d2 < best_d2 {
            best_d2 = d2;
            best_idx = i;
        }
    }
    best_idx
}

fn class_at(segs: &[CivilSegment], cell_idx: usize) -> CivilClass {
    for s in segs {
        if cell_idx >= s.from_idx && cell_idx <= s.to_idx {
            return s.class;
        }
    }
    CivilClass::AtGrade
}

/// Force every cell in [from_idx, to_idx] on `line` to `target_class`,
/// then re-collapse runs to keep the segment list canonical.
fn reclass_window(
    bundle: &RasterBundle,
    line: &Line,
    segs: &[CivilSegment],
    from_idx: usize,
    to_idx: usize,
    target: CivilClass,
) -> Vec<CivilSegment> {
    let n = line.cells.len();
    if n == 0 {
        return segs.to_vec();
    }
    // Per-cell class — start by reading the existing segment table.
    let mut classes: Vec<CivilClass> = vec![CivilClass::AtGrade; n];
    for s in segs {
        for class in classes
            .iter_mut()
            .take(s.to_idx.min(n - 1) + 1)
            .skip(s.from_idx)
        {
            *class = s.class;
        }
    }
    for class in classes
        .iter_mut()
        .take(to_idx.min(n - 1) + 1)
        .skip(from_idx)
    {
        *class = target;
    }
    // Re-collapse runs.
    let mut out: Vec<CivilSegment> = Vec::new();
    let mut run_start = 0;
    for i in 1..=n {
        if i == n || classes[i] != classes[run_start] {
            // Assign the edge into the next run to the preceding span.
            // This matches the emitted half-open chainage boundaries and
            // ensures every route edge contributes to civil quantities.
            let length_end = if i < n { i + 1 } else { i };
            let length_m = segment_length_m(bundle, &line.cells[run_start..length_end]);
            out.push(CivilSegment {
                class: classes[run_start],
                from_idx: run_start,
                to_idx: i - 1,
                length_m,
            });
            run_start = i;
        }
    }
    out
}

fn segment_length_m(bundle: &RasterBundle, cells: &[(usize, usize)]) -> f64 {
    if cells.len() < 2 {
        return 0.0;
    }
    let cell_m = bundle.grid.reference.cell_m;
    let mut total = 0.0;
    for pair in cells.windows(2) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        total += (dr * dr + dc * dc).sqrt() * cell_m;
    }
    total
}

// ---- design.toml -----------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn write_design_toml(
    out_dir: &Path,
    slug: &str,
    country: &str,
    climate: Option<&str>,
    profile: Option<&str>,
    population: u64,
    bundle: &RasterBundle,
    lines: &[Line],
    stations: &[Station],
    civil_per_line: &[Vec<CivilSegment>],
    elevated_junctions: &[ElevatedJunction],
) -> Result<()> {
    let mut out = String::new();
    out.push_str("# Auto-generated by osr-design from real OSM data.\n");
    out.push_str("# Do not hand-edit without re-running the recipe; changes will be\n");
    out.push_str("# overwritten on the next pipeline run. Override via\n");
    out.push_str("# lib/recipes/city-to-design.toml rule additions instead.\n\n");

    out.push_str("[city]\n");
    out.push_str(&format!("slug            = \"{slug}\"\n"));
    out.push_str(&format!("country         = \"{country}\"\n"));
    out.push_str(&format!("population      = {population}\n"));
    out.push_str(&format!(
        "bbox            = {{ south = {}, west = {}, north = {}, east = {} }}\n",
        bundle.grid.reference.bbox_south,
        bundle.grid.reference.bbox_west,
        bundle.grid.reference.bbox_north,
        bundle.grid.reference.bbox_east,
    ));
    let (hub_row, hub_col) = hub_cell(&bundle.grid);
    let (hub_lat, hub_lon) = bundle.grid.reference.rc_to_latlon(hub_row, hub_col);
    out.push_str(&format!("centroid_lat    = {hub_lat}\n"));
    out.push_str(&format!("centroid_lon    = {hub_lon}\n"));
    out.push('\n');

    out.push_str("[climate]\n");
    let climate_preset = climate.unwrap_or("temperate-continental");
    out.push_str(&format!("preset          = \"{climate_preset}\"\n\n"));

    if let Some(p) = profile {
        out.push_str("[composition]\n");
        out.push_str(&format!("profile         = \"{p}\"\n\n"));
    }

    // This is part of the authoritative design, not an implicit simulator
    // default.  Every downstream scenario therefore carries the same
    // deterministic response to delivered charging energy: preserve the
    // three-minute peaks and widen only off-peak service as pack margin falls.
    out.push_str("[operations.energy_adaptive_service]\n");
    out.push_str("enabled                     = true\n");
    out.push_str("normal_service_soc          = 0.40\n");
    out.push_str("maximum_headway_multiplier  = 3.0\n");
    out.push_str("protected_peak_headway_min  = 3\n\n");

    // The original 3.0 kWh/car-km value is retained as an auditable
    // conservative reference.  The emitted operating model applies the
    // specified PMSM + SiC drivetrain as a single explicit factor, rather
    // than hiding the improvement in a simulator-only constant.
    out.push_str("[operations.traction_energy]\n");
    out.push_str("reference_energy_kwh_per_car_km = 3.0\n");
    out.push_str("modern_drive_energy_factor      = 0.80\n");
    out.push_str("nominal_energy_kwh_per_car_km   = 2.4\n");
    out.push_str("technology                      = \"PMSM traction motors + SiC inverters\"\n\n");

    // Charging stops on radial services exchange energy for a longer dwell.
    // Halts without chargers keep the short standard dwell, while terminal
    // and depot turnbacks retain their already-longer operating allowances.
    out.push_str("[operations.radial_service]\n");
    out.push_str("minimum_charging_dwell_seconds = 120\n\n");

    out.push_str("[operations.ring_service]\n");
    out.push_str("station_spacing_multiplier  = 1.0\n");
    // Ring and radial dwells share a two-minute lower bound. Each line also
    // carries a calculated charging_dwell_seconds value based on its energy
    // per traversal and the aggregate power of its own charging platforms.
    out.push_str("opportunity_charging_required = true\n");
    out.push_str("minimum_dwell_seconds        = 120\n");
    out.push_str("minimum_traversal_energy_margin = 1.10\n");
    out.push_str("maximum_charging_dwell_seconds = 600\n\n");
    out.push_str("peak_headway_min             = 6\n");
    out.push_str("off_peak_headway_min         = 12\n");
    out.push_str("late_headway_min             = 24\n\n");

    // Rolling-stock family + geometry preset per RFC 0008 §5 / RFC 0009 §10.
    // One family applies consist-wide across every line; the auto-gen
    // does not pick different families for different lines in the same
    // city (RFC 0008 rollout §7 keeps a single-family bet per city).
    let family = family_for_population(population);
    let geometry = geometry_for_family(family);
    let consist_length_m = family_length_m(family);

    // Precompute station archetypes: terminal (line endpoints on
    // radial lines), interchange (cross-line stations within 200 m),
    // and otherwise demand-based major/standard/halt per RFC 0010 §3.
    // Junctions reclassified by the elevated-junction pass are promoted
    // to "interchange-elevated".
    let elevated_groups: std::collections::BTreeSet<u32> =
        elevated_junctions.iter().map(|j| j.group_id).collect();
    let archetypes = compute_archetypes(lines, stations, &elevated_groups);

    // One [[lines]] block per synthesized line.
    for line in lines {
        let length_m = line_length_m(bundle, line);
        let charging_dwell_seconds = planned_charging_dwell_seconds(
            length_m,
            family,
            line.name.as_str(),
            stations,
            &archetypes,
        );
        out.push_str("[[lines]]\n");
        out.push_str(&format!("name            = \"{}\"\n", line.name));
        out.push_str(&format!(
            "shape           = \"{}\"\n",
            match line.shape {
                osr_routing::topology::LineShape::Radial => "radial",
                osr_routing::topology::LineShape::Ring => "ring",
            }
        ));
        out.push_str(&format!("length_m        = {length_m:.1}\n"));
        if matches!(line.shape, osr_routing::topology::LineShape::Ring) {
            let last_platform_m = stations
                .iter()
                .filter(|station| station.line_name == line.name)
                .map(|station| station.s_m)
                .fold(0.0_f64, f64::max);
            let wrap_length_m = (length_m - last_platform_m).round().max(1.0) as u64;
            out.push_str(&format!("ring_wrap_length_m = {wrap_length_m}\n"));
        }
        out.push_str(&format!("rolling_stock   = \"{family}\"\n"));
        out.push_str(&format!("geometry        = \"{geometry}\"\n\n"));
        out.push_str(&format!(
            "charging_dwell_seconds = {charging_dwell_seconds}\n\n"
        ));
    }

    // Persist the planner's per-line civil classification. Earlier
    // design.toml files retained only network-wide cost totals, which
    // meant downstream OSR-ALN exports could not reproduce where the
    // alignment changes between at-grade, elevated, and bridge work.
    // Boundaries use the same cell-space chainage as stations and line
    // lengths. Each row is half-open [from, to), and the last row ends
    // exactly at the line length so consumers can enforce full coverage.
    for (line, segments) in lines.iter().zip(civil_per_line) {
        let length_m = line_length_m(bundle, line);
        let cell_m = bundle.grid.reference.cell_m;
        for (index, segment) in segments.iter().enumerate() {
            let from_station_m = cumulative_cell_chainage_m(&line.cells, segment.from_idx, cell_m);
            let to_station_m = if index + 1 == segments.len() {
                length_m
            } else {
                cumulative_cell_chainage_m(&line.cells, segments[index + 1].from_idx, cell_m)
            };
            if to_station_m <= from_station_m {
                continue;
            }
            let class = match segment.class {
                CivilClass::AtGrade => "at-grade",
                CivilClass::Elevated => "elevated",
                CivilClass::Bridge => "bridge",
            };
            out.push_str("[[civil_segments]]\n");
            out.push_str(&format!("line            = \"{}\"\n", line.name));
            out.push_str(&format!("from_station_m  = {from_station_m:.1}\n"));
            out.push_str(&format!("to_station_m    = {to_station_m:.1}\n"));
            out.push_str(&format!("class           = \"{class}\"\n\n"));
        }
    }

    // Stations — the critical output. Every one has lat/lon.
    for (idx, s) in stations.iter().enumerate() {
        let sid = station_id(s);
        let archetype = archetypes[idx];
        let clearance_m = if archetype == "halt" { 6 } else { 10 };
        let platform_length_m = consist_length_m + clearance_m as f32;

        out.push_str("[[stations]]\n");
        out.push_str(&format!("id              = \"{sid}\"\n"));
        out.push_str(&format!("line            = \"{}\"\n", s.line_name));
        out.push_str(&format!("lat             = {}\n", s.lat));
        out.push_str(&format!("lon             = {}\n", s.lon));
        out.push_str(&format!("s_m             = {:.1}\n", s.s_m));
        if let Some(k) = s.anchor_kind.as_deref() {
            out.push_str(&format!("anchor_kind     = \"{k}\"\n"));
        }
        if let Some(n) = s.anchor_name.as_deref() {
            out.push_str(&format!(
                "anchor_name     = \"{}\"\n",
                escape_toml_string(n)
            ));
        }
        out.push_str(&format!("archetype       = \"{archetype}\"\n"));
        out.push_str(&format!("platform_length_m = {:.1}\n", platform_length_m));
        if let Some(g) = s.junction_group {
            out.push_str(&format!("junction_group  = {g}\n"));
        }
        out.push('\n');
    }

    // Interchange complexes are first-class design objects. Routing and
    // simulation retain one platform record per participating line, while
    // downstream GIS and maps use this single centroid record as the public
    // station symbol. BTreeMap ordering keeps the output byte-deterministic.
    let mut interchange_groups: BTreeMap<u32, Vec<&Station>> = BTreeMap::new();
    for station in stations {
        if let Some(group) = station.junction_group {
            interchange_groups.entry(group).or_default().push(station);
        }
    }
    for (group, members) in interchange_groups {
        let mut line_names: Vec<&str> = members
            .iter()
            .map(|station| station.line_name.as_str())
            .collect();
        line_names.sort_unstable();
        line_names.dedup();
        if line_names.len() < 2 {
            continue;
        }
        let lat = members.iter().map(|station| station.lat).sum::<f64>() / members.len() as f64;
        let lon = members.iter().map(|station| station.lon).sum::<f64>() / members.len() as f64;
        let mut platform_ids: Vec<String> =
            members.iter().map(|station| station_id(station)).collect();
        platform_ids.sort_unstable();

        out.push_str("[[interchanges]]\n");
        out.push_str(&format!("id              = \"interchange-{group:03}\"\n"));
        out.push_str(&format!("junction_group  = {group}\n"));
        out.push_str(&format!("lat             = {lat}\n"));
        out.push_str(&format!("lon             = {lon}\n"));
        out.push_str("lines           = [");
        for (index, line_name) in line_names.iter().enumerate() {
            if index > 0 {
                out.push_str(", ");
            }
            out.push_str(&format!("\"{}\"", escape_toml_string(line_name)));
        }
        out.push_str("]\n");
        out.push_str("platforms       = [");
        for (index, platform_id) in platform_ids.iter().enumerate() {
            if index > 0 {
                out.push_str(", ");
            }
            out.push_str(&format!("\"{}\"", escape_toml_string(platform_id)));
        }
        out.push_str("]\n\n");
    }

    // Depots — per RFC 0014 §8. The farthest-terminal station becomes the
    // maintenance-focused `main-heavy`. Healthy sets stable at powered
    // passenger stations, so ordinary terminals and rings do not emit
    // separate layup depots.
    let depot_blocks = compute_depots(lines, stations, &archetypes, family);
    if !depot_blocks.is_empty() {
        out.push_str("# [[depots]] — maintenance/defect facilities per RFC 0014; healthy sets stable at powered stations.\n");
        for d in &depot_blocks {
            out.push_str("[[depots]]\n");
            out.push_str(&format!("station      = \"{}\"\n", d.station_id));
            out.push_str(&format!("archetype    = \"{}\"\n", d.archetype));
            out.push_str(&format!("fleet_stalls = {}\n", d.fleet_stalls));
            out.push('\n');
        }
    }

    // Switches — per RFC 0012 §9. One turnback at every terminal; a
    // depot fan (one per stall pair, 1:9) at every depot-terminal.
    let switches = compute_switches(stations, &archetypes, &depot_blocks);
    if !switches.is_empty() {
        out.push_str("# switches — turnbacks at terminals + depot fans per RFC 0012 §9.\n");
        out.push_str("switches = [\n");
        for sw in &switches {
            out.push_str(&format!(
                "  {{ id = \"{}\", kit = \"{}\", station = \"{}\", side = \"{}\" }},\n",
                sw.id, sw.kit, sw.station_id, sw.side,
            ));
        }
        out.push_str("]\n\n");
    }

    // Junctions where one line had to be elevated to clear the other —
    // these get the configured elevated-interchange premium per junction
    // (1 km of elevation
    // including approach + departure, plus the multi-level station
    // structure) on top of the per-segment civil cost the elevated
    // window already incurs.
    if !elevated_junctions.is_empty() {
        out.push_str("# [[junctions]] — elevated-junction upgrades for cross-at-grade\n");
        out.push_str("# interchanges, per RFC 0011 §8 follow-up. Each adds the 1 km\n");
        out.push_str("# Elevated section already visible in the civil mix above.\n");
        for j in elevated_junctions {
            out.push_str("[[junctions]]\n");
            out.push_str(&format!("group_id        = {}\n", j.group_id));
            out.push_str(&format!("elevated_line   = \"{}\"\n", j.elevated_line));
            out.push_str(&format!("lat             = {}\n", j.lat));
            out.push_str(&format!("lon             = {}\n", j.lon));
            out.push_str(&format!(
                "premium_usd     = {:.0}\n",
                junction_premium_usd()
            ));
            out.push_str(&format!(
                "premium_eur     = {:.0}\n",
                junction_premium_eur()
            ));
            out.push('\n');
        }
    }

    // Fleets — per-line revenue / spare / cold-reserve counts so the
    // python README emitter and the sim scenario emitter can read fleet
    // sizing from design.toml without re-deriving it. Sized per
    // RFC 0014 §4: radial peak from round-trip / 3 min headway; ring peak
    // from one complete loop / 6 min headway; depot service is
    // scheduled only in lower-frequency windows and needs no dedicated fleet;
    // spare = peak/10 (min 1), and cold-reserve = 1 per line.
    out.push_str("# [[fleets]] — per-line fleet sizing per RFC 0014 §4.\n");
    let mut fleet_total_trainsets: u32 = 0;
    for line in lines {
        let len_m = line_cells_length_m(line);
        let station_count = line_station_count(line.name.as_str(), stations);
        let charging_station_count =
            line_charging_station_count(line.name.as_str(), stations, &archetypes);
        let charging_dwell_seconds = planned_charging_dwell_seconds(
            len_m,
            family,
            line.name.as_str(),
            stations,
            &archetypes,
        );
        let peak = peak_revenue_trainsets(
            len_m,
            family,
            matches!(line.shape, osr_routing::topology::LineShape::Ring),
            station_count,
            charging_station_count,
            charging_dwell_seconds,
        );
        let service_rotation = fleet_service_rotation();
        let spare = fleet_spare(peak);
        let reserve = fleet_cold_reserve();
        let total = peak + service_rotation + spare + reserve;
        fleet_total_trainsets += total;
        out.push_str("[[fleets]]\n");
        out.push_str(&format!("line               = \"{}\"\n", line.name));
        out.push_str(&format!("peak_count         = {peak}\n"));
        out.push_str(&format!("service_rotation_count = {service_rotation}\n"));
        out.push_str(&format!("spare_count        = {spare}\n"));
        out.push_str(&format!("cold_reserve_count = {reserve}\n"));
        out.push_str(&format!("trainset_count     = {total}\n\n"));
    }

    // Costs — full planning-grade CAPEX stack per RFC 0011 §9: civil
    // works (USD/km × civil mix) + stations (RFC 0010 archetype catalogue)
    // + depots (RFC 0014 archetype catalogue) + rolling stock (RFC 0008
    // delivered family acquisition cost × fleet) + systems (residual wayside +
    // station/depot charging microgrids)
    // + 7 % EPC overhead. `country-costs.toml` scales the totals
    // downstream; the base figure goes in design.toml so the operator
    // has a one-number headline when reviewing the output.
    let costs = compute_costs(
        civil_per_line,
        &archetypes,
        &depot_blocks,
        elevated_junctions.len(),
        fleet_total_trainsets,
        family,
    );
    out.push_str("# [costs] — RFC 0011 §9 planning-grade CAPEX (USD\n");
    out.push_str("# direct-procurement planning basis). country-costs.toml applies\n");
    out.push_str("# the per-country labour/material multiplier downstream.\n");
    out.push_str("[schema]\n");
    out.push_str("version = 2\n");
    out.push('\n');
    out.push_str("[costs]\n");
    out.push_str(&format!(
        "currency_basis      = \"{}\"\n",
        escape_toml_string(cost_config().schema.currency_basis.as_str())
    ));
    out.push_str(&format!("usd_to_eur          = {:.2}\n", usd_to_eur()));
    out.push_str("# Civil works (USD/km x civil mix; EUR mirror at usd_to_eur).\n");
    out.push_str(&format!(
        "at_grade_usd         = {:.0}\n",
        costs.at_grade_usd
    ));
    out.push_str(&format!(
        "at_grade_eur         = {:.0}\n",
        costs.at_grade_eur
    ));
    out.push_str(&format!(
        "elevated_usd         = {:.0}\n",
        costs.elevated_usd
    ));
    out.push_str(&format!(
        "elevated_eur         = {:.0}\n",
        costs.elevated_eur
    ));
    out.push_str(&format!("bridge_usd           = {:.0}\n", costs.bridge_usd));
    out.push_str(&format!("bridge_eur           = {:.0}\n", costs.bridge_eur));
    out.push_str(&format!(
        "junction_premium_usd = {:.0}  # ${:.1} M per elevated interchange.\n",
        costs.junction_premium_usd,
        junction_premium_usd() / 1_000_000.0
    ));
    out.push_str(&format!(
        "junction_premium_eur = {:.0}  # EUR {:.1} M per elevated interchange.\n",
        costs.junction_premium_eur,
        junction_premium_eur() / 1_000_000.0
    ));
    out.push_str(&format!(
        "civil_subtotal_usd   = {:.0}\n",
        costs.civil_subtotal_usd
    ));
    out.push_str(&format!(
        "civil_subtotal_eur   = {:.0}\n",
        costs.civil_subtotal_eur
    ));
    out.push_str("# Stations (RFC 0010 archetype catalogue).\n");
    out.push_str(&format!(
        "stations_usd         = {:.0}\n",
        costs.stations_usd
    ));
    out.push_str(&format!(
        "stations_eur         = {:.0}\n",
        costs.stations_eur
    ));
    out.push_str("# Depots (RFC 0014 archetype catalogue).\n");
    out.push_str(&format!("depots_usd           = {:.0}\n", costs.depots_usd));
    out.push_str(&format!("depots_eur           = {:.0}\n", costs.depots_eur));
    out.push_str("# Rolling stock (RFC 0008 family × fleet count; local-owner production unit).\n");
    out.push_str(&format!(
        "rolling_stock_usd    = {:.0}\n",
        costs.rolling_stock_usd
    ));
    out.push_str(&format!(
        "rolling_stock_eur    = {:.0}\n",
        costs.rolling_stock_eur
    ));
    out.push_str("# Shared national railway production plant is excluded from city CAPEX.\n");
    out.push_str(&format!(
        "production_plant_usd = {:.0}\n",
        costs.production_plant_usd
    ));
    out.push_str(&format!(
        "production_plant_eur = {:.0}\n",
        costs.production_plant_eur
    ));
    out.push_str(
        "# Systems: residual train-control wayside + station/depot charging microgrids.\n",
    );
    out.push_str(&format!(
        "signalling_usd       = {:.0}\n",
        costs.signalling_usd
    ));
    out.push_str(&format!(
        "signalling_eur       = {:.0}\n",
        costs.signalling_eur
    ));
    out.push_str(&format!(
        "charging_microgrid_usd = {:.0}\n",
        costs.charging_microgrid_usd
    ));
    out.push_str(&format!(
        "charging_microgrid_eur = {:.0}\n",
        costs.charging_microgrid_eur
    ));
    out.push_str("# EPC integration + project management (7 % of subtotal).\n");
    out.push_str(&format!(
        "epc_overhead_usd     = {:.0}\n",
        costs.epc_overhead_usd
    ));
    out.push_str(&format!(
        "epc_overhead_eur     = {:.0}\n",
        costs.epc_overhead_eur
    ));
    out.push_str(&format!(
        "total_usd            = {:.0}  # base CAPEX before timetable-sized dedicated solar\n",
        costs.total_usd
    ));
    out.push_str(&format!(
        "total_eur            = {:.0}  # base CAPEX before timetable-sized dedicated solar\n",
        costs.total_eur
    ));

    // Keep the commodity 800 V architecture visible inside every generated
    // city's cost record. These values reconcile the rolling-stock and
    // charging-site planning units; they are audit components already
    // included in CAPEX and must never be added a second time.
    let onboard = &cost_config().trainset_800v_core_electrical_usd;
    let station_module = &cost_config().station_800v_module_usd;
    let car_count = family_car_count(family);
    let core_electrical_per_trainset = onboard.core_electrical_total_per_car * f64::from(car_count);
    let fleet_core_electrical = core_electrical_per_trainset * f64::from(fleet_total_trainsets);
    out.push_str("\n[costs.technology_basis]\n");
    out.push_str("cost_treatment = \"included in planning units; do not add again\"\n");
    out.push_str(&format!(
        "onboard_architecture = \"{}\"\n",
        escape_toml_string(onboard.architecture.as_str())
    ));
    out.push_str(&format!("car_count = {car_count}\n"));
    out.push_str(&format!(
        "gross_battery_kwh_per_car = {:.0}\n",
        onboard.gross_battery_kwh_per_car
    ));
    out.push_str(&format!(
        "traction_battery_system_usd_per_car = {:.2}\n",
        onboard.traction_battery_system_per_car
    ));
    out.push_str(&format!(
        "motor_controller_sets_per_car = {}\n",
        onboard.motor_controller_sets_per_car
    ));
    out.push_str(&format!(
        "motor_controller_set_usd = {:.0}\n",
        onboard.motor_controller_set
    ));
    out.push_str(&format!(
        "hv_distribution_usd_per_car = {:.2}\n",
        onboard.hv_distribution_per_car
    ));
    out.push_str(&format!(
        "lv_dc_dc_usd_per_car = {:.0}\n",
        onboard.lv_dc_dc_per_car
    ));
    out.push_str(&format!(
        "roof_pv_mppt_usd_per_car = {:.0}\n",
        onboard.roof_pv_mppt_per_car
    ));
    out.push_str(&format!(
        "core_electrical_usd_per_car = {:.0}\n",
        onboard.core_electrical_total_per_car
    ));
    out.push_str(&format!(
        "core_electrical_usd_per_trainset = {:.0}\n",
        core_electrical_per_trainset
    ));
    out.push_str(&format!(
        "fleet_core_electrical_usd = {:.0}\n",
        fleet_core_electrical
    ));
    out.push_str(&format!(
        "station_architecture = \"{}\"\n",
        escape_toml_string(station_module.architecture.as_str())
    ));
    out.push_str(&format!(
        "stationary_lfp_500kwh_usd = {:.0}\n",
        station_module.stationary_lfp_500kwh
    ));
    out.push_str(&format!(
        "station_dcdc_500kw_usd = {:.0}\n",
        station_module.dcdc_500kw
    ));
    out.push_str(&format!(
        "station_contact_protection_control_usd = {:.0}\n",
        station_module.contact_protection_control
    ));
    out.push_str(&format!(
        "station_equipment_total_usd = {:.0}\n",
        station_module.equipment_total
    ));
    out.push_str(&format!(
        "normal_integrated_charging_site_usd = {:.0}\n",
        station_module.normal_integrated_site
    ));
    out.push_str(&format!(
        "station_charging_cabinet_count = {}\n",
        charging_cabinet_count(family)
    ));

    let path = out_dir.join("design.toml");
    fs::write(&path, out)?;
    Ok(())
}

// ---- RFC 0014 §8 depot-block emission --------------------------------------

#[derive(Debug, Clone)]
struct DepotBlock {
    station_id: String,
    archetype: &'static str,
    fleet_stalls: u32,
}

/// Derive depot blocks from the station archetypes. Rules:
/// - A `depot-terminal` emits the city's maintenance-focused `main-heavy`.
/// - Other terminals and rings use powered passenger stations for healthy
///   overnight stabling and do not emit a parking depot.
/// - A ring-only city gets one `main-heavy` at its first station.
/// - Workshop/inspection bays = max(4, ceil(total fleet × 0.15)); this is
///   maintenance concurrency, not one parking stall per trainset.
fn compute_depots(
    lines: &[Line],
    stations: &[Station],
    archetypes: &[&'static str],
    family: &str,
) -> Vec<DepotBlock> {
    // Precompute each line's fleet sizing from length.
    let mut fleet_by_line: std::collections::BTreeMap<&str, u32> =
        std::collections::BTreeMap::new();
    for line in lines {
        let len_m = line_cells_length_m(line);
        let station_count = line_station_count(line.name.as_str(), stations);
        let charging_station_count =
            line_charging_station_count(line.name.as_str(), stations, archetypes);
        let charging_dwell_seconds =
            planned_charging_dwell_seconds(len_m, family, line.name.as_str(), stations, archetypes);
        fleet_by_line.insert(
            line.name.as_str(),
            fleet_total(peak_revenue_trainsets(
                len_m,
                family,
                matches!(line.shape, osr_routing::topology::LineShape::Ring),
                station_count,
                charging_station_count,
                charging_dwell_seconds,
            )),
        );
    }

    let total_fleet: u32 = fleet_by_line.values().sum();
    let workshop_bays = ((f64::from(total_fleet) * 0.15).ceil() as u32).max(4);
    let mut out = Vec::new();
    for (i, s) in stations.iter().enumerate() {
        let archetype = archetypes[i];
        if !is_depot_terminal_archetype(archetype) {
            continue;
        }
        out.push(DepotBlock {
            station_id: station_id(s),
            archetype: "main-heavy",
            fleet_stalls: workshop_bays,
        });
    }
    if out.is_empty()
        && lines
            .iter()
            .all(|line| matches!(line.shape, osr_routing::topology::LineShape::Ring))
    {
        let Some(station) = stations.iter().min_by(|a, b| {
            a.s_m
                .partial_cmp(&b.s_m)
                .unwrap_or(std::cmp::Ordering::Equal)
        }) else {
            return out;
        };
        out.push(DepotBlock {
            station_id: station_id(station),
            archetype: "main-heavy",
            fleet_stalls: workshop_bays,
        });
    }
    out
}

// ---- RFC 0008 §5 + RFC 0014 §4 fleet-sizing helpers ------------------------

/// Peak-revenue trainsets sized from the line's round-trip cycle
/// time vs. the peak headway:
///
/// ```text
///   peak = ceil(round_trip_min / headway_min)
///   round_trip_min = 2 × (line_length / cruise_speed + stop penalties) + 2 × turnback
/// ```
///
/// Run time is keyed off the rolling-stock family and the actual number of
/// station stops. Wider 1.6 / 3 / 7 km station spacing removes stop-start
/// cycles, so end-to-end time improves instead of being stuck at a fixed
/// commercial-speed proxy.
///
/// Turnback at each end is 3 min (single-tail, switch + driver-panel
/// changeover for the driverless GoA 4 control logic per RFC 0015).
/// The commercial-speed reference includes a one-minute platform stop.
/// Every charging platform is assigned a line-specific dwell from that
/// line's energy balance, so its increment above one minute is added
/// explicitly for each visit. A 10% recovery allowance
/// then absorbs control margins and minor perturbations without silently
/// reducing the published peak service.
/// Floor of 2.
fn peak_revenue_trainsets(
    line_length_m: f64,
    family: &str,
    is_ring: bool,
    station_count: u32,
    charging_station_count: u32,
    charging_dwell_seconds: u32,
) -> u32 {
    const TURNBACK_MIN: f64 = 3.0;
    const REFERENCE_DWELL_MIN: f64 = 1.0;
    let schedule_recovery_factor = match family {
        // High-throughput fleets also provide distributed onboard energy
        // reserve. The larger factors are calibrated to the mandatory EOL,
        // maximum-climate and ten-hour grid-outage screens; shortening dwell
        // must not silently remove that resilience capacity.
        "light-metro-3car" => 1.62,
        "metro-4car" => 1.30,
        "metro-6car" => 1.45,
        _ => 1.10,
    };
    let cruise_kmh = match family {
        "tram-2car" => 48.0,
        "light-metro-3car" => 62.0,
        "metro-4car" | "metro-6car" => 72.0,
        _ => 62.0,
    };
    let stop_penalty_min = match family {
        "tram-2car" => 1.45,
        "light-metro-3car" => 1.35,
        "metro-4car" | "metro-6car" => 1.30,
        _ => 1.35,
    };
    let stop_count = if is_ring {
        station_count
    } else {
        station_count.saturating_sub(2)
    };
    let one_way_min =
        (line_length_m / 1_000.0) / cruise_kmh * 60.0 + f64::from(stop_count) * stop_penalty_min;
    let charging_dwell_min = f64::from(charging_dwell_seconds) / 60.0;
    let extra_dwell_per_visit_min = (charging_dwell_min - REFERENCE_DWELL_MIN).max(0.0);
    let added_cycle_dwell_min = f64::from(charging_station_count) * extra_dwell_per_visit_min;
    let (base_cycle_min, peak_headway_min) = if is_ring {
        (one_way_min + added_cycle_dwell_min, 6.0)
    } else {
        (
            2.0 * one_way_min + 2.0 * TURNBACK_MIN + 2.0 * added_cycle_dwell_min,
            3.0,
        )
    };
    let cycle_min = base_cycle_min * schedule_recovery_factor;
    let k = (cycle_min / peak_headway_min).ceil().max(2.0);
    k as u32
}

/// Compute one common platform dwell for a line. A fully charged train can
/// spend its battery margin on the first traversal; repeated service must be
/// energy-neutral, so the scheduled dwell replaces a complete traversal's
/// climate-adjusted use across all charging platforms. Values are rounded up
/// to a 30-second operating interval and bounded to keep bad input explicit.
fn planned_charging_dwell_seconds(
    line_length_m: f64,
    family: &str,
    line_name: &str,
    stations: &[Station],
    archetypes: &[&str],
) -> u32 {
    const NOMINAL_ENERGY_KWH_PER_CAR_KM: f64 = 2.4;
    const MAX_CLIMATE_UPLIFT: f64 = 1.25;
    // The timetable needs headroom beyond energy neutrality because two
    // platform contacts share one 500 kW cabinet and arrivals can overlap.
    // Twenty-five percent covers conversion loss plus deterministic contact
    // contention in the catalog-scale operating screen.
    const CHARGING_MARGIN: f64 = 1.25;
    const MIN_DWELL_SECONDS: u32 = 120;
    const MAX_DWELL_SECONDS: u32 = 600;
    const DWELL_INTERVAL_SECONDS: f64 = 30.0;

    // Four- and six-car high-throughput families repeat the same 500 kW
    // cabinet so an energy-derived dwell does not exceed a three-minute peak headway and
    // occupy both shared contacts continuously.
    let cabinet_count = charging_cabinet_count(family);
    let total_charging_power_kw: u32 = stations
        .iter()
        .zip(archetypes)
        .filter(|(station, _)| station.line_name == line_name)
        .map(|(_, archetype)| {
            if *archetype == "halt" {
                0
            } else {
                500 * cabinet_count
            }
        })
        .sum();
    if total_charging_power_kw == 0 {
        return MIN_DWELL_SECONDS;
    }
    let traversal_energy_kwh = line_length_m / 1_000.0
        * f64::from(family_car_count(family))
        * NOMINAL_ENERGY_KWH_PER_CAR_KM
        * MAX_CLIMATE_UPLIFT
        * CHARGING_MARGIN;
    let raw_seconds = traversal_energy_kwh * 3_600.0 / f64::from(total_charging_power_kw);
    let rounded_seconds = (raw_seconds / DWELL_INTERVAL_SECONDS).ceil() * DWELL_INTERVAL_SECONDS;
    (rounded_seconds as u32).clamp(MIN_DWELL_SECONDS, MAX_DWELL_SECONDS)
}

fn line_charging_station_count(line_name: &str, stations: &[Station], archetypes: &[&str]) -> u32 {
    stations
        .iter()
        .zip(archetypes)
        .filter(|(station, archetype)| station.line_name == line_name && **archetype != "halt")
        .count() as u32
}

fn line_station_count(line_name: &str, stations: &[Station]) -> u32 {
    stations
        .iter()
        .filter(|station| station.line_name == line_name)
        .count() as u32
}

fn charging_cabinet_count(family: &str) -> u32 {
    match family {
        "metro-4car" => 3,
        "metro-6car" => 4,
        _ => 1,
    }
}

/// Planned-maintenance spare per RFC 0014 §4: 1 per 10 peak,
/// minimum 1.
fn fleet_spare(peak: u32) -> u32 {
    (peak / 10).max(1)
}

/// Cold reserve per RFC 0014 §4: 1 per line, fixed.
fn fleet_cold_reserve() -> u32 {
    1
}

/// Depot clean/inspect/recharge work runs only in lower-frequency timetable
/// windows, when the peak fleet already provides idle cover.
fn fleet_service_rotation() -> u32 {
    0
}

fn fleet_total(peak: u32) -> u32 {
    peak + fleet_service_rotation() + fleet_spare(peak) + fleet_cold_reserve()
}

fn line_cells_length_m(line: &Line) -> f64 {
    // This reuses the same accounting `line_length_m` uses, but we
    // don't have the RasterBundle here; approximate by counting
    // Manhattan-ish cell-to-cell distance. For the compute_depots
    // heuristic we need rough length only.
    let mut total = 0.0;
    for pair in line.cells.windows(2) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        total += (dr * dr + dc * dc).sqrt() * 20.0; // 20 m/cell
    }
    total
}

// ---- RFC 0012 §9 switch emission ------------------------------------------

#[derive(Debug, Clone)]
struct SwitchEntry {
    id: String,
    kit: &'static str,
    station_id: String,
    side: &'static str,
}

/// Derive the switch list:
/// - One `turnback` switch at every `terminal` / `depot-terminal`.
/// - One `yard-throat` switch per stall at every `depot-terminal`
///   (the depot fan is parametric in stall count).
/// - One `yard-throat` access switch at a ring-line layup depot.
///
/// All switches use `no-9-mainline` per RFC 0012 §3 — one tangent
/// across the deployment, matching the simplicity bet.
fn compute_switches(
    stations: &[Station],
    archetypes: &[&'static str],
    depots: &[DepotBlock],
) -> Vec<SwitchEntry> {
    let mut out = Vec::new();
    for (i, s) in stations.iter().enumerate() {
        let archetype = archetypes[i];
        if !is_terminal_archetype(archetype) {
            continue;
        }
        let sid = station_id(s);
        out.push(SwitchEntry {
            id: format!("sw-{sid}-tb"),
            kit: "no-9-mainline",
            station_id: sid.clone(),
            side: "turnback",
        });
        if is_depot_terminal_archetype(archetype) {
            // Yard fan: one switch per stall (simple linear fan; a
            // deployment civil design will refine into a proper
            // ladder track).
            let stalls = depots
                .iter()
                .find(|d| d.station_id == sid)
                .map(|d| d.fleet_stalls)
                .unwrap_or(0);
            for n in 1..=stalls {
                out.push(SwitchEntry {
                    id: format!("sw-{sid}-yd-{n:02}"),
                    kit: "no-9-mainline",
                    station_id: sid.clone(),
                    side: "yard-throat",
                });
            }
        }
    }
    for depot in depots {
        if out
            .iter()
            .any(|switch| switch.station_id == depot.station_id)
        {
            continue;
        }
        out.push(SwitchEntry {
            id: format!("sw-{}-yd-01", depot.station_id),
            kit: "no-9-mainline",
            station_id: depot.station_id.clone(),
            side: "yard-throat",
        });
    }
    out
}

// ---- RFC 0011 §9 cost estimation -------------------------------------------

#[derive(Debug, Clone, Copy, Default)]
struct CostSummary {
    // Civil works (RFC 0011 §9 USD/km × civil mix, with EUR mirrors).
    at_grade_usd: f64,
    at_grade_eur: f64,
    elevated_usd: f64,
    elevated_eur: f64,
    bridge_usd: f64,
    bridge_eur: f64,
    junction_premium_usd: f64,
    junction_premium_eur: f64,
    civil_subtotal_usd: f64,
    civil_subtotal_eur: f64,
    // Stations (RFC 0010 archetype catalogue).
    stations_usd: f64,
    stations_eur: f64,
    // Depots (RFC 0014 archetype catalogue).
    depots_usd: f64,
    depots_eur: f64,
    // Rolling stock (RFC 0008 local-owner production cost × fleet count).
    rolling_stock_usd: f64,
    rolling_stock_eur: f64,
    // Shared national railway production plant; zero in every city cost block.
    production_plant_usd: f64,
    production_plant_eur: f64,
    // Systems — onboard-first train control + station/depot charging.
    signalling_usd: f64,
    signalling_eur: f64,
    charging_microgrid_usd: f64,
    charging_microgrid_eur: f64,
    // EPC integration + project management overhead on the subtotal.
    epc_overhead_usd: f64,
    epc_overhead_eur: f64,
    // Grand total across every bucket above.
    total_usd: f64,
    total_eur: f64,
}

const CAPEX_COSTS_TOML: &str = include_str!("../../../lib/templates/capex-costs.toml");

#[derive(Debug, Deserialize)]
struct CapexCostConfig {
    schema: CostSchema,
    civil_usd_per_km: CivilCostRates,
    junctions: JunctionCostRates,
    station_unit_usd: BTreeMap<String, f64>,
    depot_unit_usd: BTreeMap<String, f64>,
    trainset_unit_usd: BTreeMap<String, f64>,
    trainset_800v_core_electrical_usd: Trainset800vCoreElectrical,
    station_800v_module_usd: Station800vModule,
    systems: SystemCostRates,
    charging_microgrid_unit_usd: BTreeMap<String, f64>,
    overhead: OverheadCostRates,
}

#[derive(Debug, Deserialize)]
struct Trainset800vCoreElectrical {
    architecture: String,
    gross_battery_kwh_per_car: f64,
    traction_battery_system_per_car: f64,
    motor_controller_sets_per_car: u32,
    motor_controller_set: f64,
    hv_distribution_per_car: f64,
    lv_dc_dc_per_car: f64,
    roof_pv_mppt_per_car: f64,
    core_electrical_total_per_car: f64,
}

#[derive(Debug, Deserialize)]
struct Station800vModule {
    architecture: String,
    stationary_lfp_500kwh: f64,
    dcdc_500kw: f64,
    contact_protection_control: f64,
    equipment_total: f64,
    normal_integrated_site: f64,
}

#[derive(Debug, Deserialize)]
struct CostSchema {
    currency_basis: String,
    usd_to_eur: f64,
}

#[derive(Debug, Deserialize)]
struct CivilCostRates {
    at_grade: f64,
    elevated: f64,
    bridge: f64,
}

#[derive(Debug, Deserialize)]
struct JunctionCostRates {
    elevated_interchange_premium_usd: f64,
}

#[derive(Debug, Deserialize)]
struct SystemCostRates {
    signalling_usd_per_km: f64,
}

#[derive(Debug, Deserialize)]
struct OverheadCostRates {
    epc_fraction: f64,
}

static COST_CONFIG: OnceLock<CapexCostConfig> = OnceLock::new();

fn cost_config() -> &'static CapexCostConfig {
    COST_CONFIG.get_or_init(|| {
        toml::from_str(CAPEX_COSTS_TOML).expect("lib/templates/capex-costs.toml must parse")
    })
}

fn usd_to_eur() -> f64 {
    cost_config().schema.usd_to_eur
}

fn eur_from_usd(usd: f64) -> f64 {
    usd * usd_to_eur()
}

fn junction_premium_usd() -> f64 {
    cost_config().junctions.elevated_interchange_premium_usd
}

fn junction_premium_eur() -> f64 {
    eur_from_usd(junction_premium_usd())
}

fn mapped_cost(costs: &BTreeMap<String, f64>, key: &str, fallback_key: &str) -> f64 {
    costs
        .get(key)
        .or_else(|| costs.get(fallback_key))
        .copied()
        .unwrap_or(0.0)
}

fn station_cost_usd(archetype: &str) -> f64 {
    mapped_cost(&cost_config().station_unit_usd, archetype, "standard")
}

fn depot_cost_usd(archetype: &str) -> f64 {
    mapped_cost(&cost_config().depot_unit_usd, archetype, "main-heavy")
}

fn trainset_cost_usd(family: &str) -> f64 {
    mapped_cost(&cost_config().trainset_unit_usd, family, "light-metro-3car")
}

fn charging_microgrid_cost_usd(archetype: &str) -> f64 {
    mapped_cost(
        &cost_config().charging_microgrid_unit_usd,
        archetype,
        "standard",
    )
}

fn compute_costs(
    civil_per_line: &[Vec<CivilSegment>],
    station_archetypes: &[&str],
    depots: &[DepotBlock],
    elevated_junctions_count: usize,
    fleet_total_trainsets: u32,
    family: &str,
) -> CostSummary {
    let mut at_grade_m = 0.0_f64;
    let mut elevated_m = 0.0_f64;
    let mut bridge_m = 0.0_f64;
    for segs in civil_per_line {
        for s in segs {
            match s.class {
                CivilClass::AtGrade => at_grade_m += s.length_m,
                CivilClass::Elevated => elevated_m += s.length_m,
                CivilClass::Bridge => bridge_m += s.length_m,
            }
        }
    }
    let rates = cost_config();
    let at_grade_usd = at_grade_m / 1_000.0 * rates.civil_usd_per_km.at_grade;
    let elevated_usd = elevated_m / 1_000.0 * rates.civil_usd_per_km.elevated;
    let bridge_usd = bridge_m / 1_000.0 * rates.civil_usd_per_km.bridge;
    let junction_premium_usd = (elevated_junctions_count as f64) * junction_premium_usd();
    let at_grade_eur = eur_from_usd(at_grade_usd);
    let elevated_eur = eur_from_usd(elevated_usd);
    let bridge_eur = eur_from_usd(bridge_usd);
    let junction_premium_eur = eur_from_usd(junction_premium_usd);
    let civil_subtotal_usd = at_grade_usd + elevated_usd + bridge_usd + junction_premium_usd;
    let civil_subtotal_eur = at_grade_eur + elevated_eur + bridge_eur + junction_premium_eur;

    let stations_usd: f64 = station_archetypes.iter().map(|a| station_cost_usd(a)).sum();
    let stations_eur = eur_from_usd(stations_usd);
    let depots_usd: f64 = depots.iter().map(|d| depot_cost_usd(d.archetype)).sum();
    let depots_eur = eur_from_usd(depots_usd);
    let rolling_stock_usd = f64::from(fleet_total_trainsets) * trainset_cost_usd(family);
    let rolling_stock_eur = eur_from_usd(rolling_stock_usd);
    // Trainset production is a national shared asset, not one factory per
    // city. City CAPEX therefore carries no production-plant setup charge;
    // `scripts/generate-national-briefs.py` sizes one plant to the largest
    // city fleet programme and adds it once to the national capital plan.
    let production_plant_usd = 0.0;
    let production_plant_eur = 0.0;

    let route_km = (at_grade_m + elevated_m + bridge_m) / 1_000.0;
    let signalling_usd = route_km * rates.systems.signalling_usd_per_km;
    let signalling_eur = eur_from_usd(signalling_usd);
    let charging_cabinet_multiplier = f64::from(charging_cabinet_count(family));
    let charging_microgrid_usd: f64 = station_archetypes
        .iter()
        .map(|a| charging_microgrid_cost_usd(a) * charging_cabinet_multiplier)
        .sum();
    let charging_microgrid_eur = eur_from_usd(charging_microgrid_usd);

    let pre_epc_usd = civil_subtotal_usd
        + stations_usd
        + depots_usd
        + rolling_stock_usd
        + production_plant_usd
        + signalling_usd
        + charging_microgrid_usd;
    let epc_overhead_usd = pre_epc_usd * rates.overhead.epc_fraction;
    let total_usd = pre_epc_usd + epc_overhead_usd;
    let epc_overhead_eur = eur_from_usd(epc_overhead_usd);
    let total_eur = eur_from_usd(total_usd);

    CostSummary {
        at_grade_usd,
        at_grade_eur,
        elevated_usd,
        elevated_eur,
        bridge_usd,
        bridge_eur,
        junction_premium_usd,
        junction_premium_eur,
        civil_subtotal_usd,
        civil_subtotal_eur,
        stations_usd,
        stations_eur,
        depots_usd,
        depots_eur,
        rolling_stock_usd,
        rolling_stock_eur,
        production_plant_usd,
        production_plant_eur,
        signalling_usd,
        signalling_eur,
        charging_microgrid_usd,
        charging_microgrid_eur,
        epc_overhead_usd,
        epc_overhead_eur,
        total_usd,
        total_eur,
    }
}

// ---- RFC 0008 §5 rolling-stock policy --------------------------------------

/// Pick a rolling-stock family id for a population per RFC 0008 §5.
fn family_for_population(population: u64) -> &'static str {
    match population {
        0..=150_000 => "urban-shuttle-1car",
        150_001..=300_000 => "tram-2car",
        300_001..=1_000_000 => "light-metro-3car",
        1_000_001..=3_000_000 => "metro-4car",
        _ => "metro-6car",
    }
}

/// Pick the tightest geometry preset compatible with a rolling-stock
/// family per RFC 0009 §10. "Tightest" = the preset with the smallest
/// supported consist — it gives the operator the most flexibility
/// downstream without over-engineering the alignment.
fn geometry_for_family(family: &str) -> &'static str {
    match family {
        "urban-shuttle-1car" => "standard-urban",
        "tram-2car" => "standard-urban",
        "light-metro-3car" => "standard-urban",
        "metro-4car" => "standard-metro",
        "metro-6car" => "standard-metro", // mainline-mixed only when explicit
        _ => "standard-urban",
    }
}

/// Nominal consist length per family (RFC 0008 §1). Used to derive
/// platform_length_m per RFC 0010 §4.1.
fn family_length_m(family: &str) -> f32 {
    match family {
        "urban-shuttle-1car" => 21.0,
        "tram-2car" => 39.0,
        "light-metro-3car" => 49.5,
        "metro-4car" => 75.0,
        "metro-6car" => 111.0,
        _ => 49.5,
    }
}

fn family_car_count(family: &str) -> u32 {
    match family {
        "urban-shuttle-1car" => 1,
        "tram-2car" => 2,
        "light-metro-3car" => 3,
        "metro-4car" => 4,
        "metro-6car" => 6,
        _ => 3,
    }
}

// ---- RFC 0010 §3 archetype selection ---------------------------------------

/// Return an archetype string per station (same order/length as the
/// input `stations` slice). See RFC 0010 §3. Stations whose
/// `junction_group` appears in `elevated_groups` are promoted from
/// `"interchange"` to `"interchange-elevated"` — the new archetype
/// covers multi-level platform construction at junctions where one of
/// the crossing lines had to be lifted.
fn compute_archetypes(
    lines: &[Line],
    stations: &[Station],
    elevated_groups: &std::collections::BTreeSet<u32>,
) -> Vec<&'static str> {
    // Group station indices by line name to find endpoints.
    let mut by_line: std::collections::BTreeMap<&str, Vec<usize>> =
        std::collections::BTreeMap::new();
    for (i, s) in stations.iter().enumerate() {
        by_line.entry(s.line_name.as_str()).or_default().push(i);
    }
    // Endpoints: first + last by s_m on each radial line.
    let mut is_terminal = vec![false; stations.len()];
    for line in lines {
        let line_is_ring = matches!(line.shape, osr_routing::topology::LineShape::Ring);
        if line_is_ring {
            continue; // Rings have no terminal.
        }
        let Some(idxs) = by_line.get(line.name.as_str()) else {
            continue;
        };
        let mut sorted = idxs.clone();
        sorted.sort_by(|&a, &b| {
            stations[a]
                .s_m
                .partial_cmp(&stations[b].s_m)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        if let Some(&first) = sorted.first() {
            is_terminal[first] = true;
        }
        if let Some(&last) = sorted.last() {
            if sorted.len() > 1 {
                is_terminal[last] = true;
            }
        }
    }

    // Interchanges come only from the explicit cross-line junction groups
    // assigned by `merge_interchanges`, so topology and station classification
    // share one transfer envelope.
    let mut is_interchange = vec![false; stations.len()];
    let mut junction_lines: std::collections::BTreeMap<u32, std::collections::BTreeSet<&str>> =
        std::collections::BTreeMap::new();
    for station in stations {
        if let Some(group) = station.junction_group {
            junction_lines
                .entry(group)
                .or_default()
                .insert(station.line_name.as_str());
        }
    }
    for (index, station) in stations.iter().enumerate() {
        if station
            .junction_group
            .and_then(|group| junction_lines.get(&group))
            .is_some_and(|lines| lines.len() >= 2)
        {
            is_interchange[index] = true;
        }
    }
    // Depot-terminal: the single "far" terminal on the city's longest
    // radial line — a common convention for siting the fleet depot at
    // the operator's main spare yard. If no radial terminal exists
    // (all-ring city), skip.
    let mut depot_terminal_idx: Option<usize> = None;
    let mut best_s_m: f64 = -1.0;
    for (i, t) in is_terminal.iter().enumerate() {
        if *t && stations[i].s_m > best_s_m {
            best_s_m = stations[i].s_m;
            depot_terminal_idx = Some(i);
        }
    }

    // Terminal/depot-terminal remains the physical product archetype even when
    // the station also belongs to a transfer group. `junction_group` carries
    // that additional operational role without inventing a bespoke station
    // shell, so turnback, depot, charging, manufacturing and cost semantics
    // stay on the standard kit.
    // An interchange whose junction_group was elevated promotes to
    // "interchange-elevated".
    let mut out: Vec<&'static str> = Vec::with_capacity(stations.len());
    for i in 0..stations.len() {
        let elevated_here = stations[i]
            .junction_group
            .map(|g| elevated_groups.contains(&g))
            .unwrap_or(false);
        let archetype = if Some(i) == depot_terminal_idx {
            "depot-terminal"
        } else if is_terminal[i] {
            "terminal"
        } else if is_interchange[i] && elevated_here {
            "interchange-elevated"
        } else if is_interchange[i] {
            "interchange"
        } else if stations[i].demand > 0.6 {
            "major"
        } else if stations[i].demand > 0.25 {
            "standard"
        } else {
            "halt"
        };
        out.push(archetype);
    }
    out
}

fn is_terminal_archetype(archetype: &str) -> bool {
    matches!(archetype, "terminal" | "depot-terminal")
}

fn is_depot_terminal_archetype(archetype: &str) -> bool {
    archetype == "depot-terminal"
}

/// Great-circle distance between two lat/lon points, in metres.
/// Small-angle approximation suffices at the ≤ 200 m scales we use.
#[cfg(test)]
fn haversine_m(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let to_rad = std::f64::consts::PI / 180.0;
    let dlat = (lat2 - lat1) * to_rad;
    let dlon = (lon2 - lon1) * to_rad;
    let mid_lat = ((lat1 + lat2) * 0.5) * to_rad;
    let r = 6_371_000.0_f64;
    ((r * dlat).powi(2) + (r * mid_lat.cos() * dlon).powi(2)).sqrt()
}

fn station_id(s: &Station) -> String {
    // Stable ID derived from line + cell + route chainage. The chainage keeps
    // a self-crossing route's two operational stop records distinct while
    // avoiding non-ASCII or mutable anchor names.
    format!(
        "{}-{:04}-{:04}-s{:06}",
        s.line_name,
        s.row,
        s.col,
        s.s_m.round().max(0.0) as u64
    )
}

fn escape_toml_string(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}

fn line_length_m(bundle: &RasterBundle, line: &Line) -> f64 {
    let cell_m = bundle.grid.reference.cell_m;
    let mut total = 0.0_f64;
    for pair in line.cells.windows(2) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        total += (dr * dr + dc * dc).sqrt() * cell_m;
    }
    total
}

fn cumulative_cell_chainage_m(cells: &[(usize, usize)], end_index: usize, cell_m: f64) -> f64 {
    let mut total = 0.0_f64;
    for pair in cells.windows(2).take(end_index) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        total += (dr * dr + dc * dc).sqrt() * cell_m;
    }
    total
}

// ---- corridor.geojson ------------------------------------------------

fn write_corridor_geojson(
    out_dir: &Path,
    slug: &str,
    bundle: &RasterBundle,
    lines: &[Line],
    stations: &[Station],
) -> Result<()> {
    let mut features: Vec<serde_json::Value> = Vec::new();

    // Shared-track detection: for every cell that two or more lines
    // pass through, we offset each line's drawn polyline perpendicularly
    // by `(rank - (n-1)/2) * SHARED_OFFSET_M` so both lines remain
    // visible instead of stacking on the same pixel. Single-occupant
    // cells get no offset, so non-shared sections render in their true
    // location.
    const SHARED_OFFSET_M: f64 = 12.0;
    let cell_owners = compute_cell_owners(lines);

    for (li, line) in lines.iter().enumerate() {
        let step = (line.cells.len() / 400).max(1);
        let mut coords: Vec<[f64; 2]> = Vec::new();
        let n = line.cells.len();
        for i in 0..n {
            // Decimate identically to the previous behaviour.
            if i != 0 && i != n - 1 && i % step != 0 {
                continue;
            }
            let (r, c) = line.cells[i];
            // Tangent from the (i-1, i+1) neighbours when available.
            let (pr, pc) = line.cells[i.saturating_sub(1)];
            let (nr, nc) = line.cells[(i + 1).min(n - 1)];
            let dr = nr as f64 - pr as f64;
            let dc = nc as f64 - pc as f64;
            let mag = (dr * dr + dc * dc).sqrt().max(1e-6);
            // Perpendicular in (row, col) space: (-dc, dr). Row grows
            // southward, so positive perp_lat = north when perp_row<0;
            // we just need consistent left/right separation so the
            // sign convention is fine as long as each line gets a
            // distinct rank.
            let perp_r = -dc / mag;
            let perp_c = dr / mag;

            let offset_m = perp_offset(&cell_owners, (r, c), li, SHARED_OFFSET_M);
            let (lat, lon) = if offset_m == 0.0 {
                bundle.grid.reference.rc_to_latlon(r, c)
            } else {
                offset_latlon(&bundle.grid.reference, r, c, perp_r, perp_c, offset_m)
            };
            coords.push([lon, lat]);
        }
        features.push(serde_json::json!({
            "type": "Feature",
            "properties": {
                "kind": "line",
                "name": line.name,
                "shape": match line.shape {
                    osr_routing::topology::LineShape::Radial => "radial",
                    osr_routing::topology::LineShape::Ring => "ring",
                },
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            }
        }));
    }

    for s in stations {
        features.push(serde_json::json!({
            "type": "Feature",
            "properties": {
                "kind": "station",
                "line": s.line_name,
                "anchor_kind": s.anchor_kind,
                "anchor_name": s.anchor_name,
                "junction_group": s.junction_group,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [s.lon, s.lat],
            }
        }));
    }

    let geojson = serde_json::json!({
        "type": "FeatureCollection",
        "features": features,
    });
    let path = out_dir.join(format!("{slug}.corridor.geojson"));
    fs::write(&path, serde_json::to_string_pretty(&geojson)?)?;
    Ok(())
}

/// Map every cell to the sorted list of line indices that pass through
/// it. Cells touched by only one line are absent (we skip the
/// allocation for them since the common case in non-trunk areas is
/// single-occupancy).
fn compute_cell_owners(lines: &[Line]) -> std::collections::HashMap<(usize, usize), Vec<usize>> {
    let mut tmp: std::collections::HashMap<(usize, usize), Vec<usize>> =
        std::collections::HashMap::new();
    for (li, line) in lines.iter().enumerate() {
        for &cell in &line.cells {
            let entry = tmp.entry(cell).or_default();
            if !entry.contains(&li) {
                entry.push(li);
            }
        }
    }
    tmp.retain(|_, v| v.len() >= 2);
    for v in tmp.values_mut() {
        v.sort();
    }
    tmp
}

/// Compute the perpendicular offset in metres for line `li` at `cell`.
/// Returns (0.0, 1) if the cell is single-occupant.
fn perp_offset(
    owners: &std::collections::HashMap<(usize, usize), Vec<usize>>,
    cell: (usize, usize),
    li: usize,
    offset_m: f64,
) -> f64 {
    let Some(v) = owners.get(&cell) else {
        return 0.0;
    };
    let n = v.len();
    let rank = v.iter().position(|&i| i == li).unwrap_or(0) as f64;
    let centred = rank - (n as f64 - 1.0) * 0.5;
    centred * offset_m
}

/// Apply a perpendicular metres-offset to a cell centre's lat/lon.
/// `perp_r` / `perp_c` is the unit perpendicular in (row, col) space.
fn offset_latlon(
    gref: &osr_routing::raster::GridRef,
    row: usize,
    col: usize,
    perp_r: f64,
    perp_c: f64,
    offset_m: f64,
) -> (f64, f64) {
    let (base_lat, base_lon) = gref.rc_to_latlon(row, col);
    // perp in (row, col) translated to metres; row grows southward so
    // dlat = -perp_r * offset / m_per_deg_lat.
    let dlat = -(perp_r * offset_m) / gref.m_per_deg_lat;
    let dlon = (perp_c * offset_m) / gref.m_per_deg_lon;
    (base_lat + dlat, base_lon + dlon)
}

// ---- stations.json ---------------------------------------------------

#[derive(Serialize)]
struct StationSummary<'a> {
    id: String,
    line: &'a str,
    lat: f64,
    lon: f64,
    s_m: f64,
    anchor_kind: Option<&'a str>,
    anchor_name: Option<&'a str>,
    #[serde(skip_serializing_if = "Option::is_none")]
    junction_group: Option<u32>,
    demand: f32,
}

fn write_stations_json(out_dir: &Path, slug: &str, stations: &[Station]) -> Result<()> {
    let rows: Vec<StationSummary> = stations
        .iter()
        .map(|s| StationSummary {
            id: station_id(s),
            line: &s.line_name,
            lat: s.lat,
            lon: s.lon,
            s_m: s.s_m,
            anchor_kind: s.anchor_kind.as_deref(),
            anchor_name: s.anchor_name.as_deref(),
            junction_group: s.junction_group,
            demand: s.demand,
        })
        .collect();
    let path = out_dir.join(format!("{slug}.stations.json"));
    fs::write(&path, serde_json::to_string_pretty(&rows)?)?;
    Ok(())
}

// ---- design-quality.yaml --------------------------------------------
//
// This is the automated gate that lets us ship 500 cities without
// human inspection. Each city gets scored; failing thresholds route the
// city back for retry with different topology parameters.

fn write_quality_yaml(
    out_dir: &Path,
    slug: &str,
    bundle: &RasterBundle,
    lines: &[Line],
    stations: &[Station],
    civil_per_line: &[Vec<CivilSegment>],
) -> Result<()> {
    let total_line_m: f64 = lines.iter().map(|l| line_length_m(bundle, l)).sum();
    let anchor_hit = {
        let hit = stations.iter().filter(|s| s.anchor_id.is_some()).count();
        if stations.is_empty() {
            0.0
        } else {
            hit as f64 / stations.len() as f64
        }
    };

    // Coverage: fraction of high-demand cells within 400m (20 cells at 20m)
    // of any line.
    let coverage_pct = compute_coverage(bundle, lines, 20);

    // Civil class mix. No tunnel class per RFC 0011 §1; only
    // at-grade / elevated / bridge exist in the catalogue. Viaducts
    // and water-crossing bridges share the same reference U-girder
    // (RFC 0011 §§5–6), so their shares are reported separately but
    // priced from the same structural envelope downstream.
    let mut at_grade = 0.0_f64;
    let mut elevated = 0.0_f64;
    let mut bridge = 0.0_f64;
    for segs in civil_per_line {
        for s in segs {
            match s.class {
                CivilClass::AtGrade => at_grade += s.length_m,
                CivilClass::Elevated => elevated += s.length_m,
                CivilClass::Bridge => bridge += s.length_m,
            }
        }
    }
    let total_structure_m = at_grade + elevated + bridge;
    let elevated_fraction = if total_structure_m > 0.0 {
        (elevated + bridge) / total_structure_m
    } else {
        0.0
    };

    // Quality gates: hard (design is invalid if any fail) vs soft
    // (flagged for review but still shippable).
    //
    // Thresholds calibrated against a 3-city ground truth (Samawah,
    // Nairobi, Lyon). The soft bar lets auto-generated designs ship
    // when they are a reasonable first draft — tuning comes from
    // recipe edits, not per-city interventions.
    let hard_has_stations = !stations.is_empty();
    let hard_length_reasonable = (3_000.0..=500_000.0).contains(&total_line_m);
    let hard_all = hard_has_stations && hard_length_reasonable;

    let soft_coverage = coverage_pct >= 0.30;
    let soft_anchor_hit = anchor_hit >= 0.20;
    // RFC 0011 §8: > 30 % elevated share is a warning; the
    // at-grade-dominant design is the mission-aligned one.
    let soft_elevated_ok = elevated_fraction <= 0.30;
    let soft_all = soft_coverage && soft_anchor_hit && soft_elevated_ok;

    // A design "passes" if the hard gates pass. Soft gates surface in the
    // report for triage but do not block scale-up.
    let pass_all = hard_all;

    let mut yaml = String::new();
    yaml.push_str(&format!("slug: {slug}\n"));
    yaml.push_str(&format!("pass: {pass_all}\n"));
    yaml.push_str("metrics:\n");
    yaml.push_str(&format!("  total_route_m: {total_line_m:.1}\n"));
    yaml.push_str(&format!("  n_lines: {}\n", lines.len()));
    yaml.push_str(&format!("  n_stations: {}\n", stations.len()));
    yaml.push_str(&format!("  anchor_hit_rate: {anchor_hit:.3}\n"));
    yaml.push_str(&format!("  high_demand_coverage: {coverage_pct:.3}\n"));
    yaml.push_str("  civil_mix_m:\n");
    yaml.push_str(&format!("    at_grade: {at_grade:.1}\n"));
    yaml.push_str(&format!("    elevated: {elevated:.1}\n"));
    yaml.push_str(&format!("    bridge:   {bridge:.1}\n"));
    yaml.push_str(&format!("  elevated_fraction: {elevated_fraction:.3}\n"));
    yaml.push_str("gates:\n");
    yaml.push_str("  hard:\n");
    yaml.push_str(&format!("    has_stations:      {hard_has_stations}\n"));
    yaml.push_str(&format!(
        "    length_reasonable: {hard_length_reasonable}\n"
    ));
    yaml.push_str("  soft:\n");
    yaml.push_str(&format!("    coverage_ge_0.30:   {soft_coverage}\n"));
    yaml.push_str(&format!("    anchor_hit_ge_0.20: {soft_anchor_hit}\n"));
    yaml.push_str(&format!("    elevated_le_0.30:   {soft_elevated_ok}\n"));
    yaml.push_str(&format!("    soft_pass_all:      {soft_all}\n"));

    let path = out_dir.join(format!("{slug}.design-quality.yaml"));
    let mut f = fs::File::create(path)?;
    f.write_all(yaml.as_bytes())?;
    Ok(())
}

/// What fraction of cells with demand > 0.5 are within `radius_cells` of
/// any line cell? Cheap distance transform via BFS from line cells.
fn compute_coverage(bundle: &RasterBundle, lines: &[Line], radius_cells: usize) -> f64 {
    let h = bundle.grid.reference.height;
    let w = bundle.grid.reference.width;
    let mut covered = vec![false; h * w];

    for line in lines {
        for &(r, c) in &line.cells {
            let r_min = r.saturating_sub(radius_cells);
            let r_max = (r + radius_cells).min(h - 1);
            let c_min = c.saturating_sub(radius_cells);
            let c_max = (c + radius_cells).min(w - 1);
            let rr2 = (radius_cells * radius_cells) as isize;
            for rr in r_min..=r_max {
                for cc in c_min..=c_max {
                    let dr = rr as isize - r as isize;
                    let dc = cc as isize - c as isize;
                    if dr * dr + dc * dc <= rr2 {
                        covered[rr * w + cc] = true;
                    }
                }
            }
        }
    }

    let mut hi_cells = 0_u64;
    let mut hi_covered = 0_u64;
    for (demand, is_covered) in bundle.grid.demand.iter().zip(&covered).take(h * w) {
        if *demand >= 0.5 {
            hi_cells += 1;
            if *is_covered {
                hi_covered += 1;
            }
        }
    }
    if hi_cells == 0 {
        return 0.0;
    }
    hi_covered as f64 / hi_cells as f64
}

// ---------------------------------------------------------------------------
// Tests — exercise the RFC 0008/0009/0010 policy helpers in isolation so the
// compatibility matrix stays regression-guarded without spinning the full
// raster + solver pipeline.
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use osr_routing::topology::{Line, LineShape};

    #[test]
    fn family_band_boundaries_match_rfc_0008_section_5() {
        assert_eq!(family_for_population(50_000), "urban-shuttle-1car");
        assert_eq!(family_for_population(150_000), "urban-shuttle-1car");
        assert_eq!(family_for_population(150_001), "tram-2car");
        assert_eq!(family_for_population(300_000), "tram-2car");
        assert_eq!(family_for_population(300_001), "light-metro-3car");
        assert_eq!(family_for_population(1_000_000), "light-metro-3car");
        assert_eq!(family_for_population(1_000_001), "metro-4car");
        assert_eq!(family_for_population(3_000_000), "metro-4car");
        assert_eq!(family_for_population(3_000_001), "metro-6car");
    }

    #[test]
    fn geometry_matches_family_compatibility() {
        // Every family must resolve to a geometry preset that RFC 0009 §10
        // lists as compatible.
        assert_eq!(geometry_for_family("tram-2car"), "standard-urban");
        assert_eq!(geometry_for_family("light-metro-3car"), "standard-urban");
        assert_eq!(geometry_for_family("metro-4car"), "standard-metro");
        assert_eq!(geometry_for_family("metro-6car"), "standard-metro");
    }

    fn st(line: &str, s_m: f64, lat: f64, lon: f64, demand: f32) -> Station {
        Station {
            row: 0,
            col: 0,
            lat,
            lon,
            anchor_id: None,
            anchor_kind: None,
            anchor_name: None,
            line_name: line.to_string(),
            s_m,
            demand,
            junction_group: None,
        }
    }

    fn no_elevated() -> std::collections::BTreeSet<u32> {
        std::collections::BTreeSet::new()
    }

    fn radial_line(name: &str) -> Line {
        Line {
            name: name.to_string(),
            shape: LineShape::Radial,
            cells: vec![],
            anchor_ids: vec![],
        }
    }

    fn ring_line(name: &str) -> Line {
        Line {
            name: name.to_string(),
            shape: LineShape::Ring,
            cells: vec![],
            anchor_ids: vec![],
        }
    }

    #[test]
    fn terminal_is_first_and_last_of_radial_line() {
        // 3 stations on one radial line — first and last should be terminal.
        let lines = vec![radial_line("L1")];
        let stations = vec![
            st("L1", 0.0, 0.0, 0.0, 0.3),
            st("L1", 1_000.0, 0.01, 0.0, 0.3),
            st("L1", 2_000.0, 0.02, 0.0, 0.3),
        ];
        let a = compute_archetypes(&lines, &stations, &no_elevated());
        // Longest s_m terminal wins depot-terminal promotion.
        assert_eq!(a[0], "terminal");
        assert_eq!(a[1], "standard");
        assert_eq!(a[2], "depot-terminal");
    }

    #[test]
    fn ring_has_no_terminal() {
        let lines = vec![ring_line("R1")];
        let stations = vec![
            st("R1", 0.0, 0.0, 0.0, 0.3),
            st("R1", 500.0, 0.005, 0.0, 0.3),
            st("R1", 1_000.0, 0.01, 0.0, 0.3),
        ];
        let a = compute_archetypes(&lines, &stations, &no_elevated());
        for arch in &a {
            assert_ne!(*arch, "terminal");
            assert_ne!(*arch, "depot-terminal");
        }
    }

    #[test]
    fn ring_only_city_gets_main_maintenance_depot_without_becoming_terminal() {
        let lines = vec![ring_line("R1")];
        let stations = vec![
            st("R1", 0.0, 0.0, 0.0, 0.3),
            st("R1", 500.0, 0.005, 0.0, 0.3),
            st("R1", 1_000.0, 0.01, 0.0, 0.3),
        ];
        let archetypes = compute_archetypes(&lines, &stations, &no_elevated());
        let depots = compute_depots(&lines, &stations, &archetypes, "tram-2car");
        assert_eq!(depots.len(), 1);
        assert_eq!(depots[0].station_id, station_id(&stations[0]));
        assert_eq!(depots[0].archetype, "main-heavy");

        let switches = compute_switches(&stations, &archetypes, &depots);
        assert_eq!(switches.len(), 1);
        assert_eq!(switches[0].station_id, depots[0].station_id);
        assert_eq!(switches[0].side, "yard-throat");
    }

    #[test]
    fn elevated_groups_promote_interchange_to_interchange_elevated() {
        let lines = vec![radial_line("L1"), radial_line("L2")];
        let mut a = st("L1", 1_000.0, 0.001, 0.001, 0.3);
        a.junction_group = Some(7);
        let mut b = st("L2", 1_000.0, 0.001, 0.001, 0.3);
        b.junction_group = Some(7);
        let stations = vec![
            st("L1", 0.0, 0.0, 0.0, 0.3),
            a,
            st("L1", 2_000.0, 0.02, 0.02, 0.3),
            st("L2", 0.0, 0.05, 0.05, 0.3),
            b,
            st("L2", 2_000.0, 0.06, 0.06, 0.3),
        ];
        let mut elevated = std::collections::BTreeSet::new();
        elevated.insert(7);
        let archetypes = compute_archetypes(&lines, &stations, &elevated);
        assert_eq!(archetypes[1], "interchange-elevated");
        assert_eq!(archetypes[4], "interchange-elevated");
    }

    #[test]
    fn explicit_transfer_group_marks_connected_platforms() {
        let lines = vec![radial_line("L1"), ring_line("R1")];
        let mut radial = st("L1", 0.0, 0.0, 0.0, 0.3);
        let mut ring = st("R1", 500.0, 0.0, 0.004, 0.3); // ~445 m
        radial.junction_group = Some(12);
        ring.junction_group = Some(12);
        assert_eq!(radial.junction_group, ring.junction_group);
        let archetypes = compute_archetypes(&lines, &[radial, ring], &no_elevated());
        assert_eq!(archetypes[0], "depot-terminal");
        assert_eq!(archetypes[1], "interchange");
    }

    #[test]
    fn terminal_interchange_keeps_depot_and_turnback_semantics() {
        let lines = vec![radial_line("L1"), ring_line("R1")];
        let mut first = st("L1", 0.0, 0.0, 0.0, 0.3);
        let last = st("L1", 2000.0, 0.02, 0.0, 0.3);
        let mut ring = st("R1", 500.0, 0.0, 0.004, 0.3);
        first.junction_group = Some(7);
        ring.junction_group = Some(7);
        let stations = vec![first, last, ring];
        let archetypes = compute_archetypes(&lines, &stations, &no_elevated());
        assert_eq!(archetypes[0], "terminal");
        assert_eq!(archetypes[1], "depot-terminal");
        assert_eq!(stations[0].junction_group, stations[2].junction_group);
        let depots = compute_depots(&lines, &stations, &archetypes, "tram-2car");
        assert!(depots
            .iter()
            .any(|depot| depot.station_id == station_id(&stations[1])));
        assert!(!depots
            .iter()
            .any(|depot| depot.station_id == station_id(&stations[0])));
        let switches = compute_switches(&stations, &archetypes, &depots);
        assert!(switches.iter().any(|switch| {
            switch.station_id == station_id(&stations[0]) && switch.side == "turnback"
        }));
    }

    #[test]
    fn demand_picks_major_vs_standard_vs_halt_when_no_override() {
        let lines = vec![radial_line("L1")];
        let stations = vec![
            // First + last will be terminals; middle ones stay demand-based.
            st("L1", 0.0, 0.0, 0.0, 0.3),
            st("L1", 1_000.0, 0.01, 0.0, 0.8),
            st("L1", 2_000.0, 0.02, 0.0, 0.1),
            st("L1", 3_000.0, 0.03, 0.0, 0.5),
            st("L1", 4_000.0, 0.04, 0.0, 0.3),
        ];
        let a = compute_archetypes(&lines, &stations, &no_elevated());
        assert_eq!(a[0], "terminal");
        assert_eq!(a[1], "major"); // demand 0.8
        assert_eq!(a[2], "halt"); // demand 0.1
        assert_eq!(a[3], "standard"); // demand 0.5
        assert_eq!(a[4], "depot-terminal"); // farthest endpoint
    }

    #[test]
    fn haversine_recovers_small_distances_under_one_percent() {
        // ~111 m at the equator between lat 0 and lat 0.001.
        let d = haversine_m(0.0, 0.0, 0.001, 0.0);
        assert!((d - 111.0).abs() < 1.0, "expected ≈ 111 m, got {d:.2} m");
    }

    #[test]
    fn cumulative_cell_chainage_uses_diagonal_distance() {
        let cells = vec![(10, 10), (10, 11), (11, 12)];
        assert_eq!(cumulative_cell_chainage_m(&cells, 0, 20.0), 0.0);
        assert_eq!(cumulative_cell_chainage_m(&cells, 1, 20.0), 20.0);
        let total = cumulative_cell_chainage_m(&cells, 2, 20.0);
        assert!((total - (20.0 + 20.0_f64 * 2.0_f64.sqrt())).abs() < 1e-9);
    }

    // ---- v2 emitter: depot blocks, switches, costs --------------------

    #[test]
    fn fleet_sizing_formula_matches_rfc_0014_samawah_example() {
        // RFC 0014 §4 Samawah example, v0.3 calibration. Runtime is cruise
        // time plus stop-start penalties, so wider station spacing reduces
        // the round-trip cycle instead of being hidden inside a fixed
        // commercial-speed proxy. Three charging stops at 180 seconds add
        // their increment above the 60-second reference dwell.
        let peak = peak_revenue_trainsets(12_000.0, "tram-2car", false, 8, 3, 180);
        assert_eq!(peak, 24);
        let peak_metro = peak_revenue_trainsets(12_000.0, "metro-6car", false, 8, 3, 180);
        assert_eq!(peak_metro, 26);
        let fleet = fleet_total(peak);
        assert_eq!(fleet, 27);
        assert!(
            peak_revenue_trainsets(12_000.0, "tram-2car", false, 6, 3, 180)
                < peak_revenue_trainsets(12_000.0, "tram-2car", false, 10, 3, 180)
        );
        assert_eq!(
            peak_revenue_trainsets(63_000.0, "metro-4car", true, 20, 20, 180),
            26
        );
    }

    #[test]
    fn depot_blocks_emit_one_main_heavy_and_use_station_stabling_elsewhere() {
        let lines = vec![radial_line("L1")];
        let stations = vec![
            st("L1", 0.0, 0.0, 0.0, 0.3),
            st("L1", 6_000.0, 0.05, 0.0, 0.3),
            st("L1", 12_000.0, 0.10, 0.0, 0.3),
        ];
        // Mimic compute_archetypes output: first is `terminal`, last
        // is `depot-terminal` (farthest), middle is `standard`.
        let archetypes: Vec<&'static str> = vec!["terminal", "standard", "depot-terminal"];

        let depots = compute_depots(&lines, &stations, &archetypes, "tram-2car");
        assert_eq!(depots.len(), 1);
        // depot-terminal → main-heavy.
        assert!(depots.iter().any(|d| d.archetype == "main-heavy"));
        // The plain terminal is a powered overnight stabling point, not a depot.
        assert!(!depots.iter().any(|d| d.archetype == "layup-minimal"));
        // Every emitted depot has non-zero stalls.
        for d in &depots {
            assert!(d.fleet_stalls > 0);
        }
    }

    #[test]
    fn switches_emit_turnback_at_every_terminal_and_yard_fan_at_depot() {
        let lines = vec![radial_line("L1")];
        let stations = vec![
            st("L1", 0.0, 0.0, 0.0, 0.3),
            st("L1", 12_000.0, 0.10, 0.0, 0.3),
        ];
        let archetypes: Vec<&'static str> = vec!["terminal", "depot-terminal"];
        let depots = compute_depots(&lines, &stations, &archetypes, "tram-2car");
        let switches = compute_switches(&stations, &archetypes, &depots);

        // One turnback per terminal archetype = 2 turnbacks.
        let tbs: Vec<_> = switches.iter().filter(|s| s.side == "turnback").collect();
        assert_eq!(tbs.len(), 2);
        // Yard-throat count = depot-terminal's fleet_stalls.
        let yd: Vec<_> = switches
            .iter()
            .filter(|s| s.side == "yard-throat")
            .collect();
        let dt_stalls = depots
            .iter()
            .find(|d| d.archetype == "main-heavy")
            .unwrap()
            .fleet_stalls;
        assert_eq!(yd.len() as u32, dt_stalls);
        // Every switch uses no-9-mainline per RFC 0012 §3.
        for s in &switches {
            assert_eq!(s.kit, "no-9-mainline");
        }
    }

    #[test]
    fn cost_estimate_applies_rfc_0011_rates() {
        use osr_routing::civil::CivilSegment;
        // Toy line: 10 km at-grade + 1 km elevated + 0.5 km bridge =
        // 11.5 route-km. Three stations (1 standard, 1 terminal, 1
        // depot-terminal) and two depots (1 main-heavy + 1 layup).
        // Fleet: 12 trainsets of metro-6car at the configured
        // local-owner rolling-stock family cost.
        let civil_per_line = vec![vec![
            CivilSegment {
                class: CivilClass::AtGrade,
                from_idx: 0,
                to_idx: 10,
                length_m: 10_000.0, // 10 km x $3.0 M = $30.0 M
            },
            CivilSegment {
                class: CivilClass::Elevated,
                from_idx: 10,
                to_idx: 11,
                length_m: 1_000.0, // 1 km x $12.0 M = $12.0 M
            },
            CivilSegment {
                class: CivilClass::Bridge,
                from_idx: 11,
                to_idx: 12,
                length_m: 500.0, // 0.5 km x $18 M = $9.0 M
            },
        ]];
        let archetypes: Vec<&str> = vec!["terminal", "standard", "depot-terminal"];
        let depots = vec![
            DepotBlock {
                station_id: "S1".into(),
                archetype: "main-heavy",
                fleet_stalls: 15,
            },
            DepotBlock {
                station_id: "S2".into(),
                archetype: "layup-minimal",
                fleet_stalls: 5,
            },
        ];
        let c = compute_costs(&civil_per_line, &archetypes, &depots, 0, 12, "metro-6car");
        // Civil works: USD direct-procurement floor mirrored into EUR.
        assert!((c.at_grade_usd - 30_000_000.0).abs() < 1.0);
        assert!((c.at_grade_eur - 27_600_000.0).abs() < 1.0);
        assert!((c.elevated_usd - 12_000_000.0).abs() < 1.0);
        assert!((c.elevated_eur - 11_040_000.0).abs() < 1.0);
        assert!((c.bridge_usd - 9_000_000.0).abs() < 1.0);
        assert!((c.bridge_eur - 8_280_000.0).abs() < 1.0);
        assert!((c.junction_premium_eur - 0.0).abs() < 1.0);
        assert!((c.civil_subtotal_usd - 51_000_000.0).abs() < 1.0);
        assert!((c.civil_subtotal_eur - 46_920_000.0).abs() < 1.0);
        // Stations: terminal ($4.5 M) + standard ($2.5 M) + depot-terminal ($5.0 M).
        assert!((c.stations_usd - 12_000_000.0).abs() < 1.0);
        assert!((c.stations_eur - 11_040_000.0).abs() < 1.0);
        // Depots: workshop-focused main-heavy $8.0 M + layup $0.4 M.
        assert!((c.depots_usd - 8_400_000.0).abs() < 1.0);
        assert!((c.depots_eur - 7_728_000.0).abs() < 1.0);
        // Rolling stock: 12 x $1.68 M mirrored to EUR.
        assert!((c.rolling_stock_usd - 20_160_000.0).abs() < 1.0);
        assert!((c.rolling_stock_eur - 18_547_200.0).abs() < 1.0);
        // Production plant is costed once in the national brief, not per city.
        assert_eq!(c.production_plant_usd, 0.0);
        assert_eq!(c.production_plant_eur, 0.0);
        // Systems: residual signalling at 11.5 km × $0.05 M/km,
        // plus per-stop charging microgrid allowances.
        assert!((c.signalling_usd - 575_000.0).abs() < 1.0);
        assert!((c.signalling_eur - 529_000.0).abs() < 1.0);
        assert!((c.charging_microgrid_usd - 1_800_000.0).abs() < 1.0);
        assert!((c.charging_microgrid_eur - 1_656_000.0).abs() < 1.0);
        // Subtotal before EPC = $93.935 M.
        // EPC overhead = 7 % x $93.935 M = $6.57545 M.
        assert!((c.epc_overhead_usd - 6_575_450.0).abs() < 1.0);
        assert!((c.epc_overhead_eur - 6_049_414.0).abs() < 1.0);
        // Total = $100.51045 M = EUR 92.469614 M.
        assert!((c.total_usd - 100_510_450.0).abs() < 1.0);
        assert!((c.total_eur - 92_469_614.0).abs() < 1.0);
    }

    #[test]
    fn commodity_800v_cost_basis_reconciles_without_double_counting() {
        let config = cost_config();
        let onboard = &config.trainset_800v_core_electrical_usd;
        let calculated_per_car = onboard.traction_battery_system_per_car
            + f64::from(onboard.motor_controller_sets_per_car) * onboard.motor_controller_set
            + onboard.hv_distribution_per_car
            + onboard.lv_dc_dc_per_car
            + onboard.roof_pv_mppt_per_car;
        assert!((calculated_per_car - onboard.core_electrical_total_per_car).abs() < 0.01);
        assert_eq!(onboard.gross_battery_kwh_per_car, 225.0);
        assert!(
            onboard.core_electrical_total_per_car * 3.0
                < config.trainset_unit_usd["light-metro-3car"]
        );

        let station = &config.station_800v_module_usd;
        let calculated_station =
            station.stationary_lfp_500kwh + station.dcdc_500kw + station.contact_protection_control;
        assert!((calculated_station - station.equipment_total).abs() < 0.01);
        assert!(station.equipment_total <= station.normal_integrated_site);
    }
}
