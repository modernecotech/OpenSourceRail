# T-ECU/S external interface schedule

Status: connector series and cavity-by-cavity harness drawings open. The earlier invented HSD/M12 pin tables are not a compatible train harness release.

| Interface | Required design record |
|---|---|
| Power A/B | Actual bus range, protected input, connector/current/derating, return/earth, mating halves and fuse coordination |
| Safety output A/B | Driver/series contact/feedback nets, actuator polarity and load, loss-of-power truth table |
| Brake/traction/door/fire and field inputs | Supplier signal/voltage, isolation, diagnostic coverage, channel topology and protected harness |
| CAN-FD | External controller/transceiver, termination, speed/topology, shield and supplier connector |
| Redundant network | Full Ethernet pair map, switch/controller topology, actual connector; Gigabit copper needs four pairs |
| Tachometer/IMU/temperature | Actual sensor type, excitation and data interface, protection, shielding and calibrated transfer |
| Recovery/debug | Separate keyed SWD/UART/USB interfaces, voltage, access controls and approved recovery role |

Every connector record needs part/variant, mating half, cavity view, terminal/seal, wire ID/gauge/length, shield/chassis termination, pull/reset state and continuity/insulation test. Do not share a debug header, shield or ground path across safety channels without reviewing the resulting fault path. Vendor diagrams and the actual protection study control pin assignment and rating.

See [MCU allocation](pinout-rp2350.md), [carrier interface](pinout-cm5.md), [output contract](safety-nets.md) and [bench workflow](../../../diy-assembly/README.md).
