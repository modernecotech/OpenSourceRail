//! OCC dispatcher-console library (RFC 0018).

#![forbid(unsafe_code)]

pub mod app;

pub use app::{Alert, AlertLevel, OccApp};

/// WASM entry point. Build with `trunk serve crates/osr-occ-gui/web/index.html`.
#[cfg(target_arch = "wasm32")]
#[cfg_attr(target_arch = "wasm32", wasm_bindgen::prelude::wasm_bindgen)]
pub async fn start_web(canvas_id: String) -> Result<(), wasm_bindgen::JsValue> {
    eframe::WebRunner::new()
        .start(
            &canvas_id,
            eframe::WebOptions::default(),
            Box::new(|_cc| Ok(Box::new(OccApp::new("web dispatcher".into())))),
        )
        .await
}
