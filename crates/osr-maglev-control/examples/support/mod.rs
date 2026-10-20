use osr_maglev_control::array::{
    illustrative_geometry, ArrayParams, Availability, Frame, Sample, MODULES,
};

pub fn params() -> ArrayParams {
    ArrayParams {
        stations: illustrative_geometry(),
        target_gap_m: 0.008,
        minimum_gap_m: 0.003,
        maximum_gap_m: 0.013,
        maximum_lateral_m: 0.02,
        sensor_disagreement_m: 0.0002,
        maximum_age_ns: 500_000,
        maximum_tick_ns: 2_000_000,
        mass_kg: 27_750.0,
        gravity_m_s2: 9.81,
        proportional: [2e6, 30e6, 30e6, 2e6, 30e6],
        damping: [500e3, 4e6, 4e6, 500e3, 4e6],
        force_tolerance_n: 0.1,
        moment_tolerance_nm: 0.1,
    }
}
pub fn frame(sequence: u64) -> Frame {
    Frame {
        issued_ns: sequence * 1_000_000,
        sequence,
        samples: [Sample {
            gap_m: [0.008; 2],
            lateral_m: [0.0; 2],
            healthy: true,
        }; MODULES],
        availability: [Availability::Available; MODULES],
        support_power_available: true,
        traction_requested: true,
        stop_requested: false,
        stopped: false,
        secured: false,
        reset_requested: false,
    }
}
