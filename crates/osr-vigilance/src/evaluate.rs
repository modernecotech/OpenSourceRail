//! Vigilance evaluator — the single pure entry point.

use crate::inputs::{VigilanceInputs, VigilanceParams};
use crate::output::{VigilanceOutput, VigilanceState};

/// Evaluate one vigilance tick.
///
/// Pure function of `(prev, inputs, params)`. See crate docs for the
/// state-machine definition and the V1–V6 safety properties.
#[must_use]
pub fn vigilance_evaluate(
    prev: &VigilanceOutput,
    inputs: &VigilanceInputs,
    params: &VigilanceParams,
) -> VigilanceOutput {
    // --- Suppression (V2) ------------------------------------------------
    let suppressed = inputs.speed_mmps.unsigned_abs() < params.enable_speed_mmps;
    if suppressed {
        // Preserve the ack timestamp across suppression so that the
        // moment we re-enable, the elapsed-since-ack clock is accurate.
        // However, if the driver acks during suppression, update
        // `last_ack_ns` so leaving suppression finds a fresh ack.
        let last_ack_ns = if inputs.ack_received_this_tick {
            inputs.now_ns
        } else {
            prev.last_ack_ns
        };
        return VigilanceOutput {
            state: VigilanceState::Suppressed,
            emergency_requested: false,
            last_ack_ns,
            time_since_ack_ms: elapsed_ms(inputs.now_ns, last_ack_ns),
            time_to_warning_ms: None,
            time_to_trip_ms: None,
        };
    }

    // --- Trip latch (V6) -------------------------------------------------
    if prev.state == VigilanceState::Tripped {
        // Once tripped, stay tripped until the train drops below the
        // suppression threshold (reset is a separate cab procedure).
        return VigilanceOutput {
            state: VigilanceState::Tripped,
            emergency_requested: true,
            last_ack_ns: prev.last_ack_ns,
            time_since_ack_ms: elapsed_ms(inputs.now_ns, prev.last_ack_ns),
            time_to_warning_ms: None,
            time_to_trip_ms: None,
        };
    }

    // --- Ack handling ----------------------------------------------------
    // An ack updates last_ack_ns and collapses state to Nominal (V5).
    // (Tripped already handled above.)
    let last_ack_ns = if inputs.ack_received_this_tick {
        inputs.now_ns
    } else if prev.state == VigilanceState::Suppressed {
        // Emerging from suppression: treat the enable-transition as
        // an implicit ack so we don't spuriously fire Warning on the
        // first tick at speed. Realistic — a train leaving a platform
        // has just had a driver/ATO departure action.
        inputs.now_ns
    } else {
        prev.last_ack_ns
    };

    let elapsed_ms = elapsed_ms(inputs.now_ns, last_ack_ns);

    let ack_interval_ms = u64::from(params.ack_interval_ms);
    let warning_ms = u64::from(params.warning_ms);

    let (state, time_to_warning_ms, time_to_trip_ms) =
        if elapsed_ms < ack_interval_ms {
            (
                VigilanceState::Nominal,
                Some((ack_interval_ms - elapsed_ms) as u32),
                Some((ack_interval_ms + warning_ms - elapsed_ms) as u32),
            )
        } else if elapsed_ms < ack_interval_ms + warning_ms {
            (
                VigilanceState::Warning,
                None,
                Some((ack_interval_ms + warning_ms - elapsed_ms) as u32),
            )
        } else {
            (VigilanceState::Tripped, None, None)
        };

    VigilanceOutput {
        state,
        emergency_requested: matches!(state, VigilanceState::Tripped),
        last_ack_ns,
        time_since_ack_ms: elapsed_ms,
        time_to_warning_ms,
        time_to_trip_ms,
    }
}

fn elapsed_ms(now_ns: u64, ack_ns: u64) -> u64 {
    now_ns.saturating_sub(ack_ns) / 1_000_000
}

#[cfg(test)]
mod tests {
    use super::*;

    fn at_speed(now_ns: u64, ack: bool) -> VigilanceInputs {
        VigilanceInputs {
            now_ns,
            speed_mmps: 10_000, // 10 m/s — above enable threshold
            ack_received_this_tick: ack,
        }
    }

    fn stationary(now_ns: u64, ack: bool) -> VigilanceInputs {
        VigilanceInputs {
            now_ns,
            speed_mmps: 100, // well below default 1000 mm/s
            ack_received_this_tick: ack,
        }
    }

    #[test]
    fn suppressed_when_stationary() {
        let p = VigilanceParams::light_metro_default();
        let prev = VigilanceOutput::default();
        let out = vigilance_evaluate(&prev, &stationary(5 * 60_000_000_000, false), &p);
        assert_eq!(out.state, VigilanceState::Suppressed);
        assert!(!out.emergency_requested);
    }

    #[test]
    fn nominal_on_first_tick_above_threshold() {
        let p = VigilanceParams::light_metro_default();
        let prev = VigilanceOutput::default();
        let out = vigilance_evaluate(&prev, &at_speed(1_000_000_000, false), &p);
        assert_eq!(out.state, VigilanceState::Nominal);
    }

    #[test]
    fn warning_after_ack_interval() {
        let p = VigilanceParams::light_metro_default(); // 30s ack interval
        let mut prev = VigilanceOutput::default();
        // First tick at speed — treated as implicit ack.
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        assert_eq!(prev.state, VigilanceState::Nominal);

        // Jump forward 31 s with no ack.
        let out = vigilance_evaluate(&prev, &at_speed(31_000_000_000, false), &p);
        assert_eq!(out.state, VigilanceState::Warning);
        assert!(!out.emergency_requested);
    }

    #[test]
    fn tripped_after_warning_window() {
        let p = VigilanceParams::light_metro_default();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        // 30s + 5s + 1ms: should be Tripped.
        let out = vigilance_evaluate(&prev, &at_speed(35_001_000_000, false), &p);
        assert_eq!(out.state, VigilanceState::Tripped);
        assert!(out.emergency_requested);
    }

    #[test]
    fn ack_in_warning_returns_to_nominal() {
        let p = VigilanceParams::light_metro_default();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        prev = vigilance_evaluate(&prev, &at_speed(31_000_000_000, false), &p);
        assert_eq!(prev.state, VigilanceState::Warning);
        let out = vigilance_evaluate(&prev, &at_speed(32_000_000_000, true), &p);
        assert_eq!(out.state, VigilanceState::Nominal);
    }

    #[test]
    fn ack_does_not_clear_tripped() {
        let p = VigilanceParams::light_metro_default();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        prev = vigilance_evaluate(&prev, &at_speed(40_000_000_000, false), &p);
        assert_eq!(prev.state, VigilanceState::Tripped);
        // Ack while tripped → stays tripped.
        let out = vigilance_evaluate(&prev, &at_speed(41_000_000_000, true), &p);
        assert_eq!(out.state, VigilanceState::Tripped);
        assert!(out.emergency_requested);
    }

    #[test]
    fn dropping_below_threshold_suppresses_even_if_tripped() {
        // Rationale: once the train is physically at rest (brought
        // down by the emergency application), vigilance suppresses;
        // the trip is cleared by the cab reset procedure.
        let p = VigilanceParams::light_metro_default();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        prev = vigilance_evaluate(&prev, &at_speed(40_000_000_000, false), &p);
        assert_eq!(prev.state, VigilanceState::Tripped);
        // Speed drops to 0.
        let out = vigilance_evaluate(&prev, &stationary(41_000_000_000, false), &p);
        assert_eq!(out.state, VigilanceState::Suppressed);
        assert!(!out.emergency_requested);
    }

    #[test]
    fn determinism() {
        let p = VigilanceParams::light_metro_default();
        let prev = VigilanceOutput::default();
        let inputs = at_speed(5_000_000_000, false);
        let a = vigilance_evaluate(&prev, &inputs, &p);
        let b = vigilance_evaluate(&prev, &inputs, &p);
        assert_eq!(a, b);
    }

    #[test]
    fn time_to_warning_counts_down() {
        let p = VigilanceParams::light_metro_default();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &at_speed(0, false), &p);
        assert_eq!(prev.time_to_warning_ms, Some(30_000));
        let out = vigilance_evaluate(&prev, &at_speed(10_000_000_000, false), &p);
        assert_eq!(out.time_to_warning_ms, Some(20_000));
    }
}
