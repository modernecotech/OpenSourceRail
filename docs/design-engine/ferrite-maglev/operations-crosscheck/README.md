# Independent operations cross-check

Actual Eclipse SUMO executes the same four passenger stops, six-car length and current candidate mass in both directions. Nominal, delayed dwell, receiver-unavailable berth delay and deliberately overbooked headway cases retain raw network, routes, stops, logs and output.

All declared kinematic/block screens passed: **True**. The nominal comparison uses a separate closed-form acceleration/cruise/braking timing oracle with a fixed5s comparison tolerance. Differences are reported, never calibrated away.

SUMO uses a declared constant-acceleration traction hypothesis for this independent scheduling comparison. It does not evaluate fixed-zone LSM thrust, magnetic suspension, independent capture, hardware braking, charging or actual Rust authority. Those are separate coupled system evaluators. Receiver unavailability here is a berth delay, not a magnetic stopping test.

[Eclipse SUMO railway models and custom dynamics](https://sumo.dlr.de/docs/Simulation/Railways.html)
[Eclipse SUMO installation and Python packages](https://sumo.dlr.de/docs/Downloads.php)

No physical or operational acceptance. Reproduce with `./osr design operations-crosscheck`.
