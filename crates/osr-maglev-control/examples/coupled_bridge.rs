//! Bounded line protocol for the Python flexible-guideway numerical study.
//! Input per tick: sequence then 24 relative gaps (m). Output: status followed
//! by 24 upward and 24 leftward study forces (N), or ERROR. No device access.
mod support;
use osr_maglev_control::array::{evaluate_array, ArrayState, ArraySupport, MODULES};
use std::io::{self, BufRead, Read, Write};

fn main() {
    let mut p = support::params();
    if let Some(value) = std::env::args().nth(1) {
        let Ok(mass) = value.parse::<f64>() else {
            std::process::exit(2)
        };
        if !mass.is_finite() || !(1000.0..=100_000.0).contains(&mass) {
            std::process::exit(2)
        }
        p.mass_kg = mass;
    }
    // Offline candidate parameters only; these do not authorise device outputs.
    let arguments: Vec<_> = std::env::args().collect();
    if arguments.len() > 4 {
        std::process::exit(2);
    }
    for (index, gains) in [(2, &mut p.proportional), (3, &mut p.damping)] {
        if let Some(value) = arguments.get(index) {
            let Ok(scale) = value.parse::<f64>() else {
                std::process::exit(2)
            };
            if !scale.is_finite() || !(0.25..=2.0).contains(&scale) {
                std::process::exit(2);
            }
            for gain in gains {
                *gain *= scale;
            }
        }
    }
    let mut state = ArrayState::default();
    let stdin = io::stdin();
    let mut input = stdin.lock();
    let stdout = io::stdout();
    let mut output = stdout.lock();
    for _ in 0..20_000 {
        let mut line = String::new();
        let bytes = input
            .by_ref()
            .take(8193)
            .read_line(&mut line)
            .expect("offline stdin");
        if bytes == 0 {
            break;
        }
        if bytes > 8192 {
            writeln!(output, "ERROR line-limit").unwrap();
            output.flush().unwrap();
            break;
        }
        let fields: Vec<_> = line.split_whitespace().collect();
        if fields.len() != MODULES + 1 {
            writeln!(output, "ERROR field-count").unwrap();
            output.flush().unwrap();
            break;
        }
        let Ok(sequence) = fields[0].parse::<u64>() else {
            break;
        };
        if sequence == 0 || sequence > 20_000 {
            break;
        }
        let mut frame = support::frame(sequence);
        let mut valid = true;
        for (sample, text) in frame.samples.iter_mut().zip(&fields[1..]) {
            match text.parse::<f64>() {
                Ok(gap) if gap.is_finite() => sample.gap_m = [gap; 2],
                _ => valid = false,
            }
        }
        if !valid {
            writeln!(output, "ERROR numeric").unwrap();
            output.flush().unwrap();
            break;
        }
        let result = evaluate_array(state, &frame, frame.issued_ns, &p);
        assert!(!result.physical_output_authorised);
        if result.support != ArraySupport::StudyForces {
            writeln!(output, "ERROR fallback").unwrap();
            output.flush().unwrap();
            break;
        }
        let allocation = result.allocation.expect("study force frame");
        // Flags: feasible, stop latch, physical authority (always false).
        write!(
            output,
            "{} {} false",
            allocation.within_tolerance, result.controlled_stop_required
        )
        .unwrap();
        for f in allocation.forces {
            write!(output, " {:.12e}", f.upward_n).unwrap();
        }
        for f in allocation.forces {
            write!(output, " {:.12e}", f.leftward_n).unwrap();
        }
        writeln!(output).unwrap();
        output.flush().unwrap();
        state = result.state;
    }
}
