use osr_consensus::{disk::DiskJournal, Category, Config, Entry, LogIndex, NodeId, Role, Term};
use std::{
    collections::BTreeSet,
    fs,
    io::Write,
    path::PathBuf,
    sync::atomic::{AtomicU64, Ordering},
};
static SERIAL: AtomicU64 = AtomicU64::new(0);
fn path() -> PathBuf {
    std::env::temp_dir()
        .join(format!(
            "osr-journal-{}-{}",
            std::process::id(),
            SERIAL.fetch_add(1, Ordering::Relaxed)
        ))
        .join("state")
}
fn cfg() -> Config {
    Config::with_defaults(NodeId(1), BTreeSet::from([NodeId(1), NodeId(2), NodeId(3)]))
}
#[test]
fn every_persisted_transition_recovers_lock_and_replay_fences_without_leadership() {
    let p = path();
    for transition in 1..=6 {
        let (mut store, mut node) = DiskJournal::open(&p, cfg(), [7; 32], 1).unwrap();
        node.current_term = Term(transition);
        node.voted_for = Some(NodeId(2));
        node.log.push(Entry::new(
            Term(transition),
            b"retained-owner".to_vec(),
            Category::Safety,
        ));
        node.commit_index = LogIndex(transition);
        store.sent = transition;
        store.received.insert(101, transition);
        store.application = b"recovery-required".to_vec();
        store.persist(&node).unwrap();
        drop(store);
        let (store, recovered) = DiskJournal::open(&p, cfg(), [7; 32], 10).unwrap();
        assert_eq!(recovered.log, node.log);
        assert_eq!(recovered.commit_index, node.commit_index);
        assert_eq!(recovered.voted_for, Some(NodeId(2)));
        assert_eq!(recovered.role, Role::Follower);
        assert!(recovered.quorum_acknowledgements.is_empty());
        assert_eq!(store.sent, transition);
        assert_eq!(store.received[&101], transition);
        assert_eq!(store.application, b"recovery-required");
    }
    fs::remove_dir_all(p.parent().unwrap()).unwrap();
}
#[test]
fn compaction_retains_full_log_and_an_exclusive_writer() {
    let p = path();
    let (mut store, mut node) = DiskJournal::open(&p, cfg(), [7; 32], 1).unwrap();
    node.log
        .push(Entry::new(Term(1), vec![1, 2, 3], Category::Safety));
    node.current_term = Term(1);
    node.commit_index = LogIndex(1);
    for _ in 0..8 {
        store.persist(&node).unwrap();
    }
    let before = fs::metadata(&p).unwrap().len();
    assert!(DiskJournal::open(&p, cfg(), [7; 32], 1).is_err());
    store.compact(&node).unwrap();
    assert!(fs::metadata(&p).unwrap().len() < before);
    drop(store);
    let (_, recovered) = DiskJournal::open(&p, cfg(), [7; 32], 2).unwrap();
    assert_eq!(recovered.log, node.log);
    fs::remove_dir_all(p.parent().unwrap()).unwrap();
}
#[test]
fn every_torn_suffix_and_configuration_disagreement_inhibit_startup() {
    let p = path();
    let (mut store, node) = DiskJournal::open(&p, cfg(), [7; 32], 1).unwrap();
    store.persist(&node).unwrap();
    drop(store);
    let complete = fs::read(&p).unwrap();
    assert!(DiskJournal::open(&p, cfg(), [8; 32], 1).is_err());
    for size in [0, 1, 3, 4, 7, complete.len() - 1] {
        fs::write(&p, &complete[..size]).unwrap();
        assert!(DiskJournal::open(&p, cfg(), [7; 32], 1).is_err());
    }
    fs::write(&p, &complete).unwrap();
    fs::OpenOptions::new()
        .append(true)
        .open(&p)
        .unwrap()
        .write_all(&[1])
        .unwrap();
    assert!(DiskJournal::open(&p, cfg(), [7; 32], 1).is_err());
    fs::remove_dir_all(p.parent().unwrap()).unwrap();
}
