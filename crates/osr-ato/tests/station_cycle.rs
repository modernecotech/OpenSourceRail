use osr_ato::station::*;
fn input() -> StationInputs {
    StationInputs {
        stopped_and_berthed: true,
        secured: true,
        aligned: true,
        doors_closed_and_locked: false,
        charger_isolated: false,
        connector_clear: false,
        charger_healthy: true,
        charge_complete: false,
        energy_sufficient: false,
        departure_requested: false,
        emergency_departure_requested: false,
        authority_valid: true,
    }
}
#[test]
fn full_exchange_isolation_and_departure_sequence_requires_all_proving() {
    let mut i = input();
    let a = station_step(StationPhase::Approach, i);
    assert_eq!(a.phase, StationPhase::Secured);
    let b = station_step(a.phase, i);
    assert!(b.charging_enable);
    assert!(b.passenger_exchange_enable);
    assert!(!b.departure_permitted);
    i.charge_complete = true;
    i.energy_sufficient = true;
    i.departure_requested = true;
    let c = station_step(b.phase, i);
    assert!(c.isolate_charger);
    assert!(!c.departure_permitted);
    i.charger_isolated = true;
    i.connector_clear = true;
    i.doors_closed_and_locked = true;
    let d = station_step(c.phase, i);
    assert!(d.departure_permitted);
    for field in 0..4 {
        let mut failed = i;
        match field {
            0 => failed.charger_isolated = false,
            1 => failed.connector_clear = false,
            2 => failed.doors_closed_and_locked = false,
            _ => failed.authority_valid = false,
        };
        assert!(!station_step(d.phase, failed).departure_permitted);
    }
}
#[test]
fn emergency_request_cannot_bypass_connected_charger_or_open_doors() {
    let mut i = input();
    i.emergency_departure_requested = true;
    i.energy_sufficient = true;
    let output = station_step(StationPhase::Exchange, i);
    assert!(output.isolate_charger);
    assert!(!output.charging_enable);
    assert!(!output.departure_permitted);
}
