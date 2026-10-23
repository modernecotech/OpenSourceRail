# Independent final actuator cross-check

This record verifies the exact final Rust-observer actuator packet and compares its three retained sampled trajectories with the immutable passing Python-observer baseline. The original study/source inputs remain at the hash-bound repository paths in `receipt.json`; no new coupled simulation was run for this archive.

For estimator scales0.9,1.0,1.1, all140,417 moving frames and142,417 Rust-observer calls are retained in the producer packet. The cross-check independently derives a conservative post-pose two-pole force bound from the recorded pre/post gap-field maximum: `A / mu0 * B_max**2`. It also compares every retained sampled car displacement, speed and rigid-body pose with the Python reference, and checks the exact nine-candidate fault holds. Sampled trajectory similarity is a port comparison, not an independent physical model or a proof between samples.

Reproduce from the repository root (current hash-bound sources and input packets required):

```sh
./tools/automation/osr-python -u - < engineering/assurance/v052-pilot-actuator-crosscheck/run.py > build/pilot-actuators-rust-independent-check.log
```

The driver writes `build/pilot-actuators-rust-independent-check.json`. Its exact original ignored driver is retained byte-for-byte as `run.py`; the receipt maps both paths. `result.json` and `stdout.log` are byte-for-byte copies of the successful original check. Reproduction verifies the current producer packet and reads retained results; it does not execute the full physical/numerical campaign again.

The current actuator manifest is `e7167302df17bd57de821fbc0bb8d35ad84b8d2fbd367fc445acf7810b474ee0`. All85 current calculation sources and every consumed actuator payload are hash-bound. The Python baseline study is checked against its archived manifest/history, with all eight immutable baseline files recorded as provenance inputs. Those historical source bytes are retained in that baseline's `sources.tar.gz`; they are not required to equal the current Rust configuration.

The conservative post-pose force bounds are14.272551/14.270435/14.268295kN, below the declared20kN study screen. The largest retained Python/Rust sampled longitudinal difference is0.639micrometres. These are observations for an assumed virtual magnetic plant. Magnetic core/window geometry, measured maps, lateral/guidance dynamics, cooling, joined structures and hardware timing remain unqualified. No engineering, safety, manufacturing or physical acceptance is granted.
