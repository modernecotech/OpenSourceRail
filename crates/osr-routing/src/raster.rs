//! Raster + grid I/O. Consumes the artefacts produced by `osr_geo.save_grid`.
//!
//! File layout (written by Python):
//!
//!   {slug}.grid.json       — envelope + dtypes + shapes
//!   {slug}.cost.npy        — f32 little-endian, row-major, shape (H, W)
//!   {slug}.demand.npy      — f32 little-endian, row-major, shape (H, W)
//!   {slug}.buildability.npy — u8  little-endian, row-major, shape (H, W)
//!   {slug}.anchors.json    — list of {id, kind, weight, name, row, col, lat, lon}
//!
//! The `.npy` extension is a slight lie — they are raw byte streams, not
//! numpy's own .npy format. We avoid numpy's header because reading it
//! from Rust adds a dependency we do not need for two fixed dtypes.

use std::{
    fs,
    path::{Path, PathBuf},
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
struct RasterSidecar {
    #[allow(dead_code)]
    path: String,
    dtype: String,
    shape: Vec<usize>,
    byteorder: String,
}

#[derive(Debug, Deserialize)]
struct GridSidecar {
    grid: GridRef,
    rasters: Rasters,
}

#[derive(Debug, Deserialize)]
struct Rasters {
    cost: RasterSidecar,
    demand: RasterSidecar,
    buildability: RasterSidecar,
}

// ---- Errors ----------------------------------------------------------

#[derive(Debug, Error)]
pub enum RasterError {
    #[error("I/O: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON: {0}")]
    Json(#[from] serde_json::Error),
    #[error("dtype mismatch for {name}: expected {expected}, got {got}")]
    Dtype { name: &'static str, expected: &'static str, got: String },
    #[error("shape mismatch for {name}: expected {expected:?}, got {got:?}")]
    Shape { name: &'static str, expected: Vec<usize>, got: Vec<usize> },
    #[error("unsupported byteorder for {name}: {got}")]
    ByteOrder { name: &'static str, got: String },
    #[error("raster byte length mismatch for {name}: expected {expected}, got {got}")]
    ByteLen { name: &'static str, expected: usize, got: usize },
}

// ---- Public loader ---------------------------------------------------

/// Load a raster bundle from a sidecar path. Other files are resolved
/// relative to the sidecar directory (this matches `save_grid`).
pub fn load_bundle<P: AsRef<Path>>(sidecar: P, slug: &str) -> Result<RasterBundle, RasterError> {
    let sidecar = sidecar.as_ref();
    let dir = sidecar.parent().unwrap_or_else(|| Path::new("."));

    let side: GridSidecar = serde_json::from_str(&fs::read_to_string(sidecar)?)?;
    let reference = side.grid.clone();

    let expected_shape = vec![reference.height, reference.width];
    let cost = load_f32(&dir.join(format!("{slug}.cost.npy")), "cost", &side.rasters.cost, &expected_shape)?;
    let demand = load_f32(&dir.join(format!("{slug}.demand.npy")), "demand", &side.rasters.demand, &expected_shape)?;
    let buildability = load_u8(
        &dir.join(format!("{slug}.buildability.npy")),
        "buildability",
        &side.rasters.buildability,
        &expected_shape,
    )?;

    let grid = Grid {
        reference,
        cost,
        demand,
        buildability,
    };

    let anchors_path: PathBuf = dir.join(format!("{slug}.anchors.json"));
    let anchors: Vec<Anchor> = serde_json::from_str(&fs::read_to_string(&anchors_path)?)?;

    Ok(RasterBundle {
        grid,
        anchors,
        slug: slug.to_string(),
    })
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

fn load_f32(path: &Path, name: &'static str, side: &RasterSidecar, expected_shape: &[usize]) -> Result<Vec<f32>, RasterError> {
    check_sidecar(name, &side.dtype, "f32", &side.shape, expected_shape, &side.byteorder)?;
    let bytes = fs::read(path)?;
    let ncells: usize = expected_shape.iter().product();
    let expected_bytes = ncells * 4;
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

fn load_u8(path: &Path, name: &'static str, side: &RasterSidecar, expected_shape: &[usize]) -> Result<Vec<u8>, RasterError> {
    check_sidecar(name, &side.dtype, "u8", &side.shape, expected_shape, &side.byteorder)?;
    let bytes = fs::read(path)?;
    let ncells: usize = expected_shape.iter().product();
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
}
