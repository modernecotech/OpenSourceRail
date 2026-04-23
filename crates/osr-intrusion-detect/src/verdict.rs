//! Verdict severity for the wayside intrusion detector.

use serde::{Deserialize, Serialize};

/// Three verdicts an [`crate::evaluate`] call can emit, ordered from
/// least to most restrictive:
/// `Clear < Unknown < Present`.
///
/// `Unknown` is *more* restrictive than `Clear`: the interlocking
/// withholds MA on a section whose verdict is anything other than
/// `Clear`. This is the fail-restrictive property (I2).
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub enum IntrusionVerdict {
    /// No intrusion detected; every safety-primary sensor is fresh and
    /// reports no in-profile target. MA may cross this section.
    Clear,

    /// At least one safety-primary sensor is stale or offline and no
    /// intrusion is confirmed. MA is withheld — a broken sensor does
    /// not imply safe track.
    Unknown,

    /// An intrusion is confirmed by a safety-primary sensor or a
    /// fence-line breach. MA is withheld; the dispatcher is alerted
    /// per RFC 0016 §7.1 S7.1.
    Present,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn severity_ordering_is_monotone() {
        assert!(IntrusionVerdict::Clear < IntrusionVerdict::Unknown);
        assert!(IntrusionVerdict::Unknown < IntrusionVerdict::Present);
    }
}
