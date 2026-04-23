# RFC 0017 — Cybersecurity: message authentication on the safety log

**Status:** accepted · 2026-04-23.
**Authors:** OSR project.
**Complements:** [RFC 0001](0001-track-state-consensus.md) (consensus),
[RFC 0005](0005-sbc-software-architecture.md) §4.9 (crate map).
**Amends:** `osr-crypto` (adds ed25519), `osr-interlocking` (envelope
on `Entry`), consensus wire format.

## 1. Purpose

Every entry on the track-state consensus log carries safety-critical
authority — a forged `MaintenanceOverride` or `SectionIntrusion::Clear`
could unlock a blocked section and put a train in front of a work
crew. Today the protobuf schema reserves a `leader_signature` field
but the code path that would *verify* it is not implemented: entries
are trusted because they came from a running process in tree.

This RFC closes that gap. Every entry on the committed log is
signed by the originating entity (train, wayside controller,
dispatcher console) and every consumer verifies the signature before
applying the entry to derived state.

## 2. Threat model

In scope:

- **Forged entries.** An attacker with network access to the
  consensus cluster proposes a crafted `SectionIntrusion::Clear`
  or a fake `SwitchObservation` hoping the interlocking accepts it.
- **Replay.** An attacker re-submits an old legitimate entry to
  confuse the derived state (e.g., replay a `RouteRelease`).
- **Key compromise.** A single wayside box is physically captured;
  its key is now under the attacker's control.

Out of scope for v1:

- **Side-channel attacks** on the signing key (handled at hardware
  level by the ATECC608B trust anchors on T-ECU/S, W-SBC, S-SBC).
- **Quantum-era attacks.** Ed25519 is 128-bit-classical-secure; a
  post-quantum migration is an RFC 0017.1 candidate once NIST
  finalises a PQ signature scheme in the rail-relevant performance
  bracket.
- **TLS session setup** on TRG and backhaul links — that's RFC 0018
  (not yet drafted).

## 3. Design

### 3.1 Signature scheme

**Ed25519** — curve25519 in the twisted-Edwards form, per RFC 8032.

- **64-byte signatures, 32-byte keys.** Small enough to attach to
  every consensus entry without bloating the wire format.
- **Batch verification available** — a consensus cluster can
  verify N entries in sub-N time when under load.
- **Deterministic signatures** — no per-signature nonce required
  (eliminates the ECDSA Sony-PS3 class of bugs).
- **Open-source reference implementations** — `ed25519-dalek` in
  Rust is widely audited and actively maintained.

### 3.2 Entity keys

Every entity (train, wayside box, station, OCC console) holds **one
long-lived ed25519 keypair** in its ATECC608B secure element.
Public keys are published in a per-deployment key registry at
bootstrap; private keys never leave the secure element.

Key ids mirror the existing `EntityId` scheme so the
`Entry.leader_signature` maps one-to-one to `Entry` authorship.

### 3.3 Envelope

A signed entry is encoded as:

```
SignedEntry {
    entry_bytes: Vec<u8>,   // serde-json serialisation of Entry
    issuer: EntityId,       // which entity signed
    sig: [u8; 64],          // ed25519 signature over entry_bytes
}
```

Verification:

1. Look up `issuer` in the `KeyRegistry`. If absent → reject
   (`VerifyError::UnknownIssuer`).
2. Verify `sig` over `entry_bytes` with the registry's public key.
   If invalid → reject (`VerifyError::BadSignature`).
3. Otherwise return OK, and only then deserialise and apply the
   entry.

Verification is **before** deserialisation so a hostile payload
can't exploit a parser bug before the signature check.

### 3.4 Replay protection

Each `Entry` already carries `entry_id` (monotonic) and
`timestamp_ns` (PTP-synced). The derived-state fold is idempotent
in `entry_id`: an entry already applied is a no-op when re-applied.
Replay does not trick the derived state into a bad configuration.

For completeness, the consensus layer additionally rejects entries
whose `timestamp_ns` is more than **60 seconds** older than the
cluster's current leader clock — a hard freshness check.

### 3.5 Key rotation (v2)

v1 treats keys as long-lived. v2 introduces a `KeyRotation` entry
type that transfers authority from an old key to a new one; the
registry follows the latest rotation. Deferred because it adds
operational complexity that is not needed for first-article
deployment.

## 4. What this RFC delivers (v1)

- **`osr-crypto`** extended with ed25519 sign + verify primitives.
- **`osr-secbus`** — new SIL-2 crate with `KeyRegistry`,
  `SignedBytes` envelope, and the verification API.
- **Three SIL-2 properties** (S1–S3) with Kani harnesses + proptest.
- **GSN goals G25–G27** on the safety case, anchored to the
  properties.

## 5. Safety properties (S1–S3)

- **S1 (deterministic verify):** `verify(pk, msg, sig)` is a pure
  function — identical inputs → identical output.
- **S2 (reject bad signature):** any single-bit mutation of `sig`
  causes `verify` to return `false`.
- **S3 (reject missing issuer):** a `SignedBytes` whose `issuer` is
  not in the `KeyRegistry` rejects with `VerifyError::UnknownIssuer`.

## 6. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `osr-crypto` ed25519 primitives + `osr-secbus` crate with key registry, envelope, verify; S1–S3 Kani + proptest; GSN G25–G27 close. (done 2026-04-23) | v0 |
| **v2** | Integrate into the consensus wire layer — every entry proposed to the cluster is signed; every entry committed is verified; unverified entries are dropped by the receiver before they hit derived state | v1, RFC 0001 |
| **v3** | Sim integration: fault-injection for forged / tampered entries, demonstrating they're rejected end-to-end | v2 |
| **v4** | Key rotation (`KeyRotation` entry type) + deployment tooling to mint and distribute keys | v2 |
| **v5** | Hardware integration: ATECC608B provisioning pipeline; per-entity key generation + transfer at factory | v2, RFC 0007 |

## 7. Relationship to existing RFCs

- **RFC 0001** (consensus) — adds the verify step between receive
  and apply; no changes to Raft itself.
- **RFC 0005** (software architecture) — `osr-secbus` joins the
  Phase 2f infrastructure crate family alongside `osr-crypto` and
  `osr-historian`.
- **RFC 0007** (hardware) — the ATECC608B role is already in the
  T-ECU/S + T-OBS + W-SBC specs; this RFC defines what that chip
  actually signs.
- **RFC 0015 + RFC 0016** — every `SectionIntrusion` and
  `MaintenanceOverride` is now signed by its issuing W-SBC
  (RFC 0016) or OCC console (RFC 0013 S5). Prevents the forged-
  `Clear`-verdict attack that would otherwise defeat the safety
  gate.

## 8. What this RFC does NOT include

- TLS on TRG radios or OCC backhaul — RFC 0018 candidate.
- Encryption of the log at rest — the entries are integrity-
  protected; confidentiality is not claimed.
- Perfect-forward-secrecy session keys — long-lived ed25519 keys
  are sufficient for entry authentication; PFS is a session-layer
  concern (RFC 0018).
- Post-quantum migration — deferred pending NIST standardisation
  in a performance bracket suitable for embedded rail controllers.
