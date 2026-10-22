# Active-control and launch construction execution evidence

This folder retains current-source checks for the support-current and station
launch construction build-out. Receipts record actual commands, exit status,
source hashes and raw output. Publication and simulation do not close engineering
or physical acceptance gates. The executed construction package is at
[drive-construction](../../../docs/design-engine/ferrite-maglev/drive-construction/README.md).

Retained browser captures: [report desktop](report-desktop.png),
[report mobile](report-mobile.png), [Workbench desktop](workbench-desktop.png)
and [Workbench mobile](workbench-mobile.png). The [summary](summary.json)
distinguishes 102 unique passing Python tests from the initial concurrent lock
failure and its isolated rerun. [Checksums](checksums.json) cover every retained
file; the controlled installer interruption is recorded separately.

`run-check.py` executes named checks with before/after source receipts. The
`body-axial-*` files retain a fresh full-AW3 sensitivity without overwriting the
previous source epoch. Its reproduction instructions preserve the original
driver path. No partial CAD stock is substituted for equipped vehicle mass.

The new current/commutation layer uses average-voltage coupon plants and
synthetic frames. Magnetic force maps, complete coil and board geometry,
protection timing, physical firmware/HAL, shared fields, actuator dynamics and
independent acceptance remain open. Supplier references are capabilities rather
than quotations or confirmed order origins. All release flags remain false.
