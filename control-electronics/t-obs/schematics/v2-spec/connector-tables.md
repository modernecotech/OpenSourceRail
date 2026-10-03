# T-OBS connector and harness design schedule

Status: interface schedule; connector series, contact numbers and cable assemblies are not released. All external connectors need mating-half, keying, wire/contact rating, sealing, shield termination and label definitions. The former fabricated M12/PoE pinouts are withdrawn.

| Interface ID | Function | Design requirement |
|---|---|---|
| PWR-A / PWR-B | Nominal 24 V input branches | Power-keyed connectors, individually protected; sized from corrected load/inrush/derating, not an Ethernet D-code connector |
| NET-A / NET-B | Redundant train network | Approved Ethernet connector and full pair map; 1000BASE-T needs four data pairs; controller/switch topology remains open |
| RAD-DATA | Radar EVM CAN | AWR1843BOOST J3 CAN adapter; vendor board revision and termination; external connector chosen separately |
| RAD-PWR | Radar EVM supply | 5 V barrel interface; dedicated protected branch; micro USB is debug/configuration |
| LID-DATA | HAP TX data | 100BASE-TX with the vendor cable; HAP T1 needs a different physical interface |
| LID-PWR | HAP supply | Separate vendor 9–18 V input, 12 V reference branch; no 12 V PoE over spare Gigabit contacts |
| US-01..04 | Ultrasonic position | Candidate-specific excitation/receive or TRIG/ECHO, level shifting and shield; raw piezo is not plug compatible |
| CAM-L / CAM-R | Stereo CSI | CM5IO 22-pin family with the appropriate camera adapter; internal flex length and cable orientation frozen |
| PERMIT / FEEDBACK | Channel permissions and contact monitoring | Segregated channel circuits, load/polarity truth table, test point and actuator supplier interface |
| DEBUG-A / DEBUG-B | MCU SWD | Package/board-specific keyed debug connector; production access control |

Do not fabricate a harness from this table. Release a cavity-by-cavity drawing, wire cut list, ferrule/terminal/seal list, formboard and continuity/insulation test after vendor freeze. The TI EVM does not ship a standard M12 radar interface. Radar needs an RF-qualified radome; ultrasonic faces need acoustic apertures and lidar/cameras need qualified optical paths. Fixed mounting angles, bracket hole patterns and cable limits require coverage/clearance studies.

See [bench integration](../../diy-assembly/README.md) and [reference source](../../../reference-integration.json). Primary interfaces: [TI EVM guide](https://www.ti.com/lit/ug/spruim4b/spruim4b.pdf), [Livox specification](https://www.livoxtech.com/hap/specs), [CM5 hardware](https://www.raspberrypi.com/documentation/computers/compute-module.html).
