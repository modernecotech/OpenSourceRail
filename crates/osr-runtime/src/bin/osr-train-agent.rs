use std::{io, path::Path};
fn main() -> io::Result<()> {
    let args = osr_runtime::args()?;
    let frozen = osr_runtime::load(
        Path::new(osr_runtime::required(&args, "--model")?),
        Path::new(osr_runtime::required(&args, "--deployment")?),
    )?;
    let entity = osr_core::EntityId(
        osr_runtime::required(&args, "--entity")?
            .parse()
            .map_err(osr_runtime::bad)?,
    );
    let safety_channel = match osr_runtime::required(&args, "--safety-channel")? {
        "A" => osr_brake::dual::SafetyChannel::A,
        "B" => osr_brake::dual::SafetyChannel::B,
        _ => return Err(osr_runtime::bad("safety channel must be A or B")),
    };
    let mut host = osr_runtime::train::Host::with_safety_channel(
        osr_runtime::Channel::new(frozen, entity)?,
        Path::new(osr_runtime::required(&args, "--journal")?),
        safety_channel,
    )?;
    osr_runtime::run_lines(|command| host.handle(command))
}
