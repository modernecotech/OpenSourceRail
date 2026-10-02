//! Synthetic isolated deadline/output port. Physical de-energised wiring needs HIL.
use osr_brake::deadline::{Guard, Output, Request};
use serde::{Deserialize, Serialize};
use std::io;
#[derive(Debug, Deserialize)]
#[serde(tag = "command", rename_all = "snake_case", deny_unknown_fields)]
enum Command {
    Feed {
        now: u64,
        request: Request,
        stopped: bool,
        source_valid: bool,
        recovery_authorised: bool,
    },
    Sample {
        now: u64,
        feedback_healthy: bool,
    },
}
#[derive(Debug, Serialize)]
struct Response {
    output: Output,
}
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
    let mut guard = Guard::default();
    osr_runtime::run_lines(|c: Command| {
        let output = match c {
            Command::Feed {
                now,
                request,
                stopped,
                source_valid,
                recovery_authorised,
            } => {
                guard.feed(request, now, stopped, source_valid, recovery_authorised);
                guard.sample(now, true)
            }
            Command::Sample {
                now,
                feedback_healthy,
            } => guard.sample(now, feedback_healthy),
        };
        Ok(Response { output })
    })
}
