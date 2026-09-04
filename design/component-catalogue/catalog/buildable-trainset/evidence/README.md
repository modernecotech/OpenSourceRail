# LM3 evidence workspace

Keep only genuine, attributable first-article evidence here. Use
`rfq-response-template.json` for supplier offers and controlled data,
`test-run-template.json` for performed work,
`mass-properties-record-template.json` for the complete product/car/axle/CG
reconciliation, and `submission-template.json` for the independent gate
disposition. Raw artifacts may be committed when each file is below 50 MiB;
otherwise use a controlled evidence store and commit its durable URL and
checksum.

Do not pre-sign templates, copy public marketing claims into a test result, or mark a gate accepted without an identifiable independent reviewer.

The mass-properties template is generated from the current product and mass
ledgers. Its null fields are deliberate: an empty template or a calculation
from envelope geometry is not evidence and cannot lower controlled tare.
