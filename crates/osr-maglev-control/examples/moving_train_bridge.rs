//! Six independent real Rust support controllers in one bounded offline IPC.
//! Arguments: car mass, virtual step nanoseconds, gap target/minimum/maximum.
//! Input: sequence and 144 gaps. Output per car: feasible/stop/physical flags,
//! peak lateral force, then 24 upward forces. No device addresses or I/O.
mod support;
use osr_maglev_control::array::{evaluate_array, ArrayState, ArraySupport, MODULES};
use std::io::{self, BufRead, Read, Write};
const CARS: usize = 6;
fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 5 {
        std::process::exit(2);
    }
    let values: Vec<f64> = args
        .iter()
        .map(|v| v.parse::<f64>().unwrap_or(f64::NAN))
        .collect();
    if values.iter().any(|v| !v.is_finite())
        || !(5000.0..=100000.0).contains(&values[0])
        || !(500000.0..=10000000.0).contains(&values[1])
        || values[1].fract() != 0.0
        || !(0.001..=0.03).contains(&values[2])
        || values[3] <= 0.0
        || values[3] >= values[2]
        || values[4] <= values[2]
        || values[4] > 0.05
    {
        std::process::exit(2);
    }
    let dt = values[1] as u64;
    let mut p = support::params();
    p.mass_kg = values[0];
    p.maximum_tick_ns = 2 * dt;
    p.maximum_age_ns = dt;
    p.target_gap_m = values[2];
    p.minimum_gap_m = values[3];
    p.maximum_gap_m = values[4];
    if !p.valid() {
        std::process::exit(2);
    }
    let mut states = [ArrayState::default(); CARS];
    let stdin = io::stdin();
    let mut input = stdin.lock();
    let stdout = io::stdout();
    let mut output = stdout.lock();
    for _ in 0..200000 {
        let mut line = String::new();
        let count = input.by_ref().take(16385).read_line(&mut line).unwrap();
        if count == 0 {
            break;
        }
        let fields: Vec<_> = line.split_whitespace().collect();
        if count > 16384 || fields.len() != 1 + CARS * MODULES {
            writeln!(output, "ERROR fields").unwrap();
            output.flush().unwrap();
            break;
        }
        let sequence = fields[0].parse::<u64>().unwrap_or(0);
        if sequence == 0 || sequence > 200000 {
            writeln!(output, "ERROR sequence").unwrap();
            output.flush().unwrap();
            break;
        }
        let mut response = String::new();
        let mut failed = false;
        for (car, state) in states.iter_mut().enumerate() {
            let mut frame = support::frame(sequence);
            frame.issued_ns = sequence * dt;
            for (sample, text) in frame
                .samples
                .iter_mut()
                .zip(&fields[1 + car * MODULES..1 + (car + 1) * MODULES])
            {
                let gap = text.parse::<f64>().unwrap_or(f64::NAN);
                sample.gap_m = [gap; 2];
            }
            let result = evaluate_array(*state, &frame, frame.issued_ns, &p);
            if result.physical_output_authorised || result.support != ArraySupport::StudyForces {
                response = format!("ERROR car-{car} fallback");
                failed = true;
                break;
            }
            let allocation = result.allocation.unwrap();
            use std::fmt::Write as _;
            let lateral = allocation
                .forces
                .iter()
                .map(|f| f.leftward_n.abs())
                .fold(0.0, f64::max);
            write!(
                &mut response,
                "{} {} false {:.12e}",
                allocation.within_tolerance, result.controlled_stop_required, lateral
            )
            .unwrap();
            for force in allocation.forces {
                write!(&mut response, " {:.12e}", force.upward_n).unwrap();
            }
            response.push(' ');
            *state = result.state;
        }
        writeln!(output, "{response}").unwrap();
        output.flush().unwrap();
        if failed {
            break;
        }
    }
}
