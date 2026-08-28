//! OCC dispatcher-console library (RFC 0018).

#![forbid(unsafe_code)]

pub mod app;

pub use app::{Alert, AlertLevel, OccApp};

/// WASM entry point. Build with `trunk serve crates/osr-occ-gui/web/index.html`.
#[cfg(target_arch = "wasm32")]
#[cfg_attr(target_arch = "wasm32", wasm_bindgen::prelude::wasm_bindgen)]
pub async fn start_web(
    canvas: web_sys::HtmlCanvasElement,
) -> Result<String, wasm_bindgen::JsValue> {
    let app = OccApp::with_auto_attach("web dispatcher".into(), true);
    let (recorded_events, trains, alerts, intrusions) = app.recorded_state_summary();
    eframe::WebRunner::new()
        .start(
            canvas,
            eframe::WebOptions::default(),
            Box::new(move |_cc| Ok(Box::new(app))),
        )
        .await?;
    Ok(format!(
        "{{\"recordedEvents\":{recorded_events},\"trains\":{trains},\"alerts\":{alerts},\"intrusions\":{intrusions}}}"
    ))
}
