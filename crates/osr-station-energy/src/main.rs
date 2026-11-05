use std::io::{Read, Write};

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut raw = Vec::new();
    std::io::stdin()
        .take((osr_station_energy::MAX_INPUT_BYTES + 1) as u64)
        .read_to_end(&mut raw)?;
    if raw.len() > osr_station_energy::MAX_INPUT_BYTES {
        return Err("Request exceeds 8 MiB reader budget".into());
    }
    let request: osr_station_energy::Request = serde_json::from_slice(&raw)?;
    let result = osr_station_energy::execute(request)?;
    let stdout = std::io::stdout();
    let mut out = std::io::BufWriter::new(stdout.lock());
    serde_json::to_writer(&mut out, &result)?;
    out.write_all(b"\n")?;
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("osr-station-energy: {error}");
        std::process::exit(2);
    }
}
