//! Newtype wrappers over `u64` for the identifiers in the domain.
//!
//! The wire schema uses `fixed64`; at the Rust level we want type-safety so
//! a `StationId` cannot be confused with a `SwitchId` even though both are
//! u64 underneath.

use serde::{Deserialize, Serialize};
use std::fmt;

macro_rules! define_id {
    ($name:ident, $prefix:literal) => {
        #[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub u64);

        impl $name {
            pub const fn new(v: u64) -> Self {
                Self(v)
            }
        }

        impl fmt::Debug for $name {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                write!(f, "{}{}", $prefix, self.0)
            }
        }

        impl fmt::Display for $name {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                write!(f, "{}{}", $prefix, self.0)
            }
        }
    };
}

define_id!(TrainId, "T");
define_id!(StationId, "ST");
define_id!(SectionId, "SEC");
define_id!(SwitchId, "SW");
define_id!(RouteId, "R");
define_id!(EntityId, "E");
define_id!(EntryId, "L");
define_id!(RegionId, "RG");
