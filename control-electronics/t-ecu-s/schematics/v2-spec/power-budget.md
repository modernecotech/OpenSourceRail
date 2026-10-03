# T-ECU/S host power design requirements

The former chip-level budget and converter/inrush claims are withdrawn as a complete host design. A CM5IO carrier alone has a 5 V / 5 A input envelope; dual MCU boards, secure elements, external bus controllers, isolators, relay drivers, watchdogs and field I/O must be added. The [T-OBS sizing calculation](../../../t-obs/schematics/v2-spec/power-budget.md) provides a reproducible example; its sensor loads do not automatically apply to T-ECU/S.

| Design record | Required input / calculation |
|---|---|
| Input contract | Actual auxiliary range, loss-of-power requirement, surge, reverse polarity and hold-up |
| Per-branch load sheet | Complete vendor assembly input, peak/inrush and sustained measured duty; do not add chip internal rails to an already counted module |
| Capacity | Simultaneous required output / actual efficiency, derating and margin; each surviving leg sized for its required failure duty |
| Protection | Fault current, fuse coordination, connector/contact rating, wire voltage drop and transient suppression |
| Independent channels | Separately controlled power and watchdog inhibition, with documented common-cause boundary |
| Monitoring | Rail-specific UV/OV detectors plus separate external heartbeat watchdogs; TPS3701 has no watchdog function |
| Thermal | Hot ambient, enclosure conduction, solar/dust exposure, full duty and abnormal modes |
| EMC and evidence | Actual revision burst/surge, conducted/radiated and immunity tests, instrument results and configuration hashes |

No converter, capacitor, fuse or certified thermal/EMC rating is selected from this requirements table. Inrush cannot be cleared by an uncalculated bulk capacitor or fixed delay. Complete the power/harness drawings and bench fault tests before board release. [CM5 carrier specification](https://www.raspberrypi.com/documentation/computers/compute-module.html), [TPS3701 specification](https://www.ti.com/product/TPS3701).
