//! Evaluate workforce coverage and labour allowances from a scoped workplan.

mod model;
mod output;
mod simulation;

use crate::model::{invalid, Plan, FULL_AVAILABILITY_BPS};
use sha2::{Digest, Sha256};
use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::PathBuf;

const MAX_PLAN_BYTES: u64 = 64 * 1024 * 1024;
const USAGE: &str = "Usage: osr-workforce PLAN.json NEW_OUTPUT_DIR [--availability-bps N]";

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args_os().skip(1);
    let input = args.next().ok_or_else(|| invalid(USAGE))?;
    if input == "--help" || input == "-h" {
        println!("{USAGE}");
        return Ok(());
    }
    let output = PathBuf::from(args.next().ok_or_else(|| invalid(USAGE))?);
    let availability = match args.next() {
        None => FULL_AVAILABILITY_BPS,
        Some(option) if option == "--availability-bps" => args
            .next()
            .and_then(|value| value.into_string().ok())
            .and_then(|text| text.parse::<u64>().ok())
            .filter(|value| *value <= FULL_AVAILABILITY_BPS)
            .ok_or_else(|| invalid("Availability must be between 0 and 10000 basis points"))?,
        Some(_) => return Err(invalid(USAGE).into()),
    };
    if args.next().is_some() {
        return Err(invalid(USAGE).into());
    }
    let plan_file = File::open(input)?;
    let metadata = plan_file.metadata()?;
    if !metadata.is_file() || metadata.len() > MAX_PLAN_BYTES {
        return Err(invalid("An ordinary plan file up to 64 MiB is required").into());
    }
    let mut raw = Vec::with_capacity(metadata.len() as usize);
    plan_file.take(MAX_PLAN_BYTES + 1).read_to_end(&mut raw)?;
    if raw.len() as u64 > MAX_PLAN_BYTES {
        return Err(invalid("Plan exceeds the 64 MiB input limit").into());
    }
    let plan: Plan = serde_json::from_slice(&raw)?;
    plan.validate()?;
    let input_sha256 = format!("{:x}", Sha256::digest(raw));
    output::write(&plan, &input_sha256, availability, &output)?;
    println!(
        "Evaluated {} shift rows. Results in {}",
        plan.rows.len(),
        output.display()
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("osr-workforce: {error}");
        std::process::exit(1);
    }
}
