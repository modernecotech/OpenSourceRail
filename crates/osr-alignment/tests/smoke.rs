//! Smoke tests: fit a known polyline + verify exported artefacts
//! contain the expected geometry.

use osr_alignment::{
    alignment::{Alignment, HorizontalElement, TurnDirection, VerticalElement},
    cant::cant_design,
    chainage::{sample_every, station_at},
    landxml, railml,
};

fn l_shape() -> Alignment {
    // 500 m east, then turn left (northward) and 500 m north.
    // At the corner we tuck in a 300 m radius arc. Hand-compute:
    // - arc starts at (500 - 300·tan(45°), 0) = (200, 0)
    // - arc ends at (500, 300) wait — this depends on geometry.
    // Simpler: just use an arc of π/2 total angle with 300 m radius,
    // positioned so it ends on the vertical leg.
    Alignment {
        line_slug: "l-shape".into(),
        design_speed_kmh: 80.0,
        start_chainage_m: 0.0,
        horizontal: vec![
            HorizontalElement::Tangent {
                length_m: 200.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            },
            HorizontalElement::Arc {
                length_m: std::f64::consts::PI * 150.0, // quarter circle on r=300
                radius_m: 300.0,
                direction: TurnDirection::Left,
                start_xy: (200.0, 0.0),
                start_bearing_rad: 0.0,
            },
            HorizontalElement::Tangent {
                length_m: 200.0,
                bearing_rad: std::f64::consts::FRAC_PI_2,
                start_xy: (500.0, 300.0),
            },
        ],
        vertical: vec![VerticalElement::Grade {
            length_m: 400.0 + std::f64::consts::PI * 150.0,
            grade: 0.01,
            start_z_m: 100.0,
        }],
    }
}

#[test]
fn total_length_matches() {
    let a = l_shape();
    let expected = 200.0 + std::f64::consts::PI * 150.0 + 200.0;
    assert!((a.total_length_m() - expected).abs() < 1e-6);
}

#[test]
fn station_at_midpoint_of_arc() {
    let a = l_shape();
    // Midpoint of arc = 200 m + π·75 m chainage. Position should be
    // at (500 - 300·cos(π/4), 300 - 300·sin(π/4)) wait — let me think.
    // Arc starts at (200, 0), tangent east (bearing 0), turns left,
    // ends at (500, 300) tangent north. Centre at (200, 300).
    // Midpoint of arc: halfway around (i.e., bearing changes π/4).
    // Position at midpoint: centre + R·(cos(angle), sin(angle))
    // where angle at start = -π/2 (from centre to (200,0)); at midpoint
    // angle = -π/4.
    // So midpoint = (200 + 300·cos(-π/4), 300 + 300·sin(-π/4))
    //             = (200 + 212.13, 300 - 212.13)
    //             = (412.13, 87.87)
    let s = 200.0 + std::f64::consts::PI * 75.0;
    let p = station_at(&a, s).unwrap();
    assert!(
        (p.x_m - 412.13).abs() < 0.1 && (p.y_m - 87.87).abs() < 0.1,
        "got ({}, {})",
        p.x_m,
        p.y_m
    );
}

#[test]
fn stake_out_samples_include_endpoints() {
    let a = l_shape();
    let pts = sample_every(&a, 50.0);
    assert!(pts.first().unwrap().chainage_m.abs() < 1e-6);
    assert!(
        (pts.last().unwrap().chainage_m - a.total_length_m()).abs() < 1e-3,
        "last chainage = {}",
        pts.last().unwrap().chainage_m
    );
}

#[test]
fn cant_schedule_nonzero_on_arc_segment() {
    let a = l_shape();
    let s = cant_design(&a, 150.0, 130.0);
    // 80 km/h on 300 m → 11.8·6400/300 ≈ 251.7 mm equilibrium.
    // Applied cant = 150 (capped), deficiency ≈ 101.7 mm.
    let arc = s
        .applied_cant_mm
        .iter()
        .find(|seg| seg.start_cant_mm > 0.0)
        .expect("expected at least one cant segment");
    assert!(
        (arc.start_cant_mm - 150.0).abs() < 1e-6,
        "cant = {}",
        arc.start_cant_mm
    );
    assert!(arc.max_deficiency_mm > 100.0);
}

#[test]
fn landxml_has_expected_elements() {
    let a = l_shape();
    let xml = landxml::to_landxml(&a);
    assert!(xml.contains("<Line length=\"200"));
    assert!(xml.contains("<Curve length="));
    assert!(xml.contains("radius=\"300"));
    assert!(xml.contains("rot=\"ccw\""));
}

#[test]
fn railml_emits_speed_and_radius_entries() {
    let a = l_shape();
    let xml = railml::to_railml(&a);
    assert!(xml.contains("maxSpeed=\"80.0\""));
    assert!(xml.contains("<radiusChange"));
    assert!(xml.contains("<gradientChange"));
}
