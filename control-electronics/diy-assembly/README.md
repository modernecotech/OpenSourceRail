# Bench assembly workflow

Start with the [host requirements](../README.md), [reference integration](../reference-integration.json), [candidate catalogue](parts-catalogue.md) and [release checklist](../release-checklist.md). These specify integration work; no qualified plug-and-play railway assembly or downloadable target image is released.

1. Freeze exact compute/carrier, peripherals, interfaces and target firmware.
2. Calculate bus range, converter capacity, inrush, fuse selectivity and thermal/EMC design.
3. Release harness cavities, cable/terminal list, isolation topology and enclosure drawings.
4. Build a simulated-load bench unit; verify continuity, voltage domains and fault states before connecting power.
5. Run measured device/HAL, boot, heartbeat, output, sensor, thermal and EMC tests; retain hashes and instrument records.
6. Review qualification evidence and supplier substitutions before authorising any field function.

A USB isolator does not connect two USB-device Pico boards or carry SPI. Use a correctly specified SPI isolator and controller/peripheral link. An AC-input HDR-60-24 supplies 24 V output, not a 24-to-5 V conversion. Board-package pins cannot be copied into a Pico header wiring table. See [image status](sd-card-images.md) before preparing boot media.
