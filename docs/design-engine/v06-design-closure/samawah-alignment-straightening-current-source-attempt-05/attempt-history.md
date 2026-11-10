# Preserved run history

The bounded worker retained three failed executions before attempt 04 completed.
The failures were not converted into engineering results:

| Attempt | Source state | Outcome |
|---|---|---|
| 01 | Initial straightening worker | Git packfile could not be mapped under the 1 GiB address-space limit; no candidate evaluation ran. |
| 02 | Pack-window-limited worker | Missing local body binding raised `NameError` before a scenario evaluation. |
| 03 | Body binding corrected | A rounding-boundary stop chainage exceeded the route bound; no scenario was accepted. |
| 04 | Stop vertices rebound from the simplified polyline | Calculations completed; independent review identified that the README omitted the remaining platform-envelope failure. |
| 05 | Failure display corrected and source rerun | Current packet: all three scenarios still report one platform-envelope failure; no candidate selected. |

For attempts 01–03, request, execution, failure and process logs are retained
under `attempt-history/`. Their source commit and exact worker/runner hashes are
in each `request.json`; the source revisions remain in Git history. Attempt 04's
calculation identities match attempt 05; the final run and corrected reporting
are in this packet.
