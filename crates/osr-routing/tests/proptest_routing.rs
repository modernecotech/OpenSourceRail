use osr_routing::{
    budget_for_population, classify_segments, greedy_synthesize_lines, solve_path,
    synthesize_lines, Anchor, CivilClass, DemandWeight, GreedyBudget, Grid, GridRef, LineShape,
    TopologyArchetype, TopologyError,
};
use proptest::prelude::*;

fn grid(height: usize, width: usize) -> Grid {
    let cells = height * width;
    Grid {
        reference: GridRef {
            height,
            width,
            cell_m: 20.0,
            lat0: 0.0,
            bbox_south: -1.0,
            bbox_west: -1.0,
            bbox_north: 1.0,
            bbox_east: 1.0,
            m_per_deg_lat: 111_132.0,
            m_per_deg_lon: 111_320.0,
        },
        cost: vec![8.0; cells],
        demand: vec![0.0; cells],
        buildability: vec![1; cells],
        water: Some(vec![0; cells]),
        elevation_m: Some(vec![10.0; cells]),
        terrain_slope_percent: Some(vec![0.0; cells]),
    }
}

fn anchor(id: i64, row: usize, col: usize) -> Anchor {
    Anchor {
        id,
        kind: "demand".into(),
        weight: 1.0,
        name: None,
        row,
        col,
        lat: 0.0,
        lon: 0.0,
    }
}

fn synthesis_anchors() -> Vec<Anchor> {
    [
        (1, 1),
        (1, 20),
        (1, 39),
        (20, 39),
        (39, 39),
        (39, 20),
        (39, 1),
        (20, 1),
        (6, 6),
        (6, 20),
        (6, 34),
        (20, 34),
        (34, 34),
        (34, 20),
        (34, 6),
        (20, 6),
        (12, 12),
        (12, 20),
        (12, 28),
        (20, 28),
        (28, 28),
        (28, 20),
        (28, 12),
        (20, 12),
    ]
    .into_iter()
    .enumerate()
    .map(|(id, (row, col))| anchor(id as i64, row, col))
    .collect()
}

fn assert_contiguous_in_bounds(lines: &[osr_routing::Line], height: usize, width: usize) {
    assert!(!lines.is_empty());
    for line in lines {
        assert!(!line.cells.is_empty());
        for &(row, col) in &line.cells {
            assert!(row < height && col < width);
        }
        for pair in line.cells.windows(2) {
            assert!(pair[0].0.abs_diff(pair[1].0) <= 1);
            assert!(pair[0].1.abs_diff(pair[1].1) <= 1);
            assert_ne!(pair[0], pair[1]);
        }
    }
}

#[test]
fn all_population_archetypes_produce_connected_bounded_networks() {
    let mut value = grid(41, 41);
    value.demand.fill(1.0);
    let anchors = synthesis_anchors();
    let cases = [
        (TopologyArchetype::SingleRadial, 1),
        (TopologyArchetype::RadialPlusRing, 2),
        (TopologyArchetype::CrossPlusRing, 3),
        (TopologyArchetype::HubAndSpokeDualRing, 6),
    ];
    for (archetype, expected_lines) in cases {
        let lines = synthesize_lines(&value, &anchors, archetype, DemandWeight(0.0)).unwrap();
        assert_eq!(lines.len(), expected_lines);
        assert_contiguous_in_bounds(&lines, 41, 41);
        assert!(matches!(lines[0].shape, LineShape::Radial));
        for ring in lines
            .iter()
            .filter(|line| matches!(line.shape, LineShape::Ring))
        {
            assert_eq!(ring.cells.first(), ring.cells.last());
        }
    }
}

#[test]
fn population_thresholds_select_the_documented_planner_tiers() {
    assert!(matches!(
        osr_routing::topology::pick_archetype(300_000),
        TopologyArchetype::SingleRadial
    ));
    assert!(matches!(
        osr_routing::topology::pick_archetype(300_001),
        TopologyArchetype::RadialPlusRing
    ));
    assert!(matches!(
        osr_routing::topology::pick_archetype(1_000_001),
        TopologyArchetype::CrossPlusRing
    ));
    assert!(matches!(
        osr_routing::topology::pick_archetype(3_000_001),
        TopologyArchetype::HubAndSpokeDualRing
    ));
    assert_eq!(budget_for_population(300_000).max_lines, 3);
    assert_eq!(budget_for_population(300_001).max_total_route_m, 100_000.0);
    assert_eq!(budget_for_population(1_000_001).max_lines, 6);
    assert_eq!(budget_for_population(3_000_001).max_lines, 9);
}

#[test]
fn greedy_synthesis_returns_a_real_route_and_rejects_too_few_anchors() {
    let mut value = grid(21, 21);
    value.reference.cell_m = 100.0;
    value.demand.fill(1.0);
    let anchors = vec![anchor(1, 10, 1), anchor(2, 10, 19)];
    let budget = GreedyBudget {
        max_lines: 1,
        max_total_route_m: 5_000.0,
        min_coverage_per_km: 0.0,
        coverage_radius_m: 200.0,
        min_line_length_m: 500.0,
        max_line_length_m: 4_000.0,
        min_anchor_weight: 0.1,
        top_k: 2,
        coalesce_bin_cells: 1,
        bbox_margin_frac: 0.3,
    };
    let lines = greedy_synthesize_lines(&value, &anchors, DemandWeight(0.0), &budget).unwrap();
    assert_eq!(lines.len(), 1);
    let mut endpoints = lines[0].anchor_ids.clone();
    endpoints.sort_unstable();
    assert_eq!(endpoints, vec![0, 1]);
    assert_contiguous_in_bounds(&lines, 21, 21);

    assert!(matches!(
        synthesize_lines(
            &value,
            &anchors[..1],
            TopologyArchetype::SingleRadial,
            DemandWeight(0.0)
        ),
        Err(TopologyError::TooFewAnchors { got: 1, .. })
    ));
    assert!(matches!(
        greedy_synthesize_lines(&value, &anchors[..1], DemandWeight(0.0), &budget),
        Err(TopologyError::TooFewAnchors { got: 1, .. })
    ));
}

proptest! {
    #[test]
    fn solved_uniform_paths_stay_in_bounds_and_connected(
        height in 1_usize..12,
        width in 1_usize..12,
        start_seed in any::<usize>(),
        goal_seed in any::<usize>(),
    ) {
        let start = (start_seed % height, start_seed.wrapping_div(height.max(1)) % width);
        let goal = (goal_seed % height, goal_seed.wrapping_div(height.max(1)) % width);
        let route = solve_path(&grid(height, width), start, goal, DemandWeight(0.0)).unwrap();
        prop_assert_eq!(route.first(), Some(&start));
        prop_assert_eq!(route.last(), Some(&goal));
        for &(row, col) in &route {
            prop_assert!(row < height && col < width);
        }
        for pair in route.windows(2) {
            prop_assert!(pair[0].0.abs_diff(pair[1].0) <= 1);
            prop_assert!(pair[0].1.abs_diff(pair[1].1) <= 1);
            prop_assert_ne!(pair[0], pair[1]);
        }
    }

    #[test]
    fn any_mapped_water_requires_bridge_and_excludes_station(
        coverage in 1_u8..=100,
    ) {
        let mut value = grid(1, 1);
        value.water = Some(vec![coverage]);
        prop_assert_eq!(classify_segments(&value, &[(0, 0)])[0].class, CivilClass::Bridge);
        prop_assert!(value.excludes_station_for_water(0, 0));
    }
}
