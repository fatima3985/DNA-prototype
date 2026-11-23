# Collection and retention matrix

| Evidence type | Collected by | Stored | Access | Retention | Original kept |
| --- | --- | --- | --- | --- | --- |
| Raw packets | Sensor engineer | Approved private store | Named people only | Per approved policy (to confirm) | Yes |
| Auth logs | Source owner | Approved private store | Named people only | Per approved policy (to confirm) | Yes |
| TLS syslog | Source owner | Approved private store | Named people only | Per approved policy (to confirm) | Yes |
| Packet capture window and object hash (G3) | Sensor / operations | Approved private store | Authorised grant only; separate from metadata permission | Per approved policy (to confirm) | Yes |
| Evidence manifests | SecureOps | SecureOps | Metadata permission only (not packet bytes) | Per approved policy (to confirm) | Yes |
| D01-D05 versioned results (G2) | Lloyd | Safe reference in the register | Blue Team | Per approved policy (to confirm) | Yes |
| Alert delivery records | Isha | Safe reference in the register | Blue Team | Per approved policy (to confirm) | Yes |
| Denial test results (G3) | Engineers, Blue/Red | Safe reference in the register | Blue Team | Per approved policy (to confirm) | Yes |
| Declared-load measurements (G4) | Engineering | Safe reference in the register | Blue Team | Per approved policy (to confirm) | Yes |
| Restore and rollback results (G4) | Operations | Safe reference in the register | Blue Team | Per approved policy (to confirm) | Yes |
| Sanitized run notes | Engineer who ran it | `run-results/` in Git | Repository access | Per approved policy (to confirm) | n/a |

Raw packets, credentials and sensitive logs stay in the approved private store. The repository holds safe references only. Retention values stay "to confirm" until the approved retention policy is identified.
