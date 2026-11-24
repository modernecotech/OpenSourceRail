use arrow_array::{Array, StringArray, UInt64Array};
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use serde_json::{json, Value};
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicUsize, Ordering};

static NEXT_ATTEMPT: AtomicUsize = AtomicUsize::new(0);

struct Scratch(PathBuf);

impl Scratch {
    fn new() -> Self {
        let path = Path::new(env!("CARGO_TARGET_TMPDIR")).join(format!(
            "workforce-test-{}-{}",
            std::process::id(),
            NEXT_ATTEMPT.fetch_add(1, Ordering::Relaxed),
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }

    fn run(&self, plan: &Value, availability: &str) -> Output {
        let input = self.0.join("plan.json");
        fs::write(&input, serde_json::to_vec(plan).unwrap()).unwrap();
        Command::new(env!("CARGO_BIN_EXE_osr-workforce"))
            .arg(input)
            .arg(self.0.join("result"))
            .args(["--availability-bps", availability])
            .output()
            .unwrap()
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        fs::remove_dir_all(&self.0).unwrap();
    }
}

fn row(id: impl Into<String>) -> Value {
    json!({
        "work_id": id.into(), "phase": "Factory", "role": "Tooling, \"night\"", "shift": "Night",
        "start_minute": 1320, "minutes_per_shift": 15, "days": 2, "assigned_posts": 1,
        "required_minutes": 20, "paid_minutes": 31, "utilisation_bps": 7500,
        "rates_cents_per_hour": [101, 201, 301], "rate_basis": "example", "cost_account": "vehicle price"
    })
}

fn plan(rows: Vec<Value>) -> Value {
    json!({
        "schema": "osr-workforce-plan/1", "plan_id": "test-plan",
        "scope": { "label": "Example railway", "candidate_id": "trial-candidate" },
        "source_sha256": {"scope.json": "a".repeat(64)}, "rows": rows,
        "gaps": [{"phase": "Factory", "work": "Shift transfer", "owner": "Supplier", "cost_basis": "Quote pending"}]
    })
}

fn assert_success(output: &Output) {
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
}

#[test]
fn stressed_minutes_costs_and_unpriced_rows_match_arrow_and_csv() {
    let dir = Scratch::new();
    let mut unknown = row("unknown");
    unknown["rates_cents_per_hour"] = Value::Null;
    unknown["assigned_posts"] = Value::Null;
    unknown["paid_minutes"] = 6.into();
    let mut other_account = row("zero-cost");
    other_account["cost_account"] = "public cost".into();
    other_account["assigned_posts"] = 0.into();
    other_account["paid_minutes"] = 0.into();
    let plan = plan(vec![row("known"), unknown, other_account]);
    assert_success(&dir.run(&plan, "8000"));

    let result = dir.0.join("result");
    let summary: Value =
        serde_json::from_reader(File::open(result.join("summary.json")).unwrap()).unwrap();
    assert_eq!(summary["scope"], plan["scope"]);
    assert_eq!(summary["gaps"], plan["gaps"]);
    assert_eq!(summary["row_count"], 3);
    assert_eq!(summary["source_sha256"], plan["source_sha256"]);
    assert_eq!(summary["input_sha256"].as_str().unwrap().len(), 64);
    let groups = summary["groups"].as_array().unwrap();
    assert_eq!(groups.len(), 2);
    let vehicle = &groups[1];
    assert_eq!(vehicle["known_cost_cents"], json!([52, 104, 156]));
    assert_eq!(vehicle["known_capacity_minutes"], 22);
    assert_eq!(vehicle["known_stressed_capacity_minutes"], 18);
    assert_eq!(vehicle["known_shortage_minutes"], 0);
    assert_eq!(vehicle["known_stressed_shortage_minutes"], 2);
    assert_eq!(vehicle["known_unpriced_paid_minutes"], 6);
    assert_eq!(vehicle["unknown_capacity_rows"], 1);
    assert_eq!(vehicle["unpriced_rows"], 1);
    assert_eq!(groups[0]["known_shortage_minutes"], 20);
    assert_eq!(groups[0]["known_cost_cents"], json!([0, 0, 0]));

    let parquet = File::open(result.join("workforce.parquet")).unwrap();
    let reader = ParquetRecordBatchReaderBuilder::try_new(parquet).unwrap();
    let parquet_scope: Value = serde_json::from_str(&reader.schema().metadata()["scope"]).unwrap();
    assert_eq!(parquet_scope, plan["scope"]);
    assert_eq!(reader.schema().metadata()["currency_unit"], "USD cent");
    let batch = reader.build().unwrap().next().unwrap().unwrap();
    let costs = batch
        .column_by_name("cost_base_cents")
        .unwrap()
        .as_any()
        .downcast_ref::<UInt64Array>()
        .unwrap();
    let capacity = batch
        .column_by_name("capacity_minutes")
        .unwrap()
        .as_any()
        .downcast_ref::<UInt64Array>()
        .unwrap();
    let roles = batch
        .column_by_name("role")
        .unwrap()
        .as_any()
        .downcast_ref::<StringArray>()
        .unwrap();
    assert_eq!(roles.value(0), "Tooling, \"night\"");
    assert_eq!(costs.iter().collect::<Vec<_>>(), [Some(104), None, Some(0)]);
    assert_eq!(
        capacity.iter().collect::<Vec<_>>(),
        [Some(22), None, Some(0)]
    );

    let csv = fs::read_to_string(result.join("workforce.csv")).unwrap();
    let mut lines = csv.lines();
    let fields = batch.schema();
    assert_eq!(
        lines.next().unwrap(),
        fields
            .fields()
            .iter()
            .map(|field| field.name().as_str())
            .collect::<Vec<_>>()
            .join(",")
    );
    for (index, line) in lines.enumerate() {
        assert!(line.contains("\"Tooling, \"\"night\"\"\""));
        let numbers = line
            .split("\",")
            .nth(4)
            .unwrap()
            .split(',')
            .take(18)
            .collect::<Vec<_>>();
        for (offset, cell) in numbers.iter().enumerate() {
            let column = batch
                .column(offset + 4)
                .as_any()
                .downcast_ref::<UInt64Array>()
                .unwrap();
            let value = column.is_valid(index).then(|| column.value(index));
            assert_eq!(cell.parse::<u64>().ok(), value);
        }
    }
    let rejected = dir.run(&plan, "10000");
    assert!(!rejected.status.success());
    assert_eq!(
        csv,
        fs::read_to_string(result.join("workforce.csv")).unwrap()
    );
}

#[test]
fn invalid_identity_and_numeric_overflow_leave_no_success_record() {
    let dir = Scratch::new();
    let duplicate = plan(vec![row("same"), row("same")]);
    assert!(!dir.run(&duplicate, "8000").status.success());
    assert!(!dir.0.join("result").exists());

    let mut overflow = row("overflow");
    overflow["assigned_posts"] = u64::MAX.into();
    overflow["days"] = u64::MAX.into();
    assert!(!dir.run(&plan(vec![overflow]), "8000").status.success());
    let result = dir.0.join("result");
    assert!(!result.join("summary.json").exists());
    assert!(fs::read_to_string(result.join("error.txt"))
        .unwrap()
        .contains("overflow"));
}

#[test]
fn output_row_groups_bound_batch_memory_and_keep_summary_totals() {
    let dir = Scratch::new();
    let count = 4101;
    assert_success(&dir.run(
        &plan((0..count).map(|index| row(index.to_string())).collect()),
        "10000",
    ));
    let result = dir.0.join("result");
    let parquet = File::open(result.join("workforce.parquet")).unwrap();
    let reader = ParquetRecordBatchReaderBuilder::try_new(parquet).unwrap();
    assert_eq!(reader.metadata().num_row_groups(), 2);
    assert_eq!(reader.metadata().file_metadata().num_rows(), count);
    let summary: Value =
        serde_json::from_reader(File::open(result.join("summary.json")).unwrap()).unwrap();
    assert_eq!(
        summary["groups"][0]["known_cost_cents"],
        json!([52 * count, 104 * count, 156 * count])
    );
    assert_eq!(summary["groups"][0]["known_stressed_shortage_minutes"], 0);
}
