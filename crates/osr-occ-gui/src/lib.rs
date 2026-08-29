//! OCC dispatcher-console library (RFC 0018).

#![forbid(unsafe_code)]

pub mod app;

pub use app::{Alert, AlertLevel, OccApp, RecordedStateSummary};

/// WASM entry point. Build with `trunk serve crates/osr-occ-gui/web/index.html`.
#[cfg(target_arch = "wasm32")]
#[cfg_attr(target_arch = "wasm32", wasm_bindgen::prelude::wasm_bindgen)]
pub async fn start_web(
    canvas: web_sys::HtmlCanvasElement,
    operator: String,
) -> Result<String, wasm_bindgen::JsValue> {
    let app = OccApp::with_auto_attach_duration(operator, true, 600);
    let RecordedStateSummary {
        duration_s,
        recorded_events,
        trains,
        alerts,
        intrusions,
        embedded_ticks,
        t2g_transmissions,
        station_ticks,
        wayside_ticks,
        backend_samples,
        analytics_metrics,
        ptp_ticks,
        habd_passages,
        tcms_movement_inhibits,
    } = app.recorded_state_summary();
    eframe::WebRunner::new()
        .start(
            canvas,
            eframe::WebOptions::default(),
            Box::new(move |_cc| Ok(Box::new(app))),
        )
        .await?;
    Ok(format!(
        "{{\"durationS\":{duration_s},\"recordedEvents\":{recorded_events},\"trains\":{trains},\"alerts\":{alerts},\"intrusions\":{intrusions},\"embeddedTicks\":{embedded_ticks},\"t2gTransmissions\":{t2g_transmissions},\"stationTicks\":{station_ticks},\"waysideTicks\":{wayside_ticks},\"backendSamples\":{backend_samples},\"analyticsMetrics\":{analytics_metrics},\"ptpTicks\":{ptp_ticks},\"habdPassages\":{habd_passages},\"tcmsMovementInhibits\":{tcms_movement_inhibits}}}"
    ))
}
