//! Read-only source-bound preview of a typed case core and seven-stage table.

#[path = "../case_v2_preview.rs"]
mod case_v2_preview;

fn main() {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 2 && args.len() != 3 {
        eprintln!("usage: osr-campaign-case-v2-preview <contract-state> <fresh-private-output> | verify <contract-state> <preview-output>");
        std::process::exit(2);
    }
    let result = if args.len() == 3 && args[0] == "verify" {
        case_v2_preview::verify(
            std::path::Path::new(&args[1]),
            std::path::Path::new(&args[2]),
        )
    } else if args.len() == 2 {
        case_v2_preview::build(
            std::path::Path::new(&args[0]),
            std::path::Path::new(&args[1]),
        )
    } else {
        Err("expected verify <contract-state> <preview-output>".into())
    };
    match result {
        Ok(report) => println!("{}", serde_json::to_string(&report).expect("static report")),
        Err(error) => {
            eprintln!("v2 case preview: {error}");
            std::process::exit(2);
        }
    }
}
