# Manufacture and maintenance custody

An engineering model becomes useful to a workshop when its parts can be
made or received, inspected, assembled and later identified in the field.
The v0.7 lifecycle work asks the platform to follow one exact module from
its design candidate through those ordinary business steps. The door
operator is the test case, because it includes local fabrication,
qualified purchases, electrical work and replacement during service.

## The bill of materials is a beginning

A counted door proposal names parts and quantities, but production needs
more. A maker needs drawings, materials, allowable variation, routing,
tooling and inspection points. A buyer needs an approved specification,
supplier identity and a way to check what arrives. An assembler needs a
sequence and a record of the parts that went into each serialized unit.
Without these details, a seemingly complete bill of materials can still
allow two workshops to build incompatible doors.

The current delivery tools can prepare reviewable tasks and draft groups
from a candidate. They can preserve parent assembly and child relationships
without treating an assembly as a featureless single part. They do not
authorize a purchase or shop order merely because a draft exists. Cost
estimates for assembly operations remain hypotheses until real process
routes and measured or justified times are available.

## Trace bought and made children

The software custody design distinguishes a made child from a purchased
one. A made child should have its own reviewed work record, source parts
and accepted quality inspection. A purchased child should be tied to a
received item, its serial and batch where applicable, and an incoming
inspection. When children are consumed into a parent, the records should
account for the exact units, not a convenient count of “one kit.” A
replacement parent should point to the specific removed serial and the
repair event that made the exchange legitimate.

This is especially important for the door. Of its 694 pieces per opening,
597 are proposed purchases across the standard and qualification routes.
Those items need a practical receipt and traceability policy, while the
locally fabricated pieces need process and inspection evidence. The current
software can reject some mismatched or missing child records and has
synthetic examples of made and bought custody. Those tests are useful for
the digital contract. They are not an actual receipt and installation of
the complete door in ERPNext.

## A repair should teach the next design

Once a module is in service, a condition report, alarm, inspection and
replacement should remain linked to its candidate and serial. A reader
could then ask whether a recurrent fault belongs to one supplier batch,
one assembly revision, a station environment or a maintenance method.
The answer could lead to a revised component, changed inspection interval
or different supplier. The platform's FUXA and gateway integrations can
provide observations and maintenance handoffs, but a live device and
business deployment need commissioning, roles and review.

The planned v0.7 demonstration should show a real candidate-linked door
module moving through draft, receipt or manufacture, QA, assembly,
installation, condition event, replacement and business handback. Each
step should refuse a missing document or conflicting revision. The
existing native fixture exercises a simpler discrete workpiece, not this
full chain. Physical installation and operating permission remain separate
even after the digital record is complete.

## Why the record matters years later

Railway components often outlive the software version that first described
them. A replacement door may have a revised drive while sharing a body
opening with older cars. A serial record can tell a maintainer which
revision is fitted, which inspection limits apply and which spare parts
will mate. It can also show whether a supplier change affected only a
bearing or required a new assembly test. Without that history, “like for
like” can become an unsafe assumption.

Local repair capacity grows when these records remain accessible to the
owner and its workshops. Staff can learn from failure rates, rework,
actual labour hours and incoming defects rather than relying on a
catalogue estimate forever. That feedback belongs in the next design
revision and cost model. The goal is an accountable lifecycle that a
city can operate and improve, while keeping purchasing, engineering and
safety approvals in the hands of the responsible people.
