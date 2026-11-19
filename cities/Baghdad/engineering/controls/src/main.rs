//! Offline interface replay. All proofs and commands are synthetic data.
use osr_atp::powered_wheel::{powered_wheel_evaluate, PoweredWheelInputs};
use osr_atp::BrakeCommand;
use osr_door_control::{
    door_evaluate, DoorAction, DoorInputs, DoorParams, DoorSensors, DoorSide, DoorState,
    MotorCommand,
};
use osr_tcms::protected_conductor::{evaluate_protected_conductor, ProtectedConductorStatus};
use osr_tcms::TcmsInputs;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

#[derive(Clone, Copy)]
struct Frame {
    command: DoorAction,
    station_verified: bool,
    platform: Option<DoorSide>,
    speed_mmps: i32,
    unlocked: Option<usize>,
    missing: Option<usize>,
    section_isolated: bool,
    service_supply: bool,
    identity_matches: bool,
    authority_valid: bool,
}

impl Default for Frame {
    fn default() -> Self {
        Self {
            command: DoorAction::Hold,
            station_verified: true,
            platform: Some(DoorSide::Left),
            speed_mmps: 0,
            unlocked: None,
            missing: None,
            section_isolated: false,
            service_supply: true,
            identity_matches: true,
            authority_valid: true,
        }
    }
}

#[derive(Debug, PartialEq)]
struct Trace {
    opening_left: usize,
    opening_right: usize,
    traction_enable: bool,
    brake: BrakeCommand,
}

fn sample(frame: Frame, configuration: [u8; 32], cars: usize, openings_per_side: usize) -> Trace {
    let mut opening_left = 0;
    let mut opening_right = 0;
    // Withhold departure as soon as release is requested, including the tick
    // before the physical lock switches change. Missing door status blocks it.
    let mut all_doors_locked = true;
    for index in 0..cars * 2 * openings_per_side {
        if frame.missing == Some(index) {
            all_doors_locked = false;
            continue;
        }
        let left = (index / openings_per_side) % 2 == 0;
        let inputs = DoorInputs {
            now_ns: 0,
            speed_mmps: frame.speed_mmps,
            at_station: true,
            station_identity_verified: frame.station_verified,
            door_side: if left {
                DoorSide::Left
            } else {
                DoorSide::Right
            },
            verified_platform_side: frame.platform,
            commanded: frame.command,
            emergency_unlock: false,
            emergency_egress_authorized: false,
            sensors: DoorSensors {
                closed_limit: true,
                lock_sensor: frame.unlocked != Some(index),
                open_limit: false,
                motor_current_ma: 0,
                obstruction_detected: false,
            },
        };
        let door = door_evaluate(
            &DoorState::default(),
            &inputs,
            &DoorParams::research_default(),
        );
        all_doors_locked &= door.interlock_ok;
        if door.motor == MotorCommand::DriveOpen {
            if left {
                opening_left += 1
            } else {
                opening_right += 1
            }
        }
    }

    let mut observed = configuration;
    if !frame.identity_matches {
        observed[0] ^= 1;
    }
    let supply = ProtectedConductorStatus {
        selected_configuration: configuration,
        observed_configuration: observed,
        contact_shoes_proved: true,
        powered_section_permitted: true,
        section_isolated: frame.section_isolated,
        inverter_healthy: true,
        essential_service_supply_ready: frame.service_supply,
    };
    let status = evaluate_protected_conductor(
        &TcmsInputs {
            doors_interlock_ok: all_doors_locked,
            bms_contactor_closed: frame.service_supply,
            traction_inverter_enabled: true,
            ..Default::default()
        },
        &supply,
    );
    let atp = powered_wheel_evaluate(
        &PoweredWheelInputs {
            selected_configuration: configuration,
            observed_configuration: observed,
            authority_valid: frame.authority_valid,
            localisation_known: true,
            train_integrity_known: true,
            communications_fresh: true,
            doors_locked: all_doors_locked,
            independent_brake_healthy: true,
            independent_brake_profile_valid: true,
            essential_service_supply_ready: frame.service_supply,
            contact_shoes_proved: true,
            powered_section_permitted: true,
            section_isolated: frame.section_isolated,
            inverter_healthy: true,
            traction_fault_latched: false,
            stopped: frame.speed_mmps == 0,
            parking_brake_proved: true,
            wheel_slide_active: false,
        },
        BrakeCommand::Release,
    );
    Trace {
        opening_left,
        opening_right,
        traction_enable: frame.command == DoorAction::Hold
            && status.traction_permissive
            && atp.traction_permissive,
        brake: atp.mechanical_brake,
    }
}

fn main() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(4)
        .unwrap();
    let packet: Value =
        serde_json::from_slice(&fs::read(root.join("cities/Baghdad/system-results.json")).unwrap())
            .unwrap();
    let sources = packet["source_sha256"].as_object().unwrap();
    for (path, expected) in sources {
        let digest = Sha256::digest(fs::read(root.join(path)).unwrap());
        assert_eq!(
            format!("{digest:x}"),
            expected.as_str().unwrap(),
            "stale source {path}"
        );
    }
    let first = &packet["networks"]["first"];
    assert_eq!(first["digital_cost_leader"], "protected_conductor");
    let physical = first["selected_candidate_id"].as_str().unwrap();
    assert_eq!(
        physical,
        first["power_cases"]["protected_conductor"]["physical_candidate_id"]
    );
    assert_eq!(physical.len(), 64);
    let mut configuration = [0; 32];
    for (i, byte) in configuration.iter_mut().enumerate() {
        *byte = u8::from_str_radix(&physical[2 * i..2 * i + 2], 16).unwrap();
    }
    let equipment = &first["selected_control_electronics"]["installed_train_items"];
    let cars = equipment["tcms_node"].as_u64().unwrap() as usize;
    let openings = first["selected_station_interfaces"]["vehicle"]["door_centres_m"]
        .as_array()
        .unwrap()
        .len();
    assert_eq!(
        cars * 2 * openings,
        equipment["door_controller"].as_u64().unwrap() as usize
    );
    assert_eq!(
        (cars, openings),
        (6, 4),
        "re-review cases for revised consist"
    );
    println!(
        "physical {physical}\nevaluation {}",
        first["selected_evaluation_id"]
    );
    use BrakeCommand::{Emergency, Release, Service};
    let base = Frame::default();
    let opening = Frame {
        command: DoorAction::Open,
        ..base
    };
    let cases = [
        ("departure", base, (0, 0, true, Release)),
        ("island on left", opening, (24, 0, false, Release)),
        (
            "island on right",
            Frame {
                platform: Some(DoorSide::Right),
                ..opening
            },
            (0, 24, false, Release),
        ),
        (
            "unknown platform",
            Frame {
                platform: None,
                ..opening
            },
            (0, 0, false, Release),
        ),
        (
            "unknown station",
            Frame {
                station_verified: false,
                ..opening
            },
            (0, 0, false, Release),
        ),
        (
            "reverse motion",
            Frame {
                speed_mmps: -10,
                ..opening
            },
            (0, 0, false, Release),
        ),
        (
            "last lock absent",
            Frame {
                unlocked: Some(47),
                ..base
            },
            (0, 0, false, Emergency),
        ),
        (
            "one controller silent",
            Frame {
                missing: Some(12),
                ..base
            },
            (0, 0, false, Emergency),
        ),
        (
            "section isolated in motion",
            Frame {
                section_isolated: true,
                speed_mmps: 10000,
                ..base
            },
            (0, 0, false, Service(1000)),
        ),
        (
            "service supply lost",
            Frame {
                service_supply: false,
                ..base
            },
            (0, 0, false, Emergency),
        ),
        (
            "identity mismatch",
            Frame {
                identity_matches: false,
                ..base
            },
            (0, 0, false, Emergency),
        ),
        (
            "authority withdrawn",
            Frame {
                authority_valid: false,
                ..base
            },
            (0, 0, false, Emergency),
        ),
    ];
    for (name, frame, (left, right, torque, brake)) in cases {
        let actual = sample(frame, configuration, cars, openings);
        assert_eq!(
            actual,
            Trace {
                opening_left: left,
                opening_right: right,
                traction_enable: torque,
                brake
            },
            "{name}"
        );
        println!("{name}: {actual:?}");
    }
}
