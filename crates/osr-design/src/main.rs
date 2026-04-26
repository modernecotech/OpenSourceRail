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
use std::path::{Path, PathBuf};

use anyhow::{anyhow, Context, Result};
use clap::Parser;
use osr_routing::{
    civil::classify_segments, raster::load_bundle, solver::DemandWeight,
    station::{place_stations, SpacingConfig},
    topology::{budget_for_population, greedy_synthesize_lines, hub_cell, Line, HUB_RADIUS_CELLS},
};
use serde::{Deserialize, Serialize};
mod emit;

const CORRIDOR_CACHE_SCHEMA_VERSION: u32 = 1;

/// Cached output of the greedy planner. Loading this skips the
/// (expensive) routing phase, so iteration on station placement, civil
/// classification, or emit format takes seconds instead of minutes.
///
/// Cache invalidation is by exact match of `slug`, `population`,
/// `demand_weight`, and the underlying grid dimensions/cell size. If
/// any of those change, callers should regenerate by running without
/// `--design-only`.
#[derive(Serialize, Deserialize)]
struct CorridorCache {
    schema_version: u32,
    slug: String,
    population: u64,
    demand_weight: f32,
    grid_height: usize,
    grid_width: usize,
    grid_cell_m: f64,
    lines: Vec<Line>,
}

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

    /// Skip the greedy routing phase and load corridors from
    /// `{out_dir}/corridors.json` (or `--corridor-cache` if set). Use
    /// this when iterating on station spacing, civil classification, or
    /// emit format — anything downstream of routing — so a Baghdad
    /// re-emit takes ~5 s instead of ~2 min.
    #[arg(long)]
    design_only: bool,

    /// Override location of the corridor cache file. Defaults to
    /// `{out_dir}/corridors.json`.
    #[arg(long)]
    corridor_cache: Option<PathBuf>,
}

fn corridor_cache_path(args: &Args) -> PathBuf {
    args.corridor_cache
        .clone()
        .unwrap_or_else(|| args.out_dir.join("corridors.json"))
}

fn write_corridor_cache(
    path: &Path,
    args: &Args,
    bundle: &osr_routing::raster::RasterBundle,
    lines: &[Line],
) -> Result<()> {
    let cache = CorridorCache {
        schema_version: CORRIDOR_CACHE_SCHEMA_VERSION,
        slug: args.slug.clone(),
        population: args.population,
        demand_weight: args.demand_weight,
        grid_height: bundle.grid.reference.height,
        grid_width: bundle.grid.reference.width,
        grid_cell_m: bundle.grid.reference.cell_m,
        lines: lines.to_vec(),
    };
    let json = serde_json::to_string_pretty(&cache).context("serializing corridor cache")?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).ok();
    }
    fs::write(path, json).with_context(|| format!("writing corridor cache to {:?}", path))?;
    eprintln!("cached corridors to {:?}", path);
    Ok(())
}

fn read_corridor_cache(
    path: &Path,
    args: &Args,
    bundle: &osr_routing::raster::RasterBundle,
) -> Result<Vec<Line>> {
    let bytes = fs::read(path)
        .with_context(|| format!("reading corridor cache from {:?}", path))?;
    let cache: CorridorCache =
        serde_json::from_slice(&bytes).context("parsing corridor cache JSON")?;
    if cache.schema_version != CORRIDOR_CACHE_SCHEMA_VERSION {
        return Err(anyhow!(
            "corridor cache schema {} != expected {}; rerun without --design-only",
            cache.schema_version,
            CORRIDOR_CACHE_SCHEMA_VERSION
        ));
    }
    if cache.slug != args.slug
        || cache.population != args.population
        || (cache.demand_weight - args.demand_weight).abs() > 1e-6
        || cache.grid_height != bundle.grid.reference.height
        || cache.grid_width != bundle.grid.reference.width
        || (cache.grid_cell_m - bundle.grid.reference.cell_m).abs() > 1e-6
    {
        return Err(anyhow!(
            "corridor cache parameters do not match current run \
             (slug/pop/demand-weight/grid). Rerun without --design-only \
             to regenerate."
        ));
    }
    eprintln!(
        "loaded {} cached lines from {:?} (skipping greedy routing)",
        cache.lines.len(),
        path
    );
    Ok(cache.lines)
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

    let cache_path = corridor_cache_path(&args);
    let budget = budget_for_population(args.population);

    let lines = if args.design_only {
        read_corridor_cache(&cache_path, &args, &bundle)?
    } else {
        eprintln!(
            "budget: max_lines={}, max_total_m={:.0}, min_cov/km={:.0}, top_k={}",
            budget.max_lines,
            budget.max_total_route_m,
            budget.min_coverage_per_km,
            budget.top_k,
        );
        let l = greedy_synthesize_lines(
            &bundle.grid,
            &bundle.anchors,
            DemandWeight(args.demand_weight),
            &budget,
        )?;
        // Ensure parent dir exists before the cache write.
        fs::create_dir_all(&args.out_dir)?;
        write_corridor_cache(&cache_path, &args, &bundle, &l)?;
        l
    };

    eprintln!("using {} lines", lines.len());
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
    // Bigger cities (>=4 lines under the population budget) get wider
    // station spacing — at default 800/1200/1800 m a 6-line Baghdad
    // network drops ~440 stations and the central core renders as an
    // unreadable scrum of close stops. Real megacity metros sit at
    // 1.0–1.4 km core spacing (Cairo Line 3 ≈ 1.1 km, Tehran Line 1 ≈
    // 1.2 km).
    // Megacity (>= 4-line) radials are long-haul cross-city services —
    // 40 km end-to-end. At 1.1/1.6/2.2 km the central trunk dropped a
    // stop every ~1.3 km, which made the radials look like local lines
    // rather than fast trunk routes. Bumping to 1.5/2.0/2.7 km gives a
    // ~25-stop, ~1.7 km-average pattern that matches commuter-spaced
    // metro radials (Tokyo Chuo Rapid 1.9 km, Madrid Line 1 1.4 km
    // central / 2.0 km outer, Cairo Line 3 1.5 km). The ring keeps
    // tighter spacing (it's the slow tangential service) — applied
    // separately in `ring_spacing` below.
    let spacing = if budget.max_lines >= 4 {
        SpacingConfig {
            urban_core_m: 1500.0,
            urban_m: 2000.0,
            peri_urban_m: 2700.0,
            // Wider radial snap (8 cells = 160 m) lifts anchor_hit on
            // long megacity radials. With 1.5–2.7 km spacing each radial
            // drops only ~25 stops over 40+ km, so the 6-cell default
            // misses anchor clusters on the next block.
            snap_radius_cells: 8,
            ..SpacingConfig::default()
        }
    } else {
        SpacingConfig::default()
    };
    // Rings traverse the outer urban band where anchor density is sparser
    // and anchors are spread over wider street grids. The 6-cell (120 m)
    // default snap radius then misses many real anchor clusters along the
    // ring path, dragging the network's anchor-hit rate below the soft
    // gate. Widening the ring snap to 15 cells (300 m, ~ a typical
    // suburban block) pulls ring stations onto their nearest cluster
    // without affecting in-line spacing or radial placement. The wider
    // snap is safe here because rings are routed along arterials too —
    // an anchor 300 m off-corridor is still inside the same catchment
    // and reachable on foot via the cross-street.
    let ring_spacing = SpacingConfig {
        snap_radius_cells: 15,
        ..spacing
    };
    for line in &lines {
        let cfg = match line.shape {
            osr_routing::topology::LineShape::Ring => ring_spacing,
            _ => spacing,
        };
        let stations =
            place_stations(&bundle.grid, &bundle.anchors, &line.name, &line.cells, cfg);
        eprintln!("  {}: {} stations", line.name, stations.len());
        all_stations.extend(stations);
        civil_per_line.push(classify_segments(&bundle.grid, &line.cells));
    }

    // Force every radial through one CBD interchange. Without this each
    // radial places its closest-to-centre stop on a different downtown
    // block 250-400 m away — `merge_interchanges` then refuses to fold
    // them because the cross-line distance is over its threshold, and
    // the resulting map shows three near-misses instead of one downtown
    // hub. The `synthesize_lines` corridor logic separately drops the
    // self/cross-line penalties inside the hub circle so the radials
    // can converge on the same trunk before this runs.
    let hub = hub_cell(&bundle.grid);
    osr_routing::force_hub_stations(
        &mut all_stations,
        &lines,
        hub,
        &bundle.grid,
        &bundle.anchors,
        HUB_RADIUS_CELLS,
    );

    // Force a station on each (radial, ring) pair where they cross, so
    // ring lines are *connected* to the radials geographically as well
    // as topologically. Threshold of 10 cells (≈ 200 m) catches a near-
    // miss within a typical city block. Without this, the in-line
    // station spacing places ring stops on whatever anchor is convenient
    // — almost never on the radial — and the rendered map shows a ring
    // that touches no other line.
    osr_routing::force_ring_radial_crossings(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        10,
    );

    // Collapse cross-line stops within 500 m into single interchange
    // complexes. 250 m and 400 m both left visible crowding in the
    // central core (Samawah radial+ring on adjacent blocks); 500 m folds
    // those together while still being tight enough not to merge across
    // two real neighbourhoods. Real-world reference: typical metro
    // walking transfer is 400-600 m end-to-end.
    osr_routing::merge_interchanges(&mut all_stations, 500.0);
    let merged_count = all_stations
        .iter()
        .filter_map(|s| s.junction_group)
        .collect::<std::collections::BTreeSet<_>>()
        .len();
    if merged_count > 0 {
        eprintln!("merged into {merged_count} interchange complexes");
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

