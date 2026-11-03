use std::io::{Read, Write};

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut input = Vec::new();
    std::io::stdin()
        .take((osr_design_search::MAX_INPUT_BYTES + 1) as u64)
        .read_to_end(&mut input)?;
    if input.len() > osr_design_search::MAX_INPUT_BYTES {
        return Err("Request exceeds 64 MiB reader budget".into());
    }
    let request = serde_json::from_slice::<osr_design_search::Request>(&input)?;
    let value = osr_design_search::execute(request)?;
    let stdout = std::io::stdout();
    let mut out = std::io::BufWriter::new(stdout.lock());
    serde_json::to_writer(&mut out, &value)?;
    out.write_all(b"\n")?;
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("osr-design-search: {error}");
        std::process::exit(2);
    }
}
