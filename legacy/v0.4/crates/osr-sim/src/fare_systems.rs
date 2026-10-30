//! Deterministic station fare-system software-in-the-loop workload.
//!
//! One representative single-ride purchase and tap is generated per station
//! per minute. This is a controller/settlement integration workload, not a
//! passenger-demand forecast. It executes the real TVM token issuer, AFC gate
//! validator, and AFC back-office reconciler against a shared signed token.

use std::collections::BTreeSet;

use osr_afc::{afc_evaluate, AfcInputs, AfcParams, AfcState, Decision, GateCommand};
use osr_afc_backoffice::{ingest_events, AfcBackofficeParams, AfcBackofficeState};
use osr_core::Network;
use osr_tvm::{tvm_evaluate, PaymentMethod, Product, TvmInputs, TvmOutcome, TvmState};
use serde::{Deserialize, Serialize};

use crate::fault::FaultEngine;

const TRANSACTION_INTERVAL_S: u32 = 60;
const SHARED_FARE_SECRET: &[u8] = b"osr-sim-fare-key-v1";

#[derive(Clone, Debug)]
struct FareStationShadow {
    station_id: u32,
    gate: AfcState,
    tvm: TvmState,
}

#[derive(Clone, Debug)]
pub struct FareSystemsShadow {
    stations: Vec<FareStationShadow>,
    gate_params: AfcParams,
    backoffice_params: AfcBackofficeParams,
    backoffice: AfcBackofficeState,
    blacklist: BTreeSet<u32>,
    summary: FareSystemsSummary,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct FareSystemsSummary {
    pub station_count: u32,
    pub gate_controller_ticks: u64,
    pub tvm_purchase_attempts: u64,
    pub tickets_issued: u64,
    pub tickets_denied: u64,
    pub tvm_sales_cents: u64,
    pub gate_grants: u64,
    pub gate_denials: u64,
    pub gate_open_ticks: u64,
    pub ledger_entries: u64,
    pub settled_fare_cents: u64,
    pub fraud_flags_raised: u64,
    pub flagged_accounts: u32,
}

impl FareSystemsShadow {
    #[must_use]
    pub fn new(network: &Network) -> Self {
        let stations = network
            .stations
            .keys()
            .map(|station| FareStationShadow {
                station_id: station.0.min(u64::from(u32::MAX)) as u32,
                gate: AfcState::default(),
                tvm: TvmState::default(),
            })
            .collect::<Vec<_>>();
        Self {
            summary: FareSystemsSummary {
                station_count: stations.len().min(u32::MAX as usize) as u32,
                ..FareSystemsSummary::default()
            },
            stations,
            gate_params: AfcParams::metro_default(),
            backoffice_params: AfcBackofficeParams {
                fare_cents: Product::SingleRide.price_cents(),
                ..AfcBackofficeParams::default_metro()
            },
            backoffice: AfcBackofficeState::default(),
            blacklist: BTreeSet::new(),
        }
    }
}

pub fn fare_systems_tick(shadow: &mut FareSystemsShadow, faults: &FaultEngine, sim_time_s: u32) {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let transact = sim_time_s % TRANSACTION_INTERVAL_S == 0;
    let mut events = Vec::new();

    for station in &mut shadow.stations {
        let mut scanned_token = None;
        if transact {
            shadow.summary.tvm_purchase_attempts =
                shadow.summary.tvm_purchase_attempts.saturating_add(1);
            let output = tvm_evaluate(
                &station.tvm,
                &TvmInputs {
                    now_ns,
                    issuing_station_id: station.station_id,
                    product: Product::SingleRide,
                    payment: PaymentMethod::MobileMoney {
                        confirmation_code: now_ns ^ u64::from(station.station_id),
                    },
                    account_id: station.station_id,
                    secret: SHARED_FARE_SECRET,
                },
            );
            station.tvm = output.state;
            match output.outcome {
                TvmOutcome::Issued { mut token, .. } => {
                    shadow.summary.tickets_issued = shadow.summary.tickets_issued.saturating_add(1);
                    shadow.summary.tvm_sales_cents = shadow
                        .summary
                        .tvm_sales_cents
                        .saturating_add(u64::from(Product::SingleRide.price_cents()));
                    if faults.fare_token_tampered_at(station.station_id) {
                        token.signature[0] ^= 1;
                    }
                    scanned_token = Some(token);
                }
                TvmOutcome::Denied(_) => {
                    shadow.summary.tickets_denied = shadow.summary.tickets_denied.saturating_add(1);
                }
            }
        }

        let output = afc_evaluate(
            &station.gate,
            &AfcInputs {
                now_ns,
                gate_station_id: station.station_id,
                scanned_token,
                secret: SHARED_FARE_SECRET,
                blacklist: &shadow.blacklist,
            },
            &shadow.gate_params,
        );
        station.gate = output.state;
        shadow.summary.gate_controller_ticks =
            shadow.summary.gate_controller_ticks.saturating_add(1);
        if output.gate == GateCommand::Open {
            shadow.summary.gate_open_ticks = shadow.summary.gate_open_ticks.saturating_add(1);
        }
        if let Some(event) = output.event {
            match event.decision {
                Decision::Grant => {
                    shadow.summary.gate_grants = shadow.summary.gate_grants.saturating_add(1);
                }
                Decision::Deny(_) => {
                    shadow.summary.gate_denials = shadow.summary.gate_denials.saturating_add(1);
                }
            }
            events.push(event);
        }
    }

    let output = ingest_events(&shadow.backoffice, &events, &shadow.backoffice_params);
    shadow.summary.ledger_entries = shadow
        .summary
        .ledger_entries
        .saturating_add(output.ledger.len() as u64);
    shadow.summary.settled_fare_cents = shadow.summary.settled_fare_cents.saturating_add(
        output
            .ledger
            .iter()
            .map(|entry| u64::from(entry.amount_cents))
            .sum::<u64>(),
    );
    shadow.summary.fraud_flags_raised = shadow
        .summary
        .fraud_flags_raised
        .saturating_add(output.new_flags.len() as u64);
    shadow.backoffice = output.state;
    shadow.summary.flagged_accounts = shadow
        .backoffice
        .flagged_accounts
        .len()
        .min(u32::MAX as usize) as u32;
}

#[must_use]
pub fn summarise(shadow: &FareSystemsShadow) -> FareSystemsSummary {
    shadow.summary.clone()
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{Station, StationId};

    fn network() -> Network {
        let mut network = Network::default();
        for id in 1..=2 {
            network.stations.insert(
                StationId::new(id),
                Station {
                    id: StationId::new(id),
                    name: format!("Station {id}"),
                    charging_power_kw: 0,
                    dwell_seconds: 30,
                    is_terminal: false,
                    is_depot: false,
                },
            );
        }
        network
    }

    #[test]
    fn nominal_purchase_tap_and_settlement_reconcile() {
        let mut shadow = FareSystemsShadow::new(&network());
        fare_systems_tick(&mut shadow, &FaultEngine::default(), 0);
        let summary = summarise(&shadow);
        assert_eq!(summary.tickets_issued, 2);
        assert_eq!(summary.gate_grants, 2);
        assert_eq!(summary.ledger_entries, 2);
        assert_eq!(summary.tvm_sales_cents, summary.settled_fare_cents);
    }
}
