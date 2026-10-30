//! Shared colour palette. Both GUIs use the same palette so a
//! dispatcher and a designer see a consistent picture.

use egui::Color32;

#[derive(Debug, Clone, Copy)]
pub struct Palette {
    pub background: Color32,
    pub line_track: Color32,
    pub station: Color32,
    pub label: Color32,
    pub train_traveling: Color32,
    pub train_dwelling: Color32,
    pub train_idle: Color32,
    pub train_charging: Color32,
    pub intrusion_clear: Color32,
    pub intrusion_unknown: Color32,
    pub intrusion_present: Color32,
    pub maintenance_override: Color32,
    pub alert_fire: Color32,
    pub alert_emergency_brake: Color32,
}

impl Palette {
    pub fn dark() -> Self {
        Palette {
            background: Color32::from_rgb(20, 20, 24),
            line_track: Color32::from_rgb(180, 180, 190),
            station: Color32::from_rgb(240, 240, 240),
            label: Color32::from_rgb(220, 220, 220),
            train_traveling: Color32::from_rgb(90, 200, 120),
            train_dwelling: Color32::from_rgb(90, 160, 240),
            train_idle: Color32::from_rgb(140, 140, 140),
            train_charging: Color32::from_rgb(240, 200, 60),
            intrusion_clear: Color32::from_rgba_premultiplied(80, 200, 120, 30),
            intrusion_unknown: Color32::from_rgb(240, 180, 60),
            intrusion_present: Color32::from_rgb(230, 60, 60),
            maintenance_override: Color32::from_rgb(120, 120, 230),
            alert_fire: Color32::from_rgb(230, 80, 40),
            alert_emergency_brake: Color32::from_rgb(230, 40, 40),
        }
    }
}

impl Default for Palette {
    fn default() -> Self {
        Self::dark()
    }
}
