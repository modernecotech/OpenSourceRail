//! Ordered, source-bound current comparison rows. Historical JSON packets are read elsewhere.
use arrow_array::{Array, ArrayRef, BinaryArray, RecordBatch, StringArray, UInt64Array};
use arrow_schema::{DataType, Field, Schema};
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use parquet::arrow::ArrowWriter;
use parquet::basic::Compression;
use parquet::file::properties::WriterProperties;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::error::Error;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, BufWriter, Write};
use std::path::Path;
use std::sync::Arc;

type Result<T> = std::result::Result<T, Box<dyn Error>>;
const SCHEMA: &str = "osr-coupled-comparison-rows/2";
const MAX_ROW: usize = 64 * 1024 * 1024;
const MAX_ROWS: u64 = 4096;
const BATCH_ROWS: usize = 4;
const MAX_FILE: u64 = 1024 * 1024 * 1024;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}

fn hex(bytes: impl AsRef<[u8]>) -> String {
    bytes.as_ref().iter().map(|b| format!("{b:02x}")).collect()
}

fn schema() -> Arc<Schema> {
    Arc::new(Schema::new_with_metadata(
        vec![
            Field::new("ordinal", DataType::UInt64, false),
            Field::new("candidate_id", DataType::Utf8, false),
            Field::new("body_candidate_id", DataType::Utf8, false),
            Field::new("bundle_definition_id", DataType::Utf8, false),
            Field::new("row_id", DataType::Utf8, false),
            Field::new("row_sha256", DataType::Utf8, false),
            Field::new("canonical_row", DataType::Binary, false),
        ],
        HashMap::from([("osr_schema".into(), SCHEMA.into())]),
    ))
}

struct Row {
    ordinal: u64,
    candidate: String,
    body: String,
    bundle: String,
    row_id: String,
    sha: String,
    bytes: Vec<u8>,
}

fn identity(value: &Value, key: &str) -> Result<String> {
    let id = value
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| invalid(format!("missing {key}")))?;
    if id.is_empty() || id.len() > 128 || !id.is_ascii() {
        return Err(invalid(format!("invalid {key}")).into());
    }
    Ok(id.to_owned())
}

fn row(ordinal: u64, bytes: Vec<u8>) -> Result<Row> {
    if bytes.is_empty() || bytes.len() > MAX_ROW || bytes.contains(&b'\n') {
        return Err(invalid("canonical row exceeds budget or contains a newline").into());
    }
    let value: Value = serde_json::from_slice(&bytes)?;
    if !value.is_object() {
        return Err(invalid("comparison row must be an object").into());
    }
    Ok(Row {
        ordinal,
        candidate: identity(&value, "candidate_id")?,
        body: identity(&value, "body_candidate_id")?,
        bundle: identity(&value, "bundle_definition_id")?,
        row_id: identity(&value, "row_id")?,
        sha: hex(Sha256::digest(&bytes)),
        bytes,
    })
}

fn batch(rows: &[Row]) -> Result<RecordBatch> {
    let columns: Vec<ArrayRef> = vec![
        Arc::new(UInt64Array::from(
            rows.iter().map(|r| r.ordinal).collect::<Vec<_>>(),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|r| r.candidate.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|r| r.body.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|r| r.bundle.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|r| r.row_id.as_str()),
        )),
        Arc::new(StringArray::from_iter_values(
            rows.iter().map(|r| r.sha.as_str()),
        )),
        Arc::new(BinaryArray::from_iter_values(
            rows.iter().map(|r| r.bytes.as_slice()),
        )),
    ];
    Ok(RecordBatch::try_new(schema(), columns)?)
}

fn bounded_line(input: &mut impl BufRead) -> Result<Option<Vec<u8>>> {
    let mut bytes = Vec::new();
    loop {
        let available = input.fill_buf()?;
        if available.is_empty() {
            return if bytes.is_empty() {
                Ok(None)
            } else {
                Err(invalid("unterminated row").into())
            };
        }
        let n = available
            .iter()
            .position(|b| *b == b'\n')
            .map_or(available.len(), |p| p + 1);
        if bytes.len() + n > MAX_ROW + 1 {
            return Err(invalid("row exceeds 64 MiB").into());
        }
        bytes.extend_from_slice(&available[..n]);
        input.consume(n);
        if bytes.last() == Some(&b'\n') {
            bytes.pop();
            return Ok(Some(bytes));
        }
    }
}

pub fn write(path: &Path) -> Result<()> {
    if path.exists() {
        return Err(invalid("comparison target already exists").into());
    }
    let properties = WriterProperties::builder()
        .set_compression(Compression::ZSTD(Default::default()))
        .set_dictionary_enabled(false)
        .set_max_row_group_row_count(Some(BATCH_ROWS))
        .set_max_row_group_bytes(Some(256 * 1024 * 1024))
        .build();
    let mut writer = ArrowWriter::try_new(File::create(path)?, schema(), Some(properties))?;
    let mut input = BufReader::with_capacity(64 * 1024, io::stdin().lock());
    let mut rows = Vec::with_capacity(BATCH_ROWS);
    let mut hash = Sha256::new();
    hash.update(b"[");
    let mut count = 0_u64;
    while let Some(bytes) = bounded_line(&mut input)? {
        if count >= MAX_ROWS {
            return Err(invalid("comparison exceeds row budget").into());
        }
        let record = row(count, bytes)?;
        if count > 0 {
            hash.update(b",");
        }
        hash.update(&record.bytes);
        rows.push(record);
        count += 1;
        if rows.len() == BATCH_ROWS {
            writer.write(&batch(&rows)?)?;
            rows.clear();
        }
    }
    if count == 0 {
        return Err(invalid("empty comparison").into());
    }
    if !rows.is_empty() {
        writer.write(&batch(&rows)?)?;
    }
    writer.close()?;
    if fs::metadata(path)?.len() > MAX_FILE {
        return Err(invalid("comparison exceeds 1 GiB").into());
    }
    hash.update(b"]\n");
    println!(
        "{}",
        json!({"schema":SCHEMA,"row_count":count,"canonical_sha256":hex(hash.finalize())})
    );
    Ok(())
}

pub fn scan(path: &Path, expected_sha: &str, candidate: Option<&str>, array: bool) -> Result<()> {
    if expected_sha.len() != 64 || !expected_sha.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err(invalid("expected inventory SHA-256 required").into());
    }
    if fs::metadata(path)?.len() > MAX_FILE {
        return Err(invalid("comparison exceeds 1 GiB").into());
    }
    let builder = ParquetRecordBatchReaderBuilder::try_new(File::open(path)?)?;
    if builder.schema().as_ref() != schema().as_ref() {
        return Err(invalid("comparison Arrow schema differs").into());
    }
    let reader = builder.with_batch_size(BATCH_ROWS).build()?;
    let mut output = BufWriter::new(io::stdout().lock());
    let mut hash = Sha256::new();
    hash.update(b"[");
    let mut count = 0_u64;
    if array {
        output.write_all(b"[")?;
    }
    let mut matched = false;
    for record in reader {
        let record = record?;
        let ordinal = record
            .column(0)
            .as_any()
            .downcast_ref::<UInt64Array>()
            .ok_or_else(|| invalid("ordinal type"))?;
        let candidate_ids = record
            .column(1)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or_else(|| invalid("candidate type"))?;
        let bodies = record
            .column(2)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or_else(|| invalid("body type"))?;
        let bundles = record
            .column(3)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or_else(|| invalid("bundle type"))?;
        let row_ids = record
            .column(4)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or_else(|| invalid("row ID type"))?;
        let shas = record
            .column(5)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or_else(|| invalid("SHA type"))?;
        let bytes = record
            .column(6)
            .as_any()
            .downcast_ref::<BinaryArray>()
            .ok_or_else(|| invalid("row type"))?;
        for i in 0..record.num_rows() {
            if count >= MAX_ROWS || ordinal.is_null(i) || ordinal.value(i) != count {
                return Err(invalid("comparison order differs").into());
            }
            if (1..7).any(|col| record.column(col).is_null(i)) {
                return Err(invalid("null comparison column").into());
            }
            let value = row(count, bytes.value(i).to_vec())?;
            if value.candidate != candidate_ids.value(i)
                || value.body != bodies.value(i)
                || value.bundle != bundles.value(i)
                || value.row_id != row_ids.value(i)
                || value.sha != shas.value(i)
            {
                return Err(invalid("comparison row metadata or digest differs").into());
            }
            if count > 0 {
                hash.update(b",");
            }
            hash.update(&value.bytes);
            if candidate.is_none_or(|id| id == value.candidate) {
                if array {
                    if matched {
                        output.write_all(b",")?;
                    }
                    output.write_all(&value.bytes)?;
                } else {
                    output.write_all(&value.bytes)?;
                    output.write_all(b"\n")?;
                }
                matched = true;
            }
            count += 1;
        }
    }
    if count == 0 {
        return Err(invalid("empty comparison").into());
    }
    hash.update(b"]\n");
    if hex(hash.finalize()) != expected_sha {
        return Err(invalid("comparison inventory SHA-256 differs").into());
    }
    if candidate.is_some() && !matched {
        return Err(invalid("candidate absent from comparison").into());
    }
    if array {
        output.write_all(b"]\n")?;
    }
    output.flush()?;
    Ok(())
}
