//! Typed, additive v2 migration preview. No historical case is removed.
//!
//! This first slice covers the stable row core and seven stage references.
//! `unsupported_top_level` names payload domains that still require typed
//! Arrow schemas before this can replace canonical case evidence.

use arrow_array::{
    Array, ArrayRef, BooleanArray, Float64Array, RecordBatch, StringArray, UInt8Array,
};
use arrow_schema::{DataType, Field, Schema};
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use parquet::arrow::arrow_writer::ArrowWriter;
use parquet::basic::Compression;
use parquet::file::properties::WriterProperties;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::error::Error;
use std::fs::{self, File};
use std::io::{self, BufReader, Read, Write};
use std::path::Path;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

const STAGES: [&str; 7] = [
    "installed_inventory",
    "interfaces",
    "architecture",
    "propulsion",
    "motion_and_braking",
    "civil",
    "manufacturing_and_economics",
];
const MAX_CASES: usize = 128;
const MAX_CASE_BYTES: u64 = 64 * 1024 * 1024;
const MAX_PART_BYTES: u64 = 16 * 1024 * 1024;
type Result<T> = std::result::Result<T, Box<dyn Error>>;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}

#[derive(Deserialize)]
struct Mass {
    accounted_tare_kg_per_car: Option<f64>,
}

#[derive(Deserialize)]
struct StageRef {
    stage: String,
    record_id: String,
    reused: bool,
}

#[derive(Deserialize)]
struct Case {
    candidate_id: String,
    row_id: String,
    body_candidate_id: String,
    bundle_definition_id: String,
    case_context_id: String,
    family_id: String,
    motor_component_id: String,
    accounted_mass: Option<Mass>,
    installed_mass_kg: Option<f64>,
    physical_journey_completed: bool,
    complete_body_qualified: bool,
    physical_accepted: bool,
    engineering_accepted: bool,
    configuration_adopted: bool,
    manufacturing_release: bool,
    operating_release: bool,
    stages: Vec<StageRef>,
    #[serde(flatten)]
    unsupported: std::collections::BTreeMap<String, serde::de::IgnoredAny>,
}

struct HashReader<R> {
    inner: R,
    hash: Sha256,
}

impl<R: Read> Read for HashReader<R> {
    fn read(&mut self, bytes: &mut [u8]) -> io::Result<usize> {
        let size = self.inner.read(bytes)?;
        self.hash.update(&bytes[..size]);
        Ok(size)
    }
}

fn hex(bytes: impl AsRef<[u8]>) -> String {
    bytes
        .as_ref()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn hash_id(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
}

fn read_case(path: &Path) -> Result<(Case, String)> {
    if path.is_symlink() || !path.is_file() || fs::metadata(path)?.len() > MAX_CASE_BYTES {
        return Err(invalid("case must be an ordinary file below 64 MiB").into());
    }
    let input = HashReader {
        inner: File::open(path)?,
        hash: Sha256::new(),
    };
    let mut input = BufReader::with_capacity(64 * 1024, input);
    let value: Case = serde_json::from_reader(&mut input)?;
    let digest = hex(input.into_inner().hash.finalize());
    for id in [
        &value.candidate_id,
        &value.row_id,
        &value.body_candidate_id,
        &value.bundle_definition_id,
        &value.case_context_id,
        &value.motor_component_id,
    ] {
        if !hash_id(id) {
            return Err(invalid("case has an invalid exact identity").into());
        }
    }
    if value.family_id.is_empty() || value.family_id.len() > 32 || !value.family_id.is_ascii() {
        return Err(invalid("invalid bounded architecture family").into());
    }
    if path.file_name().and_then(|name| name.to_str())
        != Some(format!("{}.json", value.case_context_id).as_str())
    {
        return Err(invalid("case filename and context differ").into());
    }
    if value.stages.len() != STAGES.len() {
        return Err(invalid("exactly seven stages required").into());
    }
    for (index, stage) in value.stages.iter().enumerate() {
        if stage.stage != STAGES[index] || !hash_id(&stage.record_id) {
            return Err(invalid("stage order or record identity differs").into());
        }
    }
    for mass in [
        value.installed_mass_kg,
        value
            .accounted_mass
            .as_ref()
            .and_then(|mass| mass.accounted_tare_kg_per_car),
    ]
    .into_iter()
    .flatten()
    {
        if !mass.is_finite() || mass < 0.0 {
            return Err(invalid("known mass must be finite and nonnegative").into());
        }
    }
    Ok((value, digest))
}

fn schema(fields: Vec<Field>, name: &str) -> Arc<Schema> {
    Arc::new(Schema::new_with_metadata(
        fields,
        std::collections::HashMap::from([("osr_schema".to_owned(), name.to_owned())]),
    ))
}

fn core_schema() -> Arc<Schema> {
    let mut fields = [
        "candidate_id",
        "row_id",
        "body_candidate_id",
        "bundle_definition_id",
        "case_context_id",
        "family_id",
        "motor_component_id",
        "case_sha256",
    ]
    .into_iter()
    .map(|name| Field::new(name, DataType::Utf8, false))
    .collect::<Vec<_>>();
    fields.extend([
        Field::new("accounted_tare_kg_per_car", DataType::Float64, true),
        Field::new("installed_mass_kg", DataType::Float64, true),
    ]);
    fields.extend(
        [
            "physical_journey_completed",
            "complete_body_qualified",
            "physical_accepted",
            "engineering_accepted",
            "configuration_adopted",
            "manufacturing_release",
            "operating_release",
        ]
        .into_iter()
        .map(|name| Field::new(name, DataType::Boolean, false)),
    );
    schema(fields, "osr-case-core-v2-preview/1")
}

fn stage_schema() -> Arc<Schema> {
    schema(
        vec![
            Field::new("case_context_id", DataType::Utf8, false),
            Field::new("stage_ordinal", DataType::UInt8, false),
            Field::new("stage", DataType::Utf8, false),
            Field::new("record_id", DataType::Utf8, false),
            Field::new("reused", DataType::Boolean, false),
        ],
        "osr-case-stage-refs-v2-preview/1",
    )
}

fn string(values: impl Iterator<Item = String>) -> ArrayRef {
    Arc::new(StringArray::from_iter_values(values))
}

fn core_batch(rows: &[(Case, String)]) -> Result<RecordBatch> {
    let columns: Vec<ArrayRef> = vec![
        string(rows.iter().map(|(case, _)| case.candidate_id.clone())),
        string(rows.iter().map(|(case, _)| case.row_id.clone())),
        string(rows.iter().map(|(case, _)| case.body_candidate_id.clone())),
        string(
            rows.iter()
                .map(|(case, _)| case.bundle_definition_id.clone()),
        ),
        string(rows.iter().map(|(case, _)| case.case_context_id.clone())),
        string(rows.iter().map(|(case, _)| case.family_id.clone())),
        string(rows.iter().map(|(case, _)| case.motor_component_id.clone())),
        string(rows.iter().map(|(_, digest)| digest.clone())),
        Arc::new(Float64Array::from(
            rows.iter()
                .map(|(case, _)| {
                    case.accounted_mass
                        .as_ref()
                        .and_then(|mass| mass.accounted_tare_kg_per_car)
                })
                .collect::<Vec<_>>(),
        )),
        Arc::new(Float64Array::from(
            rows.iter()
                .map(|(case, _)| case.installed_mass_kg)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.physical_journey_completed)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.complete_body_qualified)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.physical_accepted)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.engineering_accepted)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.configuration_adopted)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.manufacturing_release)
                .collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            rows.iter()
                .map(|(case, _)| case.operating_release)
                .collect::<Vec<_>>(),
        )),
    ];
    Ok(RecordBatch::try_new(core_schema(), columns)?)
}

fn stage_batch(rows: &[(Case, String)]) -> Result<RecordBatch> {
    let refs = rows
        .iter()
        .flat_map(|(case, _)| {
            case.stages
                .iter()
                .enumerate()
                .map(move |(ordinal, stage)| (case, ordinal, stage))
        })
        .collect::<Vec<_>>();
    let columns: Vec<ArrayRef> = vec![
        string(refs.iter().map(|(case, _, _)| case.case_context_id.clone())),
        Arc::new(UInt8Array::from(
            refs.iter()
                .map(|(_, ordinal, _)| *ordinal as u8)
                .collect::<Vec<_>>(),
        )),
        string(refs.iter().map(|(_, _, stage)| stage.stage.clone())),
        string(refs.iter().map(|(_, _, stage)| stage.record_id.clone())),
        Arc::new(BooleanArray::from(
            refs.iter()
                .map(|(_, _, stage)| stage.reused)
                .collect::<Vec<_>>(),
        )),
    ];
    Ok(RecordBatch::try_new(stage_schema(), columns)?)
}

fn write_part(path: &Path, batch: RecordBatch) -> Result<()> {
    let properties = WriterProperties::builder()
        .set_compression(Compression::ZSTD(Default::default()))
        .set_dictionary_enabled(false)
        .set_max_row_group_row_count(Some(128))
        .build();
    let mut writer = ArrowWriter::try_new(File::create(path)?, batch.schema(), Some(properties))?;
    writer.write(&batch)?;
    writer.close()?;
    if fs::metadata(path)?.len() > MAX_PART_BYTES {
        return Err(invalid("preview Parquet part exceeds 16 MiB").into());
    }
    Ok(())
}

#[derive(Serialize)]
pub struct Report {
    pub schema: &'static str,
    pub case_count: usize,
    pub stage_ref_count: usize,
    pub unsupported_top_level: Vec<String>,
    pub source_cases_unchanged: bool,
    pub replacement_admitted: bool,
}

/// Build a sealed preview, retaining every source case and stage record.
pub fn build(state: &Path, output: &Path) -> Result<Report> {
    if output.exists() {
        return Err(invalid("fresh private output required").into());
    }
    let mut paths = fs::read_dir(state.join("cases"))?
        .map(|entry| entry.map(|entry| entry.path()))
        .collect::<std::result::Result<Vec<_>, _>>()?;
    paths.sort();
    if paths.is_empty() || paths.len() > MAX_CASES {
        return Err(invalid("case count exceeds 128-row preview budget").into());
    }
    if paths.iter().any(|path| {
        path.is_symlink() || path.extension().and_then(|ext| ext.to_str()) != Some("json")
    }) {
        return Err(invalid("ordinary JSON case files required").into());
    }
    let mut rows = Vec::with_capacity(paths.len());
    let mut unsupported = BTreeSet::new();
    for path in paths {
        let row = read_case(&path)?;
        unsupported.extend(row.0.unsupported.keys().cloned());
        rows.push(row);
    }
    let parent = output
        .parent()
        .ok_or_else(|| invalid("output needs a parent"))?;
    fs::create_dir_all(parent)?;
    let nonce = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let stage = parent.join(format!(
        ".osr-case-v2-preview-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir(&stage)?;
    write_part(&stage.join("case-core.parquet"), core_batch(&rows)?)?;
    write_part(&stage.join("stage-refs.parquet"), stage_batch(&rows)?)?;
    let report = Report {
        schema: "osr-case-v2-preview/1",
        case_count: rows.len(),
        stage_ref_count: rows.len() * STAGES.len(),
        unsupported_top_level: unsupported.into_iter().collect(),
        source_cases_unchanged: true,
        replacement_admitted: false,
    };
    let mut receipt = File::create(stage.join("audit.txt"))?;
    writeln!(
        receipt,
        "schema={}\ncases={}\nstage_refs={}\nreplacement_admitted=false",
        report.schema, report.case_count, report.stage_ref_count
    )?;
    for field in &report.unsupported_top_level {
        writeln!(receipt, "unsupported={field}")?;
    }
    receipt.sync_all()?;
    fs::rename(stage, output)?;
    Ok(report)
}

fn parquet_part(path: &Path) -> Result<()> {
    if path.is_symlink() || !path.is_file() || fs::metadata(path)?.len() > MAX_PART_BYTES {
        return Err(invalid("ordinary Parquet part below 16 MiB required").into());
    }
    Ok(())
}

fn strings(batch: &RecordBatch, column: usize) -> Result<&StringArray> {
    batch
        .column(column)
        .as_any()
        .downcast_ref::<StringArray>()
        .ok_or_else(|| invalid("v2 string column type differs").into())
}

fn bools(batch: &RecordBatch, column: usize) -> Result<&BooleanArray> {
    batch
        .column(column)
        .as_any()
        .downcast_ref::<BooleanArray>()
        .ok_or_else(|| invalid("v2 boolean column type differs").into())
}

fn float_bits(batch: &RecordBatch, column: usize, row: usize) -> Result<Option<u64>> {
    let values = batch
        .column(column)
        .as_any()
        .downcast_ref::<Float64Array>()
        .ok_or_else(|| invalid("v2 float column type differs"))?;
    Ok((!values.is_null(row)).then(|| values.value(row).to_bits()))
}

fn core_matches(batch: &RecordBatch, row: usize, case: &Case, digest: &str) -> Result<bool> {
    let expected = [
        case.candidate_id.as_str(),
        case.row_id.as_str(),
        case.body_candidate_id.as_str(),
        case.bundle_definition_id.as_str(),
        case.case_context_id.as_str(),
        case.family_id.as_str(),
        case.motor_component_id.as_str(),
        digest,
    ];
    for (column, value) in expected.into_iter().enumerate() {
        if batch.column(column).is_null(row) || strings(batch, column)?.value(row) != value {
            return Ok(false);
        }
    }
    if float_bits(batch, 8, row)?
        != case
            .accounted_mass
            .as_ref()
            .and_then(|mass| mass.accounted_tare_kg_per_car)
            .map(f64::to_bits)
        || float_bits(batch, 9, row)? != case.installed_mass_kg.map(f64::to_bits)
    {
        return Ok(false);
    }
    let flags = [
        case.physical_journey_completed,
        case.complete_body_qualified,
        case.physical_accepted,
        case.engineering_accepted,
        case.configuration_adopted,
        case.manufacturing_release,
        case.operating_release,
    ];
    for (offset, expected) in flags.into_iter().enumerate() {
        if batch.column(10 + offset).is_null(row)
            || bools(batch, 10 + offset)?.value(row) != expected
        {
            return Ok(false);
        }
    }
    Ok(true)
}

fn stage_matches(batch: &RecordBatch, row: usize, case: &Case, ordinal: usize) -> Result<bool> {
    if (0..5).any(|column| batch.column(column).is_null(row)) {
        return Ok(false);
    }
    let expected = &case.stages[ordinal];
    Ok(strings(batch, 0)?.value(row) == case.case_context_id
        && batch
            .column(1)
            .as_any()
            .downcast_ref::<UInt8Array>()
            .ok_or_else(|| invalid("v2 stage ordinal type differs"))?
            .value(row)
            == ordinal as u8
        && strings(batch, 2)?.value(row) == expected.stage
        && strings(batch, 3)?.value(row) == expected.record_id
        && bools(batch, 4)?.value(row) == expected.reused)
}

fn audit_text(report: &Report) -> String {
    let mut text = format!(
        "schema={}\ncases={}\nstage_refs={}\nreplacement_admitted=false\n",
        report.schema, report.case_count, report.stage_ref_count
    );
    for field in &report.unsupported_top_level {
        text.push_str(&format!("unsupported={field}\n"));
    }
    text
}

/// Authenticate typed Arrow rows and stage references against source case bytes.
/// This does not admit a full row replacement or reinterpret stage payloads.
pub fn verify(state: &Path, preview: &Path) -> Result<Report> {
    if preview.is_symlink() || !preview.is_dir() {
        return Err(invalid("ordinary preview directory required").into());
    }
    let expected_files = ["audit.txt", "case-core.parquet", "stage-refs.parquet"];
    let mut actual_files = fs::read_dir(preview)?
        .map(|entry| entry.map(|entry| entry.file_name()))
        .collect::<std::result::Result<Vec<_>, _>>()?;
    actual_files.sort();
    if actual_files != expected_files.map(std::ffi::OsString::from) {
        return Err(invalid("v2 preview file inventory differs").into());
    }
    for name in ["case-core.parquet", "stage-refs.parquet"] {
        parquet_part(&preview.join(name))?;
    }
    let audit = preview.join("audit.txt");
    if audit.is_symlink() || !audit.is_file() || fs::metadata(&audit)?.len() > 4096 {
        return Err(invalid("ordinary bounded v2 audit required").into());
    }
    let mut paths = fs::read_dir(state.join("cases"))?
        .map(|entry| entry.map(|entry| entry.path()))
        .collect::<std::result::Result<Vec<_>, _>>()?;
    paths.sort();
    if paths.is_empty() || paths.len() > MAX_CASES {
        return Err(invalid("case count exceeds v2 budget").into());
    }
    let mut source_rows = Vec::with_capacity(paths.len());
    let mut unsupported = BTreeSet::new();
    for path in paths {
        let (case, digest) = read_case(&path)?;
        unsupported.extend(case.unsupported.keys().cloned());
        source_rows.push((case, digest));
    }

    let core_path = preview.join("case-core.parquet");
    let core = ParquetRecordBatchReaderBuilder::try_new(File::open(core_path)?)?;
    if core.schema().as_ref() != core_schema().as_ref() {
        return Err(invalid("v2 core schema differs").into());
    }
    let mut count = 0;
    for batch in core.with_batch_size(128).build()? {
        let batch = batch?;
        for row in 0..batch.num_rows() {
            let (case, digest) = source_rows
                .get(count)
                .ok_or_else(|| invalid("v2 core has extra rows"))?;
            if !core_matches(&batch, row, case, digest)? {
                return Err(invalid("v2 core/source projection differs").into());
            }
            count += 1;
        }
    }
    if count != source_rows.len() {
        return Err(invalid("v2 core omitted source rows").into());
    }

    let stage_path = preview.join("stage-refs.parquet");
    let stages = ParquetRecordBatchReaderBuilder::try_new(File::open(stage_path)?)?;
    if stages.schema().as_ref() != stage_schema().as_ref() {
        return Err(invalid("v2 stage schema differs").into());
    }
    let mut count = 0;
    for batch in stages.with_batch_size(128).build()? {
        let batch = batch?;
        for row in 0..batch.num_rows() {
            let case = &source_rows
                .get(count / STAGES.len())
                .ok_or_else(|| invalid("v2 stage table has extra rows"))?
                .0;
            if !stage_matches(&batch, row, case, count % STAGES.len())? {
                return Err(invalid("v2 stage/source reference differs").into());
            }
            count += 1;
        }
    }
    if count != source_rows.len() * STAGES.len() {
        return Err(invalid("v2 stage table omitted references").into());
    }
    let report = Report {
        schema: "osr-case-v2-preview/1",
        case_count: source_rows.len(),
        stage_ref_count: count,
        unsupported_top_level: unsupported.into_iter().collect(),
        source_cases_unchanged: true,
        replacement_admitted: false,
    };
    if fs::read_to_string(audit)? != audit_text(&report) {
        return Err(invalid("v2 audit differs").into());
    }
    Ok(report)
}

#[cfg(test)]
mod tests {
    use super::*;
    use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
    use std::path::PathBuf;

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos();
            let path = std::env::temp_dir()
                .join(format!("osr-v2-case-test-{}-{nonce}", std::process::id()));
            fs::create_dir_all(path.join("state/cases")).unwrap();
            Self(path)
        }
        fn put(&self, reverse: bool) -> Vec<u8> {
            let refs = STAGES
                .iter()
                .enumerate()
                .map(|(i, name)| {
                    serde_json::json!({
                        "stage": name, "record_id": format!("{i:064x}"), "reused": i % 2 == 0,
                        "request": {"nested_untyped_data": [1,2,3]}
                    })
                })
                .collect::<Vec<_>>();
            let refs = if reverse {
                refs.into_iter().rev().collect::<Vec<_>>()
            } else {
                refs
            };
            let row = serde_json::json!({
                "candidate_id": format!("{:064x}",1), "row_id": format!("{:064x}",2),
                "body_candidate_id": format!("{:064x}",3), "bundle_definition_id": format!("{:064x}",4),
                "case_context_id": format!("{:064x}",5), "family_id":"P1",
                "motor_component_id": format!("{:064x}",6), "accounted_mass":{"accounted_tare_kg_per_car":100.0},
                "installed_mass_kg":null, "physical_journey_completed":false,
                "complete_body_qualified":false, "physical_accepted":false,
                "engineering_accepted":false, "configuration_adopted":false,
                "manufacturing_release":false, "operating_release":false,
                "stages":refs, "economics":{"unknown_price":null}
            });
            let raw = serde_json::to_vec(&row).unwrap();
            fs::write(self.0.join(format!("state/cases/{:064x}.json", 5)), &raw).unwrap();
            raw
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn typed_core_and_refs_preserve_unknown_mass_and_source_bytes() {
        let fixture = Fixture::new();
        let raw = fixture.put(false);
        let report = build(&fixture.0.join("state"), &fixture.0.join("output")).unwrap();
        assert_eq!((report.case_count, report.stage_ref_count), (1, 7));
        assert_eq!(report.unsupported_top_level, ["economics"]);
        assert!(!report.replacement_admitted);
        let verified = verify(&fixture.0.join("state"), &fixture.0.join("output")).unwrap();
        assert_eq!((verified.case_count, verified.stage_ref_count), (1, 7));
        assert_eq!(
            fs::read(fixture.0.join(format!("state/cases/{:064x}.json", 5))).unwrap(),
            raw
        );
        let builder = ParquetRecordBatchReaderBuilder::try_new(
            File::open(fixture.0.join("output/case-core.parquet")).unwrap(),
        )
        .unwrap();
        assert_eq!(
            builder.schema().metadata()["osr_schema"],
            "osr-case-core-v2-preview/1"
        );
        let rows = builder.build().unwrap().next().unwrap().unwrap();
        assert_eq!(rows.num_rows(), 1);
        assert!(rows.column(9).is_null(0));
        let stage = ParquetRecordBatchReaderBuilder::try_new(
            File::open(fixture.0.join("output/stage-refs.parquet")).unwrap(),
        )
        .unwrap();
        assert_eq!(
            stage.build().unwrap().next().unwrap().unwrap().num_rows(),
            7
        );
    }

    #[test]
    fn altered_stage_order_is_rejected_before_output() {
        let fixture = Fixture::new();
        fixture.put(true);
        assert!(build(&fixture.0.join("state"), &fixture.0.join("output")).is_err());
        assert!(!fixture.0.join("output").exists());
    }

    #[test]
    fn verifier_rejects_changed_source_and_arrow_stage_value() {
        let fixture = Fixture::new();
        let original = fixture.put(false);
        build(&fixture.0.join("state"), &fixture.0.join("output")).unwrap();
        let source = fixture.0.join(format!("state/cases/{:064x}.json", 5));
        let mut changed: serde_json::Value = serde_json::from_slice(&original).unwrap();
        changed["row_id"] = serde_json::json!(format!("{:064x}", 99));
        fs::write(&source, serde_json::to_vec(&changed).unwrap()).unwrap();
        assert!(verify(&fixture.0.join("state"), &fixture.0.join("output")).is_err());
        fs::write(&source, original).unwrap();
        let part = fixture.0.join("output/stage-refs.parquet");
        let reader = ParquetRecordBatchReaderBuilder::try_new(File::open(&part).unwrap()).unwrap();
        let batch = reader.build().unwrap().next().unwrap().unwrap();
        let mut columns = batch.columns().to_vec();
        columns[3] = string((0..batch.num_rows()).map(|row| {
            if row == 0 {
                format!("{:064x}", 99)
            } else {
                strings(&batch, 3).unwrap().value(row).to_owned()
            }
        }));
        let changed = RecordBatch::try_new(stage_schema(), columns).unwrap();
        let mut writer =
            ArrowWriter::try_new(File::create(&part).unwrap(), stage_schema(), None).unwrap();
        writer.write(&changed).unwrap();
        writer.close().unwrap();
        assert!(verify(&fixture.0.join("state"), &fixture.0.join("output")).is_err());
    }
}
