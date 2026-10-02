--------------------------- MODULE TACSResources ---------------------------
EXTENDS Naturals, FiniteSets
CONSTANTS Trains, Resources, MaxEpoch
VARIABLES phase, owner, permission, occupant, mayEnter, epoch, quarantineDone
vars == <<phase, owner, permission, occupant, mayEnter, epoch, quarantineDone>>
Phases == {"available", "reserved", "occupied", "release-pending", "blocked", "unknown"}

Init == /\ phase = [r \in Resources |-> "unknown"]
        /\ owner = [r \in Resources |-> 0]
        /\ permission = [r \in Resources |-> FALSE]
        /\ occupant = [r \in Resources |-> 0]
        /\ mayEnter = [r \in Resources |-> FALSE]
        /\ epoch = 1 /\ quarantineDone = TRUE

Reserve(r,t) == /\ \A s \in Resources: phase[s] = "available"
                /\ \A s \in Resources: occupant[s] = 0 /\ ~mayEnter[s]
                /\ phase' = [phase EXCEPT ![r] = "reserved"]
                /\ owner' = [owner EXCEPT ![r] = t]
                /\ permission' = [permission EXCEPT ![r] = TRUE]
                /\ mayEnter' = [mayEnter EXCEPT ![r] = TRUE]
                /\ UNCHANGED <<occupant, epoch, quarantineDone>>

Enter(r) == /\ owner[r] # 0 /\ mayEnter[r] /\ occupant[r] = 0
            /\ occupant' = [occupant EXCEPT ![r] = owner[r]]
            /\ phase' = IF permission[r] THEN [phase EXCEPT ![r] = "occupied"] ELSE phase
            /\ UNCHANGED <<owner, permission, mayEnter, epoch, quarantineDone>>

Expire(r) == /\ permission[r]
             /\ permission' = [permission EXCEPT ![r] = FALSE]
             /\ phase' = [phase EXCEPT ![r] = "release-pending"]
             /\ UNCHANGED <<owner, occupant, mayEnter, epoch, quarantineDone>>

\* Qualified proof: full rear beyond the resource, or permission withdrawn
\* AND stop/approach protection proved. An empty detector or timer cannot do it.
ProveNoReentry(r) == /\ owner[r] # 0 /\ mayEnter[r] /\ phase[r] # "blocked"
                    /\ mayEnter' = [mayEnter EXCEPT ![r] = FALSE]
                    /\ occupant' = [occupant EXCEPT ![r] = 0]
                    /\ permission' = [permission EXCEPT ![r] = FALSE]
                    /\ phase' = [phase EXCEPT ![r] = "release-pending"]
                    /\ UNCHANGED <<owner, epoch, quarantineDone>>

Clear(r) == /\ phase[r] \in {"unknown", "release-pending"}
            /\ quarantineDone /\ occupant[r] = 0 /\ ~mayEnter[r]
            /\ phase' = [phase EXCEPT ![r] = "available"]
            /\ owner' = [owner EXCEPT ![r] = 0]
            /\ permission' = [permission EXCEPT ![r] = FALSE]
            /\ UNCHANGED <<occupant, mayEnter, epoch, quarantineDone>>

Restart == /\ epoch < MaxEpoch /\ epoch' = epoch + 1
           /\ quarantineDone' = FALSE
           /\ phase' = [r \in Resources |-> IF phase[r] = "blocked" THEN "blocked" ELSE "unknown"]
           /\ permission' = [r \in Resources |-> FALSE]
           /\ UNCHANGED <<owner, occupant, mayEnter>>
Elapsed == /\ ~quarantineDone /\ quarantineDone' = TRUE
           /\ UNCHANGED <<phase, owner, permission, occupant, mayEnter, epoch>>
ReconcileOwner(r) == /\ phase[r] = "unknown" /\ owner[r] # 0 /\ occupant[r] = owner[r]
                    /\ phase' = [phase EXCEPT ![r] = "occupied"]
                    /\ permission' = [permission EXCEPT ![r] = TRUE]
                    /\ UNCHANGED <<owner, occupant, mayEnter, epoch, quarantineDone>>
Block(r) == /\ phase[r] # "blocked"
            /\ phase' = [phase EXCEPT ![r] = "blocked"]
            /\ permission' = [permission EXCEPT ![r] = FALSE]
            /\ UNCHANGED <<owner, occupant, mayEnter, epoch, quarantineDone>>
IgnoreOldPacket == UNCHANGED vars

Next == (\E r \in Resources, t \in Trains: Reserve(r,t))
        \/ (\E r \in Resources: Enter(r) \/ Expire(r) \/ ProveNoReentry(r) \/ Clear(r) \/ ReconcileOwner(r) \/ Block(r))
        \/ Restart \/ Elapsed \/ IgnoreOldPacket
Spec == Init /\ [][Next]_vars
TypeOK == /\ phase \in [Resources -> Phases]
          /\ owner \in [Resources -> (Trains \cup {0})]
          /\ occupant \in [Resources -> (Trains \cup {0})]
          /\ permission \in [Resources -> BOOLEAN]
          /\ mayEnter \in [Resources -> BOOLEAN]
          /\ epoch \in 1..MaxEpoch /\ quarantineDone \in BOOLEAN
ExclusiveLocks == \A r,s \in Resources: r = s \/ owner[r] = 0 \/ owner[s] = 0
ProtectedOccupation == \A r \in Resources: occupant[r] = 0 \/ occupant[r] = owner[r]
NoConflictingOccupation == \A r,s \in Resources: r = s \/ occupant[r] = 0 \/ occupant[s] = 0
NoUnprotectedApproach == \A r \in Resources: mayEnter[r] => owner[r] # 0
AvailableClear == \A r \in Resources: phase[r] = "available" => (owner[r] = 0 /\ occupant[r] = 0 /\ ~mayEnter[r])
=============================================================================
