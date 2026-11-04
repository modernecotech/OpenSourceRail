//! Bounded canonical ASCII JSON emission and SHA256, independent of Python.
//!
//! The optional Python adapter supplies exact built-in numeric text. This core
//! never normalizes Unicode, changes a float spelling or accepts raw JSON input.
use sha2::{Digest, Sha256};

pub const MAX_BYTES: usize = 64 * 1024 * 1024;
pub const MAX_DEPTH: usize = 256;
pub const DEFAULT_DEPTH: usize = 128;

#[derive(Debug)]
pub struct Emitter {
    output: Option<Vec<u8>>,
    hash: Sha256,
    used: usize,
    limit: usize,
}

impl Emitter {
    pub fn new(limit: usize, retain_bytes: bool) -> Result<Self, &'static str> {
        if limit == 0 || limit > MAX_BYTES {
            return Err("Canonical byte limit must be between 1 and 67108864");
        }
        Ok(Self {
            output: retain_bytes.then(Vec::new),
            hash: Sha256::new(),
            used: 0,
            limit,
        })
    }

    pub fn write(&mut self, bytes: &[u8]) -> Result<(), &'static str> {
        let used = self
            .used
            .checked_add(bytes.len())
            .ok_or("Canonical byte budget exceeded")?;
        if used > self.limit {
            return Err("Canonical byte budget exceeded");
        }
        if let Some(output) = &mut self.output {
            output.extend_from_slice(bytes);
        }
        self.hash.update(bytes);
        self.used = used;
        Ok(())
    }

    pub fn remaining(&self) -> usize {
        self.limit - self.used
    }

    fn escape(&mut self, codepoint: u32) -> Result<(), &'static str> {
        match codepoint {
            8 => self.write(b"\\b"),
            9 => self.write(b"\\t"),
            10 => self.write(b"\\n"),
            12 => self.write(b"\\f"),
            13 => self.write(b"\\r"),
            34 => self.write(b"\\\""),
            92 => self.write(b"\\\\"),
            0..=31 | 127..=65535 => self.hex_escape(codepoint as u16),
            32..=126 => self.write(&[codepoint as u8]),
            65536..=0x10ffff => {
                let scalar = codepoint - 0x10000;
                self.hex_escape(0xd800 + (scalar >> 10) as u16)?;
                self.hex_escape(0xdc00 + (scalar & 1023) as u16)
            }
            _ => Err("Invalid Unicode codepoint"),
        }
    }

    fn hex_escape(&mut self, code: u16) -> Result<(), &'static str> {
        const HEX: &[u8; 16] = b"0123456789abcdef";
        self.write(&[
            b'\\',
            b'u',
            HEX[((code >> 12) & 15) as usize],
            HEX[((code >> 8) & 15) as usize],
            HEX[((code >> 4) & 15) as usize],
            HEX[(code & 15) as usize],
        ])
    }

    pub fn string(&mut self, text: &str) -> Result<(), &'static str> {
        self.write(b"\"")?;
        let mut start = 0;
        for (offset, scalar) in text.char_indices() {
            let code = scalar as u32;
            if (32..=126).contains(&code) && code != 34 && code != 92 {
                continue;
            }
            self.write(&text.as_bytes()[start..offset])?;
            self.escape(code)?;
            start = offset + scalar.len_utf8();
        }
        self.write(&text.as_bytes()[start..])?;
        self.write(b"\"")
    }

    /// Python permits lone surrogates; these are explicit codepoints, not UTF8.
    pub fn codepoints(&mut self, points: &[u32]) -> Result<(), &'static str> {
        self.write(b"\"")?;
        for codepoint in points {
            self.escape(*codepoint)?;
        }
        self.write(b"\"")
    }

    pub fn finish(mut self) -> Result<(Option<Vec<u8>>, String), &'static str> {
        self.write(b"\n")?;
        let hash = format!("{:x}", self.hash.finalize());
        Ok((self.output, hash))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ascii_controls_unicode_and_surrogates_match_python_spelling() {
        let mut out = Emitter::new(1000, true).unwrap();
        out.string("\"\\\u{8}\t\n\u{c}\r\u{0}\u{1f}\u{7f}Ω🛤")
            .unwrap();
        let (bytes, _) = out.finish().unwrap();
        assert_eq!(
            bytes.unwrap(),
            b"\"\\\"\\\\\\b\\t\\n\\f\\r\\u0000\\u001f\\u007f\\u03a9\\ud83d\\udee4\"\n"
        );
        let mut out = Emitter::new(1000, true).unwrap();
        out.codepoints(&[0xd800, 0x61, 0xdc00]).unwrap();
        assert_eq!(out.finish().unwrap().0.unwrap(), b"\"\\ud800a\\udc00\"\n");
    }

    #[test]
    fn streaming_hash_equals_retained_bytes_including_final_newline() {
        let mut retained = Emitter::new(100, true).unwrap();
        retained.write(b"{\"mass\":null}").unwrap();
        let (bytes, hash) = retained.finish().unwrap();
        assert_eq!(hash, format!("{:x}", Sha256::digest(bytes.unwrap())));
        let mut streaming = Emitter::new(100, false).unwrap();
        streaming.write(b"{\"mass\":null}").unwrap();
        assert_eq!(streaming.finish().unwrap(), (None, hash));
    }

    #[test]
    fn budget_includes_escapes_and_final_newline() {
        let mut out = Emitter::new(2, true).unwrap();
        out.write(b"{}").unwrap();
        assert!(out.finish().is_err());
        assert!(Emitter::new(0, true).is_err());
        assert!(Emitter::new(MAX_BYTES + 1, true).is_err());
        let mut out = Emitter::new(7, true).unwrap();
        assert!(out.codepoints(&[0xd800]).is_err());
        let mut out = Emitter::new(100, true).unwrap();
        assert!(out.codepoints(&[0x110000]).is_err());
    }
}
