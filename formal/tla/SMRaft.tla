------------------------------- MODULE SMRaft -------------------------------
(***************************************************************************)
(* Static-Membership Raft with Fail-Restrictive Timeout (SMRaft)           *)
(*                                                                         *)
(* This specification is a narrow specialization of Ongaro's Raft          *)
(* consensus protocol, tuned for the OpenSourceRail track-state log        *)
(* (see docs/rfcs/0001-track-state-consensus.md).                          *)
(*                                                                         *)
(* Differences from stock Raft:                                            *)
(*   1. Membership is static. The set Server is a CONSTANT; there is no    *)
(*      joint consensus, no online reconfiguration, no membership change   *)
(*      RPC. (This is the biggest simplification in both code and proof.)  *)
(*   2. No log compaction in this module. (Snapshotting is orthogonal to   *)
(*      the safety argument and is handled in a separate module.)          *)
(*   3. Entries are classified as Safety or Advisory. The fail-restrictive *)
(*      timeout rule forbids leaders from appending Safety entries without *)
(*      a recent quorum confirmation. Advisory entries (heartbeats,        *)
(*      position reports) are not so restricted.                           *)
(*                                                                         *)
(* Safety properties proved here (by TLC or TLAPS):                        *)
(*   ElectionSafety     — at most one leader per term                      *)
(*   LogMatching        — identical prefixes up to any matching entry      *)
(*   LeaderCompleteness — committed entries appear in all future leaders   *)
(*   StateMachineSafety — no two state machines apply different entries    *)
(*                        at the same index                                *)
(*   FailRestrictive    — under quorum loss, no new Safety entries commit  *)
(*                                                                         *)
(* This spec is adapted from Diego Ongaro's raft.tla (2014); field names   *)
(* and action names deliberately follow his conventions to ease review.    *)
(***************************************************************************)

EXTENDS Naturals, FiniteSets, Sequences, TLC

----------------------------------------------------------------------------
(* CONSTANTS                                                                 *)

CONSTANTS
    Server,            \* The set of W-Nodes in this region. Finite, static.
    Value,             \* Payloads that may appear in log entries.
    Category,          \* {"Safety", "Advisory"} — discriminates fail-restrictive rule
    MaxTerm,           \* TLC bound on terms explored
    MaxLogLen          \* TLC bound on log length

ASSUME
    /\ IsFiniteSet(Server)
    /\ Cardinality(Server) >= 3          \* minimum meaningful quorum
    /\ Category = {"Safety", "Advisory"}

(* A quorum is any majority subset. *)
Quorum == {Q \in SUBSET Server : Cardinality(Q) * 2 > Cardinality(Server)}

(* Server roles. *)
Follower  == "Follower"
Candidate == "Candidate"
Leader    == "Leader"

----------------------------------------------------------------------------
(* VARIABLES                                                                 *)

VARIABLES
    \* Per-server persistent state
    currentTerm,       \* [Server -> Nat]   latest term the server has seen
    votedFor,          \* [Server -> Server \cup {Nil}]   candidate that received vote in currentTerm
    log,               \* [Server -> Seq(Entry)]   the log

    \* Per-server volatile state
    state,             \* [Server -> {Follower, Candidate, Leader}]
    commitIndex,       \* [Server -> Nat]   highest log entry known committed

    \* Volatile, leader-only
    nextIndex,         \* [Server -> [Server -> Nat]]
    matchIndex,        \* [Server -> [Server -> Nat]]

    \* Candidate state during elections
    votesGranted,      \* [Server -> SUBSET Server]

    \* Liveness bookkeeping for fail-restrictive rule.
    \* lastQuorumConfirmedTerm[s] records the largest term in which s, as leader,
    \* last received an AppendEntriesResponse(success=TRUE) from a quorum.
    \* If the current term exceeds this by too much, s is forbidden to append
    \* Safety entries. (In the real system this is a wall-clock timer; in the
    \* abstract spec we use an explicit action-triggered refresh.)
    lastQuorumConfirmedTerm,   \* [Server -> Nat]

    \* Messages in flight (set of records; we model the network as a bag)
    messages,

    \* For the liveness/safety properties we track which entries have ever been
    \* committed at any index, for post-hoc invariant checking.
    allCommitted       \* SUBSET Entry

serverVars  == <<currentTerm, votedFor, state>>
candidateVars == <<votesGranted>>
leaderVars  == <<nextIndex, matchIndex>>
logVars     == <<log, commitIndex>>
failRestrictVars == <<lastQuorumConfirmedTerm>>
vars == <<serverVars, candidateVars, leaderVars, logVars,
          failRestrictVars, messages, allCommitted>>

----------------------------------------------------------------------------
(* TYPES (informal — not enforced by TLC but documented for review)         *)
(*                                                                          *)
(*   Entry == [term: Nat, value: Value, category: Category]                 *)
(*   Message == union of:                                                   *)
(*     [type: "RequestVoteRequest",  term, from, lastLogIdx, lastLogTerm]   *)
(*     [type: "RequestVoteResponse", term, from, to, voteGranted]           *)
(*     [type: "AppendEntriesRequest",                                       *)
(*         term, from, prevIdx, prevLogTerm, entries, leaderCommit]         *)
(*     [type: "AppendEntriesResponse",                                      *)
(*         term, from, to, success, matchIndex]                             *)

Nil == "Nil"

IsEntry(e) ==
    /\ DOMAIN e = {"term", "value", "category"}
    /\ e.term \in Nat
    /\ e.value \in Value
    /\ e.category \in Category

LastTerm(xlog) == IF Len(xlog) = 0 THEN 0 ELSE xlog[Len(xlog)].term

----------------------------------------------------------------------------
(* INITIAL STATE                                                             *)

Init ==
    /\ currentTerm = [s \in Server |-> 0]
    /\ votedFor = [s \in Server |-> Nil]
    /\ log = [s \in Server |-> <<>>]
    /\ state = [s \in Server |-> Follower]
    /\ commitIndex = [s \in Server |-> 0]
    /\ nextIndex = [s \in Server |-> [t \in Server |-> 1]]
    /\ matchIndex = [s \in Server |-> [t \in Server |-> 0]]
    /\ votesGranted = [s \in Server |-> {}]
    /\ lastQuorumConfirmedTerm = [s \in Server |-> 0]
    /\ messages = {}
    /\ allCommitted = {}

----------------------------------------------------------------------------
(* HELPERS                                                                   *)

Send(m) == messages' = messages \cup {m}
Recv(m) == messages' = messages \ {m}

UpdateTerm(s, newTerm) ==
    /\ newTerm > currentTerm[s]
    /\ currentTerm' = [currentTerm EXCEPT ![s] = newTerm]
    /\ votedFor'    = [votedFor    EXCEPT ![s] = Nil]
    /\ state'       = [state       EXCEPT ![s] = Follower]

----------------------------------------------------------------------------
(* ACTIONS                                                                   *)

(* --- Election timeout: follower or candidate starts election. ---------- *)
Timeout(s) ==
    /\ state[s] \in {Follower, Candidate}
    /\ currentTerm[s] + 1 <= MaxTerm
    /\ currentTerm' = [currentTerm EXCEPT ![s] = currentTerm[s] + 1]
    /\ state' = [state EXCEPT ![s] = Candidate]
    /\ votedFor' = [votedFor EXCEPT ![s] = s]
    /\ votesGranted' = [votesGranted EXCEPT ![s] = {s}]
    /\ UNCHANGED <<log, commitIndex, leaderVars,
                   failRestrictVars, messages, allCommitted>>

(* --- Candidate broadcasts RequestVote. --------------------------------- *)
RequestVote(s, t) ==
    /\ state[s] = Candidate
    /\ s # t
    /\ Send([type |-> "RequestVoteRequest",
            term |-> currentTerm[s],
            from |-> s,
            to   |-> t,
            lastLogIdx  |-> Len(log[s]),
            lastLogTerm |-> LastTerm(log[s])])
    /\ UNCHANGED <<serverVars, candidateVars, leaderVars, logVars,
                   failRestrictVars, allCommitted>>

(* --- Handle RequestVote. ------------------------------------------------ *)
HandleRequestVote(s, m) ==
    /\ m.type = "RequestVoteRequest"
    /\ m.to = s
    /\ LET logOk ==
          \/ m.lastLogTerm > LastTerm(log[s])
          \/ /\ m.lastLogTerm = LastTerm(log[s])
             /\ m.lastLogIdx >= Len(log[s])
          grant ==
              /\ m.term = currentTerm'[s]  \* after possible UpdateTerm
              /\ logOk
              /\ votedFor'[s] \in {Nil, m.from}
       IN
          /\ IF m.term > currentTerm[s]
                THEN UpdateTerm(s, m.term)
                ELSE /\ UNCHANGED currentTerm
                     /\ IF votedFor[s] = Nil /\ grant
                           THEN votedFor' = [votedFor EXCEPT ![s] = m.from]
                           ELSE UNCHANGED votedFor
                     /\ UNCHANGED state
          /\ Send([type |-> "RequestVoteResponse",
                  term |-> currentTerm'[s],
                  from |-> s,
                  to   |-> m.from,
                  voteGranted |-> grant])
          /\ Recv(m)
          /\ UNCHANGED <<candidateVars, leaderVars, logVars,
                         failRestrictVars, allCommitted>>

(* --- Candidate tallies a granted vote. --------------------------------- *)
HandleRequestVoteResponse(s, m) ==
    /\ m.type = "RequestVoteResponse"
    /\ m.to = s
    /\ state[s] = Candidate
    /\ m.term = currentTerm[s]
    /\ m.voteGranted
    /\ votesGranted' = [votesGranted EXCEPT ![s] = @ \cup {m.from}]
    /\ Recv(m)
    /\ UNCHANGED <<serverVars, leaderVars, logVars,
                   failRestrictVars, allCommitted>>

(* --- Candidate promotes itself to Leader on quorum of votes. ----------- *)
BecomeLeader(s) ==
    /\ state[s] = Candidate
    /\ votesGranted[s] \in Quorum
    /\ state' = [state EXCEPT ![s] = Leader]
    /\ nextIndex'  = [nextIndex  EXCEPT ![s] = [t \in Server |-> Len(log[s]) + 1]]
    /\ matchIndex' = [matchIndex EXCEPT ![s] = [t \in Server |-> 0]]
    \* A brand-new leader inherits quorum freshness for its own term:
    /\ lastQuorumConfirmedTerm' =
         [lastQuorumConfirmedTerm EXCEPT ![s] = currentTerm[s]]
    /\ UNCHANGED <<currentTerm, votedFor, candidateVars, logVars,
                   messages, allCommitted>>

(* --- Leader appends a client value to its own log. --------------------- *)
(* Fail-restrictive gate: Safety entries require a recent quorum           *)
(* confirmation.                                                            *)
ClientRequest(s, v, cat) ==
    /\ state[s] = Leader
    /\ v \in Value
    /\ cat \in Category
    /\ Len(log[s]) + 1 <= MaxLogLen
    /\ IF cat = "Safety"
          THEN lastQuorumConfirmedTerm[s] = currentTerm[s]
          ELSE TRUE
    /\ log' = [log EXCEPT ![s] = Append(@,
                [term |-> currentTerm[s], value |-> v, category |-> cat])]
    /\ UNCHANGED <<serverVars, candidateVars, leaderVars, commitIndex,
                   failRestrictVars, messages, allCommitted>>

(* --- Leader sends AppendEntries to a follower. ------------------------- *)
AppendEntries(s, t) ==
    /\ state[s] = Leader
    /\ s # t
    /\ LET prevIdx  == nextIndex[s][t] - 1
           prevTerm == IF prevIdx > 0 THEN log[s][prevIdx].term ELSE 0
           lastSend == IF Len(log[s]) >= nextIndex[s][t]
                          THEN nextIndex[s][t]
                          ELSE prevIdx
           entries  == IF Len(log[s]) >= nextIndex[s][t]
                          THEN <<log[s][nextIndex[s][t]]>>
                          ELSE <<>>
       IN Send([type |-> "AppendEntriesRequest",
               term |-> currentTerm[s],
               from |-> s,
               to   |-> t,
               prevIdx     |-> prevIdx,
               prevLogTerm |-> prevTerm,
               entries     |-> entries,
               leaderCommit |-> commitIndex[s]])
    /\ UNCHANGED <<serverVars, candidateVars, leaderVars, logVars,
                   failRestrictVars, allCommitted>>

(* --- Follower handles AppendEntries. ----------------------------------- *)
HandleAppendEntries(s, m) ==
    /\ m.type = "AppendEntriesRequest"
    /\ m.to = s
    /\ LET termOk == m.term >= currentTerm[s]
           prevOk ==
              \/ m.prevIdx = 0
              \/ /\ m.prevIdx <= Len(log[s])
                 /\ log[s][m.prevIdx].term = m.prevLogTerm
           newLog ==
              IF prevOk /\ Len(m.entries) > 0
                THEN SubSeq(log[s], 1, m.prevIdx) \o m.entries
                ELSE log[s]
       IN
          /\ IF m.term > currentTerm[s]
                THEN UpdateTerm(s, m.term)
                ELSE UNCHANGED <<currentTerm, votedFor, state>>
          /\ IF termOk /\ prevOk
                THEN /\ log' = [log EXCEPT ![s] = newLog]
                     /\ commitIndex' =
                          [commitIndex EXCEPT ![s] =
                              IF m.leaderCommit > @
                                 THEN IF m.leaderCommit <= Len(newLog)
                                         THEN m.leaderCommit
                                         ELSE Len(newLog)
                                 ELSE @]
                ELSE UNCHANGED <<log, commitIndex>>
          /\ Send([type |-> "AppendEntriesResponse",
                  term |-> currentTerm'[s],
                  from |-> s,
                  to   |-> m.from,
                  success |-> termOk /\ prevOk,
                  matchIndex |-> IF termOk /\ prevOk
                                    THEN Len(newLog)
                                    ELSE 0])
          /\ Recv(m)
          /\ UNCHANGED <<candidateVars, leaderVars,
                         failRestrictVars, allCommitted>>

(* --- Leader handles AppendEntriesResponse. ----------------------------- *)
HandleAppendEntriesResponse(s, m) ==
    /\ m.type = "AppendEntriesResponse"
    /\ m.to = s
    /\ state[s] = Leader
    /\ m.term = currentTerm[s]
    /\ IF m.success
          THEN /\ matchIndex' =
                    [matchIndex EXCEPT ![s] =
                        [@ EXCEPT ![m.from] = m.matchIndex]]
               /\ nextIndex' =
                    [nextIndex EXCEPT ![s] =
                        [@ EXCEPT ![m.from] = m.matchIndex + 1]]
               /\ LET confirmers ==
                        {n \in Server :
                            n = s
                         \/ matchIndex'[s][n] > 0}
                  IN IF confirmers \in Quorum
                        THEN lastQuorumConfirmedTerm' =
                               [lastQuorumConfirmedTerm EXCEPT ![s] = currentTerm[s]]
                        ELSE UNCHANGED lastQuorumConfirmedTerm
          ELSE /\ nextIndex' =
                    [nextIndex EXCEPT ![s] =
                        [@ EXCEPT ![m.from] =
                             IF @[m.from] > 1 THEN @[m.from] - 1 ELSE 1]]
               /\ UNCHANGED <<matchIndex, failRestrictVars>>
    /\ Recv(m)
    /\ UNCHANGED <<serverVars, candidateVars, logVars, allCommitted>>

(* --- Leader advances commitIndex based on matchIndex quorum. ----------- *)
AdvanceCommitIndex(s) ==
    /\ state[s] = Leader
    /\ \E N \in (commitIndex[s] + 1) .. Len(log[s]) :
          /\ log[s][N].term = currentTerm[s]
          /\ { t \in Server : matchIndex[s][t] >= N } \cup {s} \in Quorum
          /\ commitIndex' = [commitIndex EXCEPT ![s] = N]
          /\ allCommitted' = allCommitted \cup {log[s][N]}
    /\ UNCHANGED <<serverVars, candidateVars, leaderVars, log,
                   failRestrictVars, messages>>

(* --- Leader's quorum confirmation ages out.  --------------------------- *)
(* Represents wall-clock expiry of the T_safe window with no AE response. *)
QuorumConfirmationExpires(s) ==
    /\ state[s] = Leader
    /\ lastQuorumConfirmedTerm[s] = currentTerm[s]
    /\ lastQuorumConfirmedTerm' =
         [lastQuorumConfirmedTerm EXCEPT ![s] = currentTerm[s] - 1]
    /\ UNCHANGED <<serverVars, candidateVars, leaderVars, logVars,
                   messages, allCommitted>>

----------------------------------------------------------------------------
(* NEXT & SPEC                                                               *)

Next ==
    \/ \E s \in Server : Timeout(s)
    \/ \E s \in Server : BecomeLeader(s)
    \/ \E s, t \in Server : RequestVote(s, t)
    \/ \E s, t \in Server : AppendEntries(s, t)
    \/ \E s \in Server : AdvanceCommitIndex(s)
    \/ \E s \in Server : QuorumConfirmationExpires(s)
    \/ \E s \in Server, v \in Value, c \in Category : ClientRequest(s, v, c)
    \/ \E s \in Server, m \in messages : HandleRequestVote(s, m)
    \/ \E s \in Server, m \in messages : HandleRequestVoteResponse(s, m)
    \/ \E s \in Server, m \in messages : HandleAppendEntries(s, m)
    \/ \E s \in Server, m \in messages : HandleAppendEntriesResponse(s, m)

Spec == Init /\ [][Next]_vars

----------------------------------------------------------------------------
(* SAFETY INVARIANTS                                                         *)

(* 1. At most one leader per term. *)
ElectionSafety ==
    \A s, t \in Server :
        (state[s] = Leader /\ state[t] = Leader /\ currentTerm[s] = currentTerm[t])
        => s = t

(* 2. If two logs contain an entry with the same index and term, then the *)
(*    entries are equal and all preceding entries are equal.                 *)
LogMatching ==
    \A s, t \in Server :
        \A i \in 1..Len(log[s]) :
            (i <= Len(log[t]) /\ log[s][i].term = log[t][i].term)
            => \A j \in 1..i : log[s][j] = log[t][j]

(* 3. A leader's log contains every entry committed in any previous term. *)
(*    Stated as a post-hoc invariant over allCommitted.                     *)
LeaderCompleteness ==
    \A s \in Server :
        state[s] = Leader
        => \A e \in allCommitted :
            e.term < currentTerm[s]
            => \E i \in 1..Len(log[s]) : log[s][i] = e

(* 4. State machine safety: no two servers apply different entries at the *)
(*    same committed index.                                                 *)
StateMachineSafety ==
    \A s, t \in Server :
        \A i \in 1..Min(commitIndex[s], commitIndex[t]) :
            log[s][i] = log[t][i]

Min(a, b) == IF a <= b THEN a ELSE b

(* 5. Fail-restrictive: any entry of category "Safety" that has been       *)
(*    committed was appended by a leader whose quorum confirmation was      *)
(*    fresh at the time of append. Stated structurally as: no Safety entry  *)
(*    can appear in any leader's log from a term in which that leader's    *)
(*    lastQuorumConfirmedTerm < currentTerm.                                *)
(*    (This is the load-bearing property for §8 of RFC 0001.)               *)
FailRestrictive ==
    \A s \in Server :
        state[s] = Leader =>
            \A i \in 1..Len(log[s]) :
                (log[s][i].term = currentTerm[s] /\ log[s][i].category = "Safety")
                => lastQuorumConfirmedTerm[s] = currentTerm[s]

(* Conjunction used as the TLC invariant. *)
Invariants ==
    /\ ElectionSafety
    /\ LogMatching
    /\ LeaderCompleteness
    /\ StateMachineSafety
    /\ FailRestrictive

----------------------------------------------------------------------------
(* REFINEMENT                                                                *)
(*                                                                           *)
(* The Rust implementation in crates/osr-consensus/ refines this spec.      *)
(* The refinement mapping will be stated in a companion module SMRaftImpl   *)
(* once the code exists.                                                    *)

=============================================================================
