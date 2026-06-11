//! Shared network-rendering primitives for the OSR operator GUIs
//! ([`osr-sim-gui`] and [`osr-occ-gui`]) per [RFC 0018](../../docs/rfcs/0018-operator-guis.md).
//!
//! Draws the network as one horizontal strip per line, stations
//! placed along the strip by cumulative distance, with coloured
//! overlays for section state, train positions, and faults.
//!
//! The same layout drives the static HTML visualiser at
//! `osr_sim::vis` — the two are deliberately consistent so a
//! dispatcher and a designer see the same picture.

#![forbid(unsafe_code)]

use std::collections::BTreeMap;

use egui::{Align2, Color32, FontId, Painter, Pos2, Rect, Rounding, Stroke, Vec2};
use osr_core::{Line, Network, StationId};

pub mod palette;

pub use palette::Palette;

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

/// Per-line horizontal strip + per-station pixel position.
#[derive(Debug, Clone)]
pub struct NetworkLayout {
    /// One strip per line. `strips[i]` carries line `i`'s y-coordinate and
    /// its per-station x-coordinate.
    pub strips: Vec<LineStrip>,
    /// Overall layout bounding box in painter coordinates.
    pub extent: Rect,
}

#[derive(Debug, Clone)]
pub struct LineStrip {
    pub line_name: String,
    pub y: f32,
    /// Station id → x-coordinate on the strip.
    pub stations: BTreeMap<StationId, f32>,
    /// Is this line a ring? Rings get an extra "wrap" segment drawn on the
    /// right edge of the strip.
    pub is_ring: bool,
}

impl NetworkLayout {
    /// Compute a default layout for `network` inside `paint_rect`. Lines are
    /// stacked top-to-bottom; stations are spaced proportionally to
    /// cumulative `distance_from_prev_m`.
    pub fn build(network: &Network, paint_rect: Rect) -> Self {
        let n_lines = network.lines.len().max(1);
        let strip_height = paint_rect.height() / (n_lines as f32 + 1.0);
        let left_margin = paint_rect.left() + 60.0;
        let right_margin = paint_rect.right() - 30.0;

        let mut strips = Vec::new();
        for (i, line) in network.lines.iter().enumerate() {
            let y = paint_rect.top() + (i as f32 + 1.0) * strip_height;
            let is_ring = line.is_ring;
            let stations = station_positions_on_strip(network, line, left_margin, right_margin);
            strips.push(LineStrip {
                line_name: line.name.clone(),
                y,
                stations,
                is_ring,
            });
        }
        NetworkLayout {
            strips,
            extent: paint_rect,
        }
    }

    /// Convert a (line index, `station_m`) pair to a painter x-coordinate.
    /// Used to place moving trains on the strip.
    pub fn station_m_to_x(
        &self,
        line_idx: usize,
        station_m: f64,
        total_line_length_m: f64,
    ) -> Option<f32> {
        let strip = self.strips.get(line_idx)?;
        let (left, right) = strip_edges(strip)?;
        if total_line_length_m <= 0.0 {
            return Some(left);
        }
        let t = (station_m / total_line_length_m).clamp(0.0, 1.0) as f32;
        Some(left + (right - left) * t)
    }
}

fn strip_edges(strip: &LineStrip) -> Option<(f32, f32)> {
    let left = strip
        .stations
        .values()
        .copied()
        .fold(f32::INFINITY, f32::min);
    let right = strip
        .stations
        .values()
        .copied()
        .fold(f32::NEG_INFINITY, f32::max);
    if left.is_finite() && right.is_finite() {
        Some((left, right))
    } else {
        None
    }
}

fn station_positions_on_strip(
    network: &Network,
    line: &Line,
    left: f32,
    right: f32,
) -> BTreeMap<StationId, f32> {
    let total = line_total_length_m(network, line);
    let mut positions = BTreeMap::new();
    let mut cumulative = 0.0_f64;

    let station_ids: Vec<StationId> = line.stations.iter().copied().collect();
    for (i, &sid) in station_ids.iter().enumerate() {
        if i == 0 {
            positions.insert(sid, left);
            continue;
        }
        // Use forward-direction sections to compute length between
        // adjacent stations. Each line's forward_sections[i] connects
        // stations[i] → stations[i+1].
        let section_idx = i - 1;
        if let Some(sec_id) = line.forward_sections.get(section_idx) {
            if let Some(sec) = network.sections.get(sec_id) {
                cumulative += sec.length_mm as f64 / 1000.0;
            }
        }
        let t = if total > 0.0 {
            (cumulative / total) as f32
        } else {
            0.0
        };
        let x = left + (right - left) * t.clamp(0.0, 1.0);
        positions.insert(sid, x);
    }
    positions
}

/// Total line length, metres — sum of all forward-direction sections.
pub fn line_total_length_m(network: &Network, line: &Line) -> f64 {
    line.forward_sections
        .iter()
        .filter_map(|s| network.sections.get(s))
        .map(|s| s.length_mm as f64 / 1000.0)
        .sum()
}

// ---------------------------------------------------------------------------
// Drawing
// ---------------------------------------------------------------------------

/// Draw the network backbone: one horizontal strip per line, stations as
/// filled circles, ring-wrap arcs if applicable, and line labels.
pub fn draw_network(
    painter: &Painter,
    layout: &NetworkLayout,
    network: &Network,
    palette: &Palette,
) {
    for strip in &layout.strips {
        draw_strip(painter, strip, network, palette);
    }
}

fn draw_strip(painter: &Painter, strip: &LineStrip, network: &Network, palette: &Palette) {
    // Line strip.
    if let Some((left, right)) = strip_edges(strip) {
        painter.line_segment(
            [Pos2::new(left, strip.y), Pos2::new(right, strip.y)],
            Stroke::new(3.0, palette.line_track),
        );

        if strip.is_ring {
            // Ring wrap: semi-arc from right → left above the strip.
            let rect =
                Rect::from_min_max(Pos2::new(left, strip.y - 30.0), Pos2::new(right, strip.y));
            painter.rect_stroke(
                rect,
                Rounding::same(30.0),
                Stroke::new(1.5, palette.line_track),
            );
        }
    }

    // Line label.
    if let Some(&first_x) = strip.stations.values().next() {
        painter.text(
            Pos2::new(first_x - 50.0, strip.y),
            Align2::CENTER_CENTER,
            &strip.line_name,
            FontId::proportional(13.0),
            palette.label,
        );
    }

    // Stations — alternate labels above / below the strip so adjacent
    // names don't overlap on densely-stationed lines. We need to
    // iterate in line-order (not BTreeMap-key order) for the
    // alternation to follow the geographic sequence.
    let ordered_ids: Vec<(osr_core::StationId, f32)> = network
        .lines
        .iter()
        .find(|l| l.name == strip.line_name)
        .map(|line| {
            line.stations
                .iter()
                .filter_map(|sid| strip.stations.get(sid).map(|&x| (*sid, x)))
                .collect()
        })
        .unwrap_or_else(|| strip.stations.iter().map(|(s, x)| (*s, *x)).collect());

    for (i, (sid, x)) in ordered_ids.iter().enumerate() {
        let name = network
            .stations
            .get(sid)
            .map(|s| s.name.as_str())
            .unwrap_or("?");
        let pos = Pos2::new(*x, strip.y);
        painter.circle_filled(pos, 5.0, palette.station);
        painter.circle_stroke(pos, 5.0, Stroke::new(1.0, palette.label));
        // Alternate: even-index labels go below the strip, odd-index
        // labels go above. Keeps adjacent labels from overlapping
        // horizontally on dense lines.
        let (anchor, y) = if i % 2 == 0 {
            (Align2::CENTER_TOP, strip.y + 14.0)
        } else {
            (Align2::CENTER_BOTTOM, strip.y - 14.0)
        };
        painter.text(
            Pos2::new(*x, y),
            anchor,
            name,
            FontId::proportional(10.0),
            palette.label,
        );
    }
}

/// Draw a train dot at `(line_idx, station_m)` with colour `colour`.
pub fn draw_train(
    painter: &Painter,
    layout: &NetworkLayout,
    network: &Network,
    line_idx: usize,
    station_m: f64,
    label: &str,
    colour: Color32,
) {
    if let Some(line) = network.lines.get(line_idx) {
        let total = line_total_length_m(network, line);
        if let Some(x) = layout.station_m_to_x(line_idx, station_m, total) {
            let y = layout.strips.get(line_idx).map(|s| s.y).unwrap_or(0.0);
            let pos = Pos2::new(x, y - 12.0);
            painter.rect_filled(
                Rect::from_center_size(pos, Vec2::new(14.0, 10.0)),
                Rounding::same(2.0),
                colour,
            );
            painter.text(
                Pos2::new(x, y - 28.0),
                Align2::CENTER_BOTTOM,
                label,
                FontId::monospace(9.0),
                Color32::WHITE,
            );
        }
    }
}

/// Draw a coloured highlight over the strip segment between two stations —
/// used by the OCC GUI to render `SectionIntrusion::Present` and by the sim
/// GUI to show active `MaintenanceOverride` windows.
pub fn draw_section_state(
    painter: &Painter,
    layout: &NetworkLayout,
    line_idx: usize,
    from_station: StationId,
    to_station: StationId,
    colour: Color32,
) {
    let Some(strip) = layout.strips.get(line_idx) else {
        return;
    };
    let Some(&x1) = strip.stations.get(&from_station) else {
        return;
    };
    let Some(&x2) = strip.stations.get(&to_station) else {
        return;
    };
    let (left, right) = if x1 < x2 { (x1, x2) } else { (x2, x1) };
    let rect = Rect::from_min_max(
        Pos2::new(left, strip.y - 4.0),
        Pos2::new(right, strip.y + 4.0),
    );
    painter.rect_filled(rect, Rounding::same(2.0), colour);
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{Line, Network, Section, SectionId, Station};

    fn tiny_network() -> Network {
        let mut net = Network::default();
        for i in 1..=3 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("S{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 0,
                    is_terminal: false,
                    is_depot: false,
                },
            );
        }
        for i in 0..2 {
            let sec_id = SectionId::new(1000 + i);
            net.sections.insert(
                sec_id,
                Section {
                    id: sec_id,
                    from_station: StationId::new(i as u64 + 1),
                    to_station: StationId::new(i as u64 + 2),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
        }
        net.lines.push(Line {
            name: "L1".into(),
            stations: vec![StationId::new(1), StationId::new(2), StationId::new(3)],
            forward_sections: vec![SectionId::new(1000), SectionId::new(1001)],
            reverse_sections: vec![],
            is_ring: false,
        });
        net
    }

    #[test]
    fn layout_places_every_station() {
        let net = tiny_network();
        let rect = Rect::from_min_max(Pos2::new(0.0, 0.0), Pos2::new(800.0, 600.0));
        let layout = NetworkLayout::build(&net, rect);
        assert_eq!(layout.strips.len(), 1);
        assert_eq!(layout.strips[0].stations.len(), 3);
    }

    #[test]
    fn line_total_length_sums_sections() {
        let net = tiny_network();
        let len = line_total_length_m(&net, &net.lines[0]);
        assert!((len - 2000.0).abs() < 1e-6);
    }

    #[test]
    fn station_m_to_x_interpolates() {
        let net = tiny_network();
        let rect = Rect::from_min_max(Pos2::new(0.0, 0.0), Pos2::new(800.0, 600.0));
        let layout = NetworkLayout::build(&net, rect);
        let total = line_total_length_m(&net, &net.lines[0]);
        // Station 0 sits at the leftmost x; station_m = total sits at the
        // rightmost; midpoint is halfway.
        let x_mid = layout.station_m_to_x(0, total / 2.0, total).unwrap();
        let left = layout.strips[0].stations[&StationId::new(1)];
        let right = layout.strips[0].stations[&StationId::new(3)];
        let expected_mid = (left + right) / 2.0;
        assert!(
            (x_mid - expected_mid).abs() < 1.0,
            "expected ~{expected_mid}, got {x_mid}"
        );
    }
}
