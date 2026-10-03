# T-OBS reference power and thermal envelope

The source is [reference-integration.json](../../../reference-integration.json). This is a sizing envelope for the bench candidates, not measured train duty or a qualified converter/fuse selection.

| Load | Output allocation | Basis |
|---|---:|---|
| CM5IO with attached cameras | 25 W | Carrier 5 V / 5 A interface envelope |
| AWR1843BOOST radar EVM | 12.5 W | 5 V / 2.5 A interface envelope |
| Livox HAP startup | 26 W | Vendor startup specification; 12 W typical |
| Dual evaluators and integration | 8 W | Unmeasured engineering allowance |
| Total simultaneous output envelope | 71.5 W | Sum of the four branches |
| Input at 90% conversion efficiency | 79.44 W | 71.5 / 0.90 |
| Capacity including 25% margin | 99.31 W | 79.44 × 1.25; 100 W reference supply envelope |

At an **assumed** 18 V minimum bus, the input envelope is 4.41 A, or 5.52 A including the capacity margin. The real auxiliary bus range, inrush, hold-up, cable drop and selective branch protection require a released electrical load study. Each surviving power leg must support the complete required fault-state load if redundant operation is claimed. Do not reuse the former 1 A fuse or claim that a 40 W host allowance covers this assembly.

The 100 W value is capacity, not sustained energy consumption: no OPEX/traction-energy uplift is calculated from it. Update the train auxiliary energy model after measured duty and production sensor choice. Do not double-count cameras included within the carrier allocation. The 18 V sizing assumption is not a claimed train-bus standard.

Mean Well HDR-60-24 is an AC/high-voltage DC input supply with 24 V output. It does not convert a 24 V train bus to 5 V or 12 V. Choose protected DC/DC branches with approved voltage range, isolation, derating and transient behaviour.

Passive cooling, junction temperatures and EMC compliance remain unverified. Calculate conduction, enclosure thermal resistance, solar load and dirty-filter performance; test startup and sustained operation at the declared hot-desert ambient. Keep sensing and event capture powered during a commanded brake when the fault permits; thermal throttling or application-fusion loss must be handled as stale data rather than assumed harmless.

Primary specifications checked 3 October 2026: [CM5 carrier](https://www.raspberrypi.com/documentation/computers/compute-module.html), [TI radar EVM](https://www.ti.com/lit/ug/spruim4b/spruim4b.pdf), [Livox HAP](https://www.livoxtech.com/hap/specs), [HDR-60](https://www.meanwell.com/Upload/PDF/HDR-60/HDR-60-SPEC.PDF).
