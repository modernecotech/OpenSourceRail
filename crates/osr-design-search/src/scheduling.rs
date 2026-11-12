//! Opt-in deterministic delivery scheduling; no physical or business acceptance.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub tasks: Vec<Task>,
    pub resources: Vec<Resource>,
    pub max_work: u64,
}
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Task {
    pub task_id: String,
    pub ordinal: i64,
    pub duration: f64,
    pub predecessors: Vec<String>,
    pub requests: Vec<Requirement>,
}
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Requirement {
    pub resource_id: String,
    pub units: i64,
}
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Resource {
    pub resource_id: String,
    pub capacity: usize,
}
#[derive(Debug, Serialize)]
pub struct Allocation {
    pub resource_id: String,
    pub units: Vec<usize>,
}
#[derive(Debug, Serialize)]
pub struct Scheduled {
    pub task_id: String,
    pub start_workday: f64,
    pub finish_workday: f64,
    pub resource_allocations: Vec<Allocation>,
    pub status: &'static str,
}
#[derive(Debug, Serialize)]
pub struct ResultRecord {
    pub tasks: Vec<Scheduled>,
    pub finish_workday: f64,
    pub capacity_pass: bool,
    pub duration_is_conditional_bound: bool,
    pub engineering_release: bool,
}
fn max(a: f64, b: f64) -> f64 {
    if b > a {
        b
    } else {
        a
    }
}
fn id(v: &str) -> bool {
    !v.is_empty() && v.len() <= 256
}

pub fn schedule(request: Request) -> Result<ResultRecord, String> {
    if request.schema != "osr-delivery-schedule-request/1"
        || request.tasks.is_empty()
        || request.tasks.len() > 10_000
        || request.resources.len() > 10_000
        || request.max_work == 0
        || request.max_work > 100_000_000
    {
        return Err("Bounded scheduling request required".into());
    }
    let mut pools = BTreeMap::new();
    let mut total_capacity = 0usize;
    for r in &request.resources {
        total_capacity = total_capacity
            .checked_add(r.capacity)
            .ok_or("Capacity overflow")?;
        if !id(&r.resource_id)
            || r.capacity > 100_000
            || total_capacity > 1_000_000
            || pools.contains_key(&r.resource_id)
        {
            return Err("Bounded unique resource required".into());
        }
        pools.insert(
            r.resource_id.clone(),
            (0..r.capacity).map(|i| (0.0, i)).collect::<Vec<_>>(),
        );
    }
    let mut by = BTreeMap::new();
    for t in &request.tasks {
        if !id(&t.task_id)
            || !t.duration.is_finite()
            || t.duration <= 0.0
            || t.duration > 1e9
            || t.predecessors.len() > 10_000
            || t.requests.len() > 256
            || by.contains_key(&t.task_id)
            || t.requests
                .iter()
                .any(|r| !id(&r.resource_id) || r.units.abs_diff(0) > 100_000)
        {
            return Err("Bounded unique task required".into());
        }
        by.insert(t.task_id.clone(), t);
    }
    let mut successors: BTreeMap<String, Vec<String>> =
        by.keys().map(|k| (k.clone(), Vec::new())).collect();
    let mut counts = BTreeMap::new();
    for (key, t) in &by {
        let unique: BTreeSet<_> = t.predecessors.iter().collect();
        if unique.len() != t.predecessors.len() || unique.iter().any(|x| !by.contains_key(*x)) {
            return Err("Unknown or duplicate task predecessor".into());
        }
        counts.insert(key.clone(), t.predecessors.len());
        for p in &t.predecessors {
            successors.get_mut(p).unwrap().push(key.clone());
        }
    }
    let mut ready: BTreeSet<_> = counts
        .iter()
        .filter(|(_, n)| **n == 0)
        .map(|(k, _)| k.clone())
        .collect();
    let mut done: BTreeMap<String, Scheduled> = BTreeMap::new();
    let mut capacity_pass = true;
    let mut work = 0u64;
    let mut allocated = 0usize;
    let mut reservations: BTreeMap<(String, usize), Vec<(f64, f64)>> = BTreeMap::new();
    while !ready.is_empty() {
        let mut best: Option<(f64, i64, String, bool)> = None;
        for key in &ready {
            let t = by[key];
            work = work
                .checked_add(1 + t.predecessors.len() as u64 + t.requests.len() as u64)
                .ok_or("Work overflow")?;
            if work > request.max_work {
                return Err("Scheduling work budget exhausted".into());
            }
            let mut start = t
                .predecessors
                .first()
                .map_or(0.0, |p| done[p].finish_workday);
            for p in t.predecessors.iter().skip(1) {
                start = max(start, done[p].finish_workday);
            }
            let mut valid = true;
            for r in &t.requests {
                match pools.get(&r.resource_id) {
                    Some(pool) if r.units >= 1 && r.units as usize <= pool.len() => {
                        start = max(start, pool[r.units as usize - 1].0);
                    }
                    _ => {
                        valid = false;
                        break;
                    }
                }
            }
            let value = (start, t.ordinal, key.clone(), valid);
            if best
                .as_ref()
                .is_none_or(|b| start < b.0 || start == b.0 && (t.ordinal, key) < (b.1, &b.2))
            {
                best = Some(value);
            }
        }
        let (start, _, key, valid) = best.unwrap();
        ready.remove(&key);
        let t = by[&key];
        let finish = start + t.duration;
        let mut allocations = Vec::new();
        if !valid {
            capacity_pass = false;
        } else {
            for r in &t.requests {
                let pool = pools.get_mut(&r.resource_id).unwrap();
                allocated = allocated
                    .checked_add(r.units as usize)
                    .ok_or("Allocation overflow")?;
                if allocated > 1_000_000 {
                    return Err("Scheduling allocation budget exhausted".into());
                }
                work = work.checked_add(pool.len() as u64).ok_or("Work overflow")?;
                if work > request.max_work {
                    return Err("Scheduling work budget exhausted".into());
                }
                let selected: Vec<_> = pool.drain(..r.units as usize).collect();
                allocations.push(Allocation {
                    resource_id: r.resource_id.clone(),
                    units: selected.iter().map(|x| x.1).collect(),
                });
                for (_, i) in selected {
                    reservations
                        .entry((r.resource_id.clone(), i))
                        .or_default()
                        .push((start, finish));
                    pool.push((finish, i));
                }
                pool.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
            }
        }
        done.insert(
            key.clone(),
            Scheduled {
                task_id: key.clone(),
                start_workday: start,
                finish_workday: finish,
                resource_allocations: allocations,
                status: if valid {
                    "scheduled-conditional"
                } else {
                    "unpriced-resource-hold"
                },
            },
        );
        for successor in &successors[&key] {
            let n = counts.get_mut(successor).unwrap();
            *n -= 1;
            if *n == 0 {
                ready.insert(successor.clone());
            }
        }
    }
    if done.len() != by.len() {
        return Err("Cyclic delivery task graph".into());
    }
    for intervals in reservations.values_mut() {
        intervals.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.total_cmp(&b.1)));
        if intervals.windows(2).any(|p| p[0].1 > p[1].0 + 1e-9) {
            return Err("Overlapping constrained delivery resource".into());
        }
    }
    let finish = done.values().map(|x| x.finish_workday).fold(0.0, max);
    let mut tasks: Vec<_> = done.into_values().collect();
    tasks.sort_by(|a, b| {
        a.start_workday
            .total_cmp(&b.start_workday)
            .then(a.task_id.cmp(&b.task_id))
    });
    Ok(ResultRecord {
        tasks,
        finish_workday: finish,
        capacity_pass,
        duration_is_conditional_bound: true,
        engineering_release: false,
    })
}
