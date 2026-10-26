//! Wheel-supported, station-powered interface around the existing onboard ATP.
//!
//! This interface never grants motion authority or estimates adhesion. The ATP
//! still evaluates position, authority and a separately established brake profile.
//! Loss of a demanded station drive leaves wheel support intact and requests
//! independent friction braking. During the unpowered coast, departure drive
//! availability is not required; the ATP and receiving reservation still apply. These predicates are software contracts, not equipment qualification.
use crate::BrakeCommand;

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WheelStationInputs {
    pub selected_configuration: [u8; 32],
    pub observed_configuration: [u8; 32],
    pub authority_valid: bool,
    pub localisation_known: bool,
    pub train_integrity_known: bool,
    pub communications_fresh: bool,
    pub doors_locked: bool,
    pub brake_channels_healthy: bool,
    pub essential_supply_ready: bool,
    pub departure_drive_ready: bool,
    /// True only in the protected powered launch phase, not the unpowered coast.
    pub station_drive_required: bool,
    pub receiving_drive_ready: bool,
    pub receiving_berth_reserved: bool,
    pub independent_brake_profile_valid: bool,
    pub stopped: bool,
    pub parking_brake_proved: bool,
    pub wheel_slide_active: bool,
}
#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct WheelStationOutcome {
    pub launch_permissive: bool,
    pub mechanical_brake: BrakeCommand,
    pub station_thrust_inhibit: bool,
    pub support_power_required: bool,
    pub recovery_required_if_off_zone: bool,
}

#[must_use]
pub fn wheel_station_evaluate(i: &WheelStationInputs, atp: BrakeCommand) -> WheelStationOutcome {
    let independent_ready = i.selected_configuration == i.observed_configuration
        && i.authority_valid
        && i.localisation_known
        && i.train_integrity_known
        && i.communications_fresh
        && i.doors_locked
        && i.brake_channels_healthy
        && i.essential_supply_ready
        && i.independent_brake_profile_valid;
    let receiver_ready = i.receiving_drive_ready && i.receiving_berth_reserved;
    let demanded_drive_failed = i.station_drive_required && !i.departure_drive_ready;
    let mechanical_brake = if !independent_ready || !receiver_ready || demanded_drive_failed {
        BrakeCommand::Emergency
    } else if i.wheel_slide_active {
        // This demand must be modulated by qualified WSP; no invented adhesion.
        match atp {
            BrakeCommand::Emergency => atp,
            _ => BrakeCommand::Service(1000),
        }
    } else {
        atp
    };
    let launch = independent_ready
        && receiver_ready
        && i.departure_drive_ready
        && i.station_drive_required
        && i.stopped
        && i.parking_brake_proved
        && !i.wheel_slide_active
        && matches!(mechanical_brake, BrakeCommand::Release);
    WheelStationOutcome {
        launch_permissive: launch,
        station_thrust_inhibit: !independent_ready
            || !receiver_ready
            || !i.departure_drive_ready
            || !i.station_drive_required
            || (i.stopped && !launch)
            || !matches!(mechanical_brake, BrakeCommand::Release),
        mechanical_brake,
        support_power_required: false,
        recovery_required_if_off_zone: i.stopped,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn ready() -> WheelStationInputs {
        WheelStationInputs {
            selected_configuration: [1; 32],
            observed_configuration: [1; 32],
            authority_valid: true,
            localisation_known: true,
            train_integrity_known: true,
            communications_fresh: true,
            doors_locked: true,
            brake_channels_healthy: true,
            essential_supply_ready: true,
            departure_drive_ready: true,
            station_drive_required: true,
            receiving_drive_ready: true,
            receiving_berth_reserved: true,
            independent_brake_profile_valid: true,
            stopped: true,
            parking_brake_proved: true,
            wheel_slide_active: false,
        }
    }
    #[test]
    fn launch_requires_existing_atp_release_and_every_readiness_proof() {
        assert!(wheel_station_evaluate(&ready(), BrakeCommand::Release).launch_permissive);
        for brake in [BrakeCommand::Service(1), BrakeCommand::Emergency] {
            assert!(!wheel_station_evaluate(&ready(), brake).launch_permissive);
        }
    }
    #[test]
    fn independent_faults_stop_without_losing_wheel_support() {
        for fault in 0..11 {
            let mut i = ready();
            i.stopped = false;
            match fault {
                0 => i.observed_configuration = [2; 32],
                1 => i.authority_valid = false,
                2 => i.localisation_known = false,
                3 => i.train_integrity_known = false,
                4 => i.communications_fresh = false,
                5 => i.doors_locked = false,
                6 => i.brake_channels_healthy = false,
                7 => i.essential_supply_ready = false,
                8 => i.receiving_drive_ready = false,
                9 => i.receiving_berth_reserved = false,
                _ => i.independent_brake_profile_valid = false,
            }
            let o = wheel_station_evaluate(&i, BrakeCommand::Release);
            assert_eq!(o.mechanical_brake, BrakeCommand::Emergency);
            assert!(o.station_thrust_inhibit);
            assert!(!o.launch_permissive);
            assert!(!o.support_power_required);
        }
    }
    #[test]
    fn wheel_slide_does_not_cancel_atp_emergency() {
        let mut i = ready();
        i.wheel_slide_active = true;
        assert_eq!(
            wheel_station_evaluate(&i, BrakeCommand::Emergency).mechanical_brake,
            BrakeCommand::Emergency
        );
        assert_eq!(
            wheel_station_evaluate(&i, BrakeCommand::Release).mechanical_brake,
            BrakeCommand::Service(1000)
        );
    }
    #[test]
    fn stopped_train_needs_recovery_and_departure_power_proof() {
        let mut i = ready();
        i.departure_drive_ready = false;
        let o = wheel_station_evaluate(&i, BrakeCommand::Release);
        assert!(o.recovery_required_if_off_zone);
        assert!(!o.launch_permissive);
        assert!(o.station_thrust_inhibit);
        assert_eq!(o.mechanical_brake, BrakeCommand::Emergency);
    }
    #[test]
    fn failed_demanded_launch_uses_independent_brake_but_coast_does_not_require_drive() {
        let mut i = ready();
        i.stopped = false;
        i.departure_drive_ready = false;
        let powered = wheel_station_evaluate(&i, BrakeCommand::Release);
        assert_eq!(powered.mechanical_brake, BrakeCommand::Emergency);
        assert!(powered.station_thrust_inhibit);
        i.station_drive_required = false;
        let coast = wheel_station_evaluate(&i, BrakeCommand::Release);
        assert_eq!(coast.mechanical_brake, BrakeCommand::Release);
        assert!(coast.station_thrust_inhibit);
        assert!(!coast.launch_permissive);
        assert_eq!(
            wheel_station_evaluate(&i, BrakeCommand::Emergency).mechanical_brake,
            BrakeCommand::Emergency
        );
        i.receiving_drive_ready = false;
        assert_eq!(
            wheel_station_evaluate(&i, BrakeCommand::Release).mechanical_brake,
            BrakeCommand::Emergency
        );
    }
    #[test]
    fn station_thrust_stays_inhibited_without_departure_parking_proof() {
        let mut i = ready();
        i.parking_brake_proved = false;
        let o = wheel_station_evaluate(&i, BrakeCommand::Release);
        assert!(!o.launch_permissive);
        assert!(o.station_thrust_inhibit);
    }
}
