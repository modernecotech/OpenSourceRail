use std::io::{Read, Write};
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut raw = Vec::new();
    std::io::stdin()
        .take((osr_station_energy::arrestor::MAX_INPUT_BYTES + 1) as u64)
        .read_to_end(&mut raw)?;
    if raw.len() > osr_station_energy::arrestor::MAX_INPUT_BYTES {
        return Err("Request exceeds 8 MiB".into());
    }
    let request = serde_json::from_slice::<osr_station_energy::arrestor::Request>(&raw)?;
    let result = osr_station_energy::arrestor::execute(request)?;
    let stdout = std::io::stdout();
    let mut output = std::io::BufWriter::new(stdout.lock());
    serde_json::to_writer(&mut output, &result)?;
    output.write_all(b"\n")?;
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("osr-arrestor: {error}");
        std::process::exit(2);
    }
}
