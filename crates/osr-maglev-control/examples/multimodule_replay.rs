//! Reproducible virtual 1 ms frames; this measures no SBC scheduling deadline.
mod support;
use osr_maglev_control::array::{ArrayState, Availability, Forces};
use osr_maglev_control::ideal::IdealPlant;
use osr_maglev_control::io::{host_tick, ReplayIo};

fn main() {
    let params = support::params();
    let mut plant = IdealPlant {
        modes: [0.001, 0.0002, -0.0001, 0.001, 0.0001],
        velocity: [0.0; 5],
        mass_kg: params.mass_kg,
        inertia_kg_m2: [20_000.0, 600_000.0, 600_000.0],
        gravity_m_s2: params.gravity_m_s2,
    };
    let mut state = ArrayState::default();
    println!("virtual_ms,down_m,roll_rad,pitch_rad,left_m,yaw_rad,force_residual_n,moment_residual_nm,stop,physical_output_authorised");
    for sequence in 1..=10_000 {
        let mut frame = support::frame(sequence);
        // A known zero residual force is an IDEAL failure assumption. PM residual
        // force must be measured for a real failed drive/circuit configuration.
        if sequence >= 1000 {
            frame.availability[0] = Availability::Failed {
                residual: Forces::default(),
            };
        }
        frame.stop_requested = sequence >= 500;
        plant.observe(&mut frame, &params.stations, params.target_gap_m);
        let mut io = ReplayIo {
            now_ns: frame.issued_ns,
            frame,
            last_recorded: None,
        };
        let output = host_tick(&mut io, state, &params).unwrap();
        assert!(!output.physical_output_authorised);
        let allocation = output
            .allocation
            .expect("valid ideal observations and virtual timing");
        assert!(
            allocation.valid && allocation.within_tolerance,
            "lost ideal force feasibility at {sequence}"
        );
        assert!(plant.step(allocation.achieved, 0.001));
        state = output.state;
        if sequence % 500 == 0 {
            println!(
                "{sequence},{:.9},{:.9},{:.9},{:.9},{:.9},{:.6},{:.6},{},false",
                plant.modes[0],
                plant.modes[1],
                plant.modes[2],
                plant.modes[3],
                plant.modes[4],
                allocation
                    .residual
                    .force_n
                    .iter()
                    .map(|v| v.abs())
                    .fold(0.0, f64::max),
                allocation
                    .residual
                    .moment_nm
                    .iter()
                    .map(|v| v.abs())
                    .fold(0.0, f64::max),
                output.controlled_stop_required
            );
        }
    }
    assert!(
        plant.modes.iter().all(|v| v.abs() < 1e-6),
        "illustrative five-mode trajectory did not settle"
    );
    assert!(state.stop_latched);
}
