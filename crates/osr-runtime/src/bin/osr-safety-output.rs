//! Independent real-clock process port; explicit virtual mode is for replay.
use osr_brake::dual::DualGuard;
use osr_runtime::clocked_output::{ClockedOutput, OutputCommand};
use std::io::{self, BufRead, Read, Write};
use std::time::Duration;

fn main() -> io::Result<()> {
    let args = osr_runtime::args()?;
    let frozen = osr_runtime::load(
        std::path::Path::new(osr_runtime::required(&args, "--model")?),
        std::path::Path::new(osr_runtime::required(&args, "--deployment")?),
    )?;
    let entity: u64 = osr_runtime::required(&args, "--entity")?
        .parse()
        .map_err(osr_runtime::bad)?;
    frozen
        .train_config(osr_core::TrainId(entity))
        .map_err(|_| osr_runtime::bad("output train identity"))?;
    match args.get("--clock").map(String::as_str).unwrap_or("real") {
        "real" => real_port(),
        "virtual" => virtual_port(),
        _ => Err(osr_runtime::bad("--clock must be real or virtual")),
    }
}

fn virtual_port() -> io::Result<()> {
    let mut guard = DualGuard::default();
    osr_runtime::run_lines(|command: OutputCommand| {
        let pair = match command {
            OutputCommand::FeedPair {
                now,
                pair,
                feedback_a_healthy,
                feedback_b_healthy,
                ..
            } => guard.feed(now, pair, feedback_a_healthy, feedback_b_healthy),
            OutputCommand::Sample {
                now,
                feedback_a_healthy,
                feedback_b_healthy,
            } => guard.sample(now, feedback_a_healthy, feedback_b_healthy),
            OutputCommand::Clock => {
                return Err(osr_runtime::bad("virtual replay has no autonomous clock"))
            }
        };
        Ok(serde_json::json!({"pair": pair, "autonomous": false}))
    })
}

fn real_port() -> io::Result<()> {
    let host = ClockedOutput::start()?;
    let input = host.input.clone();
    std::thread::Builder::new()
        .name("safety-output-input".into())
        .spawn(move || {
            let stdin = io::stdin();
            let mut reader = stdin.lock();
            loop {
                let mut bytes = Vec::new();
                match reader.by_ref().take(4097).read_until(b'\n', &mut bytes) {
                    Ok(0) => break,
                    Ok(count) if count > 4096 || bytes.last() != Some(&b'\n') => {
                        let _ =
                            input.send(Some(Err("oversized or unterminated output frame".into())));
                        break;
                    }
                    Ok(_) => {
                        let command = serde_json::from_slice(&bytes).map_err(|e| e.to_string());
                        if input.send(Some(command)).is_err() {
                            return;
                        }
                    }
                    Err(e) => {
                        let _ = input.send(Some(Err(e.to_string())));
                        break;
                    }
                }
            }
            let _ = input.send(None);
        })?;
    let mut output = io::stdout().lock();
    loop {
        // This thread may block on its consumer; it never owns the sampler.
        // Observe closure before taking the snapshot, so EOF cannot make a
        // previously captured permit the final published frame.
        let finished = host.finished();
        let snapshot = host.snapshot();
        let value = serde_json::json!({"ok":snapshot.error.is_none(),
            "error":snapshot.error,"result":snapshot});
        serde_json::to_writer(&mut output, &value).map_err(osr_runtime::bad)?;
        output.write_all(b"\n")?;
        output.flush()?;
        if finished {
            break;
        }
        std::thread::sleep(Duration::from_millis(10));
    }
    host.join()
}
