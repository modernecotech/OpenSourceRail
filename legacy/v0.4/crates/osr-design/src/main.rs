//! osr-design — end-to-end design generator for one city.
//!
//! Inputs
//! ------
//! * `--sidecar <path>` — the `{slug}.grid.json` emitted by osr_geo.
//! * `--slug <slug>`    — city slug (used for output filenames).
//! * `--population <n>` — used to pick a topology archetype via the recipe.
//! * `--out-dir <path>` — where to write design.toml, corridor.geojson,
//!   design-quality.yaml, stations.json.
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
    civil::classify_segments,
    raster::load_bundle,
    solver::DemandWeight,
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
    version
)]
struct Args {
    /// Path to the `{slug}.grid.json` sidecar written by osr_geo.
    #[arg(long)]
    sidecar: PathBuf,

    /// City slug (e.g. "samawah").
    #[arg(long)]
    slug: String,

    /// Population — selects topology archetype. When omitted, looks up
    /// `--slug` in `--catalog` (defaults to
    /// `lib/city-batches/world-sample.toml`) and uses the canonical
    /// figure committed there. Pass explicitly only to override for
    /// what-if analysis; production runs should rely on the catalog.
    #[arg(long)]
    population: Option<u64>,

    /// Country ISO-2 for fare system + climate hints (passed through
    /// to design.toml for the recipe to resolve downstream). When
    /// omitted, looks up `--slug` in `--catalog`.
    #[arg(long)]
    country: Option<String>,

    /// Path to the city catalog (canonical population + country source
    /// of truth). Defaults to walking up from `--out-dir` to find
    /// `lib/city-batches/world-sample.toml`.
    #[arg(long)]
    catalog: Option<PathBuf>,

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
    population: u64,
    bundle: &osr_routing::raster::RasterBundle,
    lines: &[Line],
) -> Result<()> {
    let cache = CorridorCache {
        schema_version: CORRIDOR_CACHE_SCHEMA_VERSION,
        slug: args.slug.clone(),
        population,
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
    population: u64,
    bundle: &osr_routing::raster::RasterBundle,
) -> Result<Vec<Line>> {
    let bytes =
        fs::read(path).with_context(|| format!("reading corridor cache from {:?}", path))?;
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
        || cache.population != population
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

/// Minimal subset of the catalog schema — every city listed in
/// `lib/city-batches/world-sample.toml` carries at least the slug,
/// country, and population that downstream tooling consumes.
#[derive(Deserialize)]
struct CatalogCity {
    slug: String,
    country: String,
    population: u64,
    climate: Option<String>,
    profile: Option<String>,
}

#[derive(Deserialize)]
struct CatalogFile {
    cities: Vec<CatalogCity>,
}

/// Walk upward from `out_dir` (and the binary's CWD) looking for the
/// canonical catalog at `lib/city-batches/world-sample.toml`. Returns
/// the path on first hit, or None.
fn locate_catalog(out_dir: &Path) -> Option<PathBuf> {
    const REL: &str = "lib/city-batches/world-sample.toml";
    let mut starts: Vec<PathBuf> = Vec::new();
    if let Ok(abs) = std::fs::canonicalize(out_dir) {
        starts.push(abs);
    }
    if let Ok(cwd) = std::env::current_dir() {
        starts.push(cwd);
    }
    for start in &starts {
        for ancestor in start.ancestors() {
            let candidate = ancestor.join(REL);
            if candidate.exists() {
                return Some(candidate);
            }
        }
    }
    None
}

fn lookup_catalog_city(catalog_path: &Path, slug: &str) -> Result<CatalogCity> {
    let bytes = fs::read_to_string(catalog_path)
        .with_context(|| format!("reading city catalog from {:?}", catalog_path))?;
    let parsed: CatalogFile = toml::from_str(&bytes)
        .with_context(|| format!("parsing city catalog at {:?}", catalog_path))?;
    parsed
        .cities
        .into_iter()
        .find(|c| c.slug == slug)
        .ok_or_else(|| {
            anyhow!(
                "slug {:?} not found in catalog {:?}; either add it \
                 there (canonical) or pass --population and --country \
                 explicitly to override",
                slug,
                catalog_path
            )
        })
}

fn main() -> Result<()> {
    let mut args = Args::parse();

    // Resolve population + country from the catalog when not explicitly
    // overridden on the CLI. The catalog is the single source of
    // truth — see `lib/city-batches/world-sample.toml` header.
    if args.population.is_none()
        || args.country.is_none()
        || args.climate.is_none()
        || args.profile.is_none()
    {
        let catalog_path = args
            .catalog
            .clone()
            .or_else(|| locate_catalog(&args.out_dir))
            .ok_or_else(|| {
                anyhow!(
                    "could not find lib/city-batches/world-sample.toml \
                     and --population / --country were not provided. \
                     Pass --catalog or both --population and --country \
                     explicitly."
                )
            })?;
        let entry = lookup_catalog_city(&catalog_path, &args.slug)?;
        if args.population.is_none() {
            args.population = Some(entry.population);
            eprintln!(
                "catalog: {} → population = {} (from {:?})",
                args.slug, entry.population, catalog_path
            );
        }
        if args.country.is_none() {
            args.country = Some(entry.country.clone());
            eprintln!(
                "catalog: {} → country = {} (from {:?})",
                args.slug, entry.country, catalog_path
            );
        }
        if args.climate.is_none() {
            args.climate = entry.climate.clone();
            if let Some(climate) = args.climate.as_deref() {
                eprintln!(
                    "catalog: {} → climate = {} (from {:?})",
                    args.slug, climate, catalog_path
                );
            }
        }
        if args.profile.is_none() {
            args.profile = entry.profile.clone();
            if let Some(profile) = args.profile.as_deref() {
                eprintln!(
                    "catalog: {} → profile = {} (from {:?})",
                    args.slug, profile, catalog_path
                );
            }
        }
    }
    // Past this point both fields are populated.
    let population = args.population.expect("population resolved above");
    let country = args.country.clone().expect("country resolved above");

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
    let budget = budget_for_population(population);

    let mut lines = if args.design_only {
        read_corridor_cache(&cache_path, &args, population, &bundle)?
    } else {
        eprintln!(
            "budget: max_lines={}, max_total_m={:.0}, min_cov/km={:.0}, top_k={}",
            budget.max_lines, budget.max_total_route_m, budget.min_coverage_per_km, budget.top_k,
        );
        let l = greedy_synthesize_lines(
            &bundle.grid,
            &bundle.anchors,
            DemandWeight(args.demand_weight),
            &budget,
        )?;
        // Ensure parent dir exists before the cache write.
        fs::create_dir_all(&args.out_dir)?;
        write_corridor_cache(&cache_path, &args, population, &bundle, &l)?;
        l
    };

    // When a radial endpoint stops 600–1200 m short of a circle line, build a
    // real routed connector to it. Sub-600 m approaches become paired station
    // complexes below; larger gaps remain explicit topology-review findings.
    let extended_termini = osr_routing::connect_radial_termini_to_rings(
        &mut lines,
        &bundle.grid,
        30,
        60,
        DemandWeight(args.demand_weight),
    );
    if extended_termini > 0 {
        eprintln!("extended {extended_termini} radial terminus/termini onto ring lines");
    }

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
    // One explicit network-wide policy: 1.6 km in the high-demand centre,
    // 3 km across the ordinary urban area, and up to 7 km on suburban
    // approaches / the lowest-demand outer fringe.
    // Forced shared interchanges are the only intentional close-stop
    // exception. A wider metadata snap labels nearby hospitals, universities,
    // and other anchors without moving platforms off the routed corridor.
    let spacing = SpacingConfig {
        urban_core_m: 1600.0,
        urban_m: 3000.0,
        peri_urban_m: 7000.0,
        outer_m: 7000.0,
        snap_radius_cells: 25,
        ..SpacingConfig::default()
    };
    for line in &lines {
        let stations = place_stations(
            &bundle.grid,
            &bundle.anchors,
            &line.name,
            &line.cells,
            spacing,
        );
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

    // Force a station on each (radial, ring) pair where they cross or pass
    // within a viable station-complex envelope, so
    // ring lines are *connected* to the radials geographically as well
    // as topologically. Threshold of 30 cells (≈ 600 m) matches the
    // maximum transfer envelope used below and catches adjacent corridors
    // or a radial endpoint beside the ring. Without this, the in-line
    // station spacing places ring stops on whatever anchor is convenient
    // — almost never on the radial — and the rendered map shows a ring
    // that touches no other line.
    osr_routing::force_ring_radial_crossings(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );

    // Forced hub/ring stations may replace an ordinary stop close to a line
    // end. Reassert exact operational endpoints before grouping transfers so
    // SUMO chainage always spans the complete declared route.
    osr_routing::ensure_endpoint_stations(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        spacing,
    );
    osr_routing::force_ring_radial_terminal_interchanges(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );

    // Multiple forced crossings can land on the same line inside a single
    // walkable complex. Keep one deterministic platform per line before the
    // cross-line grouping pass, avoiding duplicate stops a few hundred metres
    // apart while retaining all participating lines in the interchange.
    // Assign groups once before consolidation so forced transfer platforms
    // outrank nearby ordinary stops; the final merge below renumbers the
    // retained complexes after gap repair.
    osr_routing::merge_interchanges(&mut all_stations, 700.0);
    osr_routing::consolidate_inline_station_clusters(&mut all_stations, &lines, 1200.0);

    let filled_station_gaps = osr_routing::fill_large_station_gaps(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        spacing,
    );
    if filled_station_gaps > 0 {
        eprintln!("filled {filled_station_gaps} station gap(s) above its local demand-band limit");
    }

    // Reassert terminal transfers after consolidation: a ring can have two
    // forced platforms less than 1.2 km apart. The terminal pass replaces
    // ordinary ring stops inside that spacing envelope, then gap repair fills
    // any resulting interval without disturbing the terminal complex.
    osr_routing::force_ring_radial_terminal_interchanges(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );
    osr_routing::force_ring_radial_crossings(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );
    osr_routing::merge_interchanges(&mut all_stations, 700.0);
    osr_routing::consolidate_inline_station_clusters(&mut all_stations, &lines, 1200.0);
    let terminal_repair_gaps = osr_routing::fill_large_station_gaps(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        spacing,
    );
    if terminal_repair_gaps > 0 {
        eprintln!("filled {terminal_repair_gaps} post-transfer station gap(s)");
    }
    // Grouping and consolidation affect each other: removing one member can
    // turn a former interchange platform back into an ordinary stop. Iterate
    // to a stable station set, including the ring's first/last interval.
    let mut final_stations_removed = 0;
    for _ in 0..4 {
        osr_routing::merge_interchanges(&mut all_stations, 700.0);
        let before = all_stations.len();
        osr_routing::consolidate_inline_station_clusters(&mut all_stations, &lines, 1200.0);
        osr_routing::consolidate_ring_wrap_station_clusters(
            &mut all_stations,
            &lines,
            bundle.grid.reference.cell_m,
            1200.0,
        );
        let removed = before - all_stations.len();
        final_stations_removed += removed;
        if removed == 0 {
            break;
        }
    }
    if final_stations_removed > 0 {
        eprintln!("consolidated {final_stations_removed} station(s) in final layout settling");
    }
    osr_routing::force_ring_radial_crossings(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );
    // Terminal transfers inside the 600 m walkable envelope are mandatory.
    // Reassert them after settling so consolidation cannot silently remove
    // the final ring platform serving a radial endpoint.
    osr_routing::force_ring_radial_terminal_interchanges(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );

    // Collapse forced cross-line stops into single interchange
    // complexes. The grouping radius deliberately sits just above the
    // ring-crossing threshold: the old 200 m forcing / 500 m merging / 200 m
    // archetype trio produced grouped transfers that were subsequently
    // labelled as ordinary stations.
    // A 700 m grouping radius covers the small raster-to-geodesic mismatch at
    // the edge of the 600 m grid transfer envelope without placing extra stops.
    osr_routing::merge_interchanges(&mut all_stations, 700.0);
    let before_post_terminal_settling = all_stations.len();
    osr_routing::consolidate_inline_station_clusters(&mut all_stations, &lines, 1200.0);
    let post_terminal_inline_removed = before_post_terminal_settling - all_stations.len();
    let post_terminal_wrap_removed = osr_routing::consolidate_ring_wrap_station_clusters(
        &mut all_stations,
        &lines,
        bundle.grid.reference.cell_m,
        1200.0,
    );
    if post_terminal_inline_removed > 0 || post_terminal_wrap_removed > 0 {
        osr_routing::merge_interchanges(&mut all_stations, 700.0);
    }
    // The final settling pass can remove the only grouped platform for a
    // mandatory ring/radial transfer in tight corridors. Reassert these pairs
    // after settling, then validate the exact station set we will emit.
    osr_routing::force_ring_radial_crossings(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );
    osr_routing::force_ring_radial_terminal_interchanges(
        &mut all_stations,
        &lines,
        &bundle.grid,
        &bundle.anchors,
        30,
    );
    osr_routing::merge_interchanges(&mut all_stations, 700.0);
    osr_routing::force_ring_radial_group_ids(
        &mut all_stations,
        &lines,
        bundle.grid.reference.cell_m,
        600.0,
    );
    osr_routing::consolidate_inline_station_clusters(&mut all_stations, &lines, 1200.0);
    osr_routing::consolidate_ring_wrap_station_clusters(
        &mut all_stations,
        &lines,
        bundle.grid.reference.cell_m,
        1200.0,
    );
    osr_routing::merge_interchanges(&mut all_stations, 700.0);
    osr_routing::force_ring_radial_group_ids(
        &mut all_stations,
        &lines,
        bundle.grid.reference.cell_m,
        600.0,
    );
    let merged_count = all_stations
        .iter()
        .filter_map(|s| s.junction_group)
        .collect::<std::collections::BTreeSet<_>>()
        .len();
    if merged_count > 0 {
        eprintln!("merged into {merged_count} interchange complexes");
    }

    let layout_issues = osr_routing::station_layout_issues(
        &all_stations,
        &lines,
        bundle.grid.reference.cell_m,
        600.0,
        1200.0,
        1200.0 - bundle.grid.reference.cell_m,
    );
    if !layout_issues.is_empty() {
        return Err(anyhow!(
            "generated station layout failed hard invariants:\n  - {}",
            layout_issues.join("\n  - ")
        ));
    }

    fs::create_dir_all(&args.out_dir)?;
    emit::write_all(
        &args.out_dir,
        &args.slug,
        &country,
        args.climate.as_deref(),
        args.profile.as_deref(),
        population,
        &bundle,
        &lines,
        &all_stations,
        &civil_per_line,
    )?;

    eprintln!("wrote design artefacts to {:?}", args.out_dir);
    Ok(())
}
