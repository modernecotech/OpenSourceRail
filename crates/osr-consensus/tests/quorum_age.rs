use osr_consensus::{
    step, Action, AppendEntriesResponse, Category, Config, Event, LogIndex, Message, NodeId,
    RaftNode, Role, Term,
};
use std::collections::BTreeSet;
fn ack(node: &mut RaftNode, peer: u16, now: u64) {
    step(
        node,
        Event::Recv(Message::AppendEntriesResponse(AppendEntriesResponse {
            term: Term(1),
            from: NodeId(peer),
            to: NodeId(1),
            success: true,
            match_index: LogIndex(0),
        })),
        now,
    );
}
#[test]
fn empty_heartbeats_refresh_a_real_quorum_but_historical_peers_do_not() {
    let cfg = Config::with_defaults(
        NodeId(1),
        BTreeSet::from([NodeId(1), NodeId(2), NodeId(3), NodeId(4), NodeId(5)]),
    );
    let mut node = RaftNode::new(cfg, 1);
    node.role = Role::Leader;
    node.current_term = Term(1);
    ack(&mut node, 2, 100);
    ack(&mut node, 3, 100);
    assert!(node.quorum_confirmation_fresh());
    step(&mut node, Event::Tick, 600_000_100);
    ack(&mut node, 2, 600_000_100);
    assert!(!node.quorum_confirmation_fresh());
    assert!(step(
        &mut node,
        Event::Propose {
            value: vec![1],
            category: Category::Safety
        },
        600_000_100
    )
    .iter()
    .any(|a| matches!(a, Action::ProposeRejected { .. })));
    ack(&mut node, 4, 600_000_100);
    assert!(node.quorum_confirmation_fresh());
}
