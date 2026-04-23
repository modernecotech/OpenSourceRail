//! Onboard trainset-image integrator.
//!
//! This crate aggregates the onboard stack — every crate that runs on
//! the T-ECU/S, T-ECU/A, and T-OBS host classes — into a single
//! versioned deployment unit. It does **no** orchestration itself: it
//! exposes each onboard evaluator through a stable re-export surface
//! so integrators (firmware builds, OTA update pipelines, the sim's
//! shadow stack) can depend on one crate instead of a dozen.
//!
//! # The `goa2-cab` feature flag (RFC 0015 §10.2)
//!
//! The default build is **GoA 4 (Unattended Train Operation)** per
//! [RFC 0015](../../docs/rfcs/0015-driverless-operation.md). The
//! trainset has no driver cab, no DMI, and no dead-man's handle. The
//! `goa2-cab` feature flag opts in to legacy cabbed deployments by
//! pulling in [`osr_dmi`] and [`osr_vigilance`]; without the flag,
//! those crates are not part of the image at all.
//!
//! The flag is additive (opting *in* to legacy features), not
//! subtractive, matching standard Cargo feature semantics.
//!
//! # What's always included
//!
//! The onboard safety chain and application layer that are present in
//! every deployment:
//!
//! - `osr-atp`              — SIL-4 Automatic Train Protection.
//! - `osr-ato`              — SIL-2 Automatic Train Operation (GoA 4 default).
//! - `osr-brake`            — SIL-4 EP brake controller.
//! - `osr-derailment`       — SIL-4 derailment monitor.
//! - `osr-door-control`     — SIL-4 door interlock.
//! - `osr-fire-safety`      — SIL-4 fire + suppression.
//! - `osr-obstacle-detect`  — SIL-4 obstacle detection (RFC 0015).
//! - `osr-odometry`         — SIL-4 position fusion.
//! - `osr-tcms`             — SIL-2 train-management rollup.
//!
//! # What's feature-gated under `goa2-cab`
//!
//! - `osr-dmi`              — driver touchscreen UI.
//! - `osr-vigilance`        — alerter / dead-man.
//!
//! These crates remain in the workspace (they compile on their own)
//! but are not linked into the default trainset image.

#![forbid(unsafe_code)]

pub use osr_ato as ato;
pub use osr_atp as atp;
pub use osr_brake as brake;
pub use osr_derailment as derailment;
pub use osr_door_control as door_control;
pub use osr_fire_safety as fire_safety;
pub use osr_obstacle_detect as obstacle_detect;
pub use osr_odometry as odometry;
pub use osr_tcms as tcms;

#[cfg(feature = "goa2-cab")]
pub use osr_dmi as dmi;

#[cfg(feature = "goa2-cab")]
pub use osr_vigilance as vigilance;

/// Compile-time descriptor of which cab profile was built.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CabProfile {
    /// GoA 4 default — no driver cab. This is what new deployments
    /// ship.
    Unattended,
    /// GoA 2 legacy — driver cab retained; `osr-dmi` + `osr-vigilance`
    /// are linked into the image.
    Cabbed,
}

/// The cab profile this image was compiled with.
#[must_use]
pub const fn cab_profile() -> CabProfile {
    #[cfg(feature = "goa2-cab")]
    {
        CabProfile::Cabbed
    }
    #[cfg(not(feature = "goa2-cab"))]
    {
        CabProfile::Unattended
    }
}

/// Human-readable banner the runtime prints at boot. Useful for
/// confirming which profile is active on a live unit.
#[must_use]
pub fn boot_banner() -> &'static str {
    match cab_profile() {
        CabProfile::Unattended => {
            "OSR trainset image — GoA 4 (Unattended, RFC 0015 default)"
        }
        CabProfile::Cabbed => {
            "OSR trainset image — GoA 2 legacy (goa2-cab feature enabled)"
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_build_is_unattended() {
        // Without the goa2-cab feature, the image must report
        // Unattended. This is the anchor test for the RFC 0015
        // "GoA 4 default" claim.
        #[cfg(not(feature = "goa2-cab"))]
        assert_eq!(cab_profile(), CabProfile::Unattended);
    }

    #[test]
    fn goa2_feature_build_is_cabbed() {
        #[cfg(feature = "goa2-cab")]
        assert_eq!(cab_profile(), CabProfile::Cabbed);
    }

    #[test]
    fn boot_banner_mentions_rfc_0015_in_default() {
        #[cfg(not(feature = "goa2-cab"))]
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
