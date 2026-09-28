//! Lookup-only identity contract for physical assets and lifecycle records.
//!
//! A QR code built from this contract is an index into operator-controlled
//! information. It is never a work authorization, isolation, engineering
//! release, movement authority, credential, or command channel.

use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const SCHEMA: &str = "osr-asset-identity/1";
pub const AUTHORITY: &str = "lookup-only";

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AssetIdentity {
    pub schema: String,
    pub city: String,
    pub asset_id: String,
    pub engineering_revision: String,
    pub resolver_path: String,
    pub authority: String,
}

impl AssetIdentity {
    pub fn new(
        city: &str,
        asset_id: &str,
        engineering_revision: &str,
    ) -> Result<Self, IdentityError> {
        if !valid_city(city) || !valid_asset(asset_id) || !valid_revision(engineering_revision) {
            return Err(IdentityError::Identity);
        }
        Ok(Self {
            schema: SCHEMA.into(),
            city: city.into(),
            asset_id: asset_id.into(),
            engineering_revision: engineering_revision.into(),
            resolver_path: format!("/id/osr/{city}/asset/{asset_id}"),
            authority: AUTHORITY.into(),
        })
    }

    pub fn validate(&self) -> Result<(), IdentityError> {
        if self.schema != SCHEMA {
            return Err(IdentityError::Schema);
        }
        if self.authority != AUTHORITY {
            return Err(IdentityError::Authority);
        }
        if !valid_city(&self.city)
            || !valid_asset(&self.asset_id)
            || !valid_revision(&self.engineering_revision)
        {
            return Err(IdentityError::Identity);
        }
        let expected = format!("/id/osr/{}/asset/{}", self.city, self.asset_id);
        if self.resolver_path != expected {
            return Err(IdentityError::ResolverPath);
        }
        Ok(())
    }

    pub fn qr_payload(&self, resolver_origin: &str) -> Result<String, IdentityError> {
        self.validate()?;
        let origin = validate_https_origin(resolver_origin)?;
        Ok(format!("{origin}{}", self.resolver_path))
    }
}

fn valid_city(value: &str) -> bool {
    valid_bounded(value, 80, |byte| {
        byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'-'
    }) && value
        .as_bytes()
        .first()
        .is_some_and(|byte| byte.is_ascii_alphanumeric())
}

fn valid_asset(value: &str) -> bool {
    valid_bounded(value, 160, |byte| {
        byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b':')
    }) && value
        .as_bytes()
        .first()
        .is_some_and(|byte| byte.is_ascii_alphanumeric())
}

fn valid_revision(value: &str) -> bool {
    valid_bounded(value, 160, |byte| {
        byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b':' | b'+')
    }) && value
        .as_bytes()
        .first()
        .is_some_and(|byte| byte.is_ascii_alphanumeric())
}

fn valid_bounded(value: &str, maximum: usize, allowed: impl Fn(u8) -> bool) -> bool {
    !value.is_empty() && value.len() <= maximum && value.bytes().all(allowed)
}

fn validate_https_origin(value: &str) -> Result<&str, IdentityError> {
    if value.len() > 240 || !value.is_ascii() || !value.starts_with("https://") {
        return Err(IdentityError::ResolverOrigin);
    }
    let authority = &value[8..];
    if authority.is_empty()
        || authority
            .bytes()
            .any(|byte| matches!(byte, b'/' | b'@' | b'?' | b'#'))
        || authority.starts_with('.')
        || authority.ends_with('.')
        || authority.bytes().any(|byte| byte.is_ascii_whitespace())
    {
        return Err(IdentityError::ResolverOrigin);
    }
    Ok(value)
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum IdentityError {
    #[error("unsupported asset identity schema")]
    Schema,
    #[error("asset identity attempted to claim authority")]
    Authority,
    #[error("invalid city, asset or engineering revision identity")]
    Identity,
    #[error("resolver path does not match the controlled identity")]
    ResolverPath,
    #[error("resolver must be a bounded HTTPS origin without credentials or path")]
    ResolverOrigin,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn identity_round_trips_and_builds_lookup_only_qr_payload() {
        let fixture = include_str!("../../../tests/fixtures/asset-identity.json");
        let identity: AssetIdentity = serde_json::from_str(fixture).unwrap();
        assert_eq!(
            identity,
            AssetIdentity::new("samawah", "SAM-ST-001", "rev:abc123").unwrap()
        );
        identity.validate().unwrap();
        assert_eq!(
            identity
                .qr_payload("https://assets.operator.example")
                .unwrap(),
            "https://assets.operator.example/id/osr/samawah/asset/SAM-ST-001"
        );
        let encoded = serde_json::to_string(&identity).unwrap();
        assert_eq!(
            serde_json::from_str::<AssetIdentity>(&encoded).unwrap(),
            identity
        );
    }

    #[test]
    fn authority_path_and_unknown_fields_fail_closed() {
        let mut identity = AssetIdentity::new("samawah", "SAM-ST-001", "r1").unwrap();
        identity.authority = "work-authority".into();
        assert_eq!(identity.validate(), Err(IdentityError::Authority));
        identity = AssetIdentity::new("samawah", "SAM-ST-001", "r1").unwrap();
        identity.resolver_path = "/command/SAM-ST-001".into();
        assert_eq!(identity.validate(), Err(IdentityError::ResolverPath));
        let unknown = r#"{"schema":"osr-asset-identity/1","city":"samawah","asset_id":"SAM-ST-001","engineering_revision":"r1","resolver_path":"/id/osr/samawah/asset/SAM-ST-001","authority":"lookup-only","command":true}"#;
        assert!(serde_json::from_str::<AssetIdentity>(unknown).is_err());
    }

    #[test]
    fn invalid_identifiers_and_resolver_origins_fail_closed() {
        assert_eq!(
            AssetIdentity::new("Samawah", "SAM-ST-001", "r1"),
            Err(IdentityError::Identity)
        );
        assert_eq!(
            AssetIdentity::new("samawah", "SAM/ST/001", "r1"),
            Err(IdentityError::Identity)
        );
        let identity = AssetIdentity::new("samawah", "SAM-ST-001", "r1").unwrap();
        for origin in [
            "http://assets.example",
            "https://user@assets.example",
            "https://assets.example/path",
            "https://assets.example?token=x",
            "https://",
        ] {
            assert_eq!(
                identity.qr_payload(origin),
                Err(IdentityError::ResolverOrigin)
            );
        }
    }
}
