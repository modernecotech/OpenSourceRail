------------------------------ MODULE MCSmall ------------------------------
(* Small model-checking harness for SMRaft.                                 *)
(* Run with TLC: a 3-node cluster, 2 possible values, bounded terms/log.    *)
(* This is deliberately the smallest cluster that exercises a real quorum  *)
(* (2-of-3).                                                                *)

EXTENDS SMRaft

CONSTANTS n1, n2, n3, v1, v2

McServer == {n1, n2, n3}
McValue  == {v1, v2}
McCategory == {"Safety", "Advisory"}
McMaxTerm   == 3
McMaxLogLen == 3

=============================================================================
