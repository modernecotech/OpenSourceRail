use crate::model::{Gap, Plan, Shift, FULL_AVAILABILITY_BPS};
use crate::simulation::{
    evaluate_columns, nullable_value, Group, GroupedTotals, NumericInputs, NumericResults,
};
use arrow_array::{Array, ArrayRef, RecordBatch, StringArray, UInt64Array};
use arrow_schema::{DataType, Field, Schema, SchemaRef};
use parquet::arrow::ArrowWriter;
use parquet::basic::{Compression, ZstdLevel};
use parquet::file::properties::WriterProperties;
use serde::Serialize;
use std::collections::{BTreeMap, HashMap};
use std::error::Error;
use std::fs::{self, File};
use std::io::{self, BufWriter, Write};
use std::path::Path;
use std::sync::Arc;

const BATCH_SIZE: usize = 4096;
const OUTPUT_SCHEMA: &str = "osr-workforce-result/1";

const TEXT_ID_FIELDS: [&str; 4] = ["work_id", "phase", "role", "shift"];
const TEXT_SCOPE_FIELDS: [&str; 2] = ["rate_basis", "cost_account"];
const NUMBER_FIELDS: [(&str, bool); 18] = [
    ("start_minute", true),
    ("minutes_per_shift", true),
    ("days", true),
    ("assigned_posts", true),
    ("required_minutes", true),
    ("paid_minutes", true),
    ("utilisation_bps", false),
    ("rate_low_cents_per_hour", true),
    ("rate_base_cents_per_hour", true),
    ("rate_high_cents_per_hour", true),
    ("capacity_minutes", true),
    ("stressed_capacity_minutes", true),
    ("shortage_minutes", true),
    ("stressed_shortage_minutes", true),
    ("cost_low_cents", true),
    ("cost_base_cents", true),
    ("cost_high_cents", true),
    ("availability_bps", false),
];

fn schema(
    plan: &Plan,
    input_sha256: &str,
    availability_bps: u64,
) -> Result<SchemaRef, Box<dyn Error>> {
    let metadata = HashMap::from([
        ("schema".to_owned(), OUTPUT_SCHEMA.to_owned()),
        ("plan_id".to_owned(), plan.plan_id.clone()),
        ("scope".to_owned(), serde_json::to_string(&plan.scope)?),
        ("input_sha256".to_owned(), input_sha256.to_owned()),
        (
            "source_sha256".to_owned(),
            serde_json::to_string(&plan.source_sha256)?,
        ),
        ("availability_bps".to_owned(), availability_bps.to_string()),
        ("currency_unit".to_owned(), "USD cent".to_owned()),
    ]);
    let fields = TEXT_ID_FIELDS
        .into_iter()
        .map(|name| Field::new(name, DataType::Utf8, false))
        .chain(
            NUMBER_FIELDS
                .into_iter()
                .map(|(name, nullable)| Field::new(name, DataType::UInt64, nullable)),
        )
        .chain(
            TEXT_SCOPE_FIELDS
                .into_iter()
                .map(|name| Field::new(name, DataType::Utf8, false)),
        )
        .collect::<Vec<_>>();
    Ok(Arc::new(Schema::new_with_metadata(fields, metadata)))
}

fn batch(
    schema: &SchemaRef,
    rows: &[Shift],
    input: NumericInputs,
    result: NumericResults,
    availability_bps: u64,
) -> Result<RecordBatch, arrow_schema::ArrowError> {
    let text_column = |get: fn(&Shift) -> &str| -> ArrayRef {
        Arc::new(StringArray::from_iter_values(rows.iter().map(get)))
    };
    let mut columns = Vec::with_capacity(schema.fields().len());
    columns.extend([
        text_column(|row| &row.work_id),
        text_column(|row| &row.phase),
        text_column(|row| &row.role),
        text_column(|row| &row.shift),
    ]);
    let [low_rate, base_rate, high_rate] = input.rates;
    let [low_cost, base_cost, high_cost] = result.costs;
    let integer_columns = [
        rows.iter().map(|row| row.start_minute).collect(),
        input.minutes_per_shift,
        input.days,
        input.assigned_posts,
        input.required,
        input.paid,
        input.utilisation,
        low_rate,
        base_rate,
        high_rate,
        result.capacity,
        result.stressed_capacity,
        result.shortage,
        result.stressed_shortage,
        low_cost,
        base_cost,
        high_cost,
        UInt64Array::from_iter_values(std::iter::repeat_n(availability_bps, rows.len())),
    ];
    columns.extend(integer_columns.map(|column| Arc::new(column) as ArrayRef));
    columns.extend([
        text_column(|row| &row.rate_basis),
        text_column(|row| &row.cost_account),
    ]);
    RecordBatch::try_new(Arc::clone(schema), columns)
}

enum CsvColumn<'a> {
    Text(&'a StringArray),
    Number(&'a UInt64Array),
}

fn quote_csv(writer: &mut impl Write, text: &str) -> io::Result<()> {
    writer.write_all(b"\"")?;
    for (index, part) in text.split('"').enumerate() {
        if index != 0 {
            writer.write_all(b"\"\"")?;
        }
        writer.write_all(part.as_bytes())?;
    }
    writer.write_all(b"\"")
}

fn csv_batch(writer: &mut impl Write, batch: &RecordBatch) -> io::Result<()> {
    let columns = batch
        .columns()
        .iter()
        .map(|column| {
            let column = column.as_any();
            if let Some(text) = column.downcast_ref::<StringArray>() {
                CsvColumn::Text(text)
            } else {
                CsvColumn::Number(
                    column
                        .downcast_ref::<UInt64Array>()
                        .expect("integer export column"),
                )
            }
        })
        .collect::<Vec<_>>();
    for row in 0..batch.num_rows() {
        for (index, column) in columns.iter().enumerate() {
            if index != 0 {
                writer.write_all(b",")?;
            }
            match column {
                CsvColumn::Text(array) => quote_csv(writer, array.value(row))?,
                CsvColumn::Number(array) => {
                    if let Some(amount) = nullable_value(array, row) {
                        write!(writer, "{amount}")?;
                    }
                }
            }
        }
        writer.write_all(b"\r\n")?;
    }
    Ok(())
}

#[derive(Serialize)]
struct Summary<'a> {
    schema: &'static str,
    currency_unit: &'static str,
    plan_id: &'a str,
    scope: &'a serde_json::Value,
    source_sha256: &'a BTreeMap<String, String>,
    input_sha256: &'a str,
    availability_bps: u64,
    row_count: usize,
    groups: Vec<Group<'a>>,
    gaps: &'a [Gap],
}

fn write_inner(
    plan: &Plan,
    input_sha256: &str,
    availability_bps: u64,
    output: &Path,
) -> Result<(), Box<dyn Error>> {
    let schema = schema(plan, input_sha256, availability_bps)?;
    let properties = WriterProperties::builder()
        .set_max_row_group_row_count(Some(BATCH_SIZE))
        .set_compression(Compression::ZSTD(ZstdLevel::default()))
        .build();
    let mut parquet = ArrowWriter::try_new(
        File::create(output.join("workforce.parquet"))?,
        Arc::clone(&schema),
        Some(properties),
    )?;
    let mut csv = BufWriter::new(File::create(output.join("workforce.csv"))?);
    for (index, field) in schema.fields().iter().enumerate() {
        if index != 0 {
            csv.write_all(b",")?;
        }
        csv.write_all(field.name().as_bytes())?;
    }
    csv.write_all(b"\r\n")?;

    let mut totals = GroupedTotals::default();
    for rows in plan.rows.chunks(BATCH_SIZE) {
        let input = NumericInputs::from_shifts(rows);
        let evaluated = evaluate_columns(&input, availability_bps)?;
        for (index, row) in rows.iter().enumerate() {
            totals.include(row, evaluated.row(index))?;
        }
        let batch = batch(&schema, rows, input, evaluated, availability_bps)?;
        csv_batch(&mut csv, &batch)?;
        parquet.write(&batch)?;
    }
    parquet.close()?;
    csv.flush()?;

    let summary = Summary {
        schema: OUTPUT_SCHEMA,
        currency_unit: "USD cent",
        plan_id: &plan.plan_id,
        scope: &plan.scope,
        source_sha256: &plan.source_sha256,
        input_sha256,
        availability_bps,
        row_count: plan.rows.len(),
        groups: totals.finish(),
        gaps: &plan.gaps,
    };
    let partial = output.join("summary.partial");
    let mut json = BufWriter::new(File::create(&partial)?);
    serde_json::to_writer_pretty(&mut json, &summary)?;
    json.write_all(b"\n")?;
    json.flush()?;
    fs::rename(partial, output.join("summary.json"))?;
    Ok(())
}

pub fn write(
    plan: &Plan,
    input_sha256: &str,
    availability_bps: u64,
    output: &Path,
) -> Result<(), Box<dyn Error>> {
    if availability_bps > FULL_AVAILABILITY_BPS {
        return Err(
            crate::model::invalid("Availability must be between 0 and 10000 basis points").into(),
        );
    }
    // Reserve the name atomically. An existing result remains untouched.
    // summary.json is written last and identifies a complete set of outputs.
    fs::create_dir(output)?;
    let outcome = write_inner(plan, input_sha256, availability_bps, output);
    if let Err(error) = &outcome {
        let _ = fs::write(output.join("error.txt"), format!("{error}\n"));
    }
    outcome
}
