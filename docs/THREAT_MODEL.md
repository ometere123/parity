# Security and economic assumptions

Parity is not escrow. It records an on-chain entitlement/price ceiling that
participating consumers can enforce; it does not collect funds, charge
customers, refund invoices or prove that every market offer was discovered.

## Trust boundaries

- A beneficiary can propose a covenant, but it remains DRAFT until the named
  provider wallet ratifies the immutable definition.
- Provider-wallet ratification endorses the exact source prefix and baseline.
  It is not cryptographic proof of DNS, GitHub or commercial-domain ownership.
- The source publisher declares published_at. The contract bounds it against
  activation and consensus time but does not attest the original publication
  timestamp.
- Repository-controlled fixtures are reproducible protocol evidence, not
  independent proof of third-party commercial pricing.
- A valid HTTP response status authenticates transport success, not the truth
  of the provider's JSON. Missing or malformed status, network failure,
  redirects, 4xx and 5xx bodies are rejected before they can affect the cap.

## Adversarial cases and controls

| Attack | Defence or honest limitation |
|---|---|
| Provider spoofed by requester | The proposal remains DRAFT without the named provider's ratification. |
| Unauthorized source or path substitution | HTTPS, public-DNS, credentials/port/query/fragment/traversal restrictions and the full ratified path prefix are checked. |
| Non-success HTTP body containing valid JSON | Response status must be an integer 2xx; 3xx/4xx/5xx/missing/malformed status is unavailable evidence. |
| Source changes between observers | Leader and validators independently refetch and require the decision-critical source/payload/economic observations to agree. |
| Fabricated cheap amount | Validators recompute strict JSON fields and the contract recomputes the integer full-term total. |
| Hidden fee or unsupported pricing model | Setup, recurring and unit fees are mandatory integer fields; non-flat or missing structures fail closed. |
| Cheaper but inferior service | Scope, tier, support, territory, exclusions and audience must all be PASS; FAIL or UNCERTAIN has no economic effect. |
| Prompt injection | Remote text is bounded as data in the semantic prompt and cannot call a transfer, alter a covenant or choose arithmetic. |
| Offer replay | The exact covenant/URL reservation and successful provider offer ID are protected by separate duplicate checks. |
| Public-pool exhaustion | MAX_OFFERS is bounded while reserved provider/beneficiary capacity remains bounded and explicit. |
| Future price increase | best_total only decreases on a strictly cheaper all-PASS assessment. |
| Consumer bypass | InvoiceGate is bound at construction, requires the beneficiary caller, the current covenant hash, the active cap and a fresh invoice hash. |
| Replay through formatting | Invoice hashes and covenant hashes are validated as fixed-length hexadecimal values and invoice keys are normalized before storage. |

## Residual assumptions

The provider can withhold an offer, change or remove public source content after
an assessment, or publish a misleading but schema-valid statement. Parity
cannot authenticate commercial truth beyond the ratified public source and
consensus observation. It does not discover private discounts, attest all
customers receive the same price, or guarantee catalogue completeness.

The current finalized StudioNet evidence is in DEPLOYMENT.md and
artifacts/studionet_proof.json. It includes the HTTP-status correction in the
current Parity deployment, a lower comparable trigger, a higher-price no-op, a
weaker-support rejection, and current InvoiceGate positive and negative
readbacks.
