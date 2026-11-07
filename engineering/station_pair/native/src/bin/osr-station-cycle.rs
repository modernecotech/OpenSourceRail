use std::io::{Read, Write};
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut raw = vec![];
    std::io::stdin()
        .take((osr_journey::MAX_INPUT_BYTES + 1) as u64)
        .read_to_end(&mut raw)?;
    if raw.len() > osr_journey::MAX_INPUT_BYTES {
        return Err("Request exceeds8MiB".into());
    }
    let request = serde_json::from_slice(&raw)?;
    let result = osr_journey::cycle::execute(request)?;
    let mut out = std::io::BufWriter::new(std::io::stdout());
    serde_json::to_writer(&mut out, &result)?;
    out.write_all(b"\n")?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("osr-station-cycle: {e}");
        std::process::exit(2);
    }
}
