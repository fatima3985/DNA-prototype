# Safe evidence register

Fatima coordinates; each implementer supplies reproducible evidence and the relevant reviewer accepts it. This scaffold contains no runtime evidence.

## Runtime evidence

| Task / gate | Exact NIS / HOST commits | Approved environment / dataset | Expected / actual result | Status | Safe private-artifact reference | Reviewer | Run record | Open defects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G0 (due 17 Nov): owners named, isolated lab approved, source inventory, tasks accepted | Not recorded | Not verified | Not executed | NOT RUN | | Hamees + engineering coordinators; Maria/Mahreen review | None | Not recorded |
| G1 (due 20-22 Nov): real network event to existing SecureOps UI; retry and rejection checks | Not recorded | Not verified | Not executed | NOT RUN | | Backend + sensor lead + Frontend + Blue/Red | None | Not recorded |
| G2 (due 29 Nov): three sources connected; D01-D05 results; finding linked to incident | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd + Hamdiya + engineering; Maria retests | None | Not recorded |
| G2 / D01 port scan (positive, benign, held-out) | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd; Maria retests | None | Not recorded |
| G2 / D02 DNS indicator | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd; Maria retests | None | Not recorded |
| G2 / D03 auth failures | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd; Maria retests | None | Not recorded |
| G2 / D04 firewall denies | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd; Maria retests | None | Not recorded |
| G2 / D05 cross-source (time-valid host mapping) | Not recorded | Not verified | Not executed | NOT RUN | | Lloyd + Warisha; Maria retests | None | Not recorded |
| G3 (due 2 Dec): real packet evidence; hash match; retrieval and denial paths | Not recorded | Not verified | Not executed | NOT RUN | | Backend + sensor/operations + Blue/Red | None | Not recorded |
| G4 (due 4-6 Dec): restart, replay, outage recovery, load, restore, rollback | Not recorded | Not verified | Not executed | NOT RUN | | Maria + Mahreen + engineering + operations | None | Not recorded |
| G5 (due 7 Dec): full connected analyst journey on recorded commits | Not recorded | Not verified | Not executed | NOT RUN | | Hamees; evidence owners sign | None | Not recorded |

Use [the evidence template](../../docs/templates/TEST_EVIDENCE.md). Create a run record in [run-results](run-results/) only when a run happens or a gate is formally marked BLOCKED or FAILED. Name it with the gate or test ID, the date and a version, for example `G1-20261122-v1.md`. Sanitized per-run notes may go in run-results; sensitive raw artifacts remain outside Git. Document checks do not establish runtime acceptance. A passing isolated test is not a passing gate.

## Document validation (separate from runtime testing)

| Item | Document | Check | Date | Reviewer | Result |
| --- | --- | --- | --- | --- | --- |
| Readiness corrections | Blue Team protocols (BT-PRO-001 and related) | [what was checked] | [date] | [name] | Open |

## Related records

- [Missing inputs](MISSING_INPUTS.md)
- [Collection and retention matrix](COLLECTION_RETENTION.md)
