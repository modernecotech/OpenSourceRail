# Safety-controller selection gate

OSR has not frozen a revenue-service safety MCU. Raspberry Pi and Radxa hosts
remain the inexpensive pilot and non-safety application baseline; they are not
the certification rationale for a SIL-4-target function.

## Required selection envelope

A deployment safety controller must be selected with the independent safety
assessor and demonstrate:

- manufacturer safety manual, diagnostic-coverage evidence and FMEDA inputs;
- lifecycle and supply assurance appropriate to the fleet life;
- independent watchdog, power, clock, I/O isolation and fail-safe output path;
- a justified redundancy, diversity and common-cause strategy at system level;
- qualified compiler/runtime, traceable configuration and hardware-in-loop tests;
- environmental, EMC, vibration and board-level evidence for the actual host.

No MCU establishes SIL-4 by part number alone. SIL capability, hardware fault
tolerance and systematic capability must be argued for the complete subsystem.

## Candidate families—not a supplier freeze

| Family | Appropriate use | Available manufacturer evidence | v0.3 decision |
|---|---|---|---|
| Infineon AURIX TC3xx | Candidate safety channel for train or wayside controller | IEC 61508 SIL 3 / ISO 26262 ASIL D capability, safety manual and FMEDA support package | Shortlist; assessor and lifecycle review required |
| TI Hercules TMS570/RM | Candidate safety channel, including long-lifecycle variants | Dual lockstep cores, ECC/BIST and IEC 61508 SIL 3 collateral | Shortlist; assessor and lifecycle review required |
| Raspberry Pi RP2350 | Software bring-up, low-cost I/O rigs and prototype 2oo2 experiments | Public datasheet; two processor sockets each boot-select Cortex-M33 or Hazard3, with the unused implementation held in reset | Prototype only; not the default certification baseline |

Primary manufacturer references:

- [Infineon AURIX TC3xx functional-safety documentation](https://documentation.infineon.com/aurixtc3xx/docs/ztz1745575952703)
- [Infineon IEC 61508 certification support](https://www.infineon.com/design-resources/platforms/aurix-software-tools/aurix-certification/aurix-iec61508-certification)
- [TI TMS570 safety manual](https://www.ti.com/lit/fs/spnu511d/spnu511d.pdf)
- [Raspberry Pi RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)

For the v0.3 pilot, the existing RP2350 boards remain useful evidence rigs.
For a revenue-service design, the operator records the selected channels,
safety package revision and architectural rationale in its controlled hardware
baseline. CM5/Radxa processors may host diagnostics, logging and applications,
but cannot bypass or command a safety output.
