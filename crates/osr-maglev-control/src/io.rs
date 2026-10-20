//! SBC host boundary. Implementations acquire frames and record study outputs;
//! this interface supplies no PWM/current API or physical enable capability.
use crate::array::{evaluate_array, ArrayOutput, ArrayParams, ArrayState, Frame};

pub trait StudyIo {
    type Error;
    fn acquire(&mut self) -> Result<(u64, Frame), Self::Error>;
    fn record(&mut self, output: &ArrayOutput) -> Result<(), Self::Error>;
}

/// State advances only when the caller receives a successful record operation.
/// A transport failure must be handled by the host's engineered protection path;
/// this study boundary cannot maintain suspension after a host/I/O failure.
pub fn host_tick<I: StudyIo>(
    io: &mut I,
    state: ArrayState,
    params: &ArrayParams,
) -> Result<ArrayOutput, I::Error> {
    let (now_ns, frame) = io.acquire()?;
    let output = evaluate_array(state, &frame, now_ns, params);
    io.record(&output)?;
    Ok(output)
}

/// Single-frame offline adapter suitable for deterministic replay; no device access.
#[derive(Debug, Clone, Copy)]
pub struct ReplayIo {
    pub now_ns: u64,
    pub frame: Frame,
    pub last_recorded: Option<ArrayOutput>,
}
impl StudyIo for ReplayIo {
    type Error = core::convert::Infallible;
    fn acquire(&mut self) -> Result<(u64, Frame), Self::Error> {
        Ok((self.now_ns, self.frame))
    }
    fn record(&mut self, output: &ArrayOutput) -> Result<(), Self::Error> {
        self.last_recorded = Some(*output);
        Ok(())
    }
}
