# T-ECU/S MCU allocation requirements

Status: exact custom-board pin allocation open. The prior native CAN0/CAN1, SPI2, dedicated PIO pins and package-independent output map are withdrawn. RP2350 uses GPIO-multiplexed supported peripherals; PIO state machines do not add physical pins. External CAN-FD controllers and transceivers are required. ATECC608B uses its selected I2C/single-wire interface, not SPI.

The [Pico 2 bench allocation](../../../reference-integration.json) is an exposed-pin example for peer SPI, I2C trust element, external CAN controller, permission and watchdog functions. It belongs to the T-OBS bench; T-ECU/S must additionally allocate IMU, tachometers, brake/traction/door/fire inputs, feedback and temperature sensing. Freeze a host-specific resource map before wiring.

The board designer must provide: package and silicon revision; pin/pad/header views; alternate function; direction and voltage domain; reset pull/state; controller/peripheral role; isolation; required peripheral/interrupt/DMA resources; channel A/B separation; harness/net identity; and test point. Validate that each required function has a physical pin and that pins, hardware peripherals and interrupt resources are not allocated twice.

Do not copy the Pico header into a custom RP2350A/B board or add cab/deadman functions to the cabless train without an approved requirement. Permission outputs default low, with external watchdog inhibition and contact feedback; see [safety contract](safety-nets.md). Firm deadline and fault tests bind the released HAL to the exact board revision.

Primary source: [Raspberry Pi chip documentation](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html).
