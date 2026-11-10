# Native GIS run07 readiness audit

## Disposition

**HOLD — the retained run07 proposal is data-only, source-stale for this closure branch, and not admitted. No run07 directory, browser, project editor, supervisor or numerical worker was started by this audit.** The full native GIS return-path gate remains open.

The private proposal is `osr-immutable-private-proposed-packet/1`, evaluation ID `2c27d760c83f184e8efacae792028aeba980860f4493fe636fb50d40c3918921`, request ID `7a6d458c4ed94f21097ddc26440cc5adfa7e14c2499155e7154d4be8270a35e4`, and descriptor SHA-256 `c02ea806c96fc91accb6780a2c58c48739ec640f20bd6cb852d6d5be58c2f1ba`. Its private manifest SHA-256 is `d047b71fa28e3d26968b45c1468939a330d651a6bfdea2f69cb42c384b5d90a2`; it seals 22 payloads totaling 2,073,333 bytes and records `UNEXECUTED_NOT_ADMITTED`, `authorization_created=false`, and `workload_launched=false`.

## Why the proposed run cannot be used

- It targets source head `897e36510812966bcef0e04fddebdd98bedee4af`, while the closure branch is `661b8414a5f77a4184978ddd70d31b22f2545800`.
- The descriptor contains 1,221 source pins. Six Git source files differ between the old source head and this closure branch: three compact-drive files and three city-service/evaluator files. A seventh checked path is a deliberate packaged browser-helper overlay whose bytes differ from the source-tree helper; it is an overlay delta, not Git source-head drift. The changed city evaluator sources mean the retained cached city result cannot be silently rebound to current code.
- The proposal `execution-request.json` explicitly records that the v2 checker/single-shot supervisor and fresh whole-source, tool-delta and runtime reviews are absent; authorization is false (execution-request SHA-256 `7f820c4d77c4af081b7eeddbe313a2aacdd38132e589763ffac55f84523be15a`). The run07 target directory is absent and the run06 authorization was consumed. A new exact-source/cache plan, reviewed supervisor, fresh review set and separate exact coordinator authorization would be needed before any attempt.
- The guard and supervisor code assume `.git` is a directory; this isolated closure worktree has a `.git` file. A new package must support and verify the actual worktree layout.
- The proposed bwrap command would stage the main checkout read-only and place run output under a private path, but the missing supervisor means the proposed containment has not been established by execution.
- The proposal covers one cached native-project upload, cached-job authentication and re-export. It does not run a native GIS editor or fresh city solver and cannot alone satisfy the full edit → geometry validation → service/fleet/cost/delivery recalculation → export → second native-edit loop.

## Resource preflight

The [local preflight receipt](native-gis-run07-preflight-20261110.json) records a 2026-11-10 00:08:40 UTC sample: 5,292,199,936 bytes free disk (4.93 GiB) and 12,643,828 KiB available memory. The proposal requires an 8 GiB reserve for both disk and `MemAvailable`; memory passes this sample, disk does not. The run remains held. Disk and memory must be rechecked immediately before any later admission.

## Audit provenance and limits

The retained readiness review is ID `309fd61d82d602399bcc2df008e28a8118c38f1fd21d553f9fd8d051ff97eafe`, review JSON SHA-256 `eafbafdc129247bcddcf74a77bac26921088d637bad0051f29ca5a5a6ce1a753`; it documents the consumed run06 failure and conditions for a later attempt. The retained packaging review is ID `87d10fa21dc9fcf77685d4e367fb65fa94a249f65b80cb7d072314141e586343`, review JSON SHA-256 `744cb2a24557f2766797d75242d9022af4eca267dbd7858b6570d7141d3eaaae`; it verifies the old missing-overlay root cause and packaging checklist. Neither report executed run07. The source-drift comparison is from this continuation's read-only comparison against closure HEAD `661b8414a5f77a4184978ddd70d31b22f2545800`; the preflight has its own recorded command outputs above.

This was a read-only source and resource audit without an OS sandbox. It grants neither run admission nor GIS, physical, engineering, manufacturing, operating or release acceptance.
