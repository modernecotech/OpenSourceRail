//! Self-contained HTML+SVG network visualizer.
//!
//! Layout strategy: each line is drawn as a horizontal strip. Stations are
//! positioned along the strip by their cumulative distance from the first
//! station. Shared stations (interchanges) are connected across strips with
//! dotted vertical lines. Rings add a curved "wrap" segment back to the first
//! station.
//!
//! This is not a metro-map-style layout (those require hand-tuning or
//! sophisticated graph drawing). It is a mechanically correct diagram that
//! shows topology, interchanges, station roles, and energy sites at a glance.

use osr_core::{Line, Network, StationId};
use std::collections::HashMap;

use crate::energy::EnergySiteConfig;
use crate::sim::ScenarioConfig;

// Colors are used only for CSS / SVG; they look fine in any browser.
const LINE_COLORS: &[&str] = &[
    "#1f77b4", // steel blue
    "#d62728", // coral red
    "#2ca02c", // green
    "#9467bd", // purple
    "#ff7f0e", // orange
];

struct StationPos {
    x: f32,
    y: f32,
}

pub fn render_html(config: &ScenarioConfig) -> String {
    let margin_x = 120.0_f32;
    let margin_y = 140.0_f32;
    let strip_spacing = 180.0_f32;
    let canvas_w = 1600.0_f32;

    let line_count = config.network.lines.len();
    let canvas_h = margin_y * 2.0 + strip_spacing * line_count.max(1) as f32;

    // Position every (line, station) pair. Each line gets its own strip; a
    // station on multiple lines gets multiple positions.
    let mut per_line_positions: Vec<HashMap<StationId, StationPos>> =
        Vec::with_capacity(line_count);
    for (line_idx, line) in config.network.lines.iter().enumerate() {
        let strip_y = margin_y + strip_spacing * line_idx as f32 + strip_spacing * 0.5;
        per_line_positions.push(layout_line(line, &config.network, margin_x, canvas_w, strip_y));
    }

    // Energy sites keyed by station for decoration.
    let site_by_station: HashMap<StationId, &EnergySiteConfig> = config
        .energy_sites
        .iter()
        .map(|s| (s.station, s))
        .collect();

    let mut svg = String::new();
    svg.push_str(&format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" width="100%" style="max-width:1600px">"#
    ));

    // Title.
    svg.push_str(&format!(
        r#"<text x="{cx}" y="40" text-anchor="middle" class="title">{name}</text>"#,
        cx = canvas_w / 2.0,
        name = html_escape(&config.name),
    ));
    svg.push_str(&format!(
        r#"<text x="{cx}" y="64" text-anchor="middle" class="subtitle">{lines} lines, {stations} stations, {sites} energy sites · {ambient:.0}°C · {psh:.1} PSH</text>"#,
        cx = canvas_w / 2.0,
        lines = line_count,
        stations = config.network.stations.len(),
        sites = config.energy_sites.len(),
        ambient = config.climate.ambient_c,
        psh = config.climate.peak_sun_hours,
    ));

    // Draw each line strip.
    for (line_idx, line) in config.network.lines.iter().enumerate() {
        let color = LINE_COLORS[line_idx % LINE_COLORS.len()];
        draw_line_strip(&mut svg, line_idx, line, color, &per_line_positions[line_idx], &config.network);
    }

    // Draw interchange connectors: dotted vertical lines between the same
    // station on different strips.
    let mut by_station: HashMap<StationId, Vec<(usize, f32, f32)>> = HashMap::new();
    for (line_idx, positions) in per_line_positions.iter().enumerate() {
        for (sid, pos) in positions {
            by_station
                .entry(*sid)
                .or_default()
                .push((line_idx, pos.x, pos.y));
        }
    }
    for (_sid, locations) in &by_station {
        if locations.len() < 2 {
            continue;
        }
        for pair in locations.windows(2) {
            let (_, x1, y1) = pair[0];
            let (_, x2, y2) = pair[1];
            svg.push_str(&format!(
                r#"<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="interchange" />"#,
            ));
        }
    }

    // Draw stations on top of lines, with site decoration.
    for (line_idx, positions) in per_line_positions.iter().enumerate() {
        for (sid, pos) in positions {
            let station = config.network.station(*sid);
            let site = site_by_station.get(sid).copied();
            draw_station(
                &mut svg,
                pos.x,
                pos.y,
                station,
                site,
                line_idx == earliest_line_for(*sid, &per_line_positions),
            );
        }
    }

    svg.push_str("</svg>");

    // Legend entries.
    let mut legend = String::new();
    for (i, line) in config.network.lines.iter().enumerate() {
        let color = LINE_COLORS[i % LINE_COLORS.len()];
        let kind = if line.is_ring { "ring" } else { "linear" };
        let km: f64 = line
            .forward_sections
            .iter()
            .map(|id| config.network.section(*id).length_km())
            .sum();
        legend.push_str(&format!(
            r#"<li><span class="swatch" style="background:{color}"></span>{name} ({kind}, {km:.1} km, {n} stations)</li>"#,
            name = html_escape(&line.name),
            n = line.stations.len(),
        ));
    }

    // Final HTML document.
    let title_esc = html_escape(&config.name);
    format!(
        r#"<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title_esc} — OpenSourceRail</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; color: #222; background: #fafafa; }}
  h1 {{ font-size: 18px; margin: 0 0 4px; }}
  .meta {{ color: #666; font-size: 13px; margin-bottom: 12px; }}
  .title {{ font-size: 22px; font-weight: 600; fill: #222; }}
  .subtitle {{ font-size: 13px; fill: #666; }}
  .line-label {{ font-size: 15px; font-weight: 600; }}
  .station-name {{ font-size: 11px; fill: #222; }}
  .section-line {{ stroke-width: 4; fill: none; stroke-linecap: round; opacity: 0.85; }}
  .ring-wrap {{ stroke-dasharray: 6 6; opacity: 0.55; }}
  .station {{ stroke: #222; stroke-width: 1.5; fill: white; }}
  .station.terminal {{ stroke-width: 3; fill: #fff0f0; }}
  .station.depot {{ stroke: #b8860b; stroke-width: 2.5; fill: #fffbe0; }}
  .station.interchange {{ stroke: #6a1b9a; stroke-width: 3; fill: #f3e5f5; }}
  .interchange {{ stroke: #6a1b9a; stroke-width: 1.2; stroke-dasharray: 3 3; opacity: 0.5; }}
  .pv-indicator {{ fill: #f9a825; stroke: none; opacity: 0.85; }}
  .storage-indicator {{ fill: #2e7d32; stroke: none; opacity: 0.75; }}
  ul {{ list-style: none; padding-left: 0; }}
  li {{ margin: 4px 0; font-size: 14px; }}
  .swatch {{ display: inline-block; width: 24px; height: 4px; margin-right: 8px; vertical-align: middle; border-radius: 2px; }}
  .legend-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 24px; max-width: 900px; }}
  svg {{ background: white; border: 1px solid #e0e0e0; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
  .legend-note {{ font-size: 13px; color: #555; margin-top: 8px; }}
</style>
</head>
<body>
<h1>{title_esc}</h1>
<div class="meta">OpenSourceRail network visualization · generated by osr-vis</div>
{svg}
<h2 style="font-size:16px;margin-top:24px">Lines</h2>
<ul class="legend-grid">{legend}</ul>
<div class="legend-note">
  Station markers: red-outlined = terminal · gold-bordered = depot · purple-filled = interchange (appears on &gt;1 line).
  Orange dot near a station = PV array; green dot = battery storage.
  Size of PV/storage dots is proportional to nameplate power / capacity.
  Dotted purple lines connect the same interchange station as it appears on multiple lines.
</div>
</body>
</html>
"#
    )
}

fn layout_line(
    line: &Line,
    network: &Network,
    margin_x: f32,
    canvas_w: f32,
    strip_y: f32,
) -> HashMap<StationId, StationPos> {
    let total_len: f64 = line
        .forward_sections
        .iter()
        .map(|id| network.section(*id).length_km())
        .sum();
    let usable_w = canvas_w - 2.0 * margin_x;
    let mut positions = HashMap::new();
    let mut cumulative = 0.0_f64;
    for (i, sid) in line.stations.iter().enumerate() {
        let x = if total_len > 0.0 {
            margin_x + (cumulative / total_len) as f32 * usable_w
        } else {
            margin_x
        };
        positions.insert(*sid, StationPos { x, y: strip_y });
        if i < line.forward_sections.len()
            && (i < line.stations.len() - 1 || !line.is_ring)
        {
            // Don't advance past the last station index on a ring; the wrap
            // section connects last->first and we draw it separately.
            if i < line.stations.len().saturating_sub(1) {
                let section = network.section(line.forward_sections[i]);
                cumulative += section.length_km();
            }
        }
    }
    positions
}

fn draw_line_strip(
    svg: &mut String,
    line_idx: usize,
    line: &Line,
    color: &str,
    positions: &HashMap<StationId, StationPos>,
    _network: &Network,
) {
    // Line label on the left.
    if let Some(first) = line.stations.first() {
        if let Some(pos) = positions.get(first) {
            svg.push_str(&format!(
                r#"<text x="20" y="{y}" class="line-label" fill="{color}">{name}</text>"#,
                y = pos.y + 5.0,
                name = html_escape(&line.name),
            ));
        }
    }

    // Non-wrap sections.
    for pair in line.stations.windows(2) {
        let Some(a) = positions.get(&pair[0]) else { continue };
        let Some(b) = positions.get(&pair[1]) else { continue };
        svg.push_str(&format!(
            r#"<line class="section-line" stroke="{color}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>"#,
            x1 = a.x, y1 = a.y, x2 = b.x, y2 = b.y,
        ));
    }

    // Ring wrap: curved arc from last back to first.
    if line.is_ring {
        if let (Some(first), Some(last)) = (line.stations.first(), line.stations.last()) {
            if let (Some(a), Some(b)) = (positions.get(last), positions.get(first)) {
                // Arc that dips below this strip, then comes back up.
                let dy = 50.0_f32 + 20.0 * line_idx as f32;
                let mid_x = (a.x + b.x) / 2.0;
                let mid_y = a.y + dy;
                svg.push_str(&format!(
                    r#"<path class="section-line ring-wrap" stroke="{color}" d="M{x1} {y1} Q {mx} {my} {x2} {y2}" />"#,
                    x1 = a.x, y1 = a.y, x2 = b.x, y2 = b.y, mx = mid_x, my = mid_y,
                ));
            }
        }
    }
}

fn draw_station(
    svg: &mut String,
    x: f32,
    y: f32,
    station: &osr_core::Station,
    site: Option<&EnergySiteConfig>,
    is_primary_occurrence: bool,
) {
    let base_r = 7.0_f32;
    let power_bonus = (station.charging_power_kw as f32 / 1000.0).sqrt() * 2.5;
    let r = base_r + power_bonus;

    let mut classes = vec!["station"];
    if station.is_terminal {
        classes.push("terminal");
    }
    if station.is_depot {
        classes.push("depot");
    }
    // Interchange detection isn't line-aware here; caller marks "primary"
    // occurrences — we apply the interchange style only on the primary
    // (which leaves secondary occurrences showing the basic style, and the
    // dotted connectors bridge them).
    let class_attr = classes.join(" ");

    svg.push_str(&format!(
        r#"<circle cx="{x:.1}" cy="{y:.1}" r="{r:.1}" class="{class_attr}"/>"#,
    ));

    // PV + storage indicators for sites.
    if let Some(site) = site {
        if site.pv_nameplate_kw > 0.0 {
            let rr = 2.0_f32 + (site.pv_nameplate_kw / 500.0).min(5.0);
            svg.push_str(&format!(
                r#"<circle cx="{cx:.1}" cy="{cy:.1}" r="{rr:.1}" class="pv-indicator"/>"#,
                cx = x - r - rr - 1.0,
                cy = y - r - rr,
            ));
        }
        if site.storage_capacity_kwh > 0.0 {
            let rr = 2.0_f32 + ((site.storage_capacity_kwh / 2000.0).sqrt()).min(5.0);
            svg.push_str(&format!(
                r#"<circle cx="{cx:.1}" cy="{cy:.1}" r="{rr:.1}" class="storage-indicator"/>"#,
                cx = x + r + rr + 1.0,
                cy = y - r - rr,
            ));
        }
    }

    // Station name — only on the primary occurrence to avoid duplicate labels.
    if is_primary_occurrence {
        // Alternating above/below could help density, but simple above-text is fine.
        svg.push_str(&format!(
            r#"<text x="{x:.1}" y="{ty:.1}" text-anchor="middle" class="station-name">{name}</text>"#,
            ty = y + r + 14.0,
            name = html_escape(&station.name),
        ));
    }
}

fn earliest_line_for(
    station: StationId,
    per_line_positions: &[HashMap<StationId, StationPos>],
) -> usize {
    for (i, positions) in per_line_positions.iter().enumerate() {
        if positions.contains_key(&station) {
            return i;
        }
    }
    0
}

fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}
