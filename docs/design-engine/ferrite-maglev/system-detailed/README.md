# Detailed candidate and system simulation

Completed bounded digital development and simulation publication, including rejected designs. A complete physically qualified train/civil/software system has NOT been reached.

Exact candidate `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`: **25.619t tare and 37.619t AW3 per car**, six cars. Geometry-derived equipment is counted; the old94ad actuator pass is a separate configuration.

| Development chain | Result |
|---|---|
| magnetic-static-support | OPEN / FAILED: Actual thin return-rail flux cross-section and saturation; target AW3 support must be achievable within current/material limits |
| magnetic-propulsion | OPEN / FAILED: Independent applicable field/convergence/demagnetisation evidence, not the parent model |
| structural-and-interface | OPEN / FAILED: Actual body,attachment,guideway,handling and provisionalground screens |
| coupled-motion-and-faults | OPEN / FAILED: Actual currents,continued fault states,guidance and authority; no detection-only pass |
| native-candidate-delivery | Implemented screens passed: Exact quantitative products through source-bound native ERP/FUXA lifecycle |
| physical-and-manufacturing-acceptance | OPEN / FAILED: Measurements,approved drawings,materials,hardware timing and independent acceptance remain required |

## Engineering and delivery packets

- [candidate-native](../candidate-native/README.md) — exact source receipt and retained results.
- [candidate-magnetics](../candidate-magnetics/README.md) — exact source receipt and retained results.
- [candidate-structures](../candidate-structures/README.md) — exact source receipt and retained results.
- [full-dynamics](../full-dynamics/README.md) — exact source receipt and retained results.
- [candidate-manufacturing](../candidate-manufacturing/README.md) — exact source receipt and retained results.
- [candidate-lifecycle](../candidate-lifecycle/README.md) — exact source receipt and retained results.
- [bim-field](../bim-field/README.md) — exact source receipt and retained results.
- [operations-crosscheck](../operations-crosscheck/README.md) — exact source receipt and retained results.
- [planning-platform](../planning-platform/README.md) — exact source receipt and retained results.
- [planning-ui](../planning-ui/README.md) — exact source receipt and retained results.

The candidate has a complete traced publication chain, not a completed engineering design. Failed field, structural or dynamic evidence blocks adoption even when BIM, purchasing or independent operations tests pass. No file or software-business result grants manufacturing or physical release.

The economics packet separates counted material/process subtotals from complete installed price. It compares identical passenger-services assumptions on a common kinematic trajectory. The new candidate has no adopted CAPEX/OPEX/debt forecast while mandatory propulsion and full-service duty evidence fail; the earlier configuration’s finance is not relabelled.

The owner/builder [planning workspace](../../../workbench/planning/index.html) can be used for controlled proposals independently of train physical qualification. Its generic workfront schedule and native navigation do not imply whole-city BIM or full OCC/HR deployment.

Remaining engineering work:

- Static lift: actual25mm return-rail flux area saturates before required AW3 support.
- Propulsion topology and refined demagnetisation/convergence.
- Joined carbody/splices,braking/capture interfaces and fatigue/crash.
- Rigid magnetic array versus terminal curvature and route recovery.
- Full four-stop motion/dwell/charging and fleet dispatch with qualified useful-field maps.
- Detailed electrical protection/PCB/insulation/thermal/hardware timing.
- Geotechnical foundation,station/depot/fire/evacuation and physical construction stages.
- Complete installed cost,local origin,verified demand and financing commitments.

Reproduce: `./osr design detailed-system` after the component packets. `./osr build` regenerates stale implemented studies; it does not autonomously produce physical qualification.
