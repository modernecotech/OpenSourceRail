//! Bounded Arrow/Parquet index of immutable coupled-campaign case records.
//!
//! The index is derived data. Its pointers and hashes refer to the existing
//! source-bound case files; it does not replace their canonical evidence bytes.

use arrow_array::{
    Array, ArrayRef, BooleanArray, Float64Array, RecordBatch, StringArray, UInt64Array,
};
use arrow_schema::{DataType, Field, Schema};
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use parquet::arrow::arrow_writer::ArrowWriter;
use parquet::basic::Compression;
use parquet::file::properties::WriterProperties;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::error::Error;
use std::fs::{self, File};
use std::io::{self, BufReader, Read};
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

pub const SCHEMA_VERSION: &str = "osr-campaign-case-index/1";
pub const MAX_CASE_BYTES: u64 = 64 * 1024 * 1024;
pub const MAX_PART_BYTES: u64 = 16 * 1024 * 1024;
pub const MAX_PART_ROWS: usize = 512;
pub const MAX_BATCH_ROWS: usize = 128;

type AnyResult<T> = Result<T, Box<dyn Error>>;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}

#[derive(Debug, Deserialize)]
struct MassProjection {
    accounted_tare_kg_per_car: Option<f64>,
}

#[derive(Debug, Deserialize)]
struct CaseProjection {
    candidate_id: String,
    row_id: String,
    body_candidate_id: String,
    bundle_definition_id: String,
    case_context_id: String,
    family_id: String,
    accounted_mass: Option<MassProjection>,
    installed_mass_kg: Option<f64>,
    physical_journey_completed: bool,
    complete_body_qualified: bool,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct IndexRow {
    pub ordinal: u64,
    pub candidate_id: String,
    pub row_id: String,
    pub body_candidate_id: String,
    pub bundle_definition_id: String,
    pub case_context_id: String,
    pub family_id: String,
    pub case_path: String,
    pub case_sha256: String,
    pub accounted_tare_kg_per_car: Option<f64>,
    pub installed_mass_kg: Option<f64>,
    pub physical_journey_completed: bool,
    pub complete_body_qualified: bool,
}

#[derive(Debug, Clone, Copy)]
pub struct IndexOptions {
    pub batch_rows: usize,
    pub part_rows: usize,
}

impl Default for IndexOptions {
    fn default() -> Self {
        Self {
            batch_rows: MAX_BATCH_ROWS,
            part_rows: MAX_PART_ROWS,
        }
    }
}

impl IndexOptions {
    fn check(self) -> AnyResult<()> {
        if self.batch_rows == 0
            || self.batch_rows > MAX_BATCH_ROWS
            || self.part_rows == 0
            || self.part_rows > MAX_PART_ROWS
            || self.batch_rows > self.part_rows
        {
            return Err(invalid("batch/part rows exceed the bounded index limits").into());
        }
        Ok(())
    }
}

fn schema() -> Arc<Schema> {
    let fields = vec![
        Field::new("ordinal", DataType::UInt64, false),
        Field::new("candidate_id", DataType::Utf8, false),
        Field::new("row_id", DataType::Utf8, false),
        Field::new("body_candidate_id", DataType::Utf8, false),
        Field::new("bundle_definition_id", DataType::Utf8, false),
        Field::new("case_context_id", DataType::Utf8, false),
        Field::new("family_id", DataType::Utf8, false),
        Field::new("case_path", DataType::Utf8, false),
        Field::new("case_sha256", DataType::Utf8, false),
        Field::new("accounted_tare_kg_per_car", DataType::Float64, true),
        Field::new("installed_mass_kg", DataType::Float64, true),
        Field::new("physical_journey_completed", DataType::Boolean, false),
        Field::new("complete_body_qualified", DataType::Boolean, false),
    ];
    Arc::new(Schema::new_with_metadata(
        fields,
        HashMap::from([("osr_schema".to_owned(), SCHEMA_VERSION.to_owned())]),
    ))
}

struct HashingReader<R> {
    inner: R,
    hasher: Sha256,
}

impl<R: Read> Read for HashingReader<R> {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        let size = self.inner.read(buf)?;
        self.hasher.update(&buf[..size]);
        Ok(size)
    }
}

fn hex_digest(hash: impl AsRef<[u8]>) -> String {
    hash.as_ref()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn read_case(path: &Path, ordinal: u64) -> AnyResult<IndexRow> {
    let size = fs::metadata(path)?.len();
    if size > MAX_CASE_BYTES {
        return Err(invalid(format!(
            "case exceeds 64 MiB reader budget: {}",
            path.display()
        ))
        .into());
    }
    let reader = HashingReader {
        inner: File::open(path)?,
        hasher: Sha256::new(),
    };
    let mut reader = BufReader::with_capacity(64 * 1024, reader);
    let value: CaseProjection = serde_json::from_reader(&mut reader)?;
    let sha256 = hex_digest(reader.into_inner().hasher.finalize());
    let ids = [
        &value.candidate_id,
        &value.row_id,
        &value.body_candidate_id,
        &value.bundle_definition_id,
        &value.case_context_id,
        &value.family_id,
    ];
    if ids
        .iter()
        .any(|id| id.is_empty() || id.len() > 128 || !id.is_ascii())
    {
        return Err(invalid("case identity fields must be bounded ASCII strings").into());
    }
    let mass = value
        .accounted_mass
        .and_then(|account| account.accounted_tare_kg_per_car);
    for number in [mass, value.installed_mass_kg].into_iter().flatten() {
        if !number.is_finite() || number < 0.0 {
            return Err(invalid("case mass must be finite and nonnegative when known").into());
        }
    }
    let case_name = path
        .file_name()
        .ok_or_else(|| invalid("case path has no filename"))?;
    let name = case_name
        .to_str()
        .ok_or_else(|| invalid("case path is not UTF-8"))?;
    if !name.ends_with(".json") || name.contains('/') || name.contains('\\') {
        return Err(invalid("case path is not an ordinary JSON filename").into());
    }
    if name.strip_suffix(".json") != Some(value.case_context_id.as_str()) {
        return Err(invalid("case filename and context identity differ").into());
    }
    Ok(IndexRow {
        ordinal,
        candidate_id: value.candidate_id,
        row_id: value.row_id,
        body_candidate_id: value.body_candidate_id,
        bundle_definition_id: value.bundle_definition_id,
        case_context_id: value.case_context_id,
        family_id: value.family_id,
        case_path: format!("cases/{name}"),
        case_sha256: sha256,
        accounted_tare_kg_per_car: mass,
        installed_mass_kg: value.installed_mass_kg,
        physical_journey_completed: value.physical_journey_completed,
        complete_body_qualified: value.complete_body_qualified,
    })
}

fn batch(rows: &[IndexRow]) -> AnyResult<RecordBatch> {
    let columns: Vec<ArrayRef> = vec![
        Arc::new(UInt64Array::from(
            rows.iter().map(|row| row.ordinal).collect::<Vec<_>>(),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.candidate_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.row_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.body_candidate_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.bundle_definition_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.case_context_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.family_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.case_path.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|row| row.case_sha256.as_str()),
        )),
        Arc::new(Float64Array::from(
            rows.iter()
                .map(|row| row.accounted_tare_kg_per_car)
                .collect::<Vec<_>>(),
        )),
        Arc::new(Float64Array::from(
            rows.iter()
                .map(|row| row.installed_mass_kg)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|row| row.physical_journey_completed)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|row| row.complete_body_qualified)
                .collect::<Vec<_>>(),
        )),
    ];
    Ok(RecordBatch::try_new(schema(), columns)?)
}

fn part_writer(path: &Path, options: IndexOptions) -> AnyResult<ArrowWriter<File>> {
    let properties = WriterProperties::builder()
        .set_compression(Compression::ZSTD(Default::default()))
        .set_dictionary_enabled(false)
        .set_max_row_group_row_count(Some(options.batch_rows))
        .set_max_row_group_bytes(Some(1024 * 1024))
        .build();
    Ok(ArrowWriter::try_new(
        File::create(path)?,
        schema(),
        Some(properties),
    )?)
}

/// Build a deterministic, size-bounded index from sorted immutable case files.
/// The target must not exist; a temporary sibling is renamed only on success.
pub fn index_cases(state_dir: &Path, target_dir: &Path, options: IndexOptions) -> AnyResult<usize> {
    options.check()?;
    if target_dir.exists() {
        return Err(invalid("index target already exists").into());
    }
    let mut paths = fs::read_dir(state_dir.join("cases"))?
        .map(|entry| entry.map(|value| value.path()))
        .collect::<Result<Vec<_>, _>>()?;
    paths.sort();
    if paths.is_empty() {
        return Err(invalid("no case files to index").into());
    }
    if paths.iter().any(|path| {
        path.is_symlink()
            || !path.is_file()
            || path.extension().and_then(|value| value.to_str()) != Some("json")
    }) {
        return Err(invalid("cases directory contains a non-ordinary JSON file").into());
    }
    let parent = target_dir
        .parent()
        .ok_or_else(|| invalid("index target needs a parent"))?;
    fs::create_dir_all(parent)?;
    let name = target_dir
        .file_name()
        .ok_or_else(|| invalid("index target needs a name"))?
        .to_string_lossy();
    let nonce = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let stage = parent.join(format!(".{name}.building-{}-{nonce}", std::process::id()));
    fs::create_dir(&stage)?;
    let mut count = 0usize;
    let mut part = 0usize;
    let mut part_rows = 0usize;
    let mut buffered = Vec::with_capacity(options.batch_rows);
    let mut writer: Option<ArrowWriter<File>> = None;
    for path in paths {
        if part_rows == options.part_rows {
            if !buffered.is_empty() {
                writer
                    .as_mut()
                    .ok_or_else(|| invalid("missing part writer"))?
                    .write(&batch(&buffered)?)?;
                buffered.clear();
            }
            writer
                .take()
                .ok_or_else(|| invalid("missing part writer"))?
                .close()?;
            let part_path = stage.join(format!("part-{part:06}.parquet"));
            if fs::metadata(&part_path)?.len() > MAX_PART_BYTES {
                return Err(invalid("Parquet part exceeded 16 MiB budget").into());
            }
            part += 1;
            part_rows = 0;
        }
        if writer.is_none() {
            writer = Some(part_writer(
                &stage.join(format!("part-{part:06}.parquet")),
                options,
            )?);
        }
        buffered.push(read_case(&path, count as u64)?);
        count += 1;
        part_rows += 1;
        if buffered.len() == options.batch_rows {
            writer
                .as_mut()
                .ok_or_else(|| invalid("missing part writer"))?
                .write(&batch(&buffered)?)?;
            buffered.clear();
        }
    }
    if !buffered.is_empty() {
        writer
            .as_mut()
            .ok_or_else(|| invalid("missing part writer"))?
            .write(&batch(&buffered)?)?;
    }
    writer
        .take()
        .ok_or_else(|| invalid("missing part writer"))?
        .close()?;
    if fs::metadata(stage.join(format!("part-{part:06}.parquet")))?.len() > MAX_PART_BYTES {
        return Err(invalid("Parquet part exceeded 16 MiB budget").into());
    }
    fs::rename(stage, target_dir)?;
    Ok(count)
}

fn parts(dir: &Path) -> AnyResult<Vec<PathBuf>> {
    let mut paths = fs::read_dir(dir)?
        .map(|entry| entry.map(|value| value.path()))
        .collect::<Result<Vec<_>, _>>()?;
    paths.sort();
    if paths.is_empty() {
        return Err(invalid("index contains no Parquet parts").into());
    }
    for (number, path) in paths.iter().enumerate() {
        if path.is_symlink()
            || !path.is_file()
            || path.file_name().and_then(|value| value.to_str())
                != Some(format!("part-{number:06}.parquet").as_str())
            || fs::metadata(path)?.len() > MAX_PART_BYTES
        {
            return Err(invalid("index part name, type or size is invalid").into());
        }
    }
    Ok(paths)
}

fn typed_column<T: Array + 'static>(batch: &RecordBatch, column: usize) -> AnyResult<&T> {
    batch
        .column(column)
        .as_any()
        .downcast_ref()
        .ok_or_else(|| invalid("index column type differs").into())
}

struct IndexColumns<'a> {
    ordinals: &'a UInt64Array,
    candidate_ids: &'a StringArray,
    row_ids: &'a StringArray,
    body_ids: &'a StringArray,
    bundle_ids: &'a StringArray,
    context_ids: &'a StringArray,
    family_ids: &'a StringArray,
    case_paths: &'a StringArray,
    case_hashes: &'a StringArray,
    tare_masses: &'a Float64Array,
    installed_masses: &'a Float64Array,
    journey_completed: &'a BooleanArray,
    body_qualified: &'a BooleanArray,
}

impl<'a> IndexColumns<'a> {
    fn new(batch: &'a RecordBatch) -> AnyResult<Self> {
        if batch
            .schema_ref()
            .fields()
            .iter()
            .zip(batch.columns())
            .any(|(field, array)| !field.is_nullable() && array.null_count() > 0)
        {
            return Err(invalid("null required index column").into());
        }
        Ok(Self {
            ordinals: typed_column(batch, 0)?,
            candidate_ids: typed_column(batch, 1)?,
            row_ids: typed_column(batch, 2)?,
            body_ids: typed_column(batch, 3)?,
            bundle_ids: typed_column(batch, 4)?,
            context_ids: typed_column(batch, 5)?,
            family_ids: typed_column(batch, 6)?,
            case_paths: typed_column(batch, 7)?,
            case_hashes: typed_column(batch, 8)?,
            tare_masses: typed_column(batch, 9)?,
            installed_masses: typed_column(batch, 10)?,
            journey_completed: typed_column(batch, 11)?,
            body_qualified: typed_column(batch, 12)?,
        })
    }

    fn row(&self, index: usize) -> IndexRow {
        let optional_mass =
            |masses: &Float64Array| (!masses.is_null(index)).then(|| masses.value(index));
        IndexRow {
            ordinal: self.ordinals.value(index),
            candidate_id: self.candidate_ids.value(index).to_owned(),
            row_id: self.row_ids.value(index).to_owned(),
            body_candidate_id: self.body_ids.value(index).to_owned(),
            bundle_definition_id: self.bundle_ids.value(index).to_owned(),
            case_context_id: self.context_ids.value(index).to_owned(),
            family_id: self.family_ids.value(index).to_owned(),
            case_path: self.case_paths.value(index).to_owned(),
            case_sha256: self.case_hashes.value(index).to_owned(),
            accounted_tare_kg_per_car: optional_mass(self.tare_masses),
            installed_mass_kg: optional_mass(self.installed_masses),
            physical_journey_completed: self.journey_completed.value(index),
            complete_body_qualified: self.body_qualified.value(index),
        }
    }
}

fn scan_rows(
    dir: &Path,
    candidate_id: Option<&str>,
    mut visit: impl FnMut(IndexRow) -> AnyResult<()>,
) -> AnyResult<usize> {
    let mut expected = 0u64;
    let expected_schema = schema();
    for path in parts(dir)? {
        let builder = ParquetRecordBatchReaderBuilder::try_new(File::open(path)?)?;
        if builder.schema().as_ref() != expected_schema.as_ref() {
            return Err(invalid("index Arrow schema/version differs").into());
        }
        let reader = builder.with_batch_size(MAX_BATCH_ROWS).build()?;
        for result in reader {
            let batch = result?;
            let columns = IndexColumns::new(&batch)?;
            for row in 0..batch.num_rows() {
                if columns.ordinals.value(row) != expected {
                    return Err(invalid("index ordinal sequence differs").into());
                }
                if candidate_id.is_none_or(|id| id == columns.candidate_ids.value(row)) {
                    visit(columns.row(row))?;
                }
                expected += 1;
            }
        }
    }
    Ok(expected as usize)
}

/// Stream typed rows from bounded Parquet parts, checking schema and ordinal order.
pub fn scan_index(dir: &Path, visit: impl FnMut(IndexRow) -> AnyResult<()>) -> AnyResult<usize> {
    scan_rows(dir, None, visit)
}

fn verify_row(row: &IndexRow, state_dir: &Path) -> AnyResult<()> {
    let name = row
        .case_path
        .strip_prefix("cases/")
        .ok_or_else(|| invalid("case pointer escapes state"))?;
    if name.contains('/')
        || name.contains('\\')
        || name.starts_with('.')
        || !name.ends_with(".json")
    {
        return Err(invalid("case pointer escapes state").into());
    }
    let path = state_dir.join("cases").join(name);
    if path.is_symlink() {
        return Err(invalid("case pointer is a symlink").into());
    }
    let actual = read_case(&path, row.ordinal)?;
    if actual != *row {
        return Err(invalid(format!(
            "case/index projection or hash differs: {}",
            row.case_path
        ))
        .into());
    }
    Ok(())
}

/// Verify each index pointer against its immutable case bytes and projection.
pub fn verify_index(dir: &Path, state_dir: &Path) -> AnyResult<usize> {
    scan_index(dir, |row| verify_row(&row, state_dir))
}

/// Return a candidate's typed index rows after authenticating matching cases.
/// Unmatched case payloads are not opened; the bounded Arrow batches are scanned.
pub fn query_candidate(
    dir: &Path,
    state_dir: &Path,
    candidate_id: &str,
) -> AnyResult<Vec<IndexRow>> {
    let mut rows = Vec::new();
    scan_rows(dir, Some(candidate_id), |row| {
        if rows.len() >= 1024 {
            return Err(invalid("candidate query exceeded bounded result count").into());
        }
        verify_row(&row, state_dir)?;
        rows.push(row);
        Ok(())
    })?;
    Ok(rows)
}
