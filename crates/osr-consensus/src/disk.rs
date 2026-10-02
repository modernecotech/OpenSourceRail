//! Reference filesystem journal. Persist and fsync before exposing ANY step action.
//! Compaction rewrites the full Raft log; no logical Raft snapshot/truncation is claimed.
use crate::{Config, Entry, LogIndex, NodeId, RaftNode, Term};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeMap,
    fs::{self, File, OpenOptions},
    io::{self, Read, Write},
    path::{Path, PathBuf},
};
const MAX_FRAME: usize = 128 * 1024 * 1024;
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Record {
    version: u16,
    binding: [u8; 32],
    node: NodeId,
    serial: u64,
    term: Term,
    vote: Option<NodeId>,
    committed: LogIndex,
    keep: usize,
    append: Vec<Entry>,
    application: Vec<u8>,
    sent: u64,
    received: BTreeMap<u64, u64>,
}
#[derive(Debug)]
pub struct DiskJournal {
    path: PathBuf,
    _lock: File,
    binding: [u8; 32],
    serial: u64,
    log: Vec<Entry>,
    pub application: Vec<u8>,
    pub sent: u64,
    pub received: BTreeMap<u64, u64>,
}
impl DiskJournal {
    pub fn open(
        path: impl AsRef<Path>,
        config: Config,
        binding: [u8; 32],
        now: u64,
    ) -> io::Result<(Self, RaftNode)> {
        let path = path.as_ref().to_path_buf();
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        let lock = OpenOptions::new()
            .create(true)
            .truncate(false)
            .read(true)
            .write(true)
            .open(path.with_extension("lock"))?;
        lock.try_lock().map_err(io::Error::other)?;
        let mut store = Self {
            _lock: lock,
            path: path.clone(),
            binding,
            serial: 0,
            log: Vec::new(),
            application: Vec::new(),
            sent: 0,
            received: BTreeMap::new(),
        };
        let mut node = RaftNode::new(config, now);
        if path.exists() {
            let file = File::open(&path)?;
            if file.metadata()?.len() > 512 * 1024 * 1024 {
                return Err(bad("journal exceeds reference capacity"));
            }
            let mut bytes = Vec::new();
            file.take(512 * 1024 * 1024 + 1).read_to_end(&mut bytes)?;
            let mut offset = 0;
            while offset < bytes.len() {
                if bytes.len() - offset < 8 {
                    return Err(bad("torn journal header; startup inhibited"));
                }
                let len = u32::from_le_bytes(
                    bytes[offset..offset + 4]
                        .try_into()
                        .map_err(|_| bad("header"))?,
                ) as usize;
                if len > MAX_FRAME || len + 8 > bytes.len() - offset {
                    return Err(bad("torn or oversized journal frame; startup inhibited"));
                }
                let payload = &bytes[offset + 4..offset + 4 + len];
                let crc = u32::from_le_bytes(
                    bytes[offset + 4 + len..offset + 8 + len]
                        .try_into()
                        .map_err(|_| bad("CRC"))?,
                );
                if crc != super::durable::crc32(payload) {
                    return Err(bad("journal CRC; startup inhibited"));
                }
                let r: Record =
                    serde_json::from_slice(payload).map_err(|_| bad("journal schema"))?;
                if r.version != 1
                    || r.binding != binding
                    || r.node != node.config.me
                    || r.serial != store.serial + 1
                    || r.keep > store.log.len()
                    || r.term < node.current_term
                    || r.sent < store.sent
                    || r.committed < node.commit_index
                    || r.keep < node.commit_index.0 as usize
                    || store.received.iter().any(|(peer, sequence)| {
                        r.received.get(peer).copied().unwrap_or(0) < *sequence
                    })
                {
                    return Err(bad("journal identity/order"));
                }
                store.log.truncate(r.keep);
                store.log.extend(r.append);
                if r.committed.0 > store.log.len() as u64 {
                    return Err(bad("commit beyond journal"));
                }
                store.serial = r.serial;
                store.application = r.application;
                store.sent = r.sent;
                store.received = r.received;
                node.current_term = r.term;
                node.voted_for = r.vote;
                node.commit_index = r.committed;
                offset += len + 8;
            }
            if store.serial == 0 {
                return Err(bad("empty existing journal"));
            }
            node.log = store.log.clone();
        }
        Ok((store, node))
    }
    pub fn persist(&mut self, node: &RaftNode) -> io::Result<()> {
        let keep = self
            .log
            .iter()
            .zip(&node.log)
            .take_while(|(a, b)| a == b)
            .count();
        let record = Record {
            version: 1,
            binding: self.binding,
            node: node.config.me,
            serial: self
                .serial
                .checked_add(1)
                .ok_or_else(|| bad("serial overflow"))?,
            term: node.current_term,
            vote: node.voted_for,
            committed: node.commit_index,
            keep,
            append: node.log[keep..].to_vec(),
            application: self.application.clone(),
            sent: self.sent,
            received: self.received.clone(),
        };
        let bytes = frame(&record)?;
        fs::create_dir_all(self.path.parent().ok_or_else(|| bad("journal directory"))?)?;
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.path)?;
        if file.metadata()?.len().saturating_add(bytes.len() as u64) > 512 * 1024 * 1024 {
            return Err(bad("journal storage capacity"));
        }
        file.write_all(&bytes)?;
        file.sync_all()?;
        File::open(self.path.parent().ok_or_else(|| bad("directory"))?)?.sync_all()?;
        self.serial = record.serial;
        self.log.truncate(keep);
        self.log.extend_from_slice(&node.log[keep..]);
        Ok(())
    }
    pub fn compact(&mut self, node: &RaftNode) -> io::Result<()> {
        let record = Record {
            version: 1,
            binding: self.binding,
            node: node.config.me,
            serial: 1,
            term: node.current_term,
            vote: node.voted_for,
            committed: node.commit_index,
            keep: 0,
            append: node.log.clone(),
            application: self.application.clone(),
            sent: self.sent,
            received: self.received.clone(),
        };
        let temp = self.path.with_extension("checkpoint.tmp");
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp)?;
        file.write_all(&frame(&record)?)?;
        file.sync_all()?;
        fs::rename(&temp, &self.path)?;
        File::open(self.path.parent().ok_or_else(|| bad("directory"))?)?.sync_all()?;
        self.serial = 1;
        self.log = node.log.clone();
        Ok(())
    }
}
fn bad(message: &str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message)
}
fn frame(record: &Record) -> io::Result<Vec<u8>> {
    let payload = serde_json::to_vec(record).map_err(|_| bad("serialize journal"))?;
    if payload.len() > MAX_FRAME {
        return Err(bad("journal frame capacity"));
    }
    let mut data = Vec::with_capacity(payload.len() + 8);
    data.extend_from_slice(&(payload.len() as u32).to_le_bytes());
    data.extend_from_slice(&payload);
    data.extend_from_slice(&super::durable::crc32(&payload).to_le_bytes());
    Ok(data)
}
