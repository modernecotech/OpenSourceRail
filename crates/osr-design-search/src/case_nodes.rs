//! Lossless typed Arrow node table for one bounded canonical case or stage record.
//! Each JSON value is a row with a parent, sibling order, node kind and typed
//! scalar columns. There is no document-sized JSON payload column.
use arrow_array::{
    Array, ArrayRef, BooleanArray, Float64Array, Int64Array, RecordBatch, StringArray, UInt32Array,
    UInt8Array,
};
use arrow_schema::{DataType, Field, Schema};
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use parquet::arrow::arrow_writer::ArrowWriter;
use parquet::basic::Compression;
use parquet::file::properties::WriterProperties;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::error::Error;
use std::fs::{self, File, OpenOptions};
use std::io;
use std::path::Path;
use std::sync::Arc;

#[allow(dead_code)]
#[path = "canonical.rs"]
mod canonical;
use canonical::Emitter;

type Result<T> = std::result::Result<T, Box<dyn Error>>;
pub const MAX_BYTES: u64 = 64 * 1024 * 1024;
const MAX_NODES: usize = 4_000_000;
const MAX_DEPTH: usize = 128;
const MAX_PART: u64 = 16 * 1024 * 1024;
const BATCH: usize = 8192;
const OBJECT: u8 = 0;
const LIST: u8 = 1;
const STRING: u8 = 2;
const INTEGER: u8 = 3;
const FLOAT: u8 = 4;
const BOOLEAN: u8 = 5;
const NULL: u8 = 6;

fn invalid(text: &'static str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, text)
}
fn schema() -> Arc<Schema> {
    Arc::new(Schema::new_with_metadata(
        vec![
            Field::new("parent", DataType::UInt32, true),
            Field::new("ordinal", DataType::UInt32, false),
            Field::new("kind", DataType::UInt8, false),
            Field::new("key", DataType::Utf8, true),
            Field::new("text", DataType::Utf8, true),
            Field::new("integer", DataType::Int64, true),
            Field::new("float", DataType::Float64, true),
            Field::new("boolean", DataType::Boolean, true),
        ],
        HashMap::from([(
            "osr_schema".to_owned(),
            "osr-canonical-node-table/1".to_owned(),
        )]),
    ))
}
#[derive(Clone)]
struct Node {
    parent: Option<u32>,
    ordinal: u32,
    kind: u8,
    key: Option<String>,
    text: Option<String>,
    integer: Option<i64>,
    float: Option<f64>,
    boolean: Option<bool>,
}
struct Parser<'a> {
    input: &'a [u8],
    at: usize,
    nodes: Vec<Node>,
}
impl<'a> Parser<'a> {
    fn quoted(&mut self) -> Result<String> {
        if self.input.get(self.at) != Some(&b'"') {
            return Err(invalid("quoted JSON string required").into());
        }
        let start = self.at;
        self.at += 1;
        let mut escape = false;
        while let Some(&byte) = self.input.get(self.at) {
            self.at += 1;
            if escape {
                escape = false;
                continue;
            }
            if byte == b'\\' {
                escape = true;
                continue;
            }
            if byte == b'"' {
                return Ok(serde_json::from_slice(&self.input[start..self.at])?);
            }
        }
        Err(invalid("unterminated JSON string").into())
    }
    fn value(
        &mut self,
        parent: Option<u32>,
        ordinal: u32,
        key: Option<String>,
        depth: usize,
    ) -> Result<()> {
        if depth > MAX_DEPTH || self.nodes.len() >= MAX_NODES {
            return Err(invalid("node or depth budget exceeded").into());
        }
        let index = u32::try_from(self.nodes.len())?;
        let byte = *self
            .input
            .get(self.at)
            .ok_or_else(|| invalid("truncated JSON value"))?;
        let mut node = Node {
            parent,
            ordinal,
            kind: NULL,
            key,
            text: None,
            integer: None,
            float: None,
            boolean: None,
        };
        match byte {
            b'{' | b'[' => {
                node.kind = if byte == b'{' { OBJECT } else { LIST };
                self.at += 1;
                self.nodes.push(node);
                let close = if byte == b'{' { b'}' } else { b']' };
                let mut position = 0u32;
                let mut previous: Option<String> = None;
                if self.input.get(self.at) == Some(&close) {
                    self.at += 1;
                    return Ok(());
                }
                loop {
                    let child_key = if byte == b'{' {
                        let key = self.quoted()?;
                        if previous.as_ref().is_some_and(|last| last >= &key) {
                            return Err(invalid("object keys not in unique canonical order").into());
                        }
                        previous = Some(key.clone());
                        if self.input.get(self.at) != Some(&b':') {
                            return Err(invalid("object colon missing").into());
                        }
                        self.at += 1;
                        Some(key)
                    } else {
                        None
                    };
                    self.value(Some(index), position, child_key, depth + 1)?;
                    position = position
                        .checked_add(1)
                        .ok_or_else(|| invalid("ordinal overflow"))?;
                    match self.input.get(self.at) {
                        Some(b',') => self.at += 1,
                        Some(value) if *value == close => {
                            self.at += 1;
                            break;
                        }
                        _ => return Err(invalid("container delimiter missing").into()),
                    }
                }
                return Ok(());
            }
            b'"' => {
                node.kind = STRING;
                node.text = Some(self.quoted()?);
            }
            b't' | b'f' => {
                let (raw, value) = if byte == b't' {
                    (b"true".as_slice(), true)
                } else {
                    (b"false".as_slice(), false)
                };
                if self.input.get(self.at..self.at + raw.len()) != Some(raw) {
                    return Err(invalid("boolean differs").into());
                }
                self.at += raw.len();
                node.kind = BOOLEAN;
                node.boolean = Some(value);
            }
            b'n' => {
                if self.input.get(self.at..self.at + 4) != Some(b"null".as_slice()) {
                    return Err(invalid("null differs").into());
                }
                self.at += 4;
            }
            b'-' | b'0'..=b'9' => {
                let start = self.at;
                while self
                    .input
                    .get(self.at)
                    .is_some_and(|b| matches!(b, b'0'..=b'9' | b'-' | b'+' | b'.' | b'e' | b'E'))
                {
                    self.at += 1;
                }
                let raw = std::str::from_utf8(&self.input[start..self.at])?;
                let _: serde_json::Number = serde_json::from_str(raw)?;
                node.text = Some(raw.to_owned());
                if raw.bytes().any(|b| matches!(b, b'.' | b'e' | b'E')) {
                    node.kind = FLOAT;
                    let number: f64 = raw.parse()?;
                    if !number.is_finite() {
                        return Err(invalid("nonfinite float").into());
                    }
                    node.float = Some(number);
                } else {
                    node.kind = INTEGER;
                    node.integer = raw.parse().ok();
                }
            }
            _ => return Err(invalid("JSON node type differs").into()),
        }
        self.nodes.push(node);
        Ok(())
    }
}
fn parse(input: &[u8]) -> Result<Vec<Node>> {
    if input.len() as u64 > MAX_BYTES {
        return Err(invalid("canonical source exceeds 64 MiB").into());
    }
    let mut parser = Parser {
        input,
        at: 0,
        nodes: Vec::new(),
    };
    parser.value(None, 0, None, 0)?;
    if input.get(parser.at..) != Some(b"\n".as_slice()) {
        return Err(invalid("canonical source must end with one newline").into());
    }
    Ok(parser.nodes)
}
fn render(nodes: &[Node]) -> Result<Vec<u8>> {
    if nodes.is_empty() || nodes.len() > MAX_NODES {
        return Err(invalid("node count differs").into());
    }
    let mut emitter = Emitter::new(MAX_BYTES as usize, true)?;
    let mut cursor = 0;
    fn visit(
        nodes: &[Node],
        cursor: &mut usize,
        parent: Option<u32>,
        ordinal: u32,
        depth: usize,
        out: &mut Emitter,
    ) -> Result<()> {
        if depth > MAX_DEPTH {
            return Err(invalid("node depth differs").into());
        }
        let index = *cursor;
        let node = nodes
            .get(index)
            .ok_or_else(|| invalid("node table truncated"))?;
        if node.parent != parent || node.ordinal != ordinal {
            return Err(invalid("node parent or ordinal differs").into());
        }
        *cursor += 1;
        match node.kind {
            OBJECT | LIST => {
                if node.text.is_some()
                    || node.integer.is_some()
                    || node.float.is_some()
                    || node.boolean.is_some()
                {
                    return Err(invalid("container scalar present").into());
                }
                out.write(if node.kind == OBJECT { b"{" } else { b"[" })?;
                let mut count = 0u32;
                let mut previous: Option<&str> = None;
                while nodes
                    .get(*cursor)
                    .is_some_and(|next| next.parent == Some(index as u32))
                {
                    if count > 0 {
                        out.write(b",")?;
                    }
                    let child = &nodes[*cursor];
                    if node.kind == OBJECT {
                        let key = child
                            .key
                            .as_deref()
                            .ok_or_else(|| invalid("object child key missing"))?;
                        if previous.is_some_and(|last| last >= key) {
                            return Err(invalid("object key order differs").into());
                        }
                        out.string(key)?;
                        out.write(b":")?;
                        previous = Some(key);
                    } else if child.key.is_some() {
                        return Err(invalid("array child key present").into());
                    }
                    visit(nodes, cursor, Some(index as u32), count, depth + 1, out)?;
                    count = count
                        .checked_add(1)
                        .ok_or_else(|| invalid("ordinal overflow"))?;
                }
                out.write(if node.kind == OBJECT { b"}" } else { b"]" })?;
            }
            STRING => {
                if node.integer.is_some() || node.float.is_some() || node.boolean.is_some() {
                    return Err(invalid("string scalar conflict").into());
                }
                out.string(
                    node.text
                        .as_deref()
                        .ok_or_else(|| invalid("string missing"))?,
                )?;
            }
            INTEGER | FLOAT => {
                if node.boolean.is_some() {
                    return Err(invalid("numeric boolean conflict").into());
                }
                let raw = node
                    .text
                    .as_deref()
                    .ok_or_else(|| invalid("number text missing"))?;
                let _: serde_json::Number = serde_json::from_str(raw)?;
                if node.kind == INTEGER {
                    if raw.bytes().any(|b| matches!(b, b'.' | b'e' | b'E'))
                        || node.float.is_some()
                        || node.integer != raw.parse().ok()
                    {
                        return Err(invalid("integer projection differs").into());
                    }
                } else {
                    let value: f64 = raw.parse()?;
                    if !value.is_finite()
                        || node.integer.is_some()
                        || node.float.map(f64::to_bits) != Some(value.to_bits())
                    {
                        return Err(invalid("float projection differs").into());
                    }
                }
                out.write(raw.as_bytes())?;
            }
            BOOLEAN => {
                if node.text.is_some() || node.integer.is_some() || node.float.is_some() {
                    return Err(invalid("boolean scalar conflict").into());
                }
                out.write(if node.boolean.ok_or_else(|| invalid("boolean missing"))? {
                    b"true"
                } else {
                    b"false"
                })?;
            }
            NULL => {
                if node.text.is_some()
                    || node.integer.is_some()
                    || node.float.is_some()
                    || node.boolean.is_some()
                {
                    return Err(invalid("null scalar present").into());
                }
                out.write(b"null")?;
            }
            _ => return Err(invalid("node kind differs").into()),
        }
        Ok(())
    }
    if nodes[0].key.is_some() {
        return Err(invalid("root key present").into());
    }
    visit(nodes, &mut cursor, None, 0, 0, &mut emitter)?;
    if cursor != nodes.len() {
        return Err(invalid("unreachable node rows").into());
    }
    Ok(emitter
        .finish()?
        .0
        .ok_or_else(|| invalid("canonical output absent"))?)
}
fn batch(nodes: &[Node]) -> Result<RecordBatch> {
    let cols: Vec<ArrayRef> = vec![
        Arc::new(UInt32Array::from(
            nodes.iter().map(|n| n.parent).collect::<Vec<_>>(),
        )),
        Arc::new(UInt32Array::from(
            nodes.iter().map(|n| n.ordinal).collect::<Vec<_>>(),
        )),
        Arc::new(UInt8Array::from(
            nodes.iter().map(|n| n.kind).collect::<Vec<_>>(),
        )),
        Arc::new(StringArray::from(
            nodes.iter().map(|n| n.key.as_deref()).collect::<Vec<_>>(),
        )),
        Arc::new(StringArray::from(
            nodes.iter().map(|n| n.text.as_deref()).collect::<Vec<_>>(),
        )),
        Arc::new(Int64Array::from(
            nodes.iter().map(|n| n.integer).collect::<Vec<_>>(),
        )),
        Arc::new(Float64Array::from(
            nodes.iter().map(|n| n.float).collect::<Vec<_>>(),
        )),
        Arc::new(BooleanArray::from(
            nodes.iter().map(|n| n.boolean).collect::<Vec<_>>(),
        )),
    ];
    Ok(RecordBatch::try_new(schema(), cols)?)
}
fn down<T: 'static>(batch: &RecordBatch, index: usize) -> Result<&T> {
    batch
        .column(index)
        .as_any()
        .downcast_ref::<T>()
        .ok_or_else(|| invalid("node column type differs").into())
}
fn rows(path: &Path) -> Result<Vec<Node>> {
    if path.is_symlink() || !path.is_file() || fs::metadata(path)?.len() > MAX_PART {
        return Err(invalid("ordinary bounded Parquet file required").into());
    }
    let reader = ParquetRecordBatchReaderBuilder::try_new(File::open(path)?)?;
    if reader.schema().as_ref() != schema().as_ref() {
        return Err(invalid("node schema differs").into());
    }
    let mut nodes = Vec::new();
    for batch in reader.with_batch_size(BATCH).build()? {
        let batch = batch?;
        let parent = down::<UInt32Array>(&batch, 0)?;
        let ordinal = down::<UInt32Array>(&batch, 1)?;
        let kind = down::<UInt8Array>(&batch, 2)?;
        let key = down::<StringArray>(&batch, 3)?;
        let text = down::<StringArray>(&batch, 4)?;
        let integer = down::<Int64Array>(&batch, 5)?;
        let float = down::<Float64Array>(&batch, 6)?;
        let boolean = down::<BooleanArray>(&batch, 7)?;
        for i in 0..batch.num_rows() {
            if nodes.len() >= MAX_NODES || ordinal.is_null(i) || kind.is_null(i) {
                return Err(invalid("node row budget or required null differs").into());
            }
            nodes.push(Node {
                parent: (!parent.is_null(i)).then(|| parent.value(i)),
                ordinal: ordinal.value(i),
                kind: kind.value(i),
                key: (!key.is_null(i)).then(|| key.value(i).to_owned()),
                text: (!text.is_null(i)).then(|| text.value(i).to_owned()),
                integer: (!integer.is_null(i)).then(|| integer.value(i)),
                float: (!float.is_null(i)).then(|| float.value(i)),
                boolean: (!boolean.is_null(i)).then(|| boolean.value(i)),
            });
        }
    }
    Ok(nodes)
}
pub fn decode(path: &Path) -> Result<Vec<u8>> {
    render(&rows(path)?)
}
pub fn verify(source: &Path, parquet: &Path) -> Result<usize> {
    if source.is_symlink() || !source.is_file() || fs::metadata(source)?.len() > MAX_BYTES {
        return Err(invalid("ordinary bounded JSON source required").into());
    }
    let expected = fs::read(source)?;
    if decode(parquet)? != expected {
        return Err(invalid("canonical bytes differ").into());
    }
    Ok(expected.len())
}
pub fn encode(source: &Path, target: &Path) -> Result<(usize, u64, String)> {
    if source.is_symlink() || !source.is_file() || fs::metadata(source)?.len() > MAX_BYTES {
        return Err(invalid("ordinary bounded JSON source required").into());
    }
    encode_bytes(&fs::read(source)?, target)
}
pub fn encode_bytes(input: &[u8], target: &Path) -> Result<(usize, u64, String)> {
    if input.len() as u64 > MAX_BYTES {
        return Err(invalid("canonical source exceeds 64 MiB").into());
    }
    if target.exists() || target.is_symlink() {
        return Err(invalid("fresh target required").into());
    }
    let nodes = parse(input)?;
    if render(&nodes)? != input {
        return Err(
            invalid("source is not exact canonical JSON or has unsupported Unicode").into(),
        );
    }
    let temp = target.with_extension("parquet.pending");
    if temp.exists() || temp.is_symlink() {
        return Err(invalid("fresh staging path required").into());
    }
    let properties = WriterProperties::builder()
        .set_compression(Compression::ZSTD(Default::default()))
        .build();
    let mut writer = ArrowWriter::try_new(
        OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp)?,
        schema(),
        Some(properties),
    )?;
    for chunk in nodes.chunks(BATCH) {
        writer.write(&batch(chunk)?)?;
    }
    writer.close()?;
    File::open(&temp)?.sync_all()?;
    let size = fs::metadata(&temp)?.len();
    if size > MAX_PART || decode(&temp)? != input {
        return Err(invalid("Parquet round-trip differs or exceeds part budget").into());
    }
    // Create the final name only if absent. Rename would replace a concurrent
    // writer's file after the earlier freshness check.
    fs::hard_link(&temp, target)?;
    fs::remove_file(&temp)?;
    if let Some(parent) = target
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
    {
        File::open(parent)?.sync_all()?;
    }
    let hash = format!("{:x}", Sha256::digest(input));
    Ok((nodes.len(), size, hash))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn canonical_nested_nodes_roundtrip() {
        let input =
            b"{\"a\":[null,true,-0.0,12,1e-07,{\"x\":\"\\u2028\"}],\"z\":9223372036854775808}\n";
        let nodes = parse(input).unwrap();
        assert_eq!(render(&nodes).unwrap(), input);
        assert_eq!(nodes[1].kind, LIST);
        assert_eq!(nodes.last().unwrap().integer, None);
    }
    #[test]
    fn noncanonical_order_rejected() {
        assert!(parse(b"{\"z\":1,\"a\":2}\n").is_err());
    }
    #[test]
    fn parquet_write_is_exact_and_refuses_replacement() {
        let root = std::env::temp_dir().join(format!(
            "osr-case-nodes-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&root).unwrap();
        let source = root.join("case.json");
        let target = root.join("case.parquet");
        let bytes = b"{\"mass\":null,\"value\":-0.0}\n";
        fs::write(&source, bytes).unwrap();
        let (count, size, digest) = encode_bytes(bytes, &target).unwrap();
        assert_eq!(count, 3);
        assert!(size > 0);
        assert_eq!(digest, format!("{:x}", Sha256::digest(bytes)));
        assert_eq!(verify(&source, &target).unwrap(), bytes.len());
        let original = fs::read(&target).unwrap();
        assert!(encode_bytes(bytes, &target).is_err());
        assert_eq!(fs::read(&target).unwrap(), original);
        fs::remove_dir_all(&root).unwrap();
    }
}
