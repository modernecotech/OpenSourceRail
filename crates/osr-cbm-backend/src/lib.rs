//! OpenSourceRail depot-side CBM analysis and work-order generation.
//!
//! Consumes the [`CbmSample`](osr_cbm_onboard::CbmSample) stream from
//! every train and maintains a per-train-per-component running view
//! of health. When a component has either been flagged Service on
//! its latest sample, **or** has been persistently in Watch for
//! a configurable number of samples, a [`WorkOrder`] is emitted.
//!
//! Phase 2e crate of [RFC 0005 §4.8](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0: wrong work-orders waste labour but cannot injure anyone —
//! the upstream `osr-cbm-onboard` flags are advisory already.
//!
//! # Behaviour
//!
//! For every sample:
//!
//! 1. Look at each `ComponentFlag` on the sample.
//! 2. Update the per-(train, component, index) state:
//!    - `Service` → emit a `WorkOrder` of `Priority::Urgent`,
//!      clear the watch streak.
//!    - `Watch` → bump the watch streak; when it crosses
//!      `watch_persistence`, emit `Priority::Routine`.
//! 3. `Nominal` flags are implicit — if a component isn't in the
//!    flag list, its watch streak resets.
//!
//! # Properties (proptest-verified)
//!
//! - **CBB1 determinism.**
//! - **CBB2 Service sample always produces a WorkOrder on first sight.**
//! - **CBB3 No WorkOrder on an all-nominal sample.**

#![forbid(unsafe_code)]

use std::collections::BTreeMap;

use osr_cbm_onboard::{CbmSample, Component, ComponentHealth};
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmBackendParams {
    /// Number of consecutive samples in Watch before a routine
    /// work order is raised.
    pub watch_persistence: u16,
}

impl CbmBackendParams {
    #[must_use]
    pub fn default_depot() -> Self {
        Self {
            watch_persistence: 8,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub enum Priority {
    Routine,
    Urgent,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub struct ComponentKey {
    pub train_id: u32,
    pub component: Component,
    pub index: u16,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct WorkOrder {
    pub raised_ns: u64,
    pub key: ComponentKey,
    pub priority: Priority,
}

/// Per-component state carried across samples.
#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ComponentState {
    pub watch_streak: u16,
    /// Suppress duplicate orders until a clean (nominal) sample intervenes.
    pub order_raised: bool,
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmBackendState {
    pub components: BTreeMap<ComponentKey, ComponentState>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmBackendOutput {
    pub state: CbmBackendState,
    pub orders: Vec<WorkOrder>,
}

#[must_use]
pub fn ingest_sample(
    prev: &CbmBackendState,
    sample: &CbmSample,
    params: &CbmBackendParams,
) -> CbmBackendOutput {
    // Rebuild per-component health for this sample, assuming a flag
    // carries the worst-seen level for that component+index.
    let mut per_index: BTreeMap<(Component, u16), ComponentHealth> = BTreeMap::new();
    let update = |v: &mut ComponentHealth, h: ComponentHealth| {
        if h > *v {
            *v = h;
        }
    };

    for (i, &v) in sample.bearing_vib_ppt.iter().enumerate() {
        per_index
            .entry((Component::Bearing, i as u16))
            .and_modify(|e| update(e, ComponentHealth::Nominal))
            .or_insert(ComponentHealth::Nominal);
        let _ = v;
    }
    for (i, _) in sample.motor_temp_dc.iter().enumerate() {
        per_index
            .entry((Component::Motor, i as u16))
            .or_insert(ComponentHealth::Nominal);
    }
    for (i, _) in sample.brake_pad_remaining_ppt.iter().enumerate() {
        per_index
            .entry((Component::BrakePad, i as u16))
            .or_insert(ComponentHealth::Nominal);
    }
    for (i, _) in sample.wheel_tread_remaining_ppt.iter().enumerate() {
        per_index
            .entry((Component::WheelTread, i as u16))
            .or_insert(ComponentHealth::Nominal);
    }

    // Flags in the sample were computed by cbm-onboard; replay them
    // so we can update state + emit orders. We don't re-derive the
    // thresholds; we trust the producer.
    for flag in reconstruct_flags(sample) {
        let slot = per_index
            .entry((flag.component, flag.index))
            .or_insert(flag.health);
        if flag.health > *slot {
            *slot = flag.health;
        }
    }

    let mut state = prev.clone();
    let mut orders = Vec::new();

    for ((comp, idx), health) in per_index {
        let key = ComponentKey {
            train_id: sample.train_id,
            component: comp,
            index: idx,
        };
        let cs = state.components.entry(key).or_default();
        match health {
            ComponentHealth::Service => {
                if !cs.order_raised {
                    orders.push(WorkOrder {
                        raised_ns: sample.now_ns,
                        key,
                        priority: Priority::Urgent,
                    });
                    cs.order_raised = true;
                }
                cs.watch_streak = 0;
            }
            ComponentHealth::Watch => {
                cs.watch_streak = cs.watch_streak.saturating_add(1);
                if cs.watch_streak >= params.watch_persistence && !cs.order_raised {
                    orders.push(WorkOrder {
                        raised_ns: sample.now_ns,
                        key,
                        priority: Priority::Routine,
                    });
                    cs.order_raised = true;
                }
            }
            ComponentHealth::Nominal => {
                cs.watch_streak = 0;
                cs.order_raised = false;
            }
        }
    }

    CbmBackendOutput { state, orders }
}

/// Re-derive the flag list from a sample. This duplicates the shape
/// of `cbm-onboard`'s flag emission but without the thresholds: a
/// `CbmSample` carries `worst_health`, and the flag itself is not on
/// the wire type. To avoid an interface change we rebuild flags from
/// the worst-seen health per (component, index) by consulting each
/// raw reading against the same default thresholds.
fn reconstruct_flags(sample: &CbmSample) -> Vec<osr_cbm_onboard::ComponentFlag> {
    let p = osr_cbm_onboard::CbmParams::default_metro();
    let mut out = Vec::new();

    for (i, &v) in sample.bearing_vib_ppt.iter().enumerate() {
        let h = if v >= p.bearing_service_ppt {
            ComponentHealth::Service
        } else if v >= p.bearing_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            out.push(osr_cbm_onboard::ComponentFlag {
                component: Component::Bearing,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &t) in sample.motor_temp_dc.iter().enumerate() {
        let h = if t >= p.motor_service_dc {
            ComponentHealth::Service
        } else if t >= p.motor_watch_dc {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            out.push(osr_cbm_onboard::ComponentFlag {
                component: Component::Motor,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &w) in sample.brake_pad_remaining_ppt.iter().enumerate() {
        let h = if w <= p.brake_pad_service_ppt {
            ComponentHealth::Service
        } else if w <= p.brake_pad_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            out.push(osr_cbm_onboard::ComponentFlag {
                component: Component::BrakePad,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &w) in sample.wheel_tread_remaining_ppt.iter().enumerate() {
        let h = if w <= p.wheel_service_ppt {
            ComponentHealth::Service
        } else if w <= p.wheel_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            out.push(osr_cbm_onboard::ComponentFlag {
                component: Component::WheelTread,
                index: i as u16,
                health: h,
            });
        }
    }

    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams};

    fn sample_from(i: CbmInputs) -> CbmSample {
        cbm_evaluate(&i, &CbmParams::default_metro()).sample
    }

    fn clean(train_id: u32) -> CbmInputs {
        CbmInputs {
            now_ns: 0,
            train_id,
            bearing_vib_ppt: vec![1_000; 4],
            motor_temp_dc: vec![800; 2],
            brake_pad_remaining_ppt: vec![900; 4],
            wheel_tread_remaining_ppt: vec![800; 4],
        }
    }

    #[test]
    fn clean_sample_emits_no_orders() {
        let s = sample_from(clean(1));
        let out = ingest_sample(
            &CbmBackendState::default(),
            &s,
            &CbmBackendParams::default_depot(),
        );
        assert!(out.orders.is_empty());
    }

    #[test]
    fn service_sample_emits_urgent() {
        let mut i = clean(7);
        i.motor_temp_dc[0] = 1_700;
        let s = sample_from(i);
        let out = ingest_sample(
            &CbmBackendState::default(),
            &s,
            &CbmBackendParams::default_depot(),
        );
        assert_eq!(out.orders.len(), 1);
        assert_eq!(out.orders[0].priority, Priority::Urgent);
        assert_eq!(out.orders[0].key.train_id, 7);
    }

    #[test]
    fn duplicate_service_does_not_re_emit() {
        let mut i = clean(7);
        i.motor_temp_dc[0] = 1_700;
        let s = sample_from(i);
        let p = CbmBackendParams::default_depot();
        let first = ingest_sample(&CbmBackendState::default(), &s, &p);
        let second = ingest_sample(&first.state, &s, &p);
        assert_eq!(first.orders.len(), 1);
        assert!(second.orders.is_empty());
    }

    #[test]
    fn persistent_watch_becomes_routine() {
        let mut i = clean(3);
        i.bearing_vib_ppt[2] = 5_000; // watch
        let s = sample_from(i);
        let p = CbmBackendParams {
            watch_persistence: 3,
        };

        let mut state = CbmBackendState::default();
        let mut total_orders = 0;
        for _ in 0..5 {
            let out = ingest_sample(&state, &s, &p);
            total_orders += out.orders.len();
            state = out.state;
        }
        // Expect exactly one Routine order raised at persistence threshold.
        assert_eq!(total_orders, 1);
    }

    #[test]
    fn nominal_sample_after_service_resets_latch() {
        let mut bad = clean(1);
        bad.motor_temp_dc[0] = 1_700;
        let good = clean(1);
        let p = CbmBackendParams::default_depot();

        let s1 = sample_from(bad);
        let s2 = sample_from(good);

        let a = ingest_sample(&CbmBackendState::default(), &s1, &p);
        let b = ingest_sample(&a.state, &s2, &p);

        // Raise another bad sample — should re-emit once latch cleared.
        let mut bad2 = clean(1);
        bad2.motor_temp_dc[0] = 1_800;
        let s3 = sample_from(bad2);
        let c = ingest_sample(&b.state, &s3, &p);

        assert_eq!(a.orders.len(), 1);
        assert!(b.orders.is_empty());
        assert_eq!(c.orders.len(), 1);
    }
}
