//! Charging and passenger exchange never bypass the physical departure interlock.
#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub enum StationPhase {
    Approach,
    Secured,
    Exchange,
    Isolating,
    Ready,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationInputs {
    pub stopped_and_berthed: bool,
    pub secured: bool,
    pub aligned: bool,
    pub doors_closed_and_locked: bool,
    pub charger_isolated: bool,
    pub connector_clear: bool,
    pub charger_healthy: bool,
    pub charge_complete: bool,
    pub energy_sufficient: bool,
    pub departure_requested: bool,
    pub emergency_departure_requested: bool,
    pub authority_valid: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationOutput {
    pub phase: StationPhase,
    pub charging_enable: bool,
    pub passenger_exchange_enable: bool,
    pub isolate_charger: bool,
    pub departure_permitted: bool,
}

pub const fn physical_departure_permitted(i: StationInputs) -> bool {
    i.doors_closed_and_locked
        && i.charger_isolated
        && i.connector_clear
        && i.energy_sufficient
        && i.authority_valid
}

pub fn station_step(phase: StationPhase, i: StationInputs) -> StationOutput {
    let phase = match phase {
        StationPhase::Approach if i.stopped_and_berthed && i.secured => StationPhase::Secured,
        StationPhase::Secured
            if i.stopped_and_berthed
                && i.secured
                && i.aligned
                && i.charger_healthy
                && !i.departure_requested
                && !i.emergency_departure_requested =>
        {
            StationPhase::Exchange
        }
        StationPhase::Exchange
            if !i.stopped_and_berthed
                || !i.secured
                || !i.aligned
                || !i.charger_healthy
                || i.charge_complete
                || i.departure_requested
                || i.emergency_departure_requested =>
        {
            StationPhase::Isolating
        }
        StationPhase::Isolating if physical_departure_permitted(i) => StationPhase::Ready,
        StationPhase::Ready if !physical_departure_permitted(i) => StationPhase::Isolating,
        other => other,
    };
    let exchange = phase == StationPhase::Exchange && i.stopped_and_berthed && i.secured;
    StationOutput {
        phase,
        charging_enable: exchange && i.aligned && i.charger_healthy,
        passenger_exchange_enable: exchange,
        isolate_charger: matches!(phase, StationPhase::Isolating | StationPhase::Ready),
        departure_permitted: phase == StationPhase::Ready && physical_departure_permitted(i),
    }
}
