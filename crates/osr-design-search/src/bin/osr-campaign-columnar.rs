//! Bounded Rust Arrow/Parquet access to coupled-campaign case records.

use osr_design_search::columnar::{index_cases, query_candidate, verify_index, IndexOptions};
use std::error::Error;
use std::path::Path;
#[path = "../publication_columnar.rs"]
mod publication_columnar;

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args().skip(1);
    let command = args
        .next()
        .ok_or("expected index, verify, query, write-comparison or scan-comparison")?;
    let first = args.next().ok_or("expected first path")?;
    if command == "write-comparison" {
        if args.next().is_some() {
            return Err("too many arguments for write-comparison".into());
        }
        return publication_columnar::write(Path::new(&first));
    }
    let second = args
        .next()
        .ok_or("expected second path or inventory SHA-256")?;
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
        "scan-comparison" | "read-comparison" | "query-comparison" => {
            let candidate = if command == "query-comparison" {
                Some(args.next().ok_or("expected candidate ID")?)
            } else {
                None
            };
            if args.next().is_some() {
                return Err("too many comparison arguments".into());
            }
            publication_columnar::scan(
                Path::new(&first),
                &second,
                candidate.as_deref(),
                command == "read-comparison",
            )?;
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
