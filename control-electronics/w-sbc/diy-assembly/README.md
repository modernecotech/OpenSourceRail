# W-SBC bench assembly requirements

Status: bench integration reference; hardware BOM, image, wiring and qualification are open. The [release checklist](../../release-checklist.md) governs the assembly. Exact SKUs and total prices are not frozen; previous retail subtotals omitted integration parts.

| Block | Required detail before assembly release |
|---|---|
| Compute and carrier | Exact CM5 configuration, compatible carrier, storage and cooling; 5 V input supplied correctly |
| Field power | Approved input range, DC/DC, fuse/selectivity, surge/EMC, inrush and hold-up |
| I/O and network | External CAN controller/transceiver where required, Ethernet switching, isolation, termination and pin map |
| Security | Channel-local I2C secure element, provisioning and recovery process |
| Harness/enclosure | Mating connectors, contacts, terminals, ferrules, wire cut list, clamps, labels, grounding and thermal design |
| Output chain | Simulated loads for bench; qualified drivers, feedback and actuator interfaces before deployment |
| Firmware/image | Real target HAL/driver mapping, immutable build, configuration/signature hashes and measured startup behaviour |

Mean Well HDR-60-24 converts AC/high-voltage DC input to **24 V output**. It may supply a suitable isolated laboratory or mains-fed wayside setup, but cannot convert a 24 V field bus to 5 V. Onboard hosts require protected DC/DC supplies. No wiring from a mains terminal is released here.

For the safety-host bench use the [validated exposed-pin allocation](../../reference-integration.json) as a proposed starting point and freeze any host-specific changes. SPI needs a digital isolator and controller/peripheral wiring; a USB isolator does not provide SPI or a direct link between two USB devices. Pico 2 GPIO30/31 and chip-package-only pins are not available on its header. Do not assume that a Pi CAN HAT independently serves both Pico channels.

For application/wayside/station hosts, the modem needs a compatible carrier and power/USB interface; multiple HATs require connector and pin conflict review. Size UPS, enclosure and converter loads from the complete host BOM. Application, station and wayside software disposition comes from [deployment/components.toml](../../../deployment/components.toml); TACS runtime remains a reference tooling host until qualified hardware composition is released.

Confirm GPIO voltage domains, loss-of-power state, wiring continuity/insulation, bus timing, EMI, thermal soak, image boot and recorded self-test on the actual revision. Procurement, construction and train actuation require the released package, not this list.
