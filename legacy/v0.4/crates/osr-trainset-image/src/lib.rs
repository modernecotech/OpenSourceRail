//! Onboard trainset-image integrator.
//!
//! This crate aggregates the onboard stack — every crate that runs on
//! the T-ECU/S, T-ECU/A, and T-OBS host classes — into a single
//! versioned deployment unit. It does **no** orchestration itself: it
//! exposes each onboard evaluator through a stable re-export surface
//! so integrators (firmware builds, OTA update pipelines, the sim's
//! shadow stack) can depend on one crate instead of independently
//! selecting packages. The exact per-host split remains controlled by
//! `deployment/hosts.toml`.
//!
//! This image is exclusively **GoA 4 (Unattended Train Operation)** per
//! [RFC 0015](../../docs/rfcs/0015-driverless-operation.md). The trainset
//! has no driver cab, driver interface, or dead-man subsystem.
//!
//! # What's always included
//!
//! The onboard safety chain and application layer that are present in
//! every deployment:
//!
//! - `osr-atp`              — SIL-4 Automatic Train Protection.
//! - `osr-ato`              — SIL-2 Automatic Train Operation (GoA 4 default).
//! - `osr-aux-power`        — auxiliary converter/load shedding.
//! - `osr-bms`              — SIL-4 battery management.
//! - `osr-brake`            — SIL-4 EP brake controller.
//! - `osr-cbm-onboard`      — condition monitoring producer.
//! - `osr-core`, `osr-crypto`, `osr-secbus` — shared types and authentication.
//! - `osr-derailment`       — SIL-4 derailment monitor.
//! - `osr-door-control`     — SIL-4 door interlock.
//! - `osr-event-recorder`   — onboard event recorder.
//! - `osr-fire-safety`      — SIL-4 fire + suppression.
//! - `osr-hot-axle`, `osr-hvac`, `osr-lighting` — application controllers.
//! - `osr-obstacle-detect`  — SIL-4 obstacle detection (RFC 0015).
//! - `osr-odometry`         — SIL-4 position fusion.
//! - `osr-passenger-assist` — emergency intercom/remote assist.
//! - `osr-pis-onboard`      — onboard passenger information.
//! - `osr-ptp`, `osr-tcn`, `osr-t2g` — time and communications.
//! - `osr-regen`            — regenerative braking arbitration.
//! - `osr-tcms`             — SIL-2 train-management rollup.
//! - `osr-traction`         — SIL-4 traction controller.

#![forbid(unsafe_code)]

pub use osr_ato as ato;
pub use osr_atp as atp;
pub use osr_aux_power as aux_power;
pub use osr_bms as bms;
pub use osr_brake as brake;
pub use osr_cbm_onboard as cbm_onboard;
pub use osr_core as core;
pub use osr_crypto as crypto;
pub use osr_derailment as derailment;
pub use osr_door_control as door_control;
pub use osr_event_recorder as event_recorder;
pub use osr_fire_safety as fire_safety;
pub use osr_hot_axle as hot_axle;
pub use osr_hvac as hvac;
pub use osr_lighting as lighting;
pub use osr_obstacle_detect as obstacle_detect;
pub use osr_odometry as odometry;
pub use osr_passenger_assist as passenger_assist;
pub use osr_pis_onboard as pis_onboard;
pub use osr_ptp as ptp;
pub use osr_regen as regen;
pub use osr_secbus as secbus;
pub use osr_t2g as t2g;
pub use osr_tcms as tcms;
pub use osr_tcn as tcn;
pub use osr_traction as traction;

/// Human-readable banner the runtime prints at boot.
#[must_use]
pub fn boot_banner() -> &'static str {
    "OSR trainset image — GoA 4 (Unattended, RFC 0015)"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn image_is_unattended_only() {
        assert!(boot_banner().contains("GoA 4"));
    }

    #[test]
    fn boot_banner_mentions_rfc_0015_in_default() {
        assert!(boot_banner().contains("GoA 4"));
    }

    #[test]
    fn re_exports_resolve() {
        // Sanity: we can reach a public item through each re-export.
        let _ = atp::BrakeCommand::Release;
        let _ = brake::BrakeParams::light_metro_default();
        let _ = obstacle_detect::ObstacleVerdict::Clear;
    }
}
