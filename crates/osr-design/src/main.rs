//! osr-design — end-to-end design generator for one city.
//!
//! Inputs
//! ------
//! * `--sidecar <path>` — the `{slug}.grid.json` emitted by osr_geo.
//! * `--slug <slug>`    — city slug (used for output filenames).
//! * `--population <n>` — used to pick a topology archetype via the recipe.
//! * `--out-dir <path>` — where to write design.toml, corridor.geojson,
//!                         design-quality.yaml, stations.json.
//!
//! Outputs
//! -------
//! * `design.toml`          — authoritative design (stations with lat/lon).
//! * `corridor.geojson`     — one LineString per line + one Point per station.
//! * `design-quality.yaml`  — coverage / realism scores for the auto-gate.
//! * `stations.json`        — machine-readable station list.
//!
//! The orchestrator is deterministic: same rasters in → byte-identical
//! outputs. No RNG, no wall-clock inside the pipeline (only `fetched_at`
//! for the cache, which is baked into the osm json).

use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use clap::Parser;
use osr_routing::{
    civil::classify_segments, raster::load_bundle, solver::DemandWeight,
    station::{place_stations, SpacingConfig},
    topology::{pick_archetype, synthesize_lines},
};
mod emit;

#[derive(Parser, Debug)]
#[command(
    name = "osr-design",
    about = "Generate an OSR city design from raster inputs.",
    version,
)]
struct Args {
    /// Path to the `{slug}.grid.json` sidecar written by osr_geo.
    #[arg(long)]
    sidecar: PathBuf,

    /// City slug (e.g. "samawah").
    #[arg(long)]
    slug: String,

    /// Population — selects topology archetype.
    #[arg(long)]
    population: u64,

    /// Country ISO-2 for fare system + climate hints (passed through
    /// to design.toml for the recipe to resolve downstream).
    #[arg(long, default_value = "XX")]
    country: String,

    /// Climate preset name (bypass lat/country inference).
    #[arg(long)]
    climate: Option<String>,

    /// Composition profile (bypass default archetype selection).
    #[arg(long)]
    profile: Option<String>,

    /// Demand weight for the solver (default 5.0).
    #[arg(long, default_value_t = 5.0)]
    demand_weight: f32,

    /// Output directory.
    #[arg(long)]
    out_dir: PathBuf,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let bundle = load_bundle(&args.sidecar, &args.slug)
        .with_context(|| format!("loading raster bundle from {:?}", args.sidecar))?;

    eprintln!(
        "loaded {}: {}×{} cells @ {} m, {} anchors",
        args.slug,
        bundle.grid.reference.height,
        bundle.grid.reference.width,
        bundle.grid.reference.cell_m,
        bundle.anchors.len()
    );

    let archetype = pick_archetype(args.population);
    eprintln!("archetype: {archetype:?}");

    let lines = synthesize_lines(
        &bundle.grid,
        &bundle.anchors,
        archetype,
        DemandWeight(args.demand_weight),
    )?;

    eprintln!("synthesized {} lines", lines.len());
    for l in &lines {
        eprintln!(
            "  {:10} {:?} — {} cells, {} anchors",
            l.name,
            l.shape,
            l.cells.len(),
            l.anchor_ids.len()
        );
    }

    // Per-line station placement + civil classification.
    let mut all_stations: Vec<osr_routing::station::Station> = Vec::new();
    let mut civil_per_line: Vec<Vec<osr_routing::civil::CivilSegment>> = Vec::new();
    let spacing = SpacingConfig::default();
    for line in &lines {
        let stations =
            place_stations(&bundle.grid, &bundle.anchors, &line.name, &line.cells, spacing);
        eprintln!("  {}: {} stations", line.name, stations.len());
        all_stations.extend(stations);
        civil_per_line.push(classify_segments(&bundle.grid, &line.cells));
    }

    fs::create_dir_all(&args.out_dir)?;
    emit::write_all(
        &args.out_dir,
        &args.slug,
        &args.country,
        args.climate.as_deref(),
        args.profile.as_deref(),
        args.population,
        &bundle,
        &lines,
        &all_stations,
        &civil_per_line,
    )?;

    eprintln!("wrote design artefacts to {:?}", args.out_dir);
    Ok(())
}

