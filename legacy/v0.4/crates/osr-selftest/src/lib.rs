//! Per-role post-assembly self-test (RFC 0019 §6).
//!
//! A commissioning tool the DIY plug-and-play assembly path
//! relies on: after flashing the SD card + wiring the board, the
//! operator runs `osr-selftest --role <role>` and gets a PASS /
//! FAIL per named check plus a one-line remediation for any
//! failure.
//!
//! The tool is not a replacement for the Kani harnesses, proptests,
//! or GSN safety case — those establish that the *software* is
//! correct by construction. `osr-selftest` establishes that the
//! *specific bolted-together unit* in front of you is functional.
//! It's the per-unit evidence stamp that the custom-PCB path gets
//! from factory flying-probe tests.
//!
//! # Checks
//!
//! Each role has a list of named checks. A check returns an
//! [`Outcome`] — `Pass`, `Fail(reason)`, or `Skip(reason)`. The
//! tool prints them in order with a final roll-up.
//!
//! # Exit codes
//!
//! - `0` — every check PASSed (or SKIPped with a reason).
//! - `1` — at least one check FAILed.
//! - `2` — invalid role / argument error.

#![forbid(unsafe_code)]

pub mod roles;
pub mod runtime;

pub use roles::Role;
pub use runtime::{Check, CheckFn, Outcome, Report};
