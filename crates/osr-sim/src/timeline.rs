//! Playback-oriented view of a finished [`SimResult`].
//!
//! Derives train positions over time from the sparse `Event` stream so
//! the GUI can animate trains along their line at any playback speed
//! without stepping the full sim again.
//!
//! The algorithm is O(events × trains) at construction time and O(1)
//! per frame at playback time. Every event boundary is a keyframe;
//! positions between adjacent keyframes are interpolated linearly in
//! the line's station_m axis.

use std::collections::{BTreeMap, HashMap};

use osr_core::{Network, StationId, TrainId};
use serde::{Deserialize, Serialize};

use crate::sim::{Event, EventKind, SimResult};

/// One frame in the playback — a per-train position snapshot at a
/// specific sim-time second.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TrainFrame {
    pub train: TrainId,
    pub line_index: usize,
    /// Distance along the line's forward direction in metres.
    /// Wraps at `line_total_length_m` for ring lines.
    pub station_m: f64,
    /// Short phase tag used by the GUI for colouring — one of
    /// "idle", "dwelling", "traveling", "charging", "soc-warning".
    pub phase: String,
    /// Last event affecting this train (for the inspector sidebar).
    pub last_event: Option<String>,
    /// State-of-charge at this frame, 0.0–1.0.
    pub soc: f32,
}

/// All frames at one sim-time second.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct TimelineFrame {
    pub sim_time_s: u32,
    pub trains: Vec<TrainFrame>,
}

/// Derived playback timeline over `[0, duration_s]` at 1 Hz.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct SimTimeline {
    pub duration_s: u32,
    pub frames: Vec<TimelineFrame>,
    /// Pre-computed line total length (m) per line index — used by the
    /// GUI to convert `station_m` to a pixel x on the strip.
    pub line_total_length_m: Vec<f64>,
}

impl SimTimeline {
    /// Build a timeline from a finished sim result.
    pub fn from_result(result: &SimResult, network: &Network) -> Self {
        let duration_s = result.sim_duration_s;

        // Pre-compute per-line total length and a station_m lookup per line
        // × station.
        let mut line_total_length_m = Vec::with_capacity(network.lines.len());
        let mut station_m_by_line: Vec<BTreeMap<StationId, f64>> =
            Vec::with_capacity(network.lines.len());
        for line in &network.lines {
            let mut total = 0.0_f64;
            let mut station_m: BTreeMap<StationId, f64> = BTreeMap::new();
            for (i, &sid) in line.stations.iter().enumerate() {
                station_m.insert(sid, total);
                if let Some(&sec_id) = line.forward_sections.get(i) {
                    if let Some(sec) = network.sections.get(&sec_id) {
                        total += sec.length_mm as f64 / 1000.0;
                    }
                }
            }
            line_total_length_m.push(total);
            station_m_by_line.push(station_m);
        }

        // Partition events by train.
        let mut events_by_train: HashMap<TrainId, Vec<&Event>> = HashMap::new();
        for event in &result.events {
            events_by_train.entry(event.train).or_default().push(event);
        }
        for (_, v) in events_by_train.iter_mut() {
            v.sort_by_key(|e| e.sim_time_s);
        }

        // Per-train line index (derived from the first event's `line`
        // field).
        let mut line_index_by_train: HashMap<TrainId, usize> = HashMap::new();
        let line_name_to_index: HashMap<String, usize> = network
            .lines
            .iter()
            .enumerate()
            .map(|(i, l)| (l.name.clone(), i))
            .collect();
        for (&tid, evs) in &events_by_train {
            if let Some(first) = evs.first() {
                if let Some(&idx) = line_name_to_index.get(&first.line) {
                    line_index_by_train.insert(tid, idx);
                }
            }
        }

        // Render each second of sim time.
        let mut frames = Vec::with_capacity(duration_s as usize + 1);
        for t in 0..=duration_s {
            let mut train_frames = Vec::new();
            for (&tid, evs) in &events_by_train {
                let Some(&line_idx) = line_index_by_train.get(&tid) else {
                    continue;
                };
                let sm_lookup = &station_m_by_line[line_idx];

                let (station_m, phase, last_event, soc) = resolve_at_time(t, evs, sm_lookup);
                train_frames.push(TrainFrame {
                    train: tid,
                    line_index: line_idx,
                    station_m,
                    phase: phase.to_string(),
                    last_event,
                    soc,
                });
            }
            frames.push(TimelineFrame {
                sim_time_s: t,
                trains: train_frames,
            });
        }

        SimTimeline {
            duration_s,
            frames,
            line_total_length_m,
        }
    }

    /// Get the frame for a given sim-time. Clamps to [0, duration_s].
    pub fn frame_at(&self, t_s: u32) -> Option<&TimelineFrame> {
        if self.frames.is_empty() {
            return None;
        }
        let idx = (t_s as usize).min(self.frames.len() - 1);
        self.frames.get(idx)
    }
}

fn resolve_at_time(
    t: u32,
    events: &[&Event],
    station_m_lookup: &BTreeMap<StationId, f64>,
) -> (f64, &'static str, Option<String>, f32) {
    // Find the most recent event at or before t, plus the next event
    // after t (for interpolation).
    let before_idx = events
        .iter()
        .rposition(|e| e.sim_time_s <= t)
        .unwrap_or(usize::MAX);
    let before = if before_idx == usize::MAX {
        None
    } else {
        Some(events[before_idx])
    };
    let after = if before_idx == usize::MAX {
        events.first().copied()
    } else {
        events.get(before_idx + 1).copied()
    };

    match before {
        None => (0.0, "idle", None, 0.95),
        Some(b) => {
            let last_text = Some(format!(
                "t={} {:?}{}",
                b.sim_time_s,
                b.kind,
                b.station_name
                    .as_ref()
                    .map(|s| format!(" @ {s}"))
                    .unwrap_or_default()
            ));
            match &b.kind {
                EventKind::ArriveStation { soc } => {
                    let station_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    (station_m, "dwelling", last_text, *soc)
                }
                EventKind::DepartStation => {
                    // Interpolate toward the next Arrive event (or the
                    // next dispatched station).
                    let start_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    let (end_m, end_t, soc_est) = match after {
                        Some(e) => {
                            let em = e
                                .station
                                .and_then(|s| station_m_lookup.get(&s).copied())
                                .unwrap_or(start_m);
                            let soc = match &e.kind {
                                EventKind::ArriveStation { soc } => *soc,
                                EventKind::SocWarning { soc } => *soc,
                                _ => 0.85,
                            };
                            (em, e.sim_time_s, soc)
                        }
                        None => (start_m, b.sim_time_s + 60, 0.85),
                    };
                    let duration = (end_t.saturating_sub(b.sim_time_s)).max(1) as f64;
                    let progress = ((t - b.sim_time_s) as f64 / duration).clamp(0.0, 1.0);
                    let station_m = start_m + (end_m - start_m) * progress;
                    (station_m, "traveling", last_text, soc_est)
                }
                EventKind::Dispatched => {
                    let station_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    (station_m, "traveling", last_text, 0.95)
                }
                EventKind::ChargingTick { .. } => {
                    let station_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    (station_m, "charging", last_text, 0.8)
                }
                EventKind::Turnaround => {
                    let station_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    (station_m, "dwelling", last_text, 0.9)
                }
                EventKind::SocWarning { soc } => {
                    let station_m = b
                        .station
                        .and_then(|s| station_m_lookup.get(&s).copied())
                        .unwrap_or(0.0);
                    (station_m, "soc-warning", last_text, *soc)
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_result_produces_empty_timeline() {
        let result = SimResult::default();
        let network = Network::default();
        let tl = SimTimeline::from_result(&result, &network);
        // duration_s = 0 but we still produce a frame at t=0.
        assert_eq!(tl.duration_s, 0);
        assert_eq!(tl.frames.len(), 1);
    }

    #[test]
    fn frame_at_clamps_to_duration() {
        let mut tl = SimTimeline::default();
        tl.duration_s = 10;
        tl.frames = (0..=10)
            .map(|t| TimelineFrame {
                sim_time_s: t,
                trains: vec![],
            })
            .collect();
        assert_eq!(tl.frame_at(0).unwrap().sim_time_s, 0);
        assert_eq!(tl.frame_at(10).unwrap().sim_time_s, 10);
        assert_eq!(tl.frame_at(999).unwrap().sim_time_s, 10);
    }
}
