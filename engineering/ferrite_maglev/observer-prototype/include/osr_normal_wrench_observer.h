#ifndef OSR_RESEARCH_NORMAL_WRENCH_V1_H
#define OSR_RESEARCH_NORMAL_WRENCH_V1_H
#include <stdint.h>

/* Offline numerical ABI only. No output authorises physical movement. */
enum { OSR_OBSERVER_CARS = 6, OSR_OBSERVER_MODULES = 24, OSR_OBSERVER_MAX_GROUPS = 200 };
typedef struct {
    uint32_t abi_version, groups;
    uint8_t configuration_sha256[32];
    double wave_number_rad_per_m, estimator_scale;
    uint64_t step_ns;
} OsrObserverConfig;
typedef struct {
    uint32_t initialized, reserved;
    uint64_t last_sequence, last_timestamp_ns;
    OsrObserverConfig config;
} OsrObserverState;
typedef struct {
    double flux_linkage_wb[6], phase_rad[6], normal_position_m[6];
    double current_alpha_a, current_beta_a;
} OsrObserverGroup;
typedef struct {
    uint64_t sequence, timestamp_ns;
    uint32_t sample_present, sample_groups;
    uint64_t sample_sequence, sample_timestamp_ns;
    uint8_t sample_configuration_sha256[32];
    double speed_m_s[6], centres_m[6];
    OsrObserverGroup groups[200];
    double desired_support_n[6][24];
} OsrObserverFrame;
typedef struct {
    OsrObserverConfig config;
    OsrObserverState state;
    OsrObserverFrame frame;
} OsrObserverInput;
typedef struct {
    uint32_t status, physical_output_authorised;
    OsrObserverState next_state;
    double raw_wrench_up_roll_pitch[6][3], scaled_wrench_up_roll_pitch[6][3];
    double correction_n[6][24], requested_support_n[6][24];
    double maximum_abs_correction_n;
} OsrObserverOutput;

#ifdef __cplusplus
extern "C" {
#endif
OsrObserverOutput osr_research_normal_wrench_v1(OsrObserverInput input);
#ifdef __cplusplus
}
#endif
#endif
