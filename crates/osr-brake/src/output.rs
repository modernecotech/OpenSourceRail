//! Brake controller outputs: actuator setpoints for friction, regen,
//! traction cut, and the parking brake, plus diagnostic state.

use osr_atp::BrakeCommand;
use serde::{Deserialize, Serialize};

/// Which emergency sources were active in the evaluation that
/// produced this output. Purely diagnostic; the safety-relevant
/// information is already encoded in `command == Emergency`.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct EmergencySources {
    pub atp: bool,
    pub vigilance: bool,
    pub fire: bool,
    pub derailment: bool,
    pub driver: bool,
}

impl EmergencySources {
    #[must_use]
    pub fn any(&self) -> bool {
        self.atp || self.vigilance || self.fire || self.derailment || self.driver
    }

    #[must_use]
    pub fn count(&self) -> u8 {
        u8::from(self.atp)
            + u8::from(self.vigilance)
            + u8::from(self.fire)
            + u8::from(self.derailment)
            + u8::from(self.driver)
    }
}

/// Full output of one brake evaluation tick.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BrakeOutput {
    /// Echo of the effective command that drove this output. Always
    /// a total of the inputs: `Emergency` if any source tripped;
    /// otherwise the ATP command.
    pub command: BrakeCommand,

    /// Friction-brake effort to apply, 0..=1000 ppt of full service
    /// capability. Emergency commands drive this to
    /// `min_friction_emergency_ppt`. WSP modulation subtracts from
    /// this value; it never adds.
    pub friction_effort_ppt: u16,

    /// Regen-torque request to the traction converter, 0..=1000 ppt.
    /// Clamped to `regen_available_ppt`. In emergency, regen is
    /// requested at full availability but not relied upon.
    pub regen_request_ppt: u16,

    /// When `true`, traction motor power is disabled. Asserted
    /// whenever the command is not `Release`.
    pub traction_cut: bool,

    /// Parking-brake engagement. Asserted iff park was requested
    /// *and* speed is below `park_brake_max_speed_mmps`.
    pub parking_brake_engaged: bool,

    /// WSP modulation is currently active. Diagnostic.
    pub wsp_active: bool,

    /// Which emergency source(s) drove this output.
    pub emergency_sources: EmergencySources,

    /// The friction effort that would have been commanded *before*
    /// WSP modulation. B4 is verified against this field:
    /// `friction_effort_ppt <= friction_command_before_wsp_ppt`
    /// must hold on every call.
    pub friction_command_before_wsp_ppt: u16,
}

impl BrakeOutput {
    #[must_use]
    pub fn is_emergency(&self) -> bool {
        matches!(self.command, BrakeCommand::Emergency)
    }
    #[must_use]
    pub fn is_release(&self) -> bool {
        matches!(self.command, BrakeCommand::Release)
    }
    #[must_use]
    pub fn is_service(&self) -> bool {
        matches!(self.command, BrakeCommand::Service(_))
    }
}
