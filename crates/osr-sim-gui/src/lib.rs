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
pub async fn start_web(canvas_id: String) -> Result<(), wasm_bindgen::JsValue> {
    eframe::WebRunner::new()
        .start(
            &canvas_id,
            eframe::WebOptions::default(),
            Box::new(|_cc| Ok(Box::new(SimApp::new(None, 3600)))),
        )
        .await
}
