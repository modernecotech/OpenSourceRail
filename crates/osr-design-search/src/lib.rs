//! Deterministic research search kernels, independent of engineering acceptance.
//!
//! Gene proposals are not physical designs. The coordinator materializes them,
//! assigns canonical physical identities and admits independent evaluators.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

pub const REQUEST_SCHEMA: &str = "osr-search-kernel-request/1";
pub const RESULT_SCHEMA: &str = "osr-search-kernel-result/1";
pub const MAX_INPUT_BYTES: usize = 64 * 1024 * 1024;
const MAX_POINTS: usize = 100_000;
const MAX_ATTEMPTS: usize = 1_000_000;

fn default_work() -> u64 {
    100_000_000
}

#[derive(Debug, Deserialize)]
#[serde(tag = "operation", deny_unknown_fields)]
pub enum Request {
    #[serde(rename = "pareto")]
    Pareto {
        schema: String,
        points: Vec<Point>,
        #[serde(default = "default_work")]
        max_work: u64,
    },
    #[serde(rename = "propose")]
    Propose {
        schema: String,
        seed: u64,
        generation: u32,
        limit: usize,
        max_attempts: usize,
        axes: Vec<Axis>,
        family_axis: usize,
        parents: Vec<Parent>,
        seen: Vec<Vec<usize>>,
        weights: [u32; 3],
    },
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Point {
    pub candidate_id: String,
    pub cell_id: String,
    pub values: Vec<f64>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Axis {
    pub name: String,
    pub choices: usize,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Parent {
    pub candidate_id: String,
    pub genes: Vec<usize>,
    /// Positive bounded proposal bias, never a physical acceptance score.
    #[serde(default = "default_parent_weight")]
    pub weight: u32,
}

fn default_parent_weight() -> u32 {
    1
}

#[derive(Debug, Serialize, PartialEq)]
#[serde(untagged)]
pub enum ResultRecord {
    Pareto(ParetoResult),
    Propose(ProposalResult),
}

#[derive(Debug, Serialize, PartialEq)]
pub struct Cell {
    pub cell_id: String,
    pub retained_candidate_ids: Vec<String>,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct Exclusion {
    pub candidate_id: String,
    pub cell_id: String,
    pub dominated_by: String,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct Statistics {
    pub point_count: usize,
    pub objective_count: usize,
    pub work: u64,
    pub max_work: u64,
    pub method: &'static str,
    pub work_scope: &'static str,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct ParetoResult {
    pub schema: &'static str,
    pub operation: &'static str,
    pub cells: Vec<Cell>,
    pub retained_candidate_ids: Vec<String>,
    pub global_front: Vec<String>,
    pub dominated: Vec<Exclusion>,
    pub statistics: Statistics,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct Proposal {
    pub genes: Vec<usize>,
    pub operator: &'static str,
    pub parent_candidate_ids: Vec<String>,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct ProposalResult {
    pub schema: &'static str,
    pub operation: &'static str,
    pub rng: &'static str,
    pub proposals: Vec<Proposal>,
    pub attempted: usize,
    pub duplicates: usize,
    pub operator_unavailable: usize,
    pub exhausted: bool,
    pub exhaustion_reason: Option<&'static str>,
    pub allocation_counts: BTreeMap<&'static str, usize>,
    pub attempt_allocation_counts: BTreeMap<&'static str, usize>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error(pub String);

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.0.fmt(f)
    }
}
impl std::error::Error for Error {}

fn fail<T>(message: &str) -> Result<T, Error> {
    Err(Error(message.into()))
}

fn valid_id(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

pub fn execute(request: Request) -> Result<ResultRecord, Error> {
    match request {
        Request::Pareto {
            schema,
            points,
            max_work,
        } => {
            if schema != REQUEST_SCHEMA {
                return fail("Unexpected request schema");
            }
            pareto(points, max_work).map(ResultRecord::Pareto)
        }
        Request::Propose {
            schema,
            seed,
            generation,
            limit,
            max_attempts,
            axes,
            family_axis,
            parents,
            seen,
            weights,
        } => {
            if schema != REQUEST_SCHEMA {
                return fail("Unexpected request schema");
            }
            propose(
                seed,
                generation,
                limit,
                max_attempts,
                axes,
                family_axis,
                parents,
                seen,
                weights,
            )
            .map(ResultRecord::Propose)
        }
    }
}

#[derive(Debug)]
struct Budget {
    used: u64,
    maximum: u64,
}
impl Budget {
    fn step(&mut self) -> Result<(), Error> {
        if self.used == self.maximum {
            return fail("Pareto work budget exhausted; no partial archive returned");
        }
        self.used += 1;
        Ok(())
    }
}

fn dominates(a: &Point, b: &Point) -> bool {
    a.values.iter().zip(&b.values).all(|(x, y)| x <= y)
        && (a.values != b.values || a.candidate_id < b.candidate_id)
}

fn prefer(points: &[Point], a: Option<usize>, b: Option<usize>) -> Option<usize> {
    match (a, b) {
        (None, value) | (value, None) => value,
        (Some(a), Some(b)) => {
            let az = *points[a].values.get(2).unwrap_or(&0.0);
            let bz = *points[b].values.get(2).unwrap_or(&0.0);
            Some(
                if az < bz || az == bz && points[a].candidate_id < points[b].candidate_id {
                    a
                } else {
                    b
                },
            )
        }
    }
}

fn sweep(
    points: &[Point],
    members: &[usize],
    budget: &mut Budget,
) -> Result<Vec<(usize, Option<usize>)>, Error> {
    let mut ordered = members.to_vec();
    ordered.sort_unstable_by(|&a, &b| {
        for (x, y) in points[a].values.iter().zip(&points[b].values) {
            let order = x.total_cmp(y);
            if !order.is_eq() {
                return order;
            }
        }
        points[a].candidate_id.cmp(&points[b].candidate_id)
    });
    let mut ys: Vec<f64> = ordered
        .iter()
        .map(|&i| *points[i].values.get(1).unwrap_or(&0.0))
        .collect();
    ys.sort_unstable_by(f64::total_cmp);
    ys.dedup();
    let mut tree = vec![None; ys.len() + 1];
    let mut result = Vec::with_capacity(members.len());
    for i in ordered {
        let y = *points[i].values.get(1).unwrap_or(&0.0);
        let position = ys
            .binary_search_by(|v| v.total_cmp(&y))
            .expect("compressed coordinate exists")
            + 1;
        let mut prefix = position;
        let mut best = None;
        while prefix > 0 {
            budget.step()?;
            best = prefer(points, best, tree[prefix]);
            prefix &= prefix - 1;
        }
        let witness = best.filter(|&j| dominates(&points[j], &points[i]));
        result.push((i, witness));
        let mut update = position;
        while update < tree.len() {
            budget.step()?;
            tree[update] = prefer(points, tree[update], Some(i));
            update += update & update.wrapping_neg();
        }
    }
    Ok(result)
}

#[derive(Debug)]
struct Node {
    lower: Vec<f64>,
    upper: Vec<f64>,
    representative: usize,
    children: Option<(Box<Node>, Box<Node>)>,
    members: Vec<usize>,
}
impl Node {
    fn build(
        points: &[Point],
        members: &mut [usize],
        depth: usize,
        budget: &mut Budget,
    ) -> Result<Self, Error> {
        budget.step()?;
        let dimensions = points[members[0]].values.len();
        let mut lower = vec![f64::INFINITY; dimensions];
        let mut upper = vec![f64::NEG_INFINITY; dimensions];
        let mut representative = members[0];
        for &i in members.iter() {
            budget.step()?;
            for k in 0..dimensions {
                lower[k] = lower[k].min(points[i].values[k]);
                upper[k] = upper[k].max(points[i].values[k]);
            }
            if points[i].candidate_id < points[representative].candidate_id {
                representative = i;
            }
        }
        let mut node = Self {
            lower,
            upper,
            representative,
            children: None,
            members: Vec::new(),
        };
        if members.len() <= 12 {
            node.members = members.to_vec();
            node.members
                .sort_unstable_by(|&a, &b| points[a].candidate_id.cmp(&points[b].candidate_id));
        } else {
            let axis = depth % dimensions;
            let middle = members.len() / 2;
            members.select_nth_unstable_by(middle, |&a, &b| {
                points[a].values[axis]
                    .total_cmp(&points[b].values[axis])
                    .then_with(|| points[a].candidate_id.cmp(&points[b].candidate_id))
            });
            let (left, right) = members.split_at_mut(middle);
            node.children = Some((
                Box::new(Self::build(points, left, depth + 1, budget)?),
                Box::new(Self::build(points, right, depth + 1, budget)?),
            ));
        }
        Ok(node)
    }

    fn witness(
        &self,
        points: &[Point],
        target: usize,
        budget: &mut Budget,
    ) -> Result<Option<usize>, Error> {
        budget.step()?;
        let query = &points[target];
        if self.lower.iter().zip(&query.values).any(|(x, y)| x > y) {
            return Ok(None);
        }
        if self.upper.iter().zip(&query.values).all(|(x, y)| x <= y)
            && dominates(&points[self.representative], query)
        {
            return Ok(Some(self.representative));
        }
        if let Some((left, right)) = &self.children {
            if let Some(result) = left.witness(points, target, budget)? {
                return Ok(Some(result));
            }
            return right.witness(points, target, budget);
        }
        for &i in &self.members {
            budget.step()?;
            if dominates(&points[i], query) {
                return Ok(Some(i));
            }
        }
        Ok(None)
    }
}

fn front(
    points: &[Point],
    members: &[usize],
    budget: &mut Budget,
) -> Result<Vec<(usize, Option<usize>)>, Error> {
    if points[members[0]].values.len() <= 3 {
        return sweep(points, members, budget);
    }
    let tree = Node::build(points, &mut members.to_vec(), 0, budget)?;
    members
        .iter()
        .map(|&i| tree.witness(points, i, budget).map(|w| (i, w)))
        .collect()
}

pub fn pareto(mut points: Vec<Point>, max_work: u64) -> Result<ParetoResult, Error> {
    if points.len() > MAX_POINTS || max_work == 0 || max_work > 1_000_000_000 {
        return fail("Explicit Pareto point/work limits exceeded");
    }
    let dimensions = points.first().map_or(0, |p| p.values.len());
    if !points.is_empty() && !(1..=8).contains(&dimensions) {
        return fail("One to eight objective values required");
    }
    let mut ids = BTreeSet::new();
    for point in &mut points {
        if !valid_id(&point.candidate_id)
            || !valid_id(&point.cell_id)
            || !ids.insert(point.candidate_id.clone())
        {
            return fail("Unique physical SHA-256 IDs and descriptor-cell SHA-256 IDs required");
        }
        if point.values.len() != dimensions
            || point.values.iter().any(|x| !x.is_finite() || *x < 0.0)
        {
            return fail("Equal-length finite nonnegative objective vectors required");
        }
        for value in &mut point.values {
            if *value == 0.0 {
                *value = 0.0;
            }
        }
    }
    points.sort_unstable_by(|a, b| a.candidate_id.cmp(&b.candidate_id));
    let mut groups: BTreeMap<String, Vec<usize>> = BTreeMap::new();
    for (i, point) in points.iter().enumerate() {
        groups.entry(point.cell_id.clone()).or_default().push(i);
    }
    let mut budget = Budget {
        used: 0,
        maximum: max_work,
    };
    let mut cells = Vec::new();
    let mut retained = Vec::new();
    let mut dominated = Vec::new();
    for (cell_id, members) in groups {
        let mut local = Vec::new();
        for (i, witness) in front(&points, &members, &mut budget)? {
            if let Some(j) = witness {
                dominated.push(Exclusion {
                    candidate_id: points[i].candidate_id.clone(),
                    cell_id: cell_id.clone(),
                    dominated_by: points[j].candidate_id.clone(),
                });
            } else {
                local.push(points[i].candidate_id.clone());
            }
        }
        local.sort();
        retained.extend(local.clone());
        cells.push(Cell {
            cell_id,
            retained_candidate_ids: local,
        });
    }
    let mut global_front = Vec::new();
    if !points.is_empty() {
        for (i, witness) in front(&points, &(0..points.len()).collect::<Vec<_>>(), &mut budget)? {
            if witness.is_none() {
                global_front.push(points[i].candidate_id.clone());
            }
        }
    }
    global_front.sort();
    retained.sort();
    dominated.sort_by(|a, b| a.candidate_id.cmp(&b.candidate_id));
    Ok(ParetoResult { schema: RESULT_SCHEMA, operation: "pareto", cells, retained_candidate_ids: retained,
        global_front, dominated, statistics: Statistics { point_count: points.len(), objective_count: dimensions,
            work: budget.used, max_work, method: "sorted Fenwick sweep (1-3 objectives); bounded KD orthant queries (4-8)",
            work_scope: "Fenwick steps or KD build/visit/point steps; excludes sorting, serialization and OS runtime/memory enforcement" } })
}

#[derive(Debug)]
struct SplitMix64(u64);
impl SplitMix64 {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut value = self.0;
        value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
        value ^ (value >> 31)
    }
    fn choose(&mut self, choices: usize) -> usize {
        (self.next() % choices as u64) as usize
    }
    fn different(&mut self, current: usize, choices: usize) -> usize {
        let value = self.choose(choices - 1);
        if value >= current {
            value + 1
        } else {
            value
        }
    }
}

fn valid_genes(genes: &[usize], axes: &[Axis]) -> bool {
    genes.len() == axes.len()
        && genes
            .iter()
            .zip(axes)
            .all(|(&gene, axis)| gene < axis.choices)
}

#[allow(clippy::too_many_arguments)]
pub fn propose(
    seed: u64,
    generation: u32,
    limit: usize,
    max_attempts: usize,
    axes: Vec<Axis>,
    family_axis: usize,
    mut parents: Vec<Parent>,
    seen: Vec<Vec<usize>>,
    weights: [u32; 3],
) -> Result<ProposalResult, Error> {
    if axes.is_empty()
        || axes.len() > 32
        || family_axis >= axes.len()
        || limit > MAX_POINTS
        || max_attempts > MAX_ATTEMPTS
        || max_attempts < limit
        || parents.is_empty()
        || parents.len() > MAX_POINTS
        || seen.len() > MAX_ATTEMPTS
    {
        return fail("Explicit proposal axis/parent/trial budgets required");
    }
    let mut names = BTreeSet::new();
    for axis in &axes {
        if axis.name.trim().is_empty()
            || axis.name.len() > 256
            || !names.insert(axis.name.clone())
            || !(1..=10_000).contains(&axis.choices)
        {
            return fail("Unique named bounded axes required");
        }
    }
    let total: u64 = weights.iter().map(|&x| u64::from(x)).sum();
    if total == 0 || total > 1_000_000 {
        return fail("Positive bounded proposal allocation weights required");
    }
    parents.sort_by(|a, b| a.candidate_id.cmp(&b.candidate_id));
    let mut parent_total = 0_u64;
    let mut cumulative_weights = Vec::with_capacity(parents.len());
    for parent in &parents {
        if !(1..=1000).contains(&parent.weight) {
            return fail("Parent proposal weights must be integers from one to 1000");
        }
        parent_total = parent_total
            .checked_add(u64::from(parent.weight))
            .ok_or_else(|| Error("Parent proposal weight sum overflow".into()))?;
        if parent_total > 100_000_000 {
            return fail("Parent proposal weight sum exceeds the bounded search domain");
        }
        cumulative_weights.push(parent_total);
    }
    let mut parent_ids = BTreeSet::new();
    if parents.iter().any(|p| {
        !valid_id(&p.candidate_id)
            || !parent_ids.insert(p.candidate_id.clone())
            || !valid_genes(&p.genes, &axes)
    }) || seen.iter().any(|g| !valid_genes(g, &axes))
    {
        return fail("Valid unique parent identities and bounded genes required");
    }
    let mut visited: BTreeSet<Vec<usize>> = seen.into_iter().collect();
    visited.extend(parents.iter().map(|p| p.genes.clone()));
    let operators = ["exploit", "alternative-family", "unconventional"];
    let mut accepted: BTreeMap<&'static str, usize> = operators.iter().map(|&k| (k, 0)).collect();
    let mut attempts = accepted.clone();
    let mutable: Vec<usize> = axes
        .iter()
        .enumerate()
        .filter_map(|(i, a)| (a.choices > 1).then_some(i))
        .collect();
    let nonfamily: Vec<usize> = mutable
        .iter()
        .copied()
        .filter(|&i| i != family_axis)
        .collect();
    let mut rng = SplitMix64(seed ^ u64::from(generation).wrapping_mul(0xd6e8feb86659fd93));
    let mut proposals = Vec::new();
    let mut attempted = 0;
    let mut duplicates = 0;
    let mut unavailable = 0;
    let space = axes
        .iter()
        .try_fold(1_u128, |n, a| n.checked_mul(a.choices as u128));
    while proposals.len() < limit
        && attempted < max_attempts
        && space.is_none_or(|n| visited.len() as u128 != n)
    {
        attempted += 1;
        let pick = rng.next() % total;
        let operator = if pick < u64::from(weights[0]) {
            0
        } else if pick < u64::from(weights[0]) + u64::from(weights[1]) {
            1
        } else {
            2
        };
        *attempts
            .get_mut(operators[operator])
            .expect("registered operator") += 1;
        // One draw with the same bound and subsequent RNG state as the former
        // uniform choice when all weights are one. Prefix lookup adds no draws.
        let pick = rng.choose(parent_total as usize) as u64;
        let parent_index = cumulative_weights.partition_point(|&total| total <= pick);
        let parent = &parents[parent_index];
        let mut genes = parent.genes.clone();
        match operator {
            0 if !nonfamily.is_empty() => {
                let axis = nonfamily[rng.choose(nonfamily.len())];
                genes[axis] = rng.different(genes[axis], axes[axis].choices);
            }
            1 if axes[family_axis].choices > 1 => {
                genes[family_axis] = rng.different(genes[family_axis], axes[family_axis].choices);
                if !nonfamily.is_empty() && rng.choose(2) == 1 {
                    let axis = nonfamily[rng.choose(nonfamily.len())];
                    genes[axis] = rng.different(genes[axis], axes[axis].choices);
                }
            }
            2 if !mutable.is_empty() => {
                for &axis in &mutable {
                    genes[axis] = rng.choose(axes[axis].choices);
                }
                let mut chosen = mutable.clone();
                for k in 0..chosen.len().min(2) {
                    let pos = k + rng.choose(chosen.len() - k);
                    chosen.swap(k, pos);
                    let axis = chosen[k];
                    genes[axis] = rng.different(parent.genes[axis], axes[axis].choices);
                }
            }
            _ => {
                unavailable += 1;
                continue;
            }
        }
        if !visited.insert(genes.clone()) {
            duplicates += 1;
            continue;
        }
        *accepted
            .get_mut(operators[operator])
            .expect("registered operator") += 1;
        proposals.push(Proposal {
            genes,
            operator: operators[operator],
            parent_candidate_ids: vec![parent.candidate_id.clone()],
        });
    }
    let exhausted = proposals.len() < limit;
    let exhaustion_reason =
        exhausted.then_some(if space.is_some_and(|n| visited.len() as u128 == n) {
            "finite-gene-space-exhausted"
        } else {
            "attempt-budget-reached"
        });
    Ok(ProposalResult {
        schema: RESULT_SCHEMA,
        operation: "propose",
        rng: "splitmix64/1; modulo bounded choice",
        proposals,
        attempted,
        duplicates,
        operator_unavailable: unavailable,
        exhausted,
        exhaustion_reason,
        allocation_counts: accepted,
        attempt_allocation_counts: attempts,
    })
}
