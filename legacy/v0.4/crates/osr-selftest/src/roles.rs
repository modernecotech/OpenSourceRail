//! Per-role check suites.
//!
//! Each role has a small, focused set of functional checks that
//! exercise the evaluators + primitives the role actually runs.
//! A pass means the bolted-together unit reproduces known-good
//! outputs for known-good inputs across every crate in its
//! deployed set.
//!
//! The checks run on the SoC doing the deployment job (not on a
//! separate test rig). They don't touch hardware peripherals
//! (relays, sensors, trust anchors) directly — per-sensor
//! hardware checks belong in the host-class-specific assembly
//! runbook under `control-electronics/<class>/diy-assembly/`. This module
//! validates that the *software* this unit is running is
//! identical to the workspace the deployment expects.

use crate::runtime::{Check, Outcome};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    TEcuS,
    TEcuA,
    TObs,
    WSbc,
    SSbc,
}

impl Role {
    pub fn from_cli(s: &str) -> Option<Self> {
        match s {
            "t-ecu-s" => Some(Role::TEcuS),
            "t-ecu-a" => Some(Role::TEcuA),
            "t-obs" => Some(Role::TObs),
            "w-sbc" => Some(Role::WSbc),
            "s-sbc" => Some(Role::SSbc),
            _ => None,
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Role::TEcuS => "t-ecu-s",
            Role::TEcuA => "t-ecu-a",
            Role::TObs => "t-obs",
            Role::WSbc => "w-sbc",
            Role::SSbc => "s-sbc",
        }
    }

    pub fn checks(self) -> Vec<Check> {
        match self {
            Role::TEcuS => t_ecu_s(),
            Role::TEcuA => t_ecu_a(),
            Role::TObs => t_obs(),
            Role::WSbc => w_sbc(),
            Role::SSbc => s_sbc(),
        }
    }
}

// ---------------------------------------------------------------------------
// T-ECU/S — onboard safety kernel
// ---------------------------------------------------------------------------

fn t_ecu_s() -> Vec<Check> {
    vec![
        Check {
            name: "osr-brake evaluator floors friction on ATP emergency",
            run: check_brake_emergency,
        },
        Check {
            name: "osr-brake evaluator releases on clean input",
            run: check_brake_release,
        },
        Check {
            name: "osr-brake propagates every non-ATP emergency source",
            run: check_brake_emergency_sources,
        },
        Check {
            name: "osr-interlocking: intrusion verdict 'Present' withholds MA (RFC 0016 gate d)",
            run: check_interlocking_intrusion_gate,
        },
        Check {
            name: "osr-secbus verifies signature roundtrip",
            run: check_secbus_roundtrip,
        },
        Check {
            name: "osr-crypto HMAC-SHA256 stable",
            run: check_hmac_stable,
        },
    ]
}

fn check_brake_emergency_sources() -> Outcome {
    use osr_atp::BrakeCommand;
    use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};

    let base = BrakeInputs {
        atp_command: BrakeCommand::Release,
        fire_emergency: false,
        derailment_emergency: false,
        remote_assist_emergency: false,
        obstacle_emergency: false,
        park_requested: false,
        measured_speed_mmps: 15_000,
        wheel_speed_mmps: 15_000,
        regen_available_ppt: 500,
        now_ns: 1_000_000_000,
    };
    let params = BrakeParams::light_metro_default();

    type EmergencySetter = fn(&mut BrakeInputs);
    let cases: [(&str, EmergencySetter); 4] = [
        ("fire", |i| i.fire_emergency = true),
        ("derailment", |i| i.derailment_emergency = true),
        ("remote-assist", |i| i.remote_assist_emergency = true),
        ("obstacle", |i| i.obstacle_emergency = true),
    ];
    for (name, set) in cases {
        let mut inputs = base.clone();
        set(&mut inputs);
        let out = brake_evaluate(&inputs, &params);
        if !out.is_emergency() {
            return Outcome::fail(format!(
                "brake did not latch Emergency for source '{name}'. \
                 Remediation: rebuild osr-brake from the tagged workspace commit."
            ));
        }
    }
    Outcome::pass()
}

fn check_interlocking_intrusion_gate() -> Outcome {
    use osr_core::{EntityId, SectionId, TrainId};
    use osr_interlocking::{section_available_to, DerivedState, IntrusionState, SectionIntrusion};

    let section = SectionId::new(1001);
    let train = TrainId::new(7);
    let mut state = DerivedState::default();
    state.section_intrusions.insert(
        section,
        SectionIntrusion {
            section,
            state: IntrusionState::Present,
            issued_by: EntityId::new(99),
            observed_at_ns: 0,
        },
    );
    if section_available_to(train, section, &state) {
        Outcome::fail(
            "intrusion 'Present' did not withhold MA — RFC 0016 gate (d) \
             inactive in this binary. Remediation: rebuild osr-interlocking \
             from the tagged workspace commit.",
        )
    } else {
        Outcome::pass()
    }
}

fn check_brake_emergency() -> Outcome {
    use osr_atp::BrakeCommand;
    use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};

    let inputs = BrakeInputs {
        atp_command: BrakeCommand::Emergency,
        fire_emergency: false,
        derailment_emergency: false,
        remote_assist_emergency: false,
        obstacle_emergency: false,
        park_requested: false,
        measured_speed_mmps: 15_000,
        wheel_speed_mmps: 15_000,
        regen_available_ppt: 500,
        now_ns: 1_000_000_000,
    };
    let params = BrakeParams::light_metro_default();
    let out = brake_evaluate(&inputs, &params);
    if out.is_emergency() && out.friction_effort_ppt >= 600 {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "Brake emergency did not floor friction; got \
             is_emergency={} friction_effort_ppt={}. \
             Remediation: verify osr-brake is built with \
             BrakeParams::light_metro_default.",
            out.is_emergency(),
            out.friction_effort_ppt
        ))
    }
}

fn check_brake_release() -> Outcome {
    use osr_atp::BrakeCommand;
    use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};

    let inputs = BrakeInputs {
        atp_command: BrakeCommand::Release,
        fire_emergency: false,
        derailment_emergency: false,
        remote_assist_emergency: false,
        obstacle_emergency: false,
        park_requested: false,
        measured_speed_mmps: 15_000,
        wheel_speed_mmps: 15_000,
        regen_available_ppt: 500,
        now_ns: 1_000_000_000,
    };
    let out = brake_evaluate(&inputs, &BrakeParams::light_metro_default());
    if out.is_release() {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "Brake clean-input expected Release; got {:?}",
            out.command
        ))
    }
}

fn check_secbus_roundtrip() -> Outcome {
    use osr_core::EntityId;
    use osr_crypto::ed25519_generate;
    use osr_secbus::{sign_bytes, verify_signed, KeyRegistry};

    let sk = ed25519_generate();
    let issuer = EntityId::new(42);
    let mut registry = KeyRegistry::new();
    registry.insert(issuer, sk.public());
    let envelope = sign_bytes(issuer, b"selftest payload".to_vec(), &sk);
    match verify_signed(&registry, &envelope) {
        Ok(payload) if payload == b"selftest payload" => Outcome::pass(),
        Ok(_) => Outcome::fail("secbus roundtrip returned wrong payload"),
        Err(e) => Outcome::fail(format!("secbus verify rejected valid sig: {e:?}")),
    }
}

fn check_hmac_stable() -> Outcome {
    use osr_crypto::{hmac_sha256, Hmac256Key};
    let k = Hmac256Key::from_bytes(b"selftest".to_vec());
    let a = hmac_sha256(&k, b"message");
    let b = hmac_sha256(&k, b"message");
    if a == b {
        Outcome::pass()
    } else {
        Outcome::fail("HMAC-SHA256 not deterministic")
    }
}

// ---------------------------------------------------------------------------
// T-ECU/A — onboard application tier
// ---------------------------------------------------------------------------

fn t_ecu_a() -> Vec<Check> {
    vec![
        Check {
            name: "osr-secbus verify roundtrip",
            run: check_secbus_roundtrip,
        },
        Check {
            name: "osr-crypto HMAC stable",
            run: check_hmac_stable,
        },
    ]
}

// ---------------------------------------------------------------------------
// T-OBS — onboard obstacle detection (RFC 0015)
// ---------------------------------------------------------------------------

fn t_obs() -> Vec<Check> {
    vec![
        Check {
            name: "osr-obstacle-detect: clear frame at rest → Clear",
            run: check_obstacle_clear,
        },
        Check {
            name: "osr-obstacle-detect: ultrasonic echo → EmergencyBrake (O1)",
            run: check_obstacle_ultrasonic_return,
        },
        Check {
            name: "osr-obstacle-detect: peer disagreement → EmergencyBrake (O3)",
            run: check_obstacle_peer_disagreement,
        },
        Check {
            name: "osr-obstacle-detect: LIDAR offline → RestrictedSpeed (O4b)",
            run: check_obstacle_lidar_offline,
        },
        Check {
            name: "osr-secbus verify roundtrip",
            run: check_secbus_roundtrip,
        },
    ]
}

fn check_obstacle_clear() -> Outcome {
    use osr_obstacle_detect::{evaluate, ObstacleVerdict, SensorFrame};
    let frame = SensorFrame::clear();
    let out = evaluate(&frame, 0, 100_000, true);
    if out.verdict == ObstacleVerdict::Clear {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "clear frame at rest expected Clear; got {:?}",
            out.verdict
        ))
    }
}

fn check_obstacle_ultrasonic_return() -> Outcome {
    use osr_obstacle_detect::{evaluate, ObstacleVerdict, SensorFrame};
    let mut frame = SensorFrame::clear();
    frame.ultrasonic[0].nearest_mm = Some(5_000);
    let out = evaluate(&frame, 0, 100_000, true);
    if out.verdict == ObstacleVerdict::EmergencyBrake {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "ultrasonic echo expected EmergencyBrake (O1); got {:?}",
            out.verdict
        ))
    }
}

fn check_obstacle_peer_disagreement() -> Outcome {
    use osr_obstacle_detect::{evaluate, ObstacleVerdict, SensorFrame};
    let frame = SensorFrame::clear();
    let out = evaluate(&frame, 0, 100_000, /* peer_clear = */ false);
    if out.verdict == ObstacleVerdict::EmergencyBrake {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "peer disagreement expected EmergencyBrake (O3); got {:?}",
            out.verdict
        ))
    }
}

fn check_obstacle_lidar_offline() -> Outcome {
    use osr_obstacle_detect::{evaluate, ObstacleVerdict, SensorFrame};
    let mut frame = SensorFrame::clear();
    frame.lidar_offline = true;
    // Radar healthy by default in clear() — so we expect RestrictedSpeed.
    let out = evaluate(&frame, 10_000, 100_000, true);
    if out.verdict == ObstacleVerdict::RestrictedSpeed {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "LIDAR offline + radar healthy expected RestrictedSpeed (O4b); \
             got {:?}",
            out.verdict
        ))
    }
}

// ---------------------------------------------------------------------------
// W-SBC — wayside SBC (RFC 0016)
// ---------------------------------------------------------------------------

fn w_sbc() -> Vec<Check> {
    vec![
        Check {
            name: "osr-intrusion-detect: clear frame → Clear",
            run: check_intrusion_clear,
        },
        Check {
            name: "osr-intrusion-detect: fence breach → Present (I3)",
            run: check_intrusion_fence_breach,
        },
        Check {
            name: "osr-intrusion-detect: stale LIDAR → Unknown (I2)",
            run: check_intrusion_stale_lidar,
        },
        Check {
            name: "osr-secbus verify roundtrip",
            run: check_secbus_roundtrip,
        },
    ]
}

fn check_intrusion_clear() -> Outcome {
    use osr_intrusion_detect::{evaluate, IntrusionParams, IntrusionVerdict, WaysideSensorFrame};
    let f = WaysideSensorFrame::clear();
    let out = evaluate(&f, 0, &IntrusionParams::default());
    if out.verdict == IntrusionVerdict::Clear {
        Outcome::pass()
    } else {
        Outcome::fail(format!("clear frame expected Clear; got {:?}", out.verdict))
    }
}

fn check_intrusion_fence_breach() -> Outcome {
    use osr_intrusion_detect::{evaluate, IntrusionParams, IntrusionVerdict, WaysideSensorFrame};
    let mut f = WaysideSensorFrame::clear();
    f.fence.breach_latched = true;
    let out = evaluate(&f, 0, &IntrusionParams::default());
    if out.verdict == IntrusionVerdict::Present {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "fence breach expected Present (I3); got {:?}",
            out.verdict
        ))
    }
}

fn check_intrusion_stale_lidar() -> Outcome {
    use osr_intrusion_detect::{
        evaluate, IntrusionParams, IntrusionVerdict, WaysideSensorFrame, MAX_SENSOR_STALE_MS,
    };
    let mut f = WaysideSensorFrame::clear();
    f.lidar_age_ms = MAX_SENSOR_STALE_MS + 50;
    let out = evaluate(&f, 0, &IntrusionParams::default());
    if out.verdict == IntrusionVerdict::Unknown {
        Outcome::pass()
    } else {
        Outcome::fail(format!(
            "stale LIDAR expected Unknown (I2); got {:?}",
            out.verdict
        ))
    }
}

// ---------------------------------------------------------------------------
// S-SBC — station / depot
// ---------------------------------------------------------------------------

fn s_sbc() -> Vec<Check> {
    vec![
        Check {
            name: "osr-crypto HMAC stable (AFC token verification baseline)",
            run: check_hmac_stable,
        },
        Check {
            name: "osr-secbus verify roundtrip (PSD-state signing baseline)",
            run: check_secbus_roundtrip,
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_role_produces_some_checks() {
        for r in [Role::TEcuS, Role::TEcuA, Role::TObs, Role::WSbc, Role::SSbc] {
            let checks = r.checks();
            assert!(!checks.is_empty(), "{} has no checks", r.name());
        }
    }

    #[test]
    fn t_ecu_s_checks_pass_on_happy_path() {
        let report = crate::runtime::run_checks("t-ecu-s", &t_ecu_s());
        assert!(report.all_pass(), "{}", report.format_text());
        // Sanity: several checks worth of coverage.
        assert!(report.entries.len() >= 5);
    }

    #[test]
    fn t_obs_checks_pass_on_happy_path() {
        let report = crate::runtime::run_checks("t-obs", &t_obs());
        assert!(report.all_pass(), "{}", report.format_text());
    }

    #[test]
    fn w_sbc_checks_pass_on_happy_path() {
        let report = crate::runtime::run_checks("w-sbc", &w_sbc());
        assert!(report.all_pass(), "{}", report.format_text());
    }

    #[test]
    fn t_ecu_a_checks_pass_on_happy_path() {
        let report = crate::runtime::run_checks("t-ecu-a", &t_ecu_a());
        assert!(report.all_pass(), "{}", report.format_text());
    }

    #[test]
    fn s_sbc_checks_pass_on_happy_path() {
        let report = crate::runtime::run_checks("s-sbc", &s_sbc());
        assert!(report.all_pass(), "{}", report.format_text());
    }

    #[test]
    fn role_from_cli_round_trip() {
        for expect in [Role::TEcuS, Role::TEcuA, Role::TObs, Role::WSbc, Role::SSbc] {
            let parsed = Role::from_cli(expect.name()).unwrap();
            assert_eq!(parsed, expect);
        }
        assert!(Role::from_cli("nonsense").is_none());
    }
}
