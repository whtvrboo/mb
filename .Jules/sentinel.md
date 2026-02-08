# Sentinel's Journal

## 2025-02-18 - Account Takeover via Email Lookup
**Vulnerability:** The application identified users solely by email address from the IDP token. This allowed an attacker to takeover an existing account by changing their email in the IDP to match the victim's email.
**Learning:** Email addresses are mutable and can be recycled or spoofed depending on IDP configuration. Relying on them for identity without verifying the stable subject identifier (`sub`) leads to account takeover risks.
**Prevention:** Always link users to the immutable `sub` claim from the IDP. When looking up by email (e.g., for legacy migration), strictly verify that the user is not already bound to a different `sub`.
