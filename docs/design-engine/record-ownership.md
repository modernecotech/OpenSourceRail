# Record Ownership And Reviewed Handoffs

The shared work queue is a read-only projection. Each entry names its owner,
native identity, city and environment; completing one entry cannot overwrite
another system's history or release a railway.

| Concern | Authoritative record | Shared interface behaviour |
|---|---|---|
| Purchase, stock, manufacture, finance and HR | Native ERPNext/Frappe record and permissions | City/project-bound native routes; no mirrored business execution |
| Railway inspection, defect, NCR and handback | OSR assurance record and appointed authority | Reference the native revision and independent decision; ERP task closure grants no handback |
| Observation, alarm and scoped supervision | Existing integration gateway/controller | Observation context is visible; no movement-authority, protection-reset or point-command path |
| Problem, candidate and numerical attempt | Immutable local design store | Failed, stale, unknown and not-run remain distinct; restart and retry retain prior attempts |
| Appointments and submitted evidence | Private scoped record intake | Authenticated separate author/reviewer, exact revision and retained document hash; verification is record integrity/completeness |
| Physical or operational acceptance | Scope-qualified appointed independent authority | Data, search, checksums, role selectors and software task completion cannot create it |

Lost replies use idempotency keys. Reusing the key with different content fails.
Evidence or appointment verification requires named authenticated accounts;
the local trusted development actor cannot perform independent verification.
Accounts, native ERP employment records, professional competence and an
appointment are separate records. Expired appointments and self-review fail.

An exported candidate may prepare a reviewed ERP change draft. It identifies
the exact candidate, original attempts, deviations, source revision and required
test roles. Its `baseline_overwrite_permitted` and physical-release flags remain
false. Existing business and railway handoff workflows retain their permissions.
