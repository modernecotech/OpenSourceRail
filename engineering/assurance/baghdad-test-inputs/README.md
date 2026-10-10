# Current Baghdad test inputs

This snapshot contains the exact current operations, solver and GIS inputs used
by repository tests. Its manifest binds every member, archive part and producer
source by SHA-256. It is separate from the historical Baghdad proposal snapshot.
Physical and operating release remain false.

Restore a clean checkout with:

```sh
tools/automation/osr-python tools/automation/bootstrap_baghdad_tests.py
```

After a deliberate input update, regenerate from current local files with:

```sh
tools/automation/osr-python tools/automation/pack-baghdad-test-inputs.py
```

The bootstrap preserves differing local inputs and rejects changed source,
archive or member receipts. Archive parts remain below 50 MiB.
