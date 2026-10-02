//! Paired-only synthetic output port. Real autonomous clocks/outputs need HIL.
use osr_brake::dual::{DualGuard, DualOutput, PairFeed};
use serde::{Deserialize, Serialize};
use std::io;
#[derive(Debug, Deserialize)]
#[serde(tag = "command", rename_all = "snake_case", deny_unknown_fields)]
enum Command {
    FeedPair {
        now: u64,
        pair: PairFeed,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    },
    Sample {
        now: u64,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    },
}
#[derive(Debug, Serialize)]
struct Response {
    pair: DualOutput,
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
    let mut guard = DualGuard::default();
    osr_runtime::run_lines(|c: Command| {
        let pair = match c {
            Command::FeedPair {
                now,
                pair,
                feedback_a_healthy,
                feedback_b_healthy,
            } => guard.feed(now, pair, feedback_a_healthy, feedback_b_healthy),
            Command::Sample {
                now,
                feedback_a_healthy,
                feedback_b_healthy,
            } => guard.sample(now, feedback_a_healthy, feedback_b_healthy),
        };
        Ok(Response { pair })
    })
}
