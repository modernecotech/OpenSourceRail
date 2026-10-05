# Retained TLC assurance executable

`tla2tools-1.8.0.jar` is the exact executable used by the retained TACS formal
evidence and the bounded-model CI job. The filename records the upstream
release asset, rather than inferring its internal version: its manifest records
TLC 2.0, build 2026-10-04 and source revision
`1813307068bbc5759a441df820f3f548948d6b7a`.

| Identity | Value |
|---|---|
| Bytes | 4,500,445 |
| SHA256 | `c2fe4e56e43bde19f213b4a7e441d037297fda733e503579623e859b79348239` |
| Published release SHA1 | `93d304f9c77595c8728c3ad939ed65b7a7149d1e` |

The [upstream release](https://github.com/tlaplus/tlaplus/releases/tag/v1.8.0)
published the matching SHA1. On 5 October 2026 its download asset was replaced:
the replacement has SHA256
`411ab54221cf0c9fa7ae18f07a3e0ebbdf9e5ba6254b79017e7007f1feb44e89`
and manifest revision `610da1d073754ea8e0dd3c2af3eae8011d20191a`.
That replacement is not adopted.

CI copies this retained input to its build directory, verifies the original
SHA256, then runs [the assurance consumer](../../../tools/automation/tacs_assurance.py).
The verification constant and model remain unchanged. Tool upgrades require
verified upstream provenance and a new actual model execution.

[License.txt](License.txt) is extracted unchanged from this JAR. Its embedded
third-party notices also remain intact. This executable is a reproducible
assurance input, not a deployed railway component or physical-release evidence.
