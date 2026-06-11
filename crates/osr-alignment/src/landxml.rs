//! LandXML 1.2 export — alignment interchange for Bentley OpenRail,
//! Civil 3D, Trimble Business Center. The simplest shared format
//! across every commercial civil-engineering tool.
//!
//! Scope: horizontal alignment (`<CoordGeom>` with `<Line>`, `<Curve>`,
//! `<Spiral>`) + vertical profile (`<Profile>` with `<PVI>` entries).
//! Not emitted here: surfaces, pipes, survey points — outside OSR's
//! alignment-only scope.
//!
//! The emitted XML validates against the LandXML 1.2 schema when
//! imported into OpenRail Designer + Civil 3D (smoke-tested on the
//! samples under `tests/`).

use std::fmt::Write as _;

use crate::alignment::{Alignment, HorizontalElement, TurnDirection};

/// Serialize the alignment to LandXML 1.2.
pub fn to_landxml(alignment: &Alignment) -> String {
    let mut s = String::new();
    writeln!(&mut s, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>").unwrap();
    writeln!(
        &mut s,
        "<LandXML xmlns=\"http://www.landxml.org/schema/LandXML-1.2\" version=\"1.2\" \
         date=\"{date}\" time=\"00:00:00\">",
        date = "2026-04-24"
    )
    .unwrap();
    writeln!(
        &mut s,
        "  <Application name=\"osr-alignment\" version=\"0.1.0\"/>"
    )
    .unwrap();
    writeln!(
        &mut s,
        "  <Units><Metric linearUnit=\"meter\" areaUnit=\"squareMeter\" volumeUnit=\"cubicMeter\" \
         temperatureUnit=\"celsius\" pressureUnit=\"millHg\" angularUnit=\"radians\" \
         directionUnit=\"radians\"/></Units>"
    )
    .unwrap();
    writeln!(&mut s, "  <Alignments>").unwrap();
    writeln!(
        &mut s,
        "    <Alignment name=\"{name}\" length=\"{len:.6}\" staStart=\"{sta:.6}\">",
        name = xml_escape(&alignment.line_slug),
        len = alignment.total_length_m(),
        sta = alignment.start_chainage_m
    )
    .unwrap();

    // Horizontal.
    writeln!(&mut s, "      <CoordGeom>").unwrap();
    let mut sta = alignment.start_chainage_m;
    for el in &alignment.horizontal {
        match el {
            HorizontalElement::Tangent {
                length_m,
                start_xy: (x0, y0),
                bearing_rad,
            } => {
                let x1 = x0 + length_m * bearing_rad.cos();
                let y1 = y0 + length_m * bearing_rad.sin();
                writeln!(
                    &mut s,
                    "        <Line length=\"{l:.6}\" staStart=\"{s:.6}\">",
                    l = length_m,
                    s = sta
                )
                .unwrap();
                writeln!(&mut s, "          <Start>{y0:.6} {x0:.6}</Start>").unwrap();
                writeln!(&mut s, "          <End>{y1:.6} {x1:.6}</End>").unwrap();
                writeln!(&mut s, "        </Line>").unwrap();
            }
            HorizontalElement::Arc {
                length_m,
                radius_m,
                direction,
                ..
            } => {
                let ((x1, y1), _) = el.end_point();
                let (x0, y0) = el.start_xy();
                let rot = match direction {
                    TurnDirection::Left => "ccw",
                    TurnDirection::Right => "cw",
                };
                // Approximate centre: midpoint of chord + perpendicular.
                let (cx, cy) = arc_centre(el);
                writeln!(
                    &mut s,
                    "        <Curve length=\"{l:.6}\" staStart=\"{s:.6}\" \
                     radius=\"{r:.6}\" rot=\"{rot}\">",
                    l = length_m,
                    s = sta,
                    r = radius_m,
                    rot = rot
                )
                .unwrap();
                writeln!(&mut s, "          <Start>{y0:.6} {x0:.6}</Start>").unwrap();
                writeln!(&mut s, "          <Center>{cy:.6} {cx:.6}</Center>").unwrap();
                writeln!(&mut s, "          <End>{y1:.6} {x1:.6}</End>").unwrap();
                writeln!(&mut s, "        </Curve>").unwrap();
            }
            HorizontalElement::Spiral {
                length_m,
                start_radius_m,
                end_radius_m,
                direction,
                ..
            } => {
                let (x0, y0) = el.start_xy();
                let ((x1, y1), _) = el.end_point();
                let rot = match direction {
                    TurnDirection::Left => "ccw",
                    TurnDirection::Right => "cw",
                };
                let rs = start_radius_m
                    .map(|r| format!("{r:.6}"))
                    .unwrap_or_else(|| "0".into());
                let re = end_radius_m
                    .map(|r| format!("{r:.6}"))
                    .unwrap_or_else(|| "0".into());
                writeln!(
                    &mut s,
                    "        <Spiral length=\"{l:.6}\" staStart=\"{s:.6}\" \
                     radiusStart=\"{rs}\" radiusEnd=\"{re}\" rot=\"{rot}\" \
                     spiType=\"clothoid\">",
                    l = length_m,
                    s = sta
                )
                .unwrap();
                writeln!(&mut s, "          <Start>{y0:.6} {x0:.6}</Start>").unwrap();
                writeln!(&mut s, "          <End>{y1:.6} {x1:.6}</End>").unwrap();
                writeln!(&mut s, "        </Spiral>").unwrap();
            }
        }
        sta += el.length_m();
    }
    writeln!(&mut s, "      </CoordGeom>").unwrap();

    // Vertical profile.
    if !alignment.vertical.is_empty() {
        writeln!(&mut s, "      <Profile name=\"P\">").unwrap();
        writeln!(&mut s, "        <ProfAlign name=\"centreline\">").unwrap();
        let mut sta = alignment.start_chainage_m;
        let first = &alignment.vertical[0];
        writeln!(
            &mut s,
            "          <PVI>{sta:.6} {z:.6}</PVI>",
            sta = sta,
            z = first.start_z_m()
        )
        .unwrap();
        for el in &alignment.vertical {
            sta += el.length_m();
            let z = el.end_z_m();
            writeln!(&mut s, "          <PVI>{sta:.6} {z:.6}</PVI>").unwrap();
        }
        writeln!(&mut s, "        </ProfAlign>").unwrap();
        writeln!(&mut s, "      </Profile>").unwrap();
    }

    writeln!(&mut s, "    </Alignment>").unwrap();
    writeln!(&mut s, "  </Alignments>").unwrap();
    writeln!(&mut s, "</LandXML>").unwrap();
    s
}

fn arc_centre(el: &HorizontalElement) -> (f64, f64) {
    if let HorizontalElement::Arc {
        radius_m,
        direction,
        start_xy: (x0, y0),
        start_bearing_rad,
        ..
    } = *el
    {
        let sign = match direction {
            TurnDirection::Left => 1.0,
            TurnDirection::Right => -1.0,
        };
        let cx = x0 - sign * radius_m * start_bearing_rad.sin();
        let cy = y0 + sign * radius_m * start_bearing_rad.cos();
        (cx, cy)
    } else {
        (0.0, 0.0)
    }
}

fn xml_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::{Alignment, HorizontalElement, VerticalElement};

    #[test]
    fn emits_valid_xml_header() {
        let a = Alignment {
            line_slug: "test".into(),
            design_speed_kmh: 80.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Tangent {
                length_m: 100.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            }],
            vertical: vec![VerticalElement::Grade {
                length_m: 100.0,
                grade: 0.0,
                start_z_m: 50.0,
            }],
        };
        let x = to_landxml(&a);
        assert!(x.contains("<?xml"));
        assert!(x.contains("<LandXML"));
        assert!(x.contains("<Alignment name=\"test\""));
        assert!(x.contains("<Line length=\"100"));
        assert!(x.contains("<PVI>0.000000 50.000000</PVI>"));
    }

    #[test]
    fn xml_escape_special_chars() {
        assert_eq!(xml_escape("a&b<c>d"), "a&amp;b&lt;c&gt;d");
    }
}
