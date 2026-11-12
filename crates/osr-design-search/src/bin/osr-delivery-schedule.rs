use std::io::{Read, Write};
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut bytes = Vec::new();
    std::io::stdin()
        .take(16 * 1024 * 1024 + 1)
        .read_to_end(&mut bytes)?;
    if bytes.len() > 16 * 1024 * 1024 {
        return Err("Scheduling request exceeds 16 MiB".into());
    }
    let request = serde_json::from_slice(&bytes)?;
    let result = osr_design_search::scheduling::schedule(request)?;
    let mut out = std::io::BufWriter::new(std::io::stdout().lock());
    serde_json::to_writer(&mut out, &result)?;
    out.write_all(b"\n")?;
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("osr-delivery-schedule: {error}");
        std::process::exit(2);
    }
}
