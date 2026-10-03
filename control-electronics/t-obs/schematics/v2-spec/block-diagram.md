# T-OBS reference functional diagram

Status: integration requirements, not a released PCB. See [machine-readable integration](../../../reference-integration.json), [power envelope](power-budget.md), [harness schedule](connector-tables.md) and [output/fault contract](safety-nets.md).

```text
Nominal 24 V auxiliary inputs
  -> protected DC/DC branches -> evaluator A + external watchdog A
                             -> evaluator B + external watchdog B
                             -> application carrier and sensors

Radar EVM -> external CAN interface -> timestamped, validated ingress
HAP TX -> 100BASE-TX + separate power -> application preprocessing
Stereo pair -> compatible CSI flex -> application preprocessing
Ultrasonic positions -> qualified driver/AFE or bench timed-echo inputs

Evaluator A <-> directionally isolated SPI peer link <-> evaluator B
Local valid agreement + watchdog health -> independent permission drivers
Permission contact A -- series -- permission contact B -> simulated brake interface
Contact feedback + rail monitoring -> diagnostics / output inhibition
```

The production brake-demand interface may also carry a diagnostic network verdict, but the network does not replace the qualified physical output path. Shared sensors, preprocessing, buses and supplies require common-cause analysis. Neither direct CAN-FD nor Ethernet/RMII is a native Pico 2 interface. Converter, transducer AFE, board/chip package, relay and cooling selection remain open until supplier and measured bench evidence close their gates.
