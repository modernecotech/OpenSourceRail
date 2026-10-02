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
    let mut host = osr_runtime::train::Host::new(
        osr_runtime::Channel::new(frozen, entity)?,
        Path::new(osr_runtime::required(&args, "--journal")?),
    )?;
    osr_runtime::run_lines(|command| host.handle(command))
}
