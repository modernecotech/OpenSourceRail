# T-ECU/S application carrier interface requirements

CM5 uses **dual 100-pin connectors**, not a 260-pin DDR4 SODIMM. Use the official module/carrier documentation and exact selected module revision; none of the previous fictitious connector pin assignments release a PCB. The official CM5IO provides one Gigabit Ethernet port. A redundant train network needs an explicitly designed second interface or suitable switch/controller topology, not two assumed native Ethernet MACs.

Define carrier power/boot/recovery, storage variant, Ethernet topology, buses, GPIO voltage domains, clock/reset, debug and isolation in a controlled interface drawing. I2C secure elements and PCIe/USB peripherals need supported buses, driver/role mapping and a bandwidth/power budget. SPI peripheral/slave support and one-way isolation must be proven on the chosen host/driver; controller direction or an isolator alone does not prove that application faults cannot affect protection.

Freeze boot permissions, supply sequencing and output inhibition from actual module reset/power signals. The prior 2 ms MCU and 60 s Linux boot numbers are not acceptance limits. Timing comes from measured revision-specific evidence. Protect access to boot/recovery and keys; record image and configuration hashes.

[Official CM5 hardware](https://www.raspberrypi.com/documentation/computers/compute-module.html), [power requirements](power-budget.md), [safety contract](safety-nets.md).
