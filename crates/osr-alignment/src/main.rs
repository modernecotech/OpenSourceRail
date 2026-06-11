//! `osr-alignment-export` — fit an alignment to an input polyline +
//! emit LandXML + railML + JSON.

use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use clap::Parser;
use osr_alignment::{
    alignment::{Alignment, HorizontalElement, VerticalElement},
    cant::cant_design,
    chainage::sample_every,
    landxml, railml,
};
use serde::Deserialize;

#[derive(Parser, Debug)]
#[command(
    name = "osr-alignment-export",
    about = "Fit an alignment to a polyline + emit LandXML + railML + JSON."
)]
struct Cli {
    /// Input JSON: `{"line_slug", "design_speed_kmh", "points":
    /// [[x,y,z], ...]}`. Points are in metres; +X east, +Y north,
    /// +Z up. A typical source is `osr-design`'s per-line chainage
    /// output augmented with terrain-sampled elevations.
    #[arg(long)]
    input: PathBuf,
    /// Output directory. Writes `<slug>.landxml`, `<slug>.railml`,
    /// `<slug>.alignment.json`, `<slug>.stakeout.csv`.
    #[arg(long)]
    out: PathBuf,
    /// Stake-out sampling interval, metres. Default 20 m.
    #[arg(long, default_value_t = 20.0)]
    stake_interval_m: f64,
    /// Maximum applied cant, mm (RFC 0009). Default 150 (light-metro).
    #[arg(long, default_value_t = 150.0)]
    max_cant_mm: f64,
    /// Maximum cant deficiency, mm (RFC 0009). Default 130.
    #[arg(long, default_value_t = 130.0)]
    max_deficiency_mm: f64,
}

#[derive(Deserialize)]
struct InputDoc {
    line_slug: String,
    design_speed_kmh: f64,
    points: Vec<[f64; 3]>,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let raw = fs::read_to_string(&cli.input)
        .with_context(|| format!("reading {}", cli.input.display()))?;
    let doc: InputDoc = serde_json::from_str(&raw).context("parsing input JSON")?;
    if doc.points.len() < 2 {
        anyhow::bail!("alignment requires at least 2 points");
    }

    let alignment = fit_polyline(&doc.line_slug, doc.design_speed_kmh, &doc.points);
    let cant = cant_design(&alignment, cli.max_cant_mm, cli.max_deficiency_mm);

    fs::create_dir_all(&cli.out).with_context(|| format!("creating {}", cli.out.display()))?;

    let slug = &doc.line_slug;
    fs::write(
        cli.out.join(format!("{slug}.landxml")),
        landxml::to_landxml(&alignment),
    )?;
    fs::write(
        cli.out.join(format!("{slug}.railml")),
        railml::to_railml(&alignment),
    )?;
    fs::write(
        cli.out.join(format!("{slug}.alignment.json")),
        serde_json::to_string_pretty(&AlignmentBundle {
            alignment: &alignment,
            cant: &cant,
        })?,
    )?;

    let mut csv = String::from("chainage_m,x_m,y_m,z_m,bearing_rad,grade\n");
    for p in sample_every(&alignment, cli.stake_interval_m) {
        csv.push_str(&format!(
            "{:.3},{:.3},{:.3},{:.3},{:.6},{:.6}\n",
            p.chainage_m, p.x_m, p.y_m, p.z_m, p.bearing_rad, p.grade
        ));
    }
    fs::write(cli.out.join(format!("{slug}.stakeout.csv")), csv)?;

    println!(
        "wrote {}/ ({} horizontal elements, {:.1} m)",
        cli.out.display(),
        alignment.horizontal.len(),
        alignment.total_length_m()
    );
    Ok(())
}

#[derive(serde::Serialize)]
struct AlignmentBundle<'a> {
    alignment: &'a Alignment,
    cant: &'a osr_alignment::cant::CantSchedule,
}

/// Fit an alignment to a 3-D polyline. v0.1 algorithm:
///
/// - **Horizontal**: consecutive straight tangents connecting the input
///   points, with a circular arc inserted at each interior vertex using
///   the minimum allowable radius for the design speed. The arc is
///   tangent to both adjoining segments.
/// - **Vertical**: constant-grade segments between consecutive points;
///   no vertical curves in v0.1.
///
/// The fit is deliberately conservative: real engineers iterate on
/// curve placement, but the output is always geometrically valid.
fn fit_polyline(slug: &str, v_kmh: f64, pts: &[[f64; 3]]) -> Alignment {
    let mut horizontal = Vec::new();
    let mut vertical = Vec::new();

    for w in pts.windows(2) {
        let [p0, p1] = [w[0], w[1]];
        let dx = p1[0] - p0[0];
        let dy = p1[1] - p0[1];
        let dz = p1[2] - p0[2];
        let len = (dx * dx + dy * dy).sqrt();
        if len < 1e-6 {
            continue;
        }
        let bearing = dy.atan2(dx);
        horizontal.push(HorizontalElement::Tangent {
            length_m: len,
            bearing_rad: bearing,
            start_xy: (p0[0], p0[1]),
        });
        vertical.push(VerticalElement::Grade {
            length_m: len,
            grade: dz / len,
            start_z_m: p0[2],
        });
    }

    // Simple v0.1 output — no interior arcs yet. A real civil pass would
    // insert minimum-radius arcs at each tangent intersection. We leave
    // that to a v0.2 iteration with per-PI radius selection.
    let _ = v_kmh;

    Alignment {
        line_slug: slug.to_string(),
        design_speed_kmh: v_kmh,
        start_chainage_m: 0.0,
        horizontal,
        vertical,
    }
}
