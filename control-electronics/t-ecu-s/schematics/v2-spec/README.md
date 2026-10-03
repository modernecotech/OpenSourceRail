# T-ECU-S board design requirements

Status: reference integration requirements; exact supplier BOM, schematic capture, pin/connector freeze, enclosure/thermal design and qualification evidence are open. This is not sufficient information to fabricate a railway control board.

| File | Current purpose |
|---|---|
| [block-diagram.md](block-diagram.md) | Functional paths and remaining common-cause boundaries |
| [power-budget.md](power-budget.md) | Capacity calculation or required complete load study; no released converter/fuse rating |
| [pinout-rp2350.md](pinout-rp2350.md) | Exposed-pin bench allocation or custom-board allocation requirements |
| [connector-tables.md](connector-tables.md) | Interface/harness schedule; supplier cavities and exact connector variants open |
| [safety-nets.md](safety-nets.md) | Hardware watchdog, permission/feedback and end-to-end fault contract |

See [reference integration](../../../reference-integration.json), [host bench requirements](../../diy-assembly/README.md) and [release checklist](../../../release-checklist.md). T-ECU/S additionally carries [CM5 carrier requirements](pinout-cm5.md) in its own folder.

A custom-board release needs the actual KiCad schematic/layout, ERC/DRC, controlled fabrication/BOM files, supplier interfaces and instrumented bring-up/fault/thermal/EMC evidence. Create fabrication directories when those artifacts exist. Do not manufacture from historical guessed pinouts or treat passing software/library tests as hardware acceptance.
