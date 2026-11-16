//! Bounded lossless canonical JSON <-> typed Parquet node table.
#[path = "../case_nodes.rs"]
mod case_nodes;
fn main() {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 3 {
        eprintln!("usage: osr-campaign-case-nodes encode SOURCE|- FRESH.parquet | verify SOURCE PARQUET | decode PARQUET -");
        std::process::exit(2);
    }
    let result: Result<String, Box<dyn std::error::Error>> = (|| {
        let mode = args[0].to_str().ok_or("mode must be UTF-8")?;
        let source = std::path::Path::new(&args[1]);
        let target = std::path::Path::new(&args[2]);
        match mode {
            "encode" => {
                let (nodes, bytes, sha) = if source == std::path::Path::new("-") {
                    use std::io::Read;
                    let mut input = Vec::new();
                    std::io::stdin()
                        .take(case_nodes::MAX_BYTES + 1)
                        .read_to_end(&mut input)?;
                    case_nodes::encode_bytes(&input, target)?
                } else {
                    case_nodes::encode(source, target)?
                };
                Ok(format!(
                    "nodes={nodes} parquet_bytes={bytes} source_sha256={sha}"
                ))
            }
            "verify" => Ok(format!(
                "verified_bytes={}",
                case_nodes::verify(source, target)?
            )),
            "decode" => {
                if target != std::path::Path::new("-") {
                    return Err("decode target must be stdout '-'".into());
                }
                let data = case_nodes::decode(source)?;
                use std::io::Write;
                std::io::stdout().write_all(&data)?;
                Ok(format!("decoded_bytes={}", data.len()))
            }
            _ => Err("unknown node-table mode".into()),
        }
    })();
    match result {
        Ok(message) => {
            if args[0] != "decode" {
                println!("{message}");
            }
        }
        Err(error) => {
            eprintln!("node table: {error}");
            std::process::exit(2);
        }
    }
}
