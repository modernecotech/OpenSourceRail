# Supplementary pole-face and return-path study

This independent research appendix retains **225 executed case records**, including overlapping controls and rejected options. It does not represent 225 completed designs. No configuration is adopted, and all engineering, manufacturing and physical acceptance flags remain false.

The current candidate's thin return-path failure remains invariant. Narrower pole faces improve some conditional static results, but larger moving mass, uncertain flux topology and guidance current/thermal failures prevent a complete viable option in this study. The original candidate and city defaults remain unchanged.

- [Technical results and limitations](archive/README.md)
- [Comparison image](archive/research-comparison.png) and [summary](archive/summary.json)
- [Self-contained portable archive](pole-return-research.tar.gz)
- [Exact numerical replay log](archive-replay.log)
- [34 archive-integrity controls](verifier-hardening-tests.json) and [executed control driver](verifier-controls.py)
- [Completion receipt and artifact hashes](completion-receipt.json)

From the repository root, replay the archived numerical inputs with:

```sh
tools/automation/osr-python engineering/assurance/v053-pole-return-research/archive/verify.py --replay
```

The standalone verifier uses a temporary reconstructed tree and compares results exactly apart from elapsed time. NumPy and SciPy are required. To repeat the integrity controls, first copy this directory to a temporary location and run its control driver with Python bytecode writing disabled; that driver writes a fresh report beside its copied archive. The retained control driver is byte-identical to the executed `test_verifier_hardening.py`, with a filename that keeps it out of ordinary test discovery.

The portable archive has its own manifest and verifier. Reproducibility and checksum consistency do not establish authenticated engineering acceptance.
