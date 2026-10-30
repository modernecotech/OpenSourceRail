//! Deterministic planning assignment. Assigned demand is not a boarding forecast.
use crate::model::{CompiledLine, CompiledStation, DemandFile, DemandMetric, PlanningAssumptions};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub struct PassengerAssignment {
    pub method: String,
    pub transfer_rule: String,
    pub capacity_constrained: bool,
    pub sections: Vec<SectionLoad>,
    pub stations: Vec<StationLoad>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SectionLoad {
    pub period: String,
    pub line: String,
    pub from_station: String,
    pub to_station: String,
    pub passengers_per_hour: u64,
    pub capacity_pphpd: u32,
    pub utilization_percent: f64,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct StationLoad {
    pub period: String,
    pub station: String,
    pub boardings_per_hour: u64,
    pub alightings_per_hour: u64,
    pub transfer_boardings_per_hour: u64,
    pub one_headway_arrivals: f64,
    pub pedestrian_release_ready: bool,
}
#[derive(Clone)]
struct Edge {
    to: usize,
    minutes: f64,
    transfer: bool,
}

pub fn assign(
    demand: &DemandFile,
    lines: &[CompiledLine],
    stations: &[CompiledStation],
    assumptions: &PlanningAssumptions,
    capacity: impl Fn(&str, &crate::model::DemandPeriod) -> u32,
) -> (Vec<DemandMetric>, PassengerAssignment) {
    let mut ordered: Vec<_> = stations.iter().collect();
    ordered.sort_by(|a, b| a.id.cmp(&b.id));
    let lookup: BTreeMap<_, _> = ordered
        .iter()
        .enumerate()
        .map(|(i, s)| (s.id.as_str(), i))
        .collect();
    let mut output = PassengerAssignment {
        method: "deterministic shortest scheduled-time all-or-nothing assignment; loads may exceed capacity".into(),
        transfer_rule: "5-minute planning transfer only between interchange-tagged stations within 1 metre; no other proximity links".into(),
        ..Default::default()
    };
    let mut metrics = Vec::new();
    for period in &demand.periods {
        let caps: Vec<_> = ordered.iter().map(|s| capacity(&s.line, period)).collect();
        let headway = |i: usize| {
            if caps[i] > 0 {
                60.0 * f64::from(assumptions.passenger_capacity_per_train) / f64::from(caps[i])
            } else {
                0.0
            }
        };
        let mut graph = vec![Vec::<Edge>::new(); ordered.len()];
        for line in lines {
            let mut nodes: Vec<_> = ordered
                .iter()
                .enumerate()
                .filter(|(_, s)| s.line == line.id)
                .collect();
            nodes.sort_by(|a, b| a.1.s_m.total_cmp(&b.1.s_m).then(a.1.id.cmp(&b.1.id)));
            let mut pairs: Vec<_> = nodes
                .windows(2)
                .map(|p| (p[0].0, p[1].0, p[1].1.s_m - p[0].1.s_m))
                .collect();
            if line.shape == "ring" && nodes.len() > 2 {
                let first = nodes[0];
                let last = nodes[nodes.len() - 1];
                pairs.push((last.0, first.0, line.length_m - last.1.s_m + first.1.s_m));
            }
            for (a, b, distance) in pairs {
                if caps[a] == 0 || caps[b] == 0 || distance <= 0.0 {
                    continue;
                }
                let minutes = distance / 1000.0 / assumptions.average_speed_kmh * 60.0
                    + assumptions.station_dwell_min;
                graph[a].push(Edge {
                    to: b,
                    minutes,
                    transfer: false,
                });
                graph[b].push(Edge {
                    to: a,
                    minutes,
                    transfer: false,
                });
            }
        }
        for a in 0..ordered.len() {
            for b in a + 1..ordered.len() {
                let (sa, sb) = (ordered[a], ordered[b]);
                if sa.line == sb.line
                    || caps[a] == 0
                    || caps[b] == 0
                    || !sa.archetype.starts_with("interchange")
                    || !sb.archetype.starts_with("interchange")
                {
                    continue;
                }
                let dy = (sa.lat - sb.lat) * 111_195.0;
                let dx =
                    (sa.lon - sb.lon) * 111_195.0 * ((sa.lat + sb.lat) * 0.5).to_radians().cos();
                if dx.hypot(dy) <= 1.0 {
                    graph[a].push(Edge {
                        to: b,
                        minutes: 5.0,
                        transfer: true,
                    });
                    graph[b].push(Edge {
                        to: a,
                        minutes: 5.0,
                        transfer: true,
                    });
                }
            }
        }
        for edges in &mut graph {
            edges.sort_by_key(|e| e.to);
        }
        let mut loads: BTreeMap<(usize, usize), u64> = BTreeMap::new();
        let mut station_loads: BTreeMap<usize, (u64, u64, u64)> = BTreeMap::new();
        let mut paths = Vec::new();
        let mut flows: Vec<_> = demand
            .flows
            .iter()
            .filter(|f| f.period == period.id)
            .collect();
        flows.sort_by(|a, b| a.id.cmp(&b.id));
        for flow in flows {
            let (Some(&start), Some(&end)) = (
                lookup.get(flow.origin_station.as_str()),
                lookup.get(flow.destination_station.as_str()),
            ) else {
                continue;
            };
            // Each station has an off-train and an on-train state. Charge
            // expected waiting only on the first ride after entering or walking.
            let states = ordered.len() * 2;
            let mut dist = vec![f64::INFINITY; states];
            let mut prev = vec![None; states];
            let mut visited = vec![false; states];
            if caps[start] > 0 && start != end {
                dist[start * 2] = 0.0;
            }
            for _ in 0..states {
                let Some(u) = (0..states)
                    .filter(|&i| !visited[i] && dist[i].is_finite())
                    .min_by(|&a, &b| dist[a].total_cmp(&dist[b]).then(a.cmp(&b)))
                else {
                    break;
                };
                if u / 2 == end {
                    break;
                }
                visited[u] = true;
                for e in &graph[u / 2] {
                    let next = e.to * 2 + usize::from(!e.transfer);
                    let wait = if !e.transfer && u % 2 == 0 {
                        headway(u / 2) / 2.0
                    } else {
                        0.0
                    };
                    let proposed = dist[u] + e.minutes + wait;
                    if proposed < dist[next] {
                        dist[next] = proposed;
                        prev[next] = Some((u, e.transfer));
                    }
                }
            }
            let finish = if dist[end * 2] <= dist[end * 2 + 1] {
                end * 2
            } else {
                end * 2 + 1
            };
            let mut route = Vec::new();
            if dist[finish].is_finite() {
                let mut node = finish;
                while node != start * 2 {
                    let (parent, transfer) = prev[node].expect("reachable route has predecessors");
                    route.push((parent / 2, node / 2, transfer));
                    node = parent;
                }
                route.reverse();
                let count = u64::from(flow.passengers_per_hour);
                let mut rode_before = false;
                for (position, &(a, b, transfer)) in route.iter().enumerate() {
                    if transfer {
                        continue;
                    }
                    *loads.entry((a, b)).or_default() += count;
                    if position == 0 || route[position - 1].2 {
                        let entry = station_loads.entry(a).or_default();
                        entry.0 += count;
                        if rode_before {
                            entry.2 += count;
                        }
                    }
                    if position + 1 == route.len() || route[position + 1].2 {
                        station_loads.entry(b).or_default().1 += count;
                    }
                    rode_before = true;
                }
            }
            paths.push((flow, start, end, dist[finish], route));
        }
        for (flow, start, end, minutes, route) in paths {
            let capacity_pphpd = route
                .iter()
                .filter(|e| !e.2)
                .map(|e| caps[e.0])
                .min()
                .unwrap_or(0);
            let utilization_percent = route
                .iter()
                .filter(|e| !e.2)
                .map(|e| *loads.get(&(e.0, e.1)).unwrap() as f64 / f64::from(caps[e.0]) * 100.0)
                .max_by(f64::total_cmp);
            let status = match utilization_percent {
                None if minutes.is_finite() => "walk-only",
                None => "unavailable",
                Some(x) if x > 100.0 => "over-capacity",
                Some(x) if x > 85.0 => "near-capacity",
                _ => "within-capacity",
            };
            let mut route_stations = Vec::new();
            if minutes.is_finite() {
                route_stations.push(ordered[start].id.clone());
                route_stations.extend(route.iter().map(|e| ordered[e.1].id.clone()));
            }
            metrics.push(DemandMetric {
                flow_id: flow.id.clone(),
                period: period.id.clone(),
                origin_line: ordered[start].line.clone(),
                destination_line: ordered[end].line.clone(),
                transfers: route.iter().filter(|e| e.2).count() as u32,
                capacity_pphpd,
                utilization_percent,
                status: status.into(),
                route_stations,
                journey_minutes: minutes.is_finite().then_some(minutes),
            });
        }
        for ((a, b), load) in loads {
            output.sections.push(SectionLoad {
                period: period.id.clone(),
                line: ordered[a].line.clone(),
                from_station: ordered[a].id.clone(),
                to_station: ordered[b].id.clone(),
                passengers_per_hour: load,
                capacity_pphpd: caps[a],
                utilization_percent: load as f64 / f64::from(caps[a]) * 100.0,
            });
        }
        for (i, (board, alight, transfer)) in station_loads {
            output.stations.push(StationLoad {
                period: period.id.clone(),
                station: ordered[i].id.clone(),
                boardings_per_hour: board,
                alightings_per_hour: alight,
                transfer_boardings_per_hour: transfer,
                one_headway_arrivals: board as f64 * headway(i) / 60.0,
                pedestrian_release_ready: false,
            });
        }
    }
    metrics.sort_by(|a, b| a.flow_id.cmp(&b.flow_id));
    (metrics, output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::{DemandFlow, DemandPeriod, IntentState};
    fn station(id: &str, line: &str, s_m: f64, lat: f64, hub: bool) -> CompiledStation {
        CompiledStation {
            id: id.into(),
            name: id.into(),
            line: line.into(),
            lat,
            lon: 0.0,
            s_m,
            archetype: if hub { "interchange" } else { "standard" }.into(),
            state: IntentState::Generated,
            reason: String::new(),
        }
    }
    fn line(id: &str, ring: bool) -> CompiledLine {
        CompiledLine {
            id: id.into(),
            name: id.into(),
            shape: if ring { "ring" } else { "linear" }.into(),
            length_m: 4000.0,
            station_count: 3,
            routing_method: String::new(),
            routing_source_ids: vec![],
            demand_weight: None,
            state: IntentState::Generated,
            reason: String::new(),
        }
    }
    fn inputs(flows: &[(&str, &str, u32)]) -> (DemandFile, PlanningAssumptions) {
        (
            DemandFile {
                schema_version: 1,
                periods: vec![DemandPeriod {
                    id: "peak".into(),
                    name: "Peak".into(),
                    day_type: "weekday".into(),
                    from: "07:00".into(),
                    to: "09:00".into(),
                }],
                flows: flows
                    .iter()
                    .enumerate()
                    .map(|(i, (a, b, n))| DemandFlow {
                        id: format!("od-{i}"),
                        period: "peak".into(),
                        origin_station: (*a).into(),
                        destination_station: (*b).into(),
                        passengers_per_hour: *n,
                    })
                    .collect(),
            },
            PlanningAssumptions {
                passenger_capacity_per_train: 100,
                average_speed_kmh: 30.0,
                station_dwell_min: 0.5,
                terminal_turnaround_min: 2.0,
                geometry_regeneration_radius_m: 100.0,
            },
        )
    }
    #[test]
    fn shared_sections_accumulate_without_mixing_directions_and_are_order_independent() {
        let (d, a) = inputs(&[("a", "c", 400), ("b", "c", 300), ("c", "a", 200)]);
        let mut s = vec![
            station("a", "l", 0.0, 0.0, false),
            station("b", "l", 1000.0, 0.01, false),
            station("c", "l", 3000.0, 0.02, false),
        ];
        let (m, r) = assign(&d, &[line("l", false)], &s, &a, |_, _| 600);
        assert_eq!(m[0].status, "over-capacity");
        assert_eq!(m[1].status, "over-capacity");
        assert_eq!(m[2].status, "within-capacity");
        assert_eq!(
            r.sections
                .iter()
                .find(|e| e.from_station == "b" && e.to_station == "c")
                .unwrap()
                .passengers_per_hour,
            700
        );
        assert_eq!(
            r.stations.iter().map(|s| s.boardings_per_hour).sum::<u64>(),
            900
        );
        assert_eq!(
            r.stations
                .iter()
                .map(|s| s.alightings_per_hour)
                .sum::<u64>(),
            900
        );
        s.reverse();
        let (m2, r2) = assign(&d, &[line("l", false)], &s, &a, |_, _| 600);
        assert_eq!(
            serde_json::to_value((m, r)).unwrap(),
            serde_json::to_value((m2, r2)).unwrap()
        );
    }
    #[test]
    fn transfers_need_colocated_interchange_tags_and_route_service() {
        let (d, a) = inputs(&[("a", "d", 50)]);
        let mut s = vec![
            station("a", "l", 0.0, 0.0, false),
            station("b", "l", 1000.0, 0.01, true),
            station("c", "m", 0.0, 0.01, true),
            station("d", "m", 1000.0, 0.02, false),
        ];
        let lines = [line("l", false), line("m", false)];
        let (m, r) = assign(&d, &lines, &s, &a, |_, _| 600);
        assert_eq!(m[0].route_stations, vec!["a", "b", "c", "d"]);
        assert_eq!(m[0].transfers, 1);
        assert_eq!(m[0].journey_minutes, Some(20.0));
        let (walk, _) = inputs(&[("b", "c", 50)]);
        let (walking, walk_loads) = assign(&walk, &lines, &s, &a, |_, _| 600);
        assert_eq!(walking[0].journey_minutes, Some(5.0));
        assert_eq!(walking[0].status, "walk-only");
        assert!(walk_loads.sections.is_empty() && walk_loads.stations.is_empty());
        let (entry, _) = inputs(&[("b", "d", 50)]);
        assert_eq!(
            assign(&entry, &lines, &s, &a, |_, _| 600).0[0].journey_minutes,
            Some(12.5)
        );
        assert_eq!(
            r.stations
                .iter()
                .map(|s| s.transfer_boardings_per_hour)
                .sum::<u64>(),
            50
        );
        assert_eq!(
            r.stations.iter().map(|s| s.boardings_per_hour).sum::<u64>(),
            100
        );
        assert_eq!(
            assign(&d, &lines, &s, &a, |l, _| if l == "m" { 0 } else { 600 }).0[0].status,
            "unavailable"
        );
        s[2].lat += 0.001;
        assert_eq!(
            assign(&d, &lines, &s, &a, |_, _| 600).0[0].status,
            "unavailable"
        );
    }
    #[test]
    fn ring_uses_closing_section_and_disconnected_flows_do_not_create_loads() {
        let (d, a) = inputs(&[("a", "c", 70)]);
        let s = vec![
            station("a", "l", 0.0, 0.0, false),
            station("b", "l", 1000.0, 0.01, false),
            station("c", "l", 3000.0, 0.02, false),
        ];
        let (m, r) = assign(&d, &[line("l", true)], &s, &a, |_, _| 600);
        assert_eq!(m[0].route_stations, vec!["a", "c"]);
        assert_eq!(r.sections.len(), 1);
        let (m, r) = assign(&d, &[line("l", true)], &s, &a, |_, _| 0);
        assert_eq!(m[0].status, "unavailable");
        assert!(r.sections.is_empty());
        assert!(r.stations.is_empty());
    }
}
