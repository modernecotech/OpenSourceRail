# Metropolitan railway layout and comparison

Start with a city’s walkable streets, residential population and named trip destinations. Generate a small set of connected networks around those trips. Allow existing routes to move or disappear. Test cross-city trunks, linked rings, suburban continuations and one additional urban connector where it can fill a measured gap. A city’s form and geography determine which patterns are viable.

Use actual street walks to measure station and named-destination access. Evaluate passenger journeys with a common operating budget. For each shortlisted network, recalculate construction quantities, operating resources and whole-life cost. Keep trade-offs visible when there is a choice between coverage, cost and the number of routes or stations. The shared comparison can rank the least-cost eligible layout only after the service, access and engineering requirements pass.

The shared method is implemented in `engineering/outline/metro_network.py`. Cities that lack the necessary walking, population or destination data retain their corridor-level planning workflow. A local adapter must supply the actual inputs and run the geography and cost models before the metropolitan ranking can be used.

[Baghdad worked study](../../../cities/Baghdad/THREE-RING-STUDY.md) · [City planning workflow](../../workbench/planning/README.md)
