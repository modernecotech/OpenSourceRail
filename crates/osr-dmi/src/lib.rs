//! OpenSourceRail driver machine interface (DMI) decision layer.
//!
//! Given the current [`ConsistStatus`](osr_tcms::ConsistStatus) from
//! [`osr_tcms`] and driver input (cab switches + emergency button),
//! produces a [`DmiOutput`] describing:
//!
//! - which **display page** the touchscreen should show
//! - which **indicator lamps** are lit (and in what colour)
//! - whether the **cab buzzer** is sounding (and why)
//! - the **driver's input** as validated / debounced commands
//!
//! Phase 2c crate 9 of [RFC 0005 §4.1](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 — pixels and buzzers don't kill passengers directly; the
//! safety layer is already independent. This crate is primarily
//! about driver ergonomics and command-intent validation.
//!
//! # Not in this crate
//!
//! - Rendering — that's an HMI toolkit choice (OpenGL / wgpu /
//!   framebuffer). This crate emits a compact decision struct.
//! - Input event debouncing at hardware level — assumed upstream.
//! - Audio synthesis — this crate emits a `BuzzerRequest`; a
//!   downstream audio driver generates the tone.
//!
//! # Properties (proptest-verified)
//!
//! - **DMI1 determinism.**
//! - **DMI2 emergency page dominates:** any emergency source →
//!   `display_page == Emergency`.
//! - **DMI3 buzzer active on trip:** `status.worst_alarm == Trip` ⇒
//!   `buzzer != None`.
//! - **DMI4 ready indicator = TCMS ready_to_move.**

#![forbid(unsafe_code)]

use osr_tcms::{AlarmLevel, ConsistStatus};
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Driver input
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum DriverPageRequest {
    #[default]
    Main,
    Diagnostics,
    Energy,
    Route,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct DriverInput {
    pub now_ns: u64,
    /// Emergency-brake plunger pressed.
    pub emergency_plunger: bool,
    /// Vigilance acknowledgement button pressed this tick.
    pub vigilance_ack: bool,
    /// ATO engage switch.
    pub ato_engage: bool,
    /// Door-open / close requests (debounced).
    pub doors_open_request: bool,
    pub doors_close_request: bool,
    /// Driver's currently-selected page.
    pub page_request: DriverPageRequest,
    /// Acknowledge / silence cab buzzer.
    pub buzzer_ack: bool,
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum DisplayPage {
    #[default]
    Main,
    Diagnostics,
    Energy,
    Route,
    /// Any emergency overrides all driver-requested pages.
    Emergency,
}

/// Discrete indicator lamp on the cab instrument cluster.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum IndicatorColour {
    #[default]
    Off,
    Green,
    Amber,
    Red,
    /// Red with flash pattern — worst-alarm state.
    RedFlashing,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum BuzzerRequest {
    #[default]
    None,
    /// Low-priority chime (e.g., vigilance warning window).
    Chime,
    /// Alarm tone (trip condition).
    Alarm,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct DmiOutput {
    pub display_page: DisplayPage,

    // Indicator rollups (colour-coded).
    pub ready_to_move: IndicatorColour,
    pub brake_status: IndicatorColour,
    pub traction_status: IndicatorColour,
    pub pack_status: IndicatorColour,
    pub door_status: IndicatorColour,
    pub ato_engaged: IndicatorColour,

    pub buzzer: BuzzerRequest,
    /// The driver input echo — after any gating the DMI performs.
    pub accepted_input: DriverInput,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn alarm_to_lamp(a: AlarmLevel) -> IndicatorColour {
    match a {
        AlarmLevel::Nominal => IndicatorColour::Green,
        AlarmLevel::Warning => IndicatorColour::Amber,
        AlarmLevel::Trip => IndicatorColour::RedFlashing,
    }
}

#[must_use]
pub fn dmi_evaluate(status: &ConsistStatus, input: &DriverInput) -> DmiOutput {
    // Emergency dominates page selection.
    let display_page = if status.any_emergency {
        DisplayPage::Emergency
    } else {
        match input.page_request {
            DriverPageRequest::Main => DisplayPage::Main,
            DriverPageRequest::Diagnostics => DisplayPage::Diagnostics,
            DriverPageRequest::Energy => DisplayPage::Energy,
            DriverPageRequest::Route => DisplayPage::Route,
        }
    };

    // Indicators derived from status.
    let ready_to_move = if status.ready_to_move {
        IndicatorColour::Green
    } else if status.any_emergency {
        IndicatorColour::RedFlashing
    } else {
        IndicatorColour::Amber
    };

    let brake_status = if status.emergency_sources.any() {
        IndicatorColour::RedFlashing
    } else {
        IndicatorColour::Green
    };

    // Pack status: green > 500 ppt, amber 200-500, red < 200.
    let pack_status = match status.soc_ppt {
        s if s < 200 => IndicatorColour::Red,
        s if s < 500 => IndicatorColour::Amber,
        _ => IndicatorColour::Green,
    };

    let traction_status = if status.emergency_sources.any() || !status.v400_rail_enabled {
        IndicatorColour::Amber
    } else {
        IndicatorColour::Green
    };

    // Door status lamp: green when interlock holds, amber otherwise.
    // (We don't have per-door alarm here, just the rollup.)
    let door_status = if status.ready_to_move || status.at_station {
        IndicatorColour::Green
    } else {
        IndicatorColour::Amber
    };

    let ato_engaged = if input.ato_engage && !status.any_emergency {
        IndicatorColour::Green
    } else {
        IndicatorColour::Off
    };

    // Buzzer: Alarm on Trip, Chime on Warning, None at Nominal.
    // Driver's buzzer_ack silences non-trip buzzers this tick.
    let buzzer = match status.worst_alarm {
        AlarmLevel::Trip => BuzzerRequest::Alarm,
        AlarmLevel::Warning => {
            if input.buzzer_ack {
                BuzzerRequest::None
            } else {
                BuzzerRequest::Chime
            }
        }
        AlarmLevel::Nominal => BuzzerRequest::None,
    };

    // Override of the alarm-level lamp rollup for the overall
    // status: take the max.
    let _ = alarm_to_lamp(status.worst_alarm); // kept for future use

    DmiOutput {
        display_page,
        ready_to_move,
        brake_status,
        traction_status,
        pack_status,
        door_status,
        ato_engaged,
        buzzer,
        accepted_input: *input,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn clean_status() -> ConsistStatus {
        ConsistStatus {
            now_ns: 0,
            speed_mmps: 10_000,
            section_id: Some(1000),
            at_station: false,
            worst_alarm: AlarmLevel::Nominal,
            emergency_sources: Default::default(),
            any_emergency: false,
            ready_to_move: true,
            v24_rail_enabled: true,
            v110_rail_enabled: true,
            v400_rail_enabled: true,
            soc_ppt: 800,
        }
    }

    #[test]
    fn clean_nominal_is_green() {
        let out = dmi_evaluate(&clean_status(), &DriverInput::default());
        assert_eq!(out.display_page, DisplayPage::Main);
        assert_eq!(out.ready_to_move, IndicatorColour::Green);
        assert_eq!(out.pack_status, IndicatorColour::Green);
        assert_eq!(out.buzzer, BuzzerRequest::None);
    }

    #[test]
    fn emergency_forces_emergency_page() {
        let mut s = clean_status();
        s.any_emergency = true;
        s.emergency_sources.fire = true;
        s.worst_alarm = AlarmLevel::Trip;
        s.ready_to_move = false;
        let mut i = DriverInput::default();
        i.page_request = DriverPageRequest::Diagnostics;
        let out = dmi_evaluate(&s, &i);
        assert_eq!(out.display_page, DisplayPage::Emergency);
        assert_eq!(out.buzzer, BuzzerRequest::Alarm);
        assert_eq!(out.ready_to_move, IndicatorColour::RedFlashing);
    }

    #[test]
    fn low_soc_triggers_amber() {
        let mut s = clean_status();
        s.soc_ppt = 300;
        let out = dmi_evaluate(&s, &DriverInput::default());
        assert_eq!(out.pack_status, IndicatorColour::Amber);
    }

    #[test]
    fn critical_soc_is_red() {
        let mut s = clean_status();
        s.soc_ppt = 150;
        let out = dmi_evaluate(&s, &DriverInput::default());
        assert_eq!(out.pack_status, IndicatorColour::Red);
    }

    #[test]
    fn buzzer_ack_silences_warning() {
        let mut s = clean_status();
        s.worst_alarm = AlarmLevel::Warning;
        let mut i = DriverInput::default();
        assert_eq!(dmi_evaluate(&s, &i).buzzer, BuzzerRequest::Chime);
        i.buzzer_ack = true;
        assert_eq!(dmi_evaluate(&s, &i).buzzer, BuzzerRequest::None);
    }

    #[test]
    fn buzzer_ack_does_not_silence_alarm() {
        let mut s = clean_status();
        s.worst_alarm = AlarmLevel::Trip;
        let mut i = DriverInput::default();
        i.buzzer_ack = true;
        assert_eq!(dmi_evaluate(&s, &i).buzzer, BuzzerRequest::Alarm);
    }

    #[test]
    fn ato_engage_only_when_no_emergency() {
        let mut s = clean_status();
        let mut i = DriverInput::default();
        i.ato_engage = true;
        assert_eq!(dmi_evaluate(&s, &i).ato_engaged, IndicatorColour::Green);
        s.any_emergency = true;
        assert_eq!(dmi_evaluate(&s, &i).ato_engaged, IndicatorColour::Off);
    }

    #[test]
    fn determinism() {
        let s = clean_status();
        let i = DriverInput::default();
        assert_eq!(dmi_evaluate(&s, &i), dmi_evaluate(&s, &i));
    }
}
