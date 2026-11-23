//! Offline interface replay. All proofs and commands are synthetic data.
mod boarding;

use osr_atp::powered_wheel::{
    powered_wheel_at_berth, powered_wheel_evaluate, powered_wheel_starting, PoweredWheelInputs,
    SecuredBerth,
};
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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Direction {
    Forward,
    Reverse,
}

impl Direction {
    fn sign(self) -> i32 {
        match self {
            Self::Forward => 1,
            Self::Reverse => -1,
        }
    }

    fn opposite(self) -> Self {
        match self {
            Self::Forward => Self::Reverse,
            Self::Reverse => Self::Forward,
        }
    }
}

#[derive(Clone, Copy)]
struct Frame {
    command: DoorAction,
    station_verified: bool,
    open_side: Option<DoorSide>,
    parking_proved: bool,
    hold_applied: bool,
    torque_inhibit_proved: bool,
    brake_healthy: bool,
    brake_profile_valid: bool,
    starting_effort_direction: Option<Direction>,
    brake_demand: BrakeCommand,
    platform: Option<DoorSide>,
    speed_mmps: i32,
    unlocked: Option<usize>,
    missing: Option<usize>,
    section_isolated: bool,
    service_supply: bool,
    identity_matches: bool,
    authority_valid: bool,
    local_reset_key: bool,
    emergency_handle: Option<usize>,
    evacuation_path_proved_for: Option<usize>,
}

impl Default for Frame {
    fn default() -> Self {
        Self {
            command: DoorAction::Hold,
            station_verified: true,
            open_side: None,
            parking_proved: true,
            hold_applied: true,
            torque_inhibit_proved: true,
            brake_healthy: true,
            brake_profile_valid: true,
            starting_effort_direction: None,
            brake_demand: BrakeCommand::Release,
            platform: Some(DoorSide::Left),
            speed_mmps: 0,
            unlocked: None,
            missing: None,
            section_isolated: false,
            service_supply: true,
            identity_matches: true,
            authority_valid: true,
            local_reset_key: false,
            emergency_handle: None,
            evacuation_path_proved_for: None,
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

fn installed_side(index: usize, openings_per_side: usize) -> DoorSide {
    if (index / openings_per_side).is_multiple_of(2) {
        DoorSide::Left
    } else {
        DoorSide::Right
    }
}

#[derive(Clone, Copy)]
enum Protection {
    Movement,
    Berth(DoorSide),
    Starting(Direction),
}

fn evaluate_frame(
    mut frame: Frame,
    configuration: [u8; 32],
    door_states: &mut [DoorState],
    openings_per_side: usize,
    now_ns: u64,
    protection: Protection,
) -> (Trace, bool) {
    if frame.emergency_handle.is_some() {
        frame.command = DoorAction::Hold;
        frame.brake_demand = BrakeCommand::Emergency;
    }
    let mut opening_left = 0;
    let mut opening_right = 0;
    // Withhold departure as soon as release is requested, including the tick
    // before the physical lock switches change. Missing door status blocks it.
    let mut all_doors_locked = !door_states.is_empty();
    let mut unreleased_doors_locked = all_doors_locked;
    for (index, state) in door_states.iter_mut().enumerate() {
        if frame.missing == Some(index) {
            all_doors_locked = false;
            continue;
        }
        let side = installed_side(index, openings_per_side);
        let is_open = frame.open_side == Some(side);
        let inputs = DoorInputs {
            now_ns,
            speed_mmps: frame.speed_mmps,
            at_station: true,
            station_identity_verified: frame.station_verified,
            door_side: side,
            verified_platform_side: frame.platform,
            commanded: frame.command,
            emergency_unlock: frame.emergency_handle == Some(index),
            emergency_egress_authorized: frame.evacuation_path_proved_for == Some(index)
                && frame.platform == Some(side)
                && frame.station_verified
                && frame.identity_matches
                && frame.service_supply
                && frame.parking_proved
                && frame.hold_applied
                && frame.brake_healthy
                && frame.torque_inhibit_proved,
            sensors: DoorSensors {
                closed_limit: !is_open,
                lock_sensor: !is_open && frame.unlocked != Some(index),
                open_limit: is_open,
                motor_current_ma: 0,
                obstruction_detected: false,
            },
        };
        let door = door_evaluate(state, &inputs, &DoorParams::research_default());
        *state = door.state;
        all_doors_locked &= door.interlock_ok;
        if !matches!(protection, Protection::Berth(released) if released == side) {
            unreleased_doors_locked &= door.interlock_ok;
        }
        if door.motor == MotorCommand::DriveOpen {
            if side == DoorSide::Left {
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
    let inputs = PoweredWheelInputs {
        selected_configuration: configuration,
        observed_configuration: observed,
        authority_valid: frame.authority_valid,
        localisation_known: true,
        train_integrity_known: true,
        communications_fresh: true,
        doors_locked: all_doors_locked,
        independent_brake_healthy: frame.brake_healthy,
        independent_brake_profile_valid: frame.brake_profile_valid,
        essential_service_supply_ready: frame.service_supply,
        contact_shoes_proved: true,
        powered_section_permitted: true,
        section_isolated: frame.section_isolated,
        inverter_healthy: true,
        traction_fault_latched: false,
        stopped: frame.speed_mmps == 0,
        parking_brake_proved: frame.parking_proved,
        wheel_slide_active: false,
    };
    let atp = match protection {
        Protection::Berth(side) => powered_wheel_at_berth(
            &inputs,
            frame.brake_demand,
            SecuredBerth {
                visit_and_platform_proved: frame.station_verified && frame.platform == Some(side),
                unreleased_doors_locked,
                all_controllers_present: frame.missing.is_none(),
                independent_hold_applied: frame.hold_applied,
                inverter_inhibit_proved: frame.torque_inhibit_proved,
            },
        ),
        Protection::Movement => powered_wheel_evaluate(&inputs, frame.brake_demand),
        Protection::Starting(direction) => powered_wheel_starting(
            &inputs,
            frame.brake_demand,
            frame.starting_effort_direction == Some(direction),
        ),
    };
    (
        Trace {
            opening_left,
            opening_right,
            traction_enable: frame.emergency_handle.is_none()
                && frame.command == DoorAction::Hold
                && status.traction_permissive
                && atp.traction_permissive,
            brake: atp.mechanical_brake,
        },
        all_doors_locked,
    )
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
    let parent_physical = first["selected_candidate_id"].as_str().unwrap();
    assert_eq!(
        parent_physical,
        first["power_cases"]["protected_conductor"]["physical_candidate_id"]
    );
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
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    let opening_bytes = match args.as_slice() {
        [] => None,
        [flag, file] if flag == "--opening" => {
            Some(fs::read(file).expect("read Airport opening JSON"))
        }
        _ => panic!("usage: baghdad-station-interface-replay [--opening OPENING.json]"),
    };
    let opening = opening_bytes
        .as_ref()
        .map(|bytes| serde_json::from_slice::<Value>(bytes).expect("valid Airport opening JSON"));
    let (physical, system_evaluation) = if let Some(case) = &opening {
        let bundle = &case["bundle"];
        let power = &case["power"];
        let fleet = power["common_service"]["fleet_trainsets"].as_u64().unwrap();
        assert!(fleet > 0);
        assert_eq!(case["parent"], parent_physical);
        assert_eq!(bundle["parent"], parent_physical);
        assert_eq!(bundle["service_group"], "Airport");
        assert_eq!(bundle["formation_cars"], cars);
        assert_eq!(bundle["supply"], "protected_conductor");
        assert_eq!(power["option"], bundle["supply"]);
        assert_eq!(power["parent_candidate_id"], case["candidate_id"]);
        assert_eq!(
            format!("{:x}", Sha256::digest(serde_json::to_vec(bundle).unwrap())),
            case["candidate_id"].as_str().unwrap(),
            "Airport bundle identity"
        );
        assert_eq!(
            case["sources"]["cities/Baghdad/system-results.json"]
                .as_str()
                .unwrap(),
            format!(
                "{:x}",
                Sha256::digest(fs::read(root.join("cities/Baghdad/system-results.json")).unwrap())
            )
        );
        assert_eq!(
            bundle["active_sets"]
                .as_u64()
                .unwrap()
                .checked_add(bundle["spares"].as_u64().unwrap()),
            Some(fleet)
        );
        for (total, per_train) in [
            ("tcms_nodes", "tcms_node"),
            ("door_controllers", "door_controller"),
            ("brake_controllers", "brake_controller"),
            ("shoe_status_channels", "shoe_status_channel"),
            ("atp_channels", "atp_channel"),
            ("radio_links", "radio_link"),
            ("train_service_power_units", "train_service_power_unit"),
            ("inverter_control_units", "inverter_control_unit"),
        ] {
            assert_eq!(
                case["controls"][total].as_u64(),
                fleet.checked_mul(equipment[per_train].as_u64().unwrap()),
                "Airport quantity for {total}"
            );
        }
        (
            case["candidate_id"].as_str().unwrap(),
            case["evaluation_id"].as_str().unwrap(),
        )
    } else {
        (
            parent_physical,
            first["selected_evaluation_id"].as_str().unwrap(),
        )
    };
    assert_eq!(physical.len(), 64);
    let mut configuration = [0; 32];
    for (i, byte) in configuration.iter_mut().enumerate() {
        *byte = u8::from_str_radix(&physical[2 * i..2 * i + 2], 16).unwrap();
    }
    let mut replay_digest = Sha256::new();
    let replay_inputs: &[&[u8]] = &[
        b"baghdad-station-visit-v1",
        physical.as_bytes(),
        system_evaluation.as_bytes(),
        include_bytes!("main.rs"),
        include_bytes!("boarding.rs"),
        include_bytes!("../Cargo.lock"),
        include_bytes!("../../../../../crates/osr-atp/src/powered_wheel.rs"),
        include_bytes!("../../../../../crates/osr-tcms/src/protected_conductor.rs"),
        include_bytes!("../../../../../crates/osr-tcms/src/lib.rs"),
        include_bytes!("../../../../../crates/osr-door-control/src/lib.rs"),
    ];
    for bytes in replay_inputs {
        replay_digest.update((bytes.len() as u64).to_be_bytes());
        replay_digest.update(bytes);
    }
    if let Some(bytes) = opening_bytes {
        replay_digest.update(Sha256::digest(bytes));
    }
    println!("physical {physical}\nsystem evaluation {system_evaluation}\nstation replay evaluation {:x}",
        replay_digest.finalize());
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
        let (actual, _) = evaluate_frame(
            frame,
            configuration,
            &mut vec![DoorState::default(); cars * 2 * openings],
            openings,
            0,
            Protection::Movement,
        );
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
    boarding::replay(configuration, cars, openings);
}
