//! Bounded Rust Arrow/Parquet access to coupled-campaign case records.

use osr_design_search::columnar::{index_cases, query_candidate, verify_index, IndexOptions};
use std::error::Error;
use std::path::Path;

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args().skip(1);
    let command = args.next().ok_or("expected index, verify or query")?;
    let first = args.next().ok_or("expected first path")?;
    let second = args.next().ok_or("expected second path")?;
    match command.as_str() {
        "index" => {
            if args.next().is_some() {
                return Err("too many arguments for index".into());
            }
            let count = index_cases(
                Path::new(&first),
                Path::new(&second),
                IndexOptions::default(),
            )?;
            println!("indexed {count} source-bound cases");
        }
        "verify" => {
            if args.next().is_some() {
                return Err("too many arguments for verify".into());
            }
            let count = verify_index(Path::new(&first), Path::new(&second))?;
            println!("verified {count} source-bound cases");
        }
        "query" => {
            let candidate_id = args.next().ok_or("expected candidate ID")?;
            if args.next().is_some() {
                return Err("too many arguments for query".into());
            }
            let rows = query_candidate(Path::new(&first), Path::new(&second), &candidate_id)?;
            for row in rows {
                println!("{}", serde_json::to_string(&row)?);
            }
        }
        _ => return Err("expected index, verify or query".into()),
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("osr-campaign-columnar: {error}");
        std::process::exit(2);
    }
}
