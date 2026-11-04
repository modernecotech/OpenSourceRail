//! Optional direct Python-object adapter. Exact builtins only; no eval or dumps.
//!
//! Float repr and arbitrary-precision integer text remain Python built-ins.
//! Recursive traversal, key ordering, ASCII escaping and SHA256 are Rust.
use crate::canonical::{Emitter, SealPlacement, DEFAULT_DEPTH, MAX_BYTES, MAX_DEPTH};
use pyo3::exceptions::{PyRecursionError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple};
use std::cmp::Ordering;
use std::collections::HashSet;

fn value_error(message: &'static str) -> PyErr {
    PyValueError::new_err(message)
}

fn points(text: &Bound<'_, PyString>) -> PyResult<Vec<u32>> {
    if let Ok(text) = text.to_str() {
        return Ok(text.chars().map(u32::from).collect());
    }
    // to_string_lossy would silently change lone surrogates and is forbidden.
    let encoded = text.call_method1("encode", ("utf-32-le", "surrogatepass"))?;
    let bytes = encoded.cast_exact::<PyBytes>()?.as_bytes();
    Ok(bytes
        .chunks_exact(4)
        .map(|b| u32::from_le_bytes([b[0], b[1], b[2], b[3]]))
        .collect())
}

/// Valid UTF8 has the same lexicographic order as Unicode scalar values.
/// Keep one byte copy instead of allocating four-byte codepoints for ordinary
/// keys; explicit surrogate codepoints retain Python's wider string domain.
enum KeyOrder {
    Utf8(String),
    Surrogates(Vec<u32>),
}

impl KeyOrder {
    fn new(text: &Bound<'_, PyString>) -> PyResult<Self> {
        match text.to_str() {
            Ok(text) => Ok(Self::Utf8(text.to_owned())),
            Err(_) => Ok(Self::Surrogates(points(text)?)),
        }
    }

    fn cmp(&self, other: &Self) -> Ordering {
        match (self, other) {
            (Self::Utf8(left), Self::Utf8(right)) => left.cmp(right),
            (Self::Surrogates(left), Self::Surrogates(right)) => left.cmp(right),
            (Self::Utf8(left), Self::Surrogates(right)) => {
                left.chars().map(u32::from).cmp(right.iter().copied())
            }
            (Self::Surrogates(left), Self::Utf8(right)) => {
                left.iter().copied().cmp(right.chars().map(u32::from))
            }
        }
    }

    fn cmp_points(&self, other: &[u32]) -> Ordering {
        match self {
            Self::Utf8(left) => left.chars().map(u32::from).cmp(other.iter().copied()),
            Self::Surrogates(left) => left.as_slice().cmp(other),
        }
    }
}

struct Walker {
    output: Emitter,
    active: HashSet<usize>,
    depth: usize,
    root_seal: Option<RootSeal>,
}

struct RootSeal {
    key_points: Vec<u32>,
    insertion: Option<(usize, SealPlacement)>,
}

impl Walker {
    fn string(&mut self, string: &Bound<'_, PyString>) -> PyResult<()> {
        match string.to_str() {
            Ok(text) => self.output.string(text).map_err(value_error),
            Err(_) => self
                .output
                .codepoints(&points(string)?)
                .map_err(value_error),
        }
    }

    fn value(&mut self, value: &Bound<'_, PyAny>, depth: usize) -> PyResult<()> {
        if depth > self.depth {
            return Err(PyRecursionError::new_err(
                "Canonical maximum depth exceeded",
            ));
        }
        if value.is_none() {
            return self.output.write(b"null").map_err(value_error);
        }
        if value.is_exact_instance_of::<PyBool>() {
            return self
                .output
                .write(if value.is_truthy()? {
                    b"true"
                } else {
                    b"false"
                })
                .map_err(value_error);
        }
        if value.is_exact_instance_of::<PyString>() {
            return self.string(value.cast_exact::<PyString>()?);
        }
        if value.is_exact_instance_of::<PyInt>() {
            let text = value.str()?;
            return self
                .output
                .write(text.to_str()?.as_bytes())
                .map_err(value_error);
        }
        if value.is_exact_instance_of::<PyFloat>() {
            if !value.extract::<f64>()?.is_finite() {
                return Err(value_error(
                    "Out of range float values are not JSON compliant",
                ));
            }
            let text = value.repr()?;
            return self
                .output
                .write(text.to_str()?.as_bytes())
                .map_err(value_error);
        }
        let is_dict = value.is_exact_instance_of::<PyDict>();
        let is_list = value.is_exact_instance_of::<PyList>();
        let is_tuple = value.is_exact_instance_of::<PyTuple>();
        if !(is_dict || is_list || is_tuple) {
            return Err(PyTypeError::new_err(
                "Canonical input requires exact built-in JSON types and string-key dictionaries",
            ));
        }
        let address = value.as_ptr() as usize;
        if !self.active.insert(address) {
            return Err(value_error("Circular reference detected"));
        }
        let result = if is_dict {
            self.dictionary(value.cast_exact::<PyDict>()?, depth)
        } else if is_list {
            let list = value.cast_exact::<PyList>()?;
            self.output.write(b"[").map_err(value_error)?;
            let mut result = Ok(());
            for (index, item) in list.iter().enumerate() {
                result = (|| {
                    if index > 0 {
                        self.output.write(b",").map_err(value_error)?;
                    }
                    self.value(&item, depth + 1)
                })();
                if result.is_err() {
                    break;
                }
            }
            result.and_then(|()| self.output.write(b"]").map_err(value_error))
        } else {
            let tuple = value.cast_exact::<PyTuple>()?;
            self.output.write(b"[").map_err(value_error)?;
            let mut result = Ok(());
            for (index, item) in tuple.iter().enumerate() {
                result = (|| {
                    if index > 0 {
                        self.output.write(b",").map_err(value_error)?;
                    }
                    self.value(&item, depth + 1)
                })();
                if result.is_err() {
                    break;
                }
            }
            result.and_then(|()| self.output.write(b"]").map_err(value_error))
        };
        self.active.remove(&address);
        result
    }

    fn dictionary(&mut self, dict: &Bound<'_, PyDict>, depth: usize) -> PyResult<()> {
        // Necessary lower bound before allocating a sortable key array. Every
        // nonempty entry needs at least a quoted key, colon and one value byte.
        if dict.len() > self.output.remaining() / 4 {
            return Err(value_error("Canonical byte budget exceeded"));
        }
        let mut entries = Vec::with_capacity(dict.len());
        for (key, value) in dict.iter() {
            let key = key.cast_exact::<PyString>().map_err(|_| {
                PyTypeError::new_err("Canonical dictionary keys must be exact built-in strings")
            })?;
            entries.push((KeyOrder::new(key)?, key.clone(), value));
        }
        // Python str order compares codepoints, including lone surrogates.
        entries.sort_unstable_by(|a, b| a.0.cmp(&b.0));
        let insertion_index = if depth == 0 {
            if let Some(seal) = &self.root_seal {
                match entries.binary_search_by(|entry| entry.0.cmp_points(&seal.key_points)) {
                    Ok(_) => {
                        return Err(value_error("Seal key must be absent from the root record"))
                    }
                    Err(index) => Some(index),
                }
            } else {
                None
            }
        } else {
            None
        };
        self.output.write(b"{").map_err(value_error)?;
        for (index, (_, key, value)) in entries.iter().enumerate() {
            if index > 0 {
                self.output.write(b",").map_err(value_error)?;
            }
            if insertion_index == Some(index) {
                self.root_seal
                    .as_mut()
                    .expect("root seal target exists")
                    .insertion = Some((self.output.byte_count(), SealPlacement::BeforeEntry));
            }
            self.string(key)?;
            self.output.write(b":").map_err(value_error)?;
            self.value(value, depth + 1)?;
        }
        if insertion_index == Some(entries.len()) {
            let placement = if entries.is_empty() {
                SealPlacement::OnlyEntry
            } else {
                SealPlacement::AfterLast
            };
            self.root_seal
                .as_mut()
                .expect("root seal target exists")
                .insertion = Some((self.output.byte_count(), placement));
        }
        self.output.write(b"}").map_err(value_error)
    }
}

fn evaluate(
    value: &Bound<'_, PyAny>,
    max_bytes: usize,
    max_depth: usize,
    retain: bool,
) -> PyResult<(Option<Vec<u8>>, String)> {
    if max_depth > MAX_DEPTH {
        return Err(value_error(
            "Canonical depth limit must be between 0 and 256",
        ));
    }
    let mut walker = Walker {
        output: Emitter::new(max_bytes, retain).map_err(value_error)?,
        active: HashSet::new(),
        depth: max_depth,
        root_seal: None,
    };
    walker.value(value, 0)?;
    walker.output.finish().map_err(value_error)
}

#[pyfunction(signature=(value, *, max_bytes=MAX_BYTES, max_depth=DEFAULT_DEPTH))]
fn encoded<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
    max_bytes: usize,
    max_depth: usize,
) -> PyResult<Bound<'py, PyBytes>> {
    let (bytes, _) = evaluate(value, max_bytes, max_depth, true)?;
    Ok(PyBytes::new(
        py,
        &bytes.expect("retaining emitter supplies bytes"),
    ))
}

#[pyfunction(signature=(value, *, max_bytes=MAX_BYTES, max_depth=DEFAULT_DEPTH))]
fn identity(value: &Bound<'_, PyAny>, max_bytes: usize, max_depth: usize) -> PyResult<String> {
    Ok(evaluate(value, max_bytes, max_depth, false)?.1)
}

#[pyfunction(signature=(value, *, max_bytes=MAX_BYTES, max_depth=DEFAULT_DEPTH))]
fn encoded_with_identity<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
    max_bytes: usize,
    max_depth: usize,
) -> PyResult<(Bound<'py, PyBytes>, String)> {
    let (bytes, hash) = evaluate(value, max_bytes, max_depth, true)?;
    Ok((
        PyBytes::new(py, &bytes.expect("retaining emitter supplies bytes")),
        hash,
    ))
}

fn default_seal_key() -> Py<PyAny> {
    Python::attach(|py| PyString::new(py, "evaluation_id").into_any().unbind())
}

#[pyfunction(
    signature=(value, key=default_seal_key(), *, max_bytes=MAX_BYTES, max_depth=DEFAULT_DEPTH),
    text_signature="(value, key='evaluation_id', *, max_bytes=67108864, max_depth=128)"
)]
fn sealed_record<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
    key: Py<PyAny>,
    max_bytes: usize,
    max_depth: usize,
) -> PyResult<(Bound<'py, PyBytes>, String)> {
    value
        .cast_exact::<PyDict>()
        .map_err(|_| PyTypeError::new_err("Sealing requires an exact built-in dictionary"))?;
    let key = key
        .bind(py)
        .cast_exact::<PyString>()
        .map_err(|_| PyTypeError::new_err("Seal key must be an exact built-in string"))?;
    let key_points = points(key)?;
    if key_points.is_empty() {
        return Err(value_error("A nonempty absent seal key is required"));
    }
    if max_depth > MAX_DEPTH {
        return Err(value_error(
            "Canonical depth limit must be between 0 and 256",
        ));
    }
    if max_depth == 0 {
        return Err(PyRecursionError::new_err(
            "The inserted seal value requires canonical depth of at least one",
        ));
    }
    let mut escaped_key = Emitter::new(max_bytes, true).map_err(value_error)?;
    escaped_key.codepoints(&key_points).map_err(value_error)?;
    let (escaped_key, _) = escaped_key.finish().map_err(value_error)?;
    let mut escaped_key = escaped_key.expect("retaining emitter supplies bytes");
    escaped_key.pop(); // Only the key's standalone encoding newline is removed.
    let mut walker = Walker {
        output: Emitter::new(max_bytes, true).map_err(value_error)?,
        active: HashSet::new(),
        depth: max_depth,
        root_seal: Some(RootSeal {
            key_points,
            insertion: None,
        }),
    };
    walker.value(value, 0)?;
    let (offset, placement) = walker
        .root_seal
        .expect("root seal target exists")
        .insertion
        .ok_or_else(|| value_error("Canonical root insertion offset was not recorded"))?;
    let (bytes, seal) = walker
        .output
        .finish_sealed(offset, &escaped_key, placement)
        .map_err(value_error)?;
    Ok((PyBytes::new(py, &bytes), seal))
}

#[pyfunction]
fn backend_info(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let result = PyDict::new(py);
    result.set_item("schema", "osr-native-canonical-backend/1")?;
    result.set_item("backend", "rust-pyo3-hybrid-canonical/1")?;
    result.set_item("pyo3_version", "0.27.2")?;
    result.set_item("float_format", "python-builtins-repr")?;
    result.set_item("integer_format", "python-builtins-str")?;
    result.set_item("escaping", "rust-json-ensure-ascii-no-normalization")?;
    result.set_item("hash", "sha256")?;
    result.set_item("max_bytes", MAX_BYTES)?;
    result.set_item("max_depth", MAX_DEPTH)?;
    result.set_item("default_depth", DEFAULT_DEPTH)?;
    result.set_item(
        "sealed_record_method",
        "one-nested-traversal-root-byte-insertion",
    )?;
    result.set_item(
        "accepted_types",
        "exact-str-int-finite-float-bool-None-list-tuple-string-key-dict",
    )?;
    Ok(result)
}

#[pymodule]
fn osr_design_native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(encoded, module)?)?;
    module.add_function(wrap_pyfunction!(identity, module)?)?;
    module.add_function(wrap_pyfunction!(encoded_with_identity, module)?)?;
    module.add_function(wrap_pyfunction!(sealed_record, module)?)?;
    module.add_function(wrap_pyfunction!(backend_info, module)?)?;
    Ok(())
}
