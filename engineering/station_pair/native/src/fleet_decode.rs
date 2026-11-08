//! Exact decimal-to-binary64 ingress is opt-in for explicitly framed FleetCases.
//! The ordinary direct typed serde parser and all legacy arithmetic stay intact.
use super::{FleetCase, Request};
use serde::de::{self, MapAccess, Visitor};
use serde::{Deserialize, Deserializer};
use serde_json::{Map, Value, value::RawValue};
use std::fmt;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RawRequest {
    schema: String,
    cases: Vec<Box<RawValue>>,
}
#[derive(Deserialize)]
struct ProbeCase {
    network: Option<ProbeNetwork>,
    departures: Vec<ProbeDeparture>,
}
#[derive(Deserialize)]
struct ProbeNetwork {
    routes: Vec<ProbeRoute>,
}
#[derive(Deserialize)]
struct ProbeRoute {
    entry_frame: Option<Box<RawValue>>,
}
#[derive(Deserialize)]
struct ProbeDeparture {
    frame_binding: Option<Box<RawValue>>,
}
fn error(message: &str) -> serde_json::Error {
    <serde_json::Error as de::Error>::custom(message)
}
fn explicitly_framed(raw: &RawValue) -> Result<bool, serde_json::Error> {
    let probe: ProbeCase = serde_json::from_str(raw.get())?;
    Ok(probe.departures.iter().any(|d| d.frame_binding.is_some())
        || probe
            .network
            .as_ref()
            .is_some_and(|n| n.routes.iter().any(|r| r.entry_frame.is_some())))
}

/// Decode only. Validation/evaluation and canonical SHA authentication are separate.
/// Arbitrary-precision Number text is converted by standard `str::parse::<f64>`
/// only in framed cases. Direct typed parsing of all other cases is unchanged.
/// A Python producer must normalize typed f64 fields before canonical hashing:
/// integers, exponent spelling and signed zero are not preserved as JSON syntax.
pub fn decode_request(raw: &[u8]) -> Result<Request, serde_json::Error> {
    if raw.len() > crate::MAX_INPUT_BYTES {
        return Err(error("Request exceeds8MiB"));
    }
    let envelope: RawRequest = serde_json::from_slice(raw)?;
    let framed = envelope
        .cases
        .iter()
        .map(|c| explicitly_framed(c))
        .collect::<Result<Vec<_>, _>>()?;
    if !framed.iter().any(|x| *x) {
        // Deliberately do not route legacy requests through Value/from_value.
        return serde_json::from_slice(raw);
    }
    let cases = envelope
        .cases
        .into_iter()
        .zip(framed)
        .map(|(case, framed)| {
            if framed {
                serde_json::from_value::<FleetCase>(exact_value(case.get(), 0)?)
            } else {
                serde_json::from_str::<FleetCase>(case.get())
            }
        })
        .collect::<Result<_, _>>()?;
    Ok(Request {
        schema: envelope.schema,
        cases,
    })
}

// Construct a Value from raw children, rejecting duplicates before a Map can
// overwrite them. from_value then retains every existing deny_unknown_fields.
// Number lexical text (including long decimals) is retained by the pinned
// arbitrary_precision feature; float_roundtrip is deliberately not enabled.
fn exact_value(raw: &str, depth: usize) -> Result<Value, serde_json::Error> {
    if depth > 128 {
        return Err(error("Framed JSON nesting exceeds128"));
    }
    let raw = raw.trim();
    match raw.as_bytes().first() {
        Some(b'{') => {
            let mut parser = serde_json::Deserializer::from_str(raw);
            let object = parser.deserialize_map(ObjectVisitor { depth })?;
            parser.end()?;
            Ok(Value::Object(object))
        }
        Some(b'[') => {
            let items: Vec<&RawValue> = serde_json::from_str(raw)?;
            items
                .iter()
                .map(|item| exact_value(item.get(), depth + 1))
                .collect::<Result<Vec<_>, _>>()
                .map(Value::Array)
        }
        Some(b'-' | b'0'..=b'9') => {
            if raw == "-0" {
                return Err(error(
                    "Framed integer -0 is canonically ambiguous; declare f64 signed zero as -0.0",
                ));
            }
            let number: serde_json::Number = serde_json::from_str(raw)?;
            if number.as_f64().is_none() {
                return Err(error("Framed number is outside finite binary64 range"));
            }
            Ok(Value::Number(number))
        }
        _ => serde_json::from_str(raw),
    }
}
struct ObjectVisitor {
    depth: usize,
}
impl<'de> Visitor<'de> for ObjectVisitor {
    type Value = Map<String, Value>;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("framed object with unique field names")
    }
    fn visit_map<A: MapAccess<'de>>(self, mut input: A) -> Result<Self::Value, A::Error> {
        let mut values = Map::new();
        while let Some(key) = input.next_key::<String>()? {
            if values.contains_key(&key) {
                return Err(de::Error::custom(format!(
                    "Duplicate framed JSON field {key:?}"
                )));
            }
            let raw: &'de RawValue = input.next_value()?;
            let value = exact_value(raw.get(), self.depth + 1).map_err(de::Error::custom)?;
            values.insert(key, value);
        }
        Ok(values)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const E1: &[u8] = include_bytes!("../tests/data/framed_numeric_control.json");
    fn framed_number(raw: &str) -> Result<f64, serde_json::Error> {
        serde_json::from_value(exact_value(raw, 0)?)
    }
    #[test]
    fn decode_all_six_e1_values_keep_python_binary64_and_declared_ids() {
        let q = decode_request(E1).unwrap();
        let c = &q.cases[0].departures[0].journey;
        let points = &c.drive.as_ref().unwrap().points;
        for (i, value) in [
            (3, 2.0380922489791318_f64),
            (17, 11.549189410881747),
            (19, 12.907917576867835),
            (21, 14.266645742853923),
            (23, 15.625373908840011),
        ] {
            assert_eq!(points[i].speed_m_s.to_bits(), value.to_bits());
        }
        assert_eq!(
            points[32].force_n.to_bits(),
            90415.43634362097_f64.to_bits()
        );
        assert_eq!(
            c.id,
            "914fcb5b0a1cbcf5599eb4b91228fe4bc15d1af77731c944eee297a343bdb7e2"
        );
        assert_eq!(
            c.control.as_ref().unwrap().policy_id,
            "6cbe437d6afb0771ec64b19fd20715cf3c7d8c85beb331da0e2e707b71b147af"
        );
        let encoded = serde_json::to_string(&q).unwrap();
        let again = decode_request(encoded.as_bytes()).unwrap();
        assert_eq!(serde_json::to_string(&again).unwrap(), encoded);
        // Exact-number tree comparison excludes insignificant object-key order.
        assert_eq!(
            exact_value(std::str::from_utf8(E1).unwrap(), 0).unwrap(),
            exact_value(&encoded, 0).unwrap()
        );
    }
    #[test]
    fn decode_legacy_direct_and_mixed_case_paths_preserve_legacy_bits() {
        let old: Value =
            serde_json::from_str(include_str!("../tests/data/fleet_legacy_control.json")).unwrap();
        let raw = old["request_raw_json"].as_str().unwrap();
        let typed: Request = serde_json::from_str(raw).unwrap();
        assert_eq!(
            serde_json::to_string(&decode_request(raw.as_bytes()).unwrap()).unwrap(),
            serde_json::to_string(&typed).unwrap()
        );
        let exact: RawRequest = serde_json::from_slice(E1).unwrap();
        let legacy: RawRequest = serde_json::from_str(raw).unwrap();
        let mixed = format!(
            "{{\"schema\":\"{}\",\"cases\":[{},{}]}}",
            exact.schema,
            legacy.cases[0].get(),
            exact.cases[0].get()
        );
        let decoded = decode_request(mixed.as_bytes()).unwrap();
        assert_eq!(
            serde_json::to_string(&decoded.cases[0]).unwrap(),
            serde_json::to_string(&typed.cases[0]).unwrap()
        );
        let actual = decoded.cases[1].departures[0]
            .journey
            .drive
            .as_ref()
            .unwrap()
            .points[3]
            .speed_m_s;
        assert_eq!(actual.to_bits(), 2.0380922489791318_f64.to_bits());
        let old_exact: Request = serde_json::from_slice(E1).unwrap();
        assert_ne!(
            old_exact.cases[0].departures[0]
                .journey
                .drive
                .as_ref()
                .unwrap()
                .points[3]
                .speed_m_s
                .to_bits(),
            actual.to_bits()
        );
    }
    #[test]
    fn decode_exponents_subnormals_and_large_finite_values_match_standard_parse() {
        for raw in [
            "2.0380922489791318",
            "1e-300",
            "5e-324",
            "2.2250738585072014e-308",
            "1.7976931348623157e308",
            "9.007199254740993e15",
            "1e+20",
            "-4.9406564584124654E-324",
        ] {
            let value = framed_number(raw).unwrap();
            assert_eq!(
                value.to_bits(),
                raw.parse::<f64>().unwrap().to_bits(),
                "{raw}"
            );
            let encoded = serde_json::to_string(&value).unwrap();
            assert_eq!(framed_number(&encoded).unwrap().to_bits(), value.to_bits());
        }
    }
    #[test]
    fn decode_integer_and_signed_zero_representation_limits_are_explicit() {
        assert_eq!(
            framed_number("-0.0").unwrap().to_bits(),
            (-0.0_f64).to_bits()
        );
        assert_eq!(framed_number("0.0").unwrap().to_bits(), 0.0_f64.to_bits());
        assert!(framed_number("-0").is_err());
        for raw in ["0", "10", "-4", "18446744073709551615", "9007199254740993"] {
            assert_eq!(
                framed_number(raw).unwrap().to_bits(),
                raw.parse::<f64>().unwrap().to_bits()
            );
        }
        assert_eq!(
            serde_json::to_string(&framed_number("10").unwrap()).unwrap(),
            "10.0"
        );
        // Typed integer fields retain integer range checking and cannot accept
        // fractional/exponent spelling via a silent f64-to-integer conversion.
        let max: u64 =
            serde_json::from_value(exact_value("18446744073709551615", 0).unwrap()).unwrap();
        assert_eq!(max, u64::MAX);
        assert!(
            serde_json::from_value::<u64>(exact_value("18446744073709551616", 0).unwrap()).is_err()
        );
        assert!(serde_json::from_value::<u64>(exact_value("1.5", 0).unwrap()).is_err());
    }
    #[test]
    fn decode_invalid_nonfinite_and_string_numbers_fail_closed() {
        for raw in [
            "NaN",
            "Infinity",
            "-Infinity",
            "1e309",
            "-1e999",
            "01",
            "1.",
            ".1",
            "1e",
            "--2",
            "\"NaN\"",
            "\"2.0\"",
        ] {
            assert!(framed_number(raw).is_err(), "{raw}");
        }
        assert!(decode_request(&vec![b' '; crate::MAX_INPUT_BYTES + 1]).is_err());
        let input = std::str::from_utf8(E1).unwrap();
        assert!(
            decode_request(
                input
                    .replace("\"mass_kg\":140700.0", "\"mass_kg\":1e309")
                    .as_bytes()
            )
            .is_err()
        );
        assert!(decode_request(format!("{input}null").as_bytes()).is_err());
    }
    #[test]
    fn decode_duplicate_fields_are_rejected_before_value_map_overwrite() {
        for raw in [
            r#"{"a":1,"a":2}"#,
            r#"{"outer":[{"a":1,"a":1}]}"#,
            r#"{"a":1,"\u0061":2}"#,
        ] {
            assert!(
                exact_value(raw, 0)
                    .unwrap_err()
                    .to_string()
                    .contains("Duplicate")
            );
        }
        let input = std::str::from_utf8(E1).unwrap();
        assert!(input.contains("\"mass_kg\":140700.0"));
        let repeated = input.replace(
            "\"mass_kg\":140700.0",
            "\"mass_kg\":140700.0,\"mass_kg\":140700.0",
        );
        assert!(
            decode_request(repeated.as_bytes())
                .unwrap_err()
                .to_string()
                .contains("Duplicate")
        );
        let repeated = input.replace(
            "\"schema\":\"osr-station-fleet-request/1\"",
            "\"schema\":\"osr-station-fleet-request/1\",\"schema\":\"osr-station-fleet-request/1\"",
        );
        assert!(decode_request(repeated.as_bytes()).is_err());
    }
    #[test]
    fn decode_unknown_fields_and_recursive_bounds_are_not_lost() {
        let input = std::str::from_utf8(E1).unwrap();
        for changed in [
            input.replacen("{", "{\"unknown_wrapper\":0,", 1),
            input.replace(
                "\"mass_kg\":140700.0",
                "\"unknown_case\":0,\"mass_kg\":140700.0",
            ),
            input.replace(
                "\"contact_force_cap_n\":120000.0",
                "\"unknown_drive\":0,\"contact_force_cap_n\":120000.0",
            ),
        ] {
            assert!(decode_request(changed.as_bytes()).is_err());
        }
        let too_deep = format!("{}0{}", "[".repeat(130), "]".repeat(130));
        assert!(exact_value(&too_deep, 0).is_err());
        let q = decode_request(E1).unwrap();
        let c = &q.cases[0].departures[0].journey;
        assert_eq!(c.control.as_ref().unwrap().mass_lower_kg, 120700.);
        assert_eq!(c.control.as_ref().unwrap().mass_upper_kg, 170700.);
        assert_eq!(c.berth_tolerance_m, 1.);
        assert_eq!(c.control.as_ref().unwrap().position_error_bound_m, 0.25);
        assert_eq!(c.control.as_ref().unwrap().reaction_time_bound_s, 0.7);
    }
}
