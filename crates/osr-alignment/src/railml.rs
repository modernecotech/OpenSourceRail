//! railML 3.2 export — rail-industry infrastructure interchange.
//!
//! railML (https://www.railml.org) is the de-facto open exchange
//! format across European rail signalling, infrastructure, and
//! rolling-stock vendors. A subset of railML 3.2 `<infrastructure>`
//! covers what OSR produces:
//!
//! - `<tracks>` — one track per alignment, with `<mileageChanges>`
//!   tracking chainage.
//! - `<trackElements>` — speed profiles, gradients, horizontal curves.
//! - `<commonSwitchesAndCrossings>` — future-work, turnout placement
//!   is still v0.2.
//! - `<signals>`, `<levelCrossings>` — emit when osr-level-crossing
//!   integrates with alignment geometry (v0.2).
//!
//! For v0.1 we emit the bare alignment geometry section, which is
//! sufficient for OpenRail / Systra Siteflow / Trassenfinder import.
//!
//! When real-world deployments need a full infrastructure package
//! (signals + interlocking routes + timetables), the extension path
//! is to add emitters into this module — the track-element skeleton
//! already wires to the alignment.

use std::fmt::Write as _;

use crate::alignment::{Alignment, HorizontalElement, VerticalElement};

pub fn to_railml(alignment: &Alignment) -> String {
    let mut s = String::new();
    writeln!(&mut s, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>").unwrap();
    writeln!(
        &mut s,
        "<railml xmlns=\"https://www.railml.org/schemas/3.2\" \
         version=\"3.2\">"
    )
    .unwrap();
    writeln!(&mut s, "  <metadata>").unwrap();
    writeln!(
        &mut s,
        "    <generator name=\"osr-alignment\" version=\"0.1.0\"/>"
    )
    .unwrap();
    writeln!(&mut s, "  </metadata>").unwrap();
    writeln!(&mut s, "  <infrastructure>").unwrap();
    writeln!(&mut s, "    <topology>").unwrap();
    writeln!(&mut s, "      <tracks>").unwrap();
    writeln!(
        &mut s,
        "        <track id=\"t-{slug}\" type=\"mainTrack\">",
        slug = escape(&alignment.line_slug)
    )
    .unwrap();

    // Track topology: one track from start to end with chainage.
    writeln!(
        &mut s,
        "          <trackTopology>\n            <trackBegin id=\"b-{slug}\" pos=\"{sta:.3}\"/>\n            \
         <trackEnd id=\"e-{slug}\" pos=\"{end:.3}\"/>\n          </trackTopology>",
        slug = escape(&alignment.line_slug),
        sta = alignment.start_chainage_m,
        end = alignment.start_chainage_m + alignment.total_length_m()
    )
    .unwrap();

    // Speed section — one profile for the whole alignment at design
    // speed (v0.1 simplification).
    writeln!(&mut s, "          <trackElements>").unwrap();
    writeln!(
        &mut s,
        "            <speedChanges>\n              <speedChange id=\"sc-{slug}-0\" pos=\"{sta:.3}\" \
         maxSpeed=\"{v:.1}\" speedType=\"signalled\"/>\n            </speedChanges>",
        slug = escape(&alignment.line_slug),
        sta = alignment.start_chainage_m,
        v = alignment.design_speed_kmh
    )
    .unwrap();

    // Radius / gradient sections — emitted as a track-element stream
    // following the horizontal alignment.
    writeln!(&mut s, "            <radiusChanges>").unwrap();
    let mut sta = alignment.start_chainage_m;
    let mut idx = 0usize;
    for el in &alignment.horizontal {
        let r = match el {
            HorizontalElement::Tangent { .. } => 0.0, // railML convention: tangent = 0
            HorizontalElement::Arc { radius_m, .. } => *radius_m,
            HorizontalElement::Spiral { .. } => 0.0, // approximated as tangent entry
        };
        writeln!(
            &mut s,
            "              <radiusChange id=\"r-{slug}-{i}\" pos=\"{p:.3}\" radius=\"{r:.3}\"/>",
            slug = escape(&alignment.line_slug),
            i = idx,
            p = sta,
            r = r
        )
        .unwrap();
        sta += el.length_m();
        idx += 1;
    }
    writeln!(&mut s, "            </radiusChanges>").unwrap();

    writeln!(&mut s, "            <gradientChanges>").unwrap();
    let mut sta = alignment.start_chainage_m;
    let mut idx = 0usize;
    for el in &alignment.vertical {
        let g = match el {
            VerticalElement::Grade { grade, .. } => grade * 1000.0, // ‰
            VerticalElement::VerticalCurve { start_grade, .. } => start_grade * 1000.0,
        };
        writeln!(
            &mut s,
            "              <gradientChange id=\"g-{slug}-{i}\" pos=\"{p:.3}\" \
             slope=\"{g:.3}\"/>",
            slug = escape(&alignment.line_slug),
            i = idx,
            p = sta,
            g = g
        )
        .unwrap();
        sta += el.length_m();
        idx += 1;
    }
    writeln!(&mut s, "            </gradientChanges>").unwrap();

    writeln!(&mut s, "          </trackElements>").unwrap();
    writeln!(&mut s, "        </track>").unwrap();
    writeln!(&mut s, "      </tracks>").unwrap();
    writeln!(&mut s, "    </topology>").unwrap();
    writeln!(&mut s, "  </infrastructure>").unwrap();
    writeln!(&mut s, "</railml>").unwrap();
    s
}

fn escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&apos;")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::HorizontalElement;

    #[test]
    fn emits_minimal_railml() {
        let a = Alignment {
            line_slug: "samawah-l1".into(),
            design_speed_kmh: 80.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Tangent {
                length_m: 1000.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            }],
            vertical: vec![],
        };
        let x = to_railml(&a);
        assert!(x.contains("<railml"));
        assert!(x.contains("<track id=\"t-samawah-l1\""));
        assert!(x.contains("maxSpeed=\"80.0\""));
    }
}
