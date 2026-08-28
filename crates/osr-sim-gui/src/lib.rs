//! Simulator GUI library (RFC 0018).
//!
//! The app logic lives in [`SimApp`] so both the native binary
//! (`src/main.rs`) and the WASM entry point (`start_web`) use the
//! same code path.

#![forbid(unsafe_code)]

pub mod app;

pub use app::SimApp;

/// WASM entry point — invoked from `web/index.html` via wasm-bindgen.
///
/// Attaches the eframe app to the `<canvas id="osr_sim_canvas">`
/// element. Build with:
///
/// ```notrust
/// trunk serve crates/osr-sim-gui/web/index.html
/// ```
#[cfg(target_arch = "wasm32")]
#[cfg_attr(target_arch = "wasm32", wasm_bindgen::prelude::wasm_bindgen)]
pub async fn start_web(
    canvas: web_sys::HtmlCanvasElement,
) -> Result<String, wasm_bindgen::JsValue> {
    let app = SimApp::with_auto_run(None, 600, true);
    let (
        duration_s,
        events,
        trains,
        controller_ticks,
        embedded_ticks,
        t2g_transmissions,
        invariant_violations,
    ) = app.run_state_summary();
    eframe::WebRunner::new()
        .start(
            canvas,
            eframe::WebOptions::default(),
            Box::new(move |_cc| Ok(Box::new(app))),
        )
        .await?;
    Ok(format!(
        "{{\"durationS\":{duration_s},\"events\":{events},\"trains\":{trains},\"controllerTicks\":{controller_ticks},\"embeddedTicks\":{embedded_ticks},\"t2gTransmissions\":{t2g_transmissions},\"invariantViolations\":{invariant_violations}}}"
    ))
}
