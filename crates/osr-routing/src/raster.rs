//! Raster + grid I/O. Consumes the artefacts produced by `osr_geo.save_grid`.
//!
//! File layout (written by Python):
//!
//!   {slug}.grid.json       — envelope + dtypes + shapes
//!   {slug}.cost.npy        — f32 little-endian, row-major, shape (H, W)
//!   {slug}.demand.npy      — f32 little-endian, row-major, shape (H, W)
//!   {slug}.buildability.npy — u8  little-endian, row-major, shape (H, W)
//!   {slug}.water.npy       — optional u8 independent water mask
//!   {slug}.elevation.npy   — optional f32 open-DEM height in metres
//!   {slug}.terrain-slope.npy — optional f32 local ground slope percent
//!   {slug}.anchors.json    — list of {id, kind, weight, name, row, col, lat, lon}
//!
//! The `.npy` extension is a slight lie — they are raw byte streams, not
//! numpy's own .npy format. We avoid numpy's header because reading it
//! from Rust adds a dependency we do not need for two fixed dtypes.

use std::{
    collections::BTreeSet,
    fs,
    path::{Component, Path, PathBuf},
};

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Geographic reference for the raster grid.
///
/// Mirrors `osr_geo.rasterize.GridRef` so serde deserializes it directly
/// from the sidecar JSON.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GridRef {
    pub height: usize,
    pub width: usize,
    pub cell_m: f64,
    pub lat0: f64,
    pub bbox_south: f64,
    pub bbox_west: f64,
    pub bbox_north: f64,
    pub bbox_east: f64,
    pub m_per_deg_lat: f64,
    pub m_per_deg_lon: f64,
}

impl GridRef {
    /// Convert a cell centre (row, col) to (lat, lon).
    #[must_use]
    pub fn rc_to_latlon(&self, row: usize, col: usize) -> (f64, f64) {
        let dx_m = (col as f64 + 0.5) * self.cell_m;
        let dy_m = (row as f64 + 0.5) * self.cell_m;
        let lon = self.bbox_west + dx_m / self.m_per_deg_lon;
        let lat = self.bbox_north - dy_m / self.m_per_deg_lat;
        (lat, lon)
    }

    #[must_use]
    pub fn cells(&self) -> usize {
        self.height * self.width
    }
}

/// An aligned set of rasters + grid reference.
#[derive(Debug, Clone)]
pub struct Grid {
    pub reference: GridRef,
    pub cost: Vec<f32>,
    pub demand: Vec<f32>,
    pub buildability: Vec<u8>,
    /// Independent evidence keeps civil meaning out of the blended cost.
    pub water: Option<Vec<u8>>,
    pub elevation_m: Option<Vec<f32>>,
    pub terrain_slope_percent: Option<Vec<f32>>,
}

impl Grid {
    #[inline]
    #[must_use]
    pub fn idx(&self, row: usize, col: usize) -> usize {
        row * self.reference.width + col
    }

    #[inline]
    #[must_use]
    pub fn in_bounds(&self, row: isize, col: isize) -> bool {
        row >= 0
            && col >= 0
            && (row as usize) < self.reference.height
            && (col as usize) < self.reference.width
    }

    #[inline]
    #[must_use]
    pub fn cost_at(&self, row: usize, col: usize) -> f32 {
        self.cost[self.idx(row, col)]
    }

    #[inline]
    #[must_use]
    pub fn demand_at(&self, row: usize, col: usize) -> f32 {
        self.demand[self.idx(row, col)]
    }

    #[inline]
    #[must_use]
    pub fn is_buildable(&self, row: usize, col: usize) -> bool {
        self.buildability[self.idx(row, col)] != 0
            && self
                .water
                .as_ref()
                .is_none_or(|values| values[self.idx(row, col)] != 255)
    }

    #[inline]
    #[must_use]
    pub fn is_water(&self, row: usize, col: usize) -> bool {
        self.water_coverage_percent_at(row, col) > 0.0
    }

    #[inline]
    #[must_use]
    pub fn water_coverage_percent_at(&self, row: usize, col: usize) -> f32 {
        self.water
            .as_ref()
            .map_or(0.0, |values| f32::from(values[self.idx(row, col)]))
    }

    #[inline]
    #[must_use]
    pub fn excludes_station_for_water(&self, row: usize, col: usize) -> bool {
        self.water_coverage_percent_at(row, col) > 0.0
    }

    #[inline]
    #[must_use]
    pub fn elevation_at(&self, row: usize, col: usize) -> Option<f32> {
        self.elevation_m
            .as_ref()
            .map(|values| values[self.idx(row, col)])
            .filter(|value| value.is_finite())
    }

    #[inline]
    #[must_use]
    pub fn terrain_slope_at(&self, row: usize, col: usize) -> Option<f32> {
        self.terrain_slope_percent
            .as_ref()
            .map(|values| values[self.idx(row, col)])
            .filter(|value| value.is_finite())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Anchor {
    pub id: i64,
    pub kind: String,
    pub weight: f32,
    pub name: Option<String>,
    pub row: usize,
    pub col: usize,
    pub lat: f64,
    pub lon: f64,
}

#[derive(Debug, Clone)]
pub struct RasterBundle {
    pub grid: Grid,
    pub anchors: Vec<Anchor>,
    pub slug: String,
}

// ---- Sidecar JSON schema ---------------------------------------------

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct RasterSidecar {
    path: String,
    dtype: String,
    shape: Vec<usize>,
    byteorder: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct GridSidecar {
    grid: GridRef,
    rasters: Rasters,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Rasters {
    cost: RasterSidecar,
    demand: RasterSidecar,
    buildability: RasterSidecar,
    #[serde(default)]
    water: Option<RasterSidecar>,
    #[serde(default)]
    elevation: Option<RasterSidecar>,
    #[serde(default)]
    terrain_slope: Option<RasterSidecar>,
}

// ---- Errors ----------------------------------------------------------

#[derive(Debug, Error)]
pub enum RasterError {
    #[error("I/O: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON: {0}")]
    Json(#[from] serde_json::Error),
    #[error("dtype mismatch for {name}: expected {expected}, got {got}")]
    Dtype {
        name: &'static str,
        expected: &'static str,
        got: String,
    },
    #[error("shape mismatch for {name}: expected {expected:?}, got {got:?}")]
    Shape {
        name: &'static str,
        expected: Vec<usize>,
        got: Vec<usize>,
    },
    #[error("unsupported byteorder for {name}: {got}")]
    ByteOrder { name: &'static str, got: String },
    #[error("raster byte length mismatch for {name}: expected {expected}, got {got}")]
    ByteLen {
        name: &'static str,
        expected: usize,
        got: usize,
    },
    #[error("invalid raster bundle: {0}")]
    Invalid(String),
}

// ---- Public loader ---------------------------------------------------

/// Load a raster bundle from a sidecar path. Other files are resolved
/// relative to the sidecar directory (this matches `save_grid`).
pub fn load_bundle<P: AsRef<Path>>(sidecar: P, slug: &str) -> Result<RasterBundle, RasterError> {
    let sidecar = sidecar.as_ref();
    let dir = sidecar.parent().unwrap_or_else(|| Path::new("."));
    if slug.is_empty()
        || slug.len() > 160
        || !slug
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        return Err(RasterError::Invalid("unsafe or empty bundle slug".into()));
    }

    let side: GridSidecar = serde_json::from_str(&fs::read_to_string(sidecar)?)?;
    let reference = side.grid.clone();
    validate_reference(&reference)?;

    let expected_shape = vec![reference.height, reference.width];
    let cost = load_f32(
        &declared_path(dir, &side.rasters.cost.path)?,
        "cost",
        &side.rasters.cost,
        &expected_shape,
    )?;
    let demand = load_f32(
        &declared_path(dir, &side.rasters.demand.path)?,
        "demand",
        &side.rasters.demand,
        &expected_shape,
    )?;
    let buildability = load_u8(
        &declared_path(dir, &side.rasters.buildability.path)?,
        "buildability",
        &side.rasters.buildability,
        &expected_shape,
    )?;
    let water = side
        .rasters
        .water
        .as_ref()
        .map(|metadata| {
            load_u8(
                &declared_path(dir, &metadata.path)?,
                "water",
                metadata,
                &expected_shape,
            )
        })
        .transpose()?;
    let elevation_m = side
        .rasters
        .elevation
        .as_ref()
        .map(|metadata| {
            load_f32(
                &declared_path(dir, &metadata.path)?,
                "elevation",
                metadata,
                &expected_shape,
            )
        })
        .transpose()?;
    let terrain_slope_percent = side
        .rasters
        .terrain_slope
        .as_ref()
        .map(|metadata| {
            load_f32(
                &declared_path(dir, &metadata.path)?,
                "terrain_slope",
                metadata,
                &expected_shape,
            )
        })
        .transpose()?;
    if elevation_m.is_some() != terrain_slope_percent.is_some() {
        return Err(RasterError::Json(serde_json::Error::io(
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "elevation and terrain_slope rasters must be supplied together",
            ),
        )));
    }

    validate_values("cost", &cost, |value| {
        !value.is_nan() && *value >= 0.0 && *value != f32::NEG_INFINITY
    })?;
    validate_values("demand", &demand, |value| {
        value.is_finite() && *value >= 0.0
    })?;
    validate_values("buildability", &buildability, |value| {
        matches!(value, 0 | 1)
    })?;
    if let Some(values) = &water {
        validate_values("water", values, |value| *value <= 100 || *value == 255)?;
    }
    if let Some(values) = &elevation_m {
        validate_values("elevation", values, |value| value.is_finite())?;
    }
    if let Some(values) = &terrain_slope_percent {
        validate_values("terrain_slope", values, |value| {
            value.is_finite() && *value >= 0.0
        })?;
    }

    let anchors_path: PathBuf = dir.join(format!("{slug}.anchors.json"));
    let anchors: Vec<Anchor> = serde_json::from_str(&fs::read_to_string(&anchors_path)?)?;
    validate_anchors(&reference, &anchors)?;

    let grid = Grid {
        reference,
        cost,
        demand,
        buildability,
        water,
        elevation_m,
        terrain_slope_percent,
    };

    Ok(RasterBundle {
        grid,
        anchors,
        slug: slug.to_string(),
    })
}

fn declared_path(dir: &Path, value: &str) -> Result<PathBuf, RasterError> {
    let path = Path::new(value);
    let mut components = path.components();
    if value.is_empty()
        || !matches!(components.next(), Some(Component::Normal(_)))
        || components.next().is_some()
    {
        return Err(RasterError::Invalid(format!(
            "raster path {value:?} must be one relative file name"
        )));
    }
    Ok(dir.join(path))
}

fn validate_reference(reference: &GridRef) -> Result<(), RasterError> {
    let dimensions = reference.height.checked_mul(reference.width);
    let finite = [
        reference.cell_m,
        reference.lat0,
        reference.bbox_south,
        reference.bbox_west,
        reference.bbox_north,
        reference.bbox_east,
        reference.m_per_deg_lat,
        reference.m_per_deg_lon,
    ]
    .into_iter()
    .all(f64::is_finite);
    if reference.height == 0
        || reference.width == 0
        || dimensions.is_none()
        || !finite
        || reference.cell_m <= 0.0
        || reference.m_per_deg_lat <= 0.0
        || reference.m_per_deg_lon <= 0.0
        || reference.bbox_south >= reference.bbox_north
        || reference.bbox_west >= reference.bbox_east
        || !(-90.0..=90.0).contains(&reference.bbox_south)
        || !(-90.0..=90.0).contains(&reference.bbox_north)
        || !(-180.0..=180.0).contains(&reference.bbox_west)
        || !(-180.0..=180.0).contains(&reference.bbox_east)
    {
        return Err(RasterError::Invalid(
            "grid dimensions or geographic reference are invalid".into(),
        ));
    }
    Ok(())
}

fn validate_values<T>(
    name: &'static str,
    values: &[T],
    valid: impl Fn(&T) -> bool,
) -> Result<(), RasterError> {
    if let Some(index) = values.iter().position(|value| !valid(value)) {
        return Err(RasterError::Invalid(format!(
            "{name} has an invalid value at cell {index}"
        )));
    }
    Ok(())
}

fn validate_anchors(reference: &GridRef, anchors: &[Anchor]) -> Result<(), RasterError> {
    let mut ids = BTreeSet::new();
    for anchor in anchors {
        if !ids.insert(anchor.id)
            || anchor.row >= reference.height
            || anchor.col >= reference.width
            || !anchor.weight.is_finite()
            || anchor.weight < 0.0
            || !anchor.lat.is_finite()
            || !anchor.lon.is_finite()
            || !(-90.0..=90.0).contains(&anchor.lat)
            || !(-180.0..=180.0).contains(&anchor.lon)
        {
            return Err(RasterError::Invalid(format!(
                "anchor {} is duplicated or outside the grid/value domain",
                anchor.id
            )));
        }
    }
    Ok(())
}

fn check_sidecar(
    name: &'static str,
    dtype: &str,
    expected_dtype: &'static str,
    shape: &[usize],
    expected_shape: &[usize],
    byteorder: &str,
) -> Result<(), RasterError> {
    if dtype != expected_dtype {
        return Err(RasterError::Dtype {
            name,
            expected: expected_dtype,
            got: dtype.to_string(),
        });
    }
    if shape != expected_shape {
        return Err(RasterError::Shape {
            name,
            expected: expected_shape.to_vec(),
            got: shape.to_vec(),
        });
    }
    if byteorder != "little" {
        return Err(RasterError::ByteOrder {
            name,
            got: byteorder.to_string(),
        });
    }
    Ok(())
}

fn load_f32(
    path: &Path,
    name: &'static str,
    side: &RasterSidecar,
    expected_shape: &[usize],
) -> Result<Vec<f32>, RasterError> {
    check_sidecar(
        name,
        &side.dtype,
        "f32",
        &side.shape,
        expected_shape,
        &side.byteorder,
    )?;
    let bytes = fs::read(path)?;
    let ncells = expected_shape
        .iter()
        .try_fold(1_usize, |product, value| product.checked_mul(*value))
        .ok_or_else(|| RasterError::Invalid("raster cell count overflows usize".into()))?;
    let expected_bytes = ncells
        .checked_mul(4)
        .ok_or_else(|| RasterError::Invalid("raster byte count overflows usize".into()))?;
    if bytes.len() != expected_bytes {
        return Err(RasterError::ByteLen {
            name,
            expected: expected_bytes,
            got: bytes.len(),
        });
    }
    let mut out = Vec::with_capacity(ncells);
    for chunk in bytes.chunks_exact(4) {
        out.push(f32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]));
    }
    Ok(out)
}

fn load_u8(
    path: &Path,
    name: &'static str,
    side: &RasterSidecar,
    expected_shape: &[usize],
) -> Result<Vec<u8>, RasterError> {
    check_sidecar(
        name,
        &side.dtype,
        "u8",
        &side.shape,
        expected_shape,
        &side.byteorder,
    )?;
    let bytes = fs::read(path)?;
    let ncells = expected_shape
        .iter()
        .try_fold(1_usize, |product, value| product.checked_mul(*value))
        .ok_or_else(|| RasterError::Invalid("raster cell count overflows usize".into()))?;
    if bytes.len() != ncells {
        return Err(RasterError::ByteLen {
            name,
            expected: ncells,
            got: bytes.len(),
        });
    }
    Ok(bytes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use tempfile::tempdir;

    #[test]
    fn gridref_rc_to_latlon_inverts_corner() {
        // 10 x 10 grid, 100 m cells, centered at 0 N / 0 E.
        let g = GridRef {
            height: 10,
            width: 10,
            cell_m: 100.0,
            lat0: 0.0,
            bbox_south: -0.0045,
            bbox_west: -0.0045,
            bbox_north: 0.0045,
            bbox_east: 0.0045,
            m_per_deg_lat: 111_132.0,
            m_per_deg_lon: 111_320.0,
        };
        // Cell (0, 0) should be near the NW corner.
        let (lat, lon) = g.rc_to_latlon(0, 0);
        assert!(lat < g.bbox_north && lat > g.bbox_south);
        assert!(lon > g.bbox_west && lon < g.bbox_east);
    }

    fn write_bundle(root: &Path, raster_path: &str, cost: f32, water: u8) -> PathBuf {
        let sidecar = root.join("test.grid.json");
        let metadata = |path: &str, dtype: &str| {
            json!({
                "path": path, "dtype": dtype, "shape": [1, 1], "byteorder": "little"
            })
        };
        fs::write(root.join("declared.cost"), cost.to_le_bytes()).unwrap();
        fs::write(root.join("demand"), 0.5_f32.to_le_bytes()).unwrap();
        fs::write(root.join("buildability"), [1]).unwrap();
        fs::write(root.join("water"), [water]).unwrap();
        fs::write(root.join("test.anchors.json"), "[]").unwrap();
        fs::write(
            &sidecar,
            serde_json::to_vec(&json!({
                "grid": {"height":1,"width":1,"cell_m":20.0,"lat0":0.5,
                    "bbox_south":0.0,"bbox_west":0.0,"bbox_north":1.0,"bbox_east":1.0,
                    "m_per_deg_lat":111132.0,"m_per_deg_lon":111320.0},
                "rasters": {
                    "cost": metadata(raster_path, "f32"),
                    "demand": metadata("demand", "f32"),
                    "buildability": metadata("buildability", "u8"),
                    "water": metadata("water", "u8")
                }
            }))
            .unwrap(),
        )
        .unwrap();
        sidecar
    }

    #[test]
    fn loader_uses_declared_paths_and_rejects_path_traversal() {
        let root = tempdir().unwrap();
        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        let bundle = load_bundle(&sidecar, "test").unwrap();
        assert_eq!(bundle.grid.cost, vec![8.0]);
        assert_eq!(bundle.grid.water, Some(vec![25]));

        let unknown = write_bundle(root.path(), "declared.cost", 8.0, 255);
        let unknown = load_bundle(&unknown, "test").unwrap();
        assert!(!unknown.grid.is_buildable(0, 0));
        assert!(unknown.grid.excludes_station_for_water(0, 0));

        let sidecar = write_bundle(root.path(), "../outside", 8.0, 25);
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Invalid(_))
        ));
    }

    #[test]
    fn loader_rejects_invalid_topography_values_and_slug() {
        let root = tempdir().unwrap();
        let sidecar = write_bundle(root.path(), "declared.cost", f32::NAN, 25);
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Invalid(_))
        ));
        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 101);
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Invalid(_))
        ));
        assert!(matches!(
            load_bundle(&sidecar, "../test"),
            Err(RasterError::Invalid(_))
        ));
    }

    fn mutate_sidecar(path: &Path, mutate: impl FnOnce(&mut serde_json::Value)) {
        let mut value: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap();
        mutate(&mut value);
        fs::write(path, serde_json::to_vec(&value).unwrap()).unwrap();
    }

    #[test]
    fn loader_rejects_inconsistent_metadata_and_byte_lengths() {
        let root = tempdir().unwrap();
        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        mutate_sidecar(&sidecar, |value| {
            value["rasters"]["cost"]["dtype"] = json!("f64");
        });
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Dtype { .. })
        ));

        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        mutate_sidecar(&sidecar, |value| {
            value["rasters"]["cost"]["shape"] = json!([1, 2]);
        });
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Shape { .. })
        ));

        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        mutate_sidecar(&sidecar, |value| {
            value["rasters"]["cost"]["byteorder"] = json!("big");
        });
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::ByteOrder { .. })
        ));

        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        fs::write(root.path().join("declared.cost"), [0_u8]).unwrap();
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::ByteLen { .. })
        ));
    }

    #[test]
    fn loader_requires_paired_dem_layers_and_valid_anchor_identity() {
        let root = tempdir().unwrap();
        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        fs::write(root.path().join("elevation"), 10.0_f32.to_le_bytes()).unwrap();
        mutate_sidecar(&sidecar, |value| {
            value["rasters"]["elevation"] = json!({
                "path": "elevation", "dtype": "f32", "shape": [1, 1],
                "byteorder": "little"
            });
        });
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Json(_))
        ));

        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        fs::write(
            root.path().join("test.anchors.json"),
            serde_json::to_vec(&json!([
                {"id": 7, "kind": "demand", "weight": 1.0, "name": null,
                 "row": 0, "col": 0, "lat": 0.5, "lon": 0.5},
                {"id": 7, "kind": "demand", "weight": 1.0, "name": null,
                 "row": 0, "col": 0, "lat": 0.5, "lon": 0.5}
            ]))
            .unwrap(),
        )
        .unwrap();
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Invalid(_))
        ));

        let sidecar = write_bundle(root.path(), "declared.cost", 8.0, 25);
        mutate_sidecar(&sidecar, |value| {
            value["grid"]["cell_m"] = json!(0.0);
        });
        assert!(matches!(
            load_bundle(&sidecar, "test"),
            Err(RasterError::Invalid(_))
        ));
    }
}
