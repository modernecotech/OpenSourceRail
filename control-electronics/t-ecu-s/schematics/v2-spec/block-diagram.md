# T-ECU/S reference functional diagram

```text
Actual auxiliary bus -> protected channel A power -> evaluator A + external watchdog A
                    -> protected channel B power -> evaluator B + external watchdog B
                    -> protected application branch -> CM5 carrier

Qualified field sensors and external bus controllers -> validated timestamped A/B ingress
Evaluator A <-> isolated peer cross-check <-> evaluator B
Local permission AND watchdog health -> independent driver A / driver B
Series monitored contacts -> qualified brake / traction actuator interface
Contact feedback / power monitoring -> fault latch and event recording
```

This is a requirements diagram. Shared inputs, grounds, buses and application-derived data remain common-cause paths requiring analysis. Native Pico CAN/RMII, fictitious CM5 SODIMM wiring, single-voltage-detector watchdogs and unqualified relay lifetime/safety claims are withdrawn. See [power](power-budget.md), [MCU allocation](pinout-rp2350.md), [carrier](pinout-cm5.md), [harness](connector-tables.md) and [fault contract](safety-nets.md).
