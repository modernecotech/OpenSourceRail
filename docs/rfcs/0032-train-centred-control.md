# RFC 0032 — Train-centred control prototype (superseded)

**Status:** superseded by [RFC 0033](0033-tacs-runtime-and-resource-control.md).

The original prototype introduced a separate `osr-tacs` movement-authority and
protection implementation. It is retired in favour of resource contracts in
`osr-core`, committed lifecycle handling in `osr-interlocking`, and thin
`osr-runtime` process hosts around the existing consensus/MA/ATP/ATO/brake path.
The previous synchronous twin results are replaced by actual process-reference
execution. Bounded resource-model evidence remains explicitly limited to its
physical-proving assumptions. No hardware or operating release is claimed.
