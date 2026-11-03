use osr_design_search::{execute, pareto, propose, Axis, Parent, Point, Request, REQUEST_SCHEMA};
use std::collections::{BTreeMap, BTreeSet};

fn id(number: usize) -> String {
    format!("{number:064x}")
}

fn point(number: usize, cell: usize, values: Vec<f64>) -> Point {
    Point {
        candidate_id: id(number),
        cell_id: id(cell + 1_000_000),
        values,
    }
}

fn dominates(a: &Point, b: &Point) -> bool {
    a.values.iter().zip(&b.values).all(|(x, y)| x <= y)
        && (a.values != b.values || a.candidate_id < b.candidate_id)
}

#[test]
fn differential_oracle_covers_ties_dimensions_cells_and_reordering() {
    let mut rng = 17_u64;
    for dimensions in 1..=8 {
        for size in [1, 2, 12, 13, 40, 160] {
            let mut points: Vec<_> = (0..size)
                .map(|i| {
                    let values = (0..dimensions)
                        .map(|_| {
                            rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                            ((rng >> 32) % 13) as f64
                        })
                        .collect();
                    point(i, i % 5, values)
                })
                .collect();
            if size > 1 {
                points[1].values = points[0].values.clone();
                points[1].cell_id = points[0].cell_id.clone();
            }
            let result = pareto(points.clone(), 100_000_000).unwrap();
            let expected: Vec<_> = points
                .iter()
                .filter(|p| !points.iter().any(|q| dominates(q, p)))
                .map(|p| p.candidate_id.clone())
                .collect();
            assert_eq!(
                result.global_front, expected,
                "dimensions {dimensions} size {size}"
            );
            let retained: BTreeSet<_> = points
                .iter()
                .filter(|p| {
                    !points
                        .iter()
                        .any(|q| q.cell_id == p.cell_id && dominates(q, p))
                })
                .map(|p| p.candidate_id.clone())
                .collect();
            assert_eq!(
                result.retained_candidate_ids,
                retained.into_iter().collect::<Vec<_>>()
            );
            for row in &result.dominated {
                let p = points
                    .iter()
                    .find(|p| p.candidate_id == row.candidate_id)
                    .unwrap();
                let q = points
                    .iter()
                    .find(|p| p.candidate_id == row.dominated_by)
                    .unwrap();
                assert_eq!(p.cell_id, q.cell_id);
                assert!(dominates(q, p));
            }
            points.reverse();
            assert_eq!(result, pareto(points, 100_000_000).unwrap());
        }
    }
}

#[test]
fn zero_sign_and_extreme_finite_values_preserve_lexical_ties() {
    let points = vec![
        point(2, 0, vec![-0.0, f64::MAX, 0.0]),
        point(1, 0, vec![0.0, f64::MAX, -0.0]),
    ];
    let result = pareto(points, 1_000_000).unwrap();
    assert_eq!(result.global_front, vec![id(1)]);
    assert_eq!(result.dominated[0].dominated_by, id(1));
}

#[test]
fn invalid_or_unknown_objectives_and_identities_cannot_become_zero() {
    for bad in [f64::NAN, f64::INFINITY, -1.0] {
        assert!(pareto(vec![point(1, 0, vec![bad])], 1000).is_err());
    }
    assert!(pareto(vec![point(1, 0, vec![1.0]), point(1, 1, vec![2.0])], 1000).is_err());
    assert!(pareto(vec![point(1, 0, vec![])], 1000).is_err());
    assert!(pareto(
        vec![point(1, 0, vec![1.0]), point(2, 0, vec![1.0, 2.0])],
        1000
    )
    .is_err());
    let mut bad = point(1, 0, vec![1.0]);
    bad.candidate_id = "g".repeat(64);
    assert!(pareto(vec![bad], 1000).is_err());
    let mut bad = point(1, 0, vec![1.0]);
    bad.cell_id = "short".into();
    assert!(pareto(vec![bad], 1000).is_err());
    assert!(pareto(vec![point(1, 0, vec![1.0; 9])], 1000).is_err());
    assert!(pareto(vec![], 0).is_err());
    assert_eq!(
        pareto(vec![], 1000).unwrap().global_front,
        Vec::<String>::new()
    );
}

#[test]
fn higher_dimension_work_exhaustion_returns_error_without_partial_archive() {
    let points = (0..50)
        .map(|i| point(i, 0, vec![i as f64, (50 - i) as f64, 1.0, 2.0]))
        .collect();
    assert!(pareto(points, 3)
        .unwrap_err()
        .0
        .contains("no partial archive"));
}

#[test]
fn hundred_thousand_nondominated_points_use_subquadratic_work() {
    for dimensions in [2, 3, 4] {
        let points = (0..100_000)
            .map(|i| {
                let mut values = vec![i as f64, (100_000 - i) as f64];
                values.resize(dimensions, 1.0);
                point(i, 0, values)
            })
            .collect();
        let result = pareto(points, 100_000_000).unwrap();
        assert_eq!(result.global_front.len(), 100_000);
        assert_eq!(result.retained_candidate_ids.len(), 100_000);
        assert!(
            result.statistics.work < 30_000_000,
            "{}",
            result.statistics.work
        );
    }
}

fn axes() -> Vec<Axis> {
    vec![
        Axis {
            name: "family".into(),
            choices: 4,
        },
        Axis {
            name: "wall".into(),
            choices: 7,
        },
        Axis {
            name: "ribs".into(),
            choices: 5,
        },
        Axis {
            name: "fixed".into(),
            choices: 1,
        },
    ]
}
fn parents() -> Vec<Parent> {
    vec![
        Parent {
            candidate_id: id(2),
            genes: vec![1, 2, 3, 0],
            weight: 1,
        },
        Parent {
            candidate_id: id(1),
            genes: vec![0, 1, 2, 0],
            weight: 1,
        },
    ]
}

#[test]
fn new_successors_are_deterministic_bounded_unique_and_have_parent_ancestry() {
    let a = propose(
        42,
        3,
        30,
        5000,
        axes(),
        0,
        parents(),
        vec![vec![0, 0, 0, 0]],
        [50, 30, 20],
    )
    .unwrap();
    let mut reverse = parents();
    reverse.reverse();
    let b = propose(
        42,
        3,
        30,
        5000,
        axes(),
        0,
        reverse,
        vec![vec![0, 0, 0, 0]],
        [50, 30, 20],
    )
    .unwrap();
    assert_eq!(a, b);
    assert_eq!(a.proposals.len(), 30);
    assert!(!a.exhausted);
    let mut seen: BTreeSet<_> = parents().into_iter().map(|p| p.genes).collect();
    seen.insert(vec![0, 0, 0, 0]);
    for proposal in a.proposals {
        assert!(seen.insert(proposal.genes.clone()));
        assert_eq!(proposal.genes.len(), 4);
        for (&gene, axis) in proposal.genes.iter().zip(axes()) {
            assert!(gene < axis.choices);
        }
        assert_eq!(proposal.parent_candidate_ids.len(), 1);
        assert!(parents()
            .iter()
            .any(|p| p.candidate_id == proposal.parent_candidate_ids[0]));
    }
}

#[test]
fn operators_have_distinct_physical_mutation_intents() {
    for (weights, name) in [
        ([1, 0, 0], "exploit"),
        ([0, 1, 0], "alternative-family"),
        ([0, 0, 1], "unconventional"),
    ] {
        let result = propose(9, 0, 10, 5000, axes(), 0, parents(), vec![], weights).unwrap();
        assert_eq!(result.proposals.len(), 10);
        for row in result.proposals {
            assert_eq!(row.operator, name);
            let parent = parents()
                .into_iter()
                .find(|p| p.candidate_id == row.parent_candidate_ids[0])
                .unwrap();
            let changes = row
                .genes
                .iter()
                .zip(&parent.genes)
                .filter(|(a, b)| a != b)
                .count();
            match name {
                "exploit" => {
                    assert_eq!(changes, 1);
                    assert_eq!(row.genes[0], parent.genes[0]);
                }
                "alternative-family" => assert_ne!(row.genes[0], parent.genes[0]),
                _ => assert!(changes >= 2),
            }
        }
    }
}

#[test]
fn finite_space_saturation_and_unavailable_operators_preserve_budget_state() {
    let axes = vec![Axis {
        name: "family".into(),
        choices: 2,
    }];
    let parent = vec![Parent {
        candidate_id: id(1),
        genes: vec![0],
        weight: 1,
    }];
    let result = propose(
        1,
        0,
        5,
        20,
        axes.clone(),
        0,
        parent.clone(),
        vec![],
        [0, 1, 0],
    )
    .unwrap();
    assert_eq!(result.proposals.len(), 1);
    assert!(result.exhausted);
    assert_eq!(
        result.exhaustion_reason,
        Some("finite-gene-space-exhausted")
    );
    let result = propose(1, 0, 5, 20, axes, 0, parent, vec![], [1, 0, 0]).unwrap();
    assert_eq!(result.proposals.len(), 0);
    assert_eq!(result.attempted, 20);
    assert_eq!(result.operator_unavailable, 20);
    assert_eq!(result.exhaustion_reason, Some("attempt-budget-reached"));
}

#[test]
fn invalid_gene_programs_and_unbounded_requests_fail_before_generation() {
    assert!(propose(1, 0, 1, 2, axes(), 0, parents(), vec![], [0, 0, 0]).is_err());
    assert!(propose(1, 0, 2, 1, axes(), 0, parents(), vec![], [1, 1, 1]).is_err());
    assert!(propose(1, 0, 1, 2, axes(), 4, parents(), vec![], [1, 1, 1]).is_err());
    assert!(propose(
        1,
        0,
        1,
        2,
        axes(),
        0,
        parents(),
        vec![vec![8, 1, 1, 0]],
        [1, 1, 1]
    )
    .is_err());
    let mut bad = parents();
    bad.push(bad[0].clone());
    assert!(propose(1, 0, 1, 2, axes(), 0, bad, vec![], [1, 1, 1]).is_err());
    let mut bad = axes();
    bad[1].name = bad[0].name.clone();
    assert!(propose(1, 0, 1, 2, bad, 0, parents(), vec![], [1, 1, 1]).is_err());
}

#[test]
fn protocol_rejects_unknown_fields_missing_values_and_unexpected_schema() {
    let value =
        serde_json::json!({"schema":REQUEST_SCHEMA,"operation":"pareto","points":[],"extra":1});
    assert!(serde_json::from_value::<Request>(value).is_err());
    let value = serde_json::json!({"schema":"other","operation":"pareto","points":[]});
    assert!(execute(serde_json::from_value(value).unwrap()).is_err());
    let value = serde_json::json!({"schema":REQUEST_SCHEMA,"operation":"pareto","points":[{"candidate_id":id(1),"cell_id":id(2),"values":[null]}]});
    assert!(serde_json::from_value::<Request>(value).is_err());
}

#[test]
fn proposal_allocation_counts_describe_accepted_and_attempted_work_separately() {
    let result = propose(17, 4, 50, 5000, axes(), 0, parents(), vec![], [50, 30, 20]).unwrap();
    let actual = result.proposals.iter().fold(BTreeMap::new(), |mut m, p| {
        *m.entry(p.operator).or_insert(0) += 1;
        m
    });
    assert_eq!(result.allocation_counts, actual);
    assert_eq!(
        result.attempt_allocation_counts.values().sum::<usize>(),
        result.attempted
    );
    assert_eq!(
        result.allocation_counts.values().sum::<usize>()
            + result.duplicates
            + result.operator_unavailable,
        result.attempted
    );
}

#[test]
fn omitted_unit_parent_weights_preserve_the_previous_complete_protocol_result() {
    let mut request = serde_json::json!({
        "schema": REQUEST_SCHEMA, "operation": "propose", "seed": 42,
        "generation": 3, "limit": 6, "max_attempts": 50,
        "axes": [{"name":"family","choices":4},{"name":"wall","choices":7},
            {"name":"ribs","choices":5},{"name":"fixed","choices":1}],
        "family_axis": 0,
        "parents": [{"candidate_id":id(2),"genes":[1,2,3,0]},
                    {"candidate_id":id(1),"genes":[0,1,2,0]}],
        "seen": [[0,0,0,0]], "weights": [50,30,20]
    });
    // Captured from the preceding executable before adding parent weights.
    let expected = serde_json::json!({
        "schema":"osr-search-kernel-result/1","operation":"propose",
        "rng":"splitmix64/1; modulo bounded choice",
        "proposals":[
            {"genes":[0,4,2,0],"operator":"exploit","parent_candidate_ids":[id(1)]},
            {"genes":[1,1,3,0],"operator":"exploit","parent_candidate_ids":[id(2)]},
            {"genes":[1,4,0,0],"operator":"unconventional","parent_candidate_ids":[id(1)]},
            {"genes":[0,6,2,0],"operator":"exploit","parent_candidate_ids":[id(1)]},
            {"genes":[0,2,1,0],"operator":"alternative-family","parent_candidate_ids":[id(2)]},
            {"genes":[0,1,1,0],"operator":"exploit","parent_candidate_ids":[id(1)]}],
        "attempted":8,"duplicates":2,"operator_unavailable":0,"exhausted":false,
        "exhaustion_reason":null,
        "allocation_counts":{"alternative-family":1,"exploit":4,"unconventional":1},
        "attempt_allocation_counts":{"alternative-family":1,"exploit":6,"unconventional":1}
    });
    let omitted = execute(serde_json::from_value(request.clone()).unwrap()).unwrap();
    assert_eq!(serde_json::to_value(&omitted).unwrap(), expected);
    for parent in request["parents"].as_array_mut().unwrap() {
        parent["weight"] = serde_json::json!(1);
    }
    assert_eq!(
        omitted,
        execute(serde_json::from_value(request).unwrap()).unwrap()
    );
}

#[test]
fn positive_parent_weights_bias_fixed_seed_sampling_without_excluding_any_parent() {
    let axes = vec![
        Axis {
            name: "family".into(),
            choices: 3,
        },
        Axis {
            name: "span".into(),
            choices: 10_000,
        },
        Axis {
            name: "wall".into(),
            choices: 10_000,
        },
    ];
    let parents: Vec<_> = [1, 3, 9]
        .into_iter()
        .enumerate()
        .map(|(i, weight)| Parent {
            candidate_id: id(i + 1),
            genes: vec![i, 0, 0],
            weight,
        })
        .collect();
    let result = propose(
        7,
        2,
        6000,
        8000,
        axes.clone(),
        0,
        parents.clone(),
        vec![],
        [0, 0, 1],
    )
    .unwrap();
    let mut reverse = parents;
    reverse.reverse();
    assert_eq!(
        result,
        propose(7, 2, 6000, 8000, axes, 0, reverse, vec![], [0, 0, 1]).unwrap()
    );
    let mut counts: BTreeMap<String, usize> = BTreeMap::new();
    for proposal in &result.proposals {
        *counts
            .entry(proposal.parent_candidate_ids[0].clone())
            .or_insert(0) += 1;
    }
    assert_eq!(result.proposals.len(), 6000);
    assert_eq!(counts.len(), 3);
    // This is a deterministic regression for a fixed stream, not a statistical
    // probability test or a claim that deduplicated acceptances equal weights.
    assert!(counts[&id(1)] > 0);
    assert!(counts[&id(1)] < counts[&id(2)] && counts[&id(2)] < counts[&id(3)]);
    assert!(result.attempted <= 8000 && !result.exhausted);
}

#[test]
fn invalid_parent_weights_are_rejected_before_generating_any_proposal() {
    for weight in [0, 1001, u32::MAX] {
        let mut values = parents();
        values[0].weight = weight;
        assert!(propose(1, 0, 0, 0, axes(), 0, values, vec![], [50, 30, 20])
            .unwrap_err()
            .0
            .contains("Parent proposal weights"));
    }
    for weight in [
        serde_json::json!(-1),
        serde_json::json!(1.5),
        serde_json::json!(true),
        serde_json::json!("1"),
        serde_json::json!(null),
        serde_json::json!(4_294_967_296_u64),
    ] {
        let request = serde_json::json!({
            "schema":REQUEST_SCHEMA,"operation":"propose","seed":1,"generation":0,
            "limit":1,"max_attempts":2,"axes":[{"name":"family","choices":2}],
            "family_axis":0,"parents":[{"candidate_id":id(1),"genes":[0],"weight":weight}],
            "seen":[],"weights":[50,30,20]
        });
        assert!(serde_json::from_value::<Request>(request).is_err());
    }
}

#[test]
fn maximum_checked_parent_weight_sum_and_weighted_saturation_remain_bounded() {
    let parents: Vec<_> = (0..100_000)
        .map(|i| Parent {
            candidate_id: id(i),
            genes: vec![0],
            weight: 1000,
        })
        .collect();
    let result = propose(
        1,
        0,
        0,
        0,
        vec![Axis {
            name: "family".into(),
            choices: 1,
        }],
        0,
        parents,
        vec![],
        [50, 30, 20],
    )
    .unwrap();
    assert_eq!(result.attempted, 0);
    assert!(result.proposals.is_empty());
    let parents = vec![
        Parent {
            candidate_id: id(1),
            genes: vec![0],
            weight: 1000,
        },
        Parent {
            candidate_id: id(2),
            genes: vec![1],
            weight: 1,
        },
    ];
    let result = propose(
        1,
        0,
        5,
        20,
        vec![Axis {
            name: "family".into(),
            choices: 2,
        }],
        0,
        parents,
        vec![],
        [0, 1, 0],
    )
    .unwrap();
    assert_eq!(result.attempted, 0);
    assert!(result.exhausted && result.proposals.is_empty());
    assert_eq!(
        result.exhaustion_reason,
        Some("finite-gene-space-exhausted")
    );
}
