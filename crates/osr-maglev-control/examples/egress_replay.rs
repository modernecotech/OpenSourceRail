//! Deterministic offline study transcript; no I/O/door/railway actuation.
use osr_maglev_control::egress::{evaluate, Inputs, Params, State};
fn main() {
    let params = Params {
        maximum_age_ns: 500_000,
        maximum_tick_ns: 2_000_000,
    };
    let args: Vec<String> = std::env::args().skip(1).collect();
    let revision = args
        .first()
        .map(|v| v.parse::<u64>().expect("study revision"))
        .unwrap_or(1);
    let path_clear = args.get(1).is_none_or(|v| v == "true");
    let height_covered = args.get(2).is_none_or(|v| v == "true");
    let mut state = State::default();
    print!("{{\"schema\":\"osr-egress-offline-replay/1\",\"physical_output_authorised\":false,\"frames\":[");
    for sequence in 1..=9 {
        let i = Inputs {
            issued_ns: sequence * 1_000_000,
            sequence,
            candidate_revision: revision,
            door_id: 1,
            emergency_requested: true,
            stopped: sequence >= 2,
            secured: sequence >= 2,
            traction_isolated: sequence >= 2,
            landing_clear: path_clear,
            height_covered: height_covered && sequence != 3,
            adjacent_clear: true,
            device_ready: true,
            assistance_ready: true,
            deployment_requested: sequence >= 5,
            deployment_confirmed: sequence >= 6,
            exit_open_confirmed: sequence >= 6,
            flow_complete: sequence >= 8,
            stowed_locked: sequence < 5,
            reset_requested: false,
        };
        let r = evaluate(state, i, i.issued_ns, params);
        print!("{}{{\"sequence\":{},\"phase\":\"{:?}\",\"missing_prerequisites\":{},\"traction_inhibit_required_in_study\":{},\"support_must_be_maintained_in_study\":{},\"physical_output_authorised\":{}}}",
            if sequence == 1 { "" } else { "," }, sequence, r.state.phase, r.missing_prerequisites,
            r.traction_inhibit_required_in_study, r.support_must_be_maintained_in_study, r.physical_output_authorised);
        state = r.state;
    }
    println!("]}}");
}
