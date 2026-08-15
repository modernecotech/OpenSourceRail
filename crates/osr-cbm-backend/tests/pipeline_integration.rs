//! Onboard CBM → T2G → backend → historian/analytics/work-order evidence.

use osr_analytics::basic_stats;
use osr_cbm_backend::{ingest_sample, CbmBackendParams, CbmBackendState, Priority};
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams, CbmSample};
use osr_historian::{Historian, Sample};
use osr_t2g::{t2g_evaluate, ActiveChannel, T2gInputs, T2gParams, T2gState};

#[test]
fn service_telemetry_reaches_history_analytics_and_one_work_order() {
    let onboard = cbm_evaluate(
        &CbmInputs {
            now_ns: 5_000_000_000,
            train_id: 17,
            bearing_vib_ppt: vec![1_000; 4],
            motor_temp_dc: vec![800, 1_700],
            brake_pad_remaining_ppt: vec![900; 4],
            wheel_tread_remaining_ppt: vec![800; 4],
        },
        &CbmParams::default_metro(),
    );

    // The transport boundary is bytes, not a shared in-process object.
    let wire = serde_json::to_vec(&onboard.sample).expect("encode CBM payload");
    let radio = t2g_evaluate(
        &T2gState::default(),
        &T2gInputs {
            now_ns: onboard.sample.now_ns,
            primary_signal: 80,
            backup_signal: 40,
            queued_payloads: 1,
            emergency_priority: false,
        },
        &T2gParams::default_metro(),
    );
    assert_eq!(radio.active, ActiveChannel::Primary);
    assert!(radio.transmit_now);
    let received: CbmSample = serde_json::from_slice(&wire).expect("decode CBM payload");
    assert_eq!(received.train_id, 17);

    let params = CbmBackendParams::default_depot();
    let first = ingest_sample(&CbmBackendState::default(), &received, &params);
    assert_eq!(first.orders.len(), 1);
    let order = first.orders[0];
    assert_eq!(order.priority, Priority::Urgent);
    assert_eq!(order.raised_ns, received.now_ns);
    assert_eq!(order.key.train_id, received.train_id);

    // Replayed telemetry is idempotent: it must not duplicate work orders.
    let replay = ingest_sample(&first.state, &received, &params);
    assert!(replay.orders.is_empty());

    let mut historian = Historian::default();
    for (index, temperature_dc) in received.motor_temp_dc.iter().enumerate() {
        historian.ingest(
            &format!("train.{}.motor.{index}.temp_dc", received.train_id),
            Sample {
                timestamp_ns: received.now_ns,
                value: f64::from(*temperature_dc),
            },
        );
    }
    let metric = "train.17.motor.1.temp_dc";
    let history = historian.query(metric, 0, u64::MAX);
    assert_eq!(history.len(), 1);
    let stats = basic_stats(&history);
    assert_eq!(stats.count, 1);
    assert_eq!(stats.max, Some(1_700.0));
}

#[test]
fn offline_transport_preserves_queue_and_creates_no_backend_state() {
    let radio = t2g_evaluate(
        &T2gState::default(),
        &T2gInputs {
            now_ns: 1_000_000_000,
            primary_signal: 0,
            backup_signal: 0,
            queued_payloads: 1,
            emergency_priority: false,
        },
        &T2gParams::default_metro(),
    );
    assert_eq!(radio.active, ActiveChannel::Offline);
    assert!(!radio.transmit_now);
    assert_eq!(radio.queue_remaining, 1);
    assert!(CbmBackendState::default().components.is_empty());
}
