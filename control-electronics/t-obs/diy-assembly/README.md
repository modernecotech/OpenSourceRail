# T-OBS bench integration design

Status: supplier and hardware freeze open; no train operation authority. Two end assemblies represent one trainset. The component and pin schedules are in [reference-integration.json](../../reference-integration.json); the [Baghdad register](../../../engineering/data/baghdad-reference-parts.json) expands fleet quantities and missing integration parts.

| Block | Per end host | Required integration |
|---|---:|---|
| Pico 2 evaluator | 2 | Separately protected supply branches, hardware watchdogs and permission outputs |
| CM5 and compatible carrier | 1 | Exact memory/storage/carrier SKU to freeze; compatible 5 V supply and camera flex cables |
| I2C secure element | 2 | Separate local channel wiring, provisioning and credentials |
| SPI digital isolator | 1 link | Channel A controller and channel B peripheral; correct directionality and separately powered sides |
| External CAN-FD controller/transceiver | Per network design | Pico 2 has no native CAN-FD; a Pi HAT does not automatically connect both evaluators |
| Radar | 1 candidate | AWR1843BOOST is an EVM; adapter harness, 5 V barrel input, micro USB debug and J3 CAN interface |
| Lidar | 1 candidate | Select HAP TX for 100BASE-TX; separate 9–18 V power and manufacturer cable; T1 requires an automotive Ethernet adapter |
| Stereo cameras | 2 | Rigid calibration bar and CM5IO-compatible 22-pin cable family; exact cable length to freeze |
| Ultrasonic sensing positions | 4 | Weatherproof transducers/AFE to select; HC-SR04 is a laboratory candidate, not qualified outdoor equipment |
| Hardware permission chain | 2 series contacts | Independent drivers/watchdog inhibition and contact feedback; relay part and failure analysis open |
| Harness/enclosure/protection | 1 kit | Fuses, TVS/filter, DC/DCs, connectors, glands, terminals, labels, heat spreader and test points |

Historical retail subtotals are withdrawn: they excluded essential power, isolation, harness and watchdog parts and did not identify a qualified complete assembly. Unit costs stay open until the complete supplier BOM is quoted.

## Bench signal path

Use the shared GPIO allocation with its pin names, not physical header numbers. A and B have separate local I2C buses and power branches. SPI peer wiring includes clock, select and correctly crossed TX/RX through a suitable isolator; a USB isolator cannot carry SPI or connect two USB device endpoints directly.

HC-SR04-style modules need VCC, GND, TRIG and timed digital ECHO. Level-shift each echo to the Pico's 3.3 V domain. Capture pulse duration using timer/PIO, not an ADS1115 analog sample. Raw piezo transducers need an excitation driver, receiver/AFE and sampling/timing design; they are not interchangeable with a four-wire ranging module. Shared transducers or an application-generated fused list are common inputs; duplicating evaluators does not make them independent sensing channels.

Mount ultrasonic acoustic faces in qualified apertures. Do not put them behind the radar radome or claim that an 8 mm polycarbonate panel is acoustically transparent. Radar needs a tested radome; lidar and cameras need separate optical windows and contamination controls. Verify alignment, weather sealing, vibration, field overlap and stopping-distance coverage on a representative nose.

## Power and outputs

Use [the power envelope](../schematics/v2-spec/power-budget.md) and [output contract](../schematics/v2-spec/safety-nets.md). No connection to actual brake or traction actuators is permitted before qualification; bench outputs drive simulated loads. Exact wire gauge, fuse, connector rating, coil suppression and contact rating follow the protection and load study.

Run bench tests for boot-low permission, stale/disagreeing sensor reports, both single-channel power failures, stuck-high/low heartbeat, welded contact, driver short, bus faults, reverse polarity, brownout, inrush and hot soak. Retain instrument traces and configuration hashes; the software self-test alone cannot establish those results.
