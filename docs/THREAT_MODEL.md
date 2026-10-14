# Security and economic assumptions

**Critical:** Parity is not an escrow and it cannot enforce refunds against external suppliers. It implements an on-chain entitlement/price ceiling that participating consumers can enforce.

## Trust boundaries

- A beneficiary can create any proposed covenant; it is not active until the named provider wallet ratifies it.
- The provider's ratification explicitly endorses the whole immutable proposal including the exact HTTPS source path. It is an on-chain endorsement, **not cryptographic proof of DNS or GitHub ownership**.
- Anyone can point the primitive to public offer JSON under that source path; the provider cannot veto a genuine candidate *after* ratification. However a provider may conceal offers elsewhere, move content, or simply decline to publish the standard JSON. There is no exhaustive market completeness proof.
- A shared hosting domain alone is unsafe. The exact path prefix must pin the provider's owned repository/path. Source host HTTPS trust and public web availability are external dependencies.
- A document can change between fetches; leader and validators require the same source bytes digest and canonical payload. If they disagree, consensus rejects/rotates.
- HTTP success does not guarantee honest publisher statements. A provider can lie in its own public JSON; buyers must choose trustworthy source rules.
- `published_at` is declared by the source publisher. The consensus timestamp ensures it is not in the future, but it is not a cryptographic original-publication timestamp. This is a **provenance limitation**; it must not be represented as otherwise.
- A posted source might be removed after a trigger. Historical results remain; no automatic retroactive cancellation of a legitimately triggered cap is possible.

## Adversarial cases

| Attack | Defence / limitation |
|---|---|
| Provider spoofed by requester | proposal stays DRAFT without supplier wallet ratification |
| Wrong source/redirect/traversal | exact HTTPS path prefix and independent downloaded evidence; response redirects are a residual HTTP-client trust dependency |
| Reuse same offer URL | duplicate URL admission guard; invalid/unavailable URL releases reservation so genuine publication can be retried |
| Same external offer under new URL | `(covenant_id, provider_offer_id)` uniqueness after successful assessment |
| Invented cheap amount | full objective quote computed from fetched strict schema and reproduced in validator |
| Hidden one-time fee | mandatory structured setup/recurring fees; dishonest or omitted commercial terms remain an external source risk |
| Cheaper but inferior service | six substantive semantic comparison facets, any FAIL or UNCERTAIN prevents trigger |
| Missing audience coverage | explicit beneficiary audience facet; a private/targeted offer cannot automatically qualify |
| Changed source mid-consensus | exact raw digest and canonical payload digest comparison, fail closed |
| Malicious leader fabricates equivalence | independent refetch and LLM re-adjudication; exact six-facet agreement |
| Unavailable site | bounded retries, no trigger, no automatic assumption of favourable pricing |
| Malicious third party spams candidates | per covenant MAX_OFFERS=64 bounds storage, and provider/beneficiary each retain a bounded trusted reserve after the public pool fills. This is a bounded permissionless-admission tradeoff, not an unlimited storage path. |
| Contract tries to repay supplier directly | deliberately impossible; no custody or generic GEN transfer interface |
| Future offer price goes up | best verified cost never increases |
| Forged consumer invoice | exact covenant hash, beneficiary caller, amount cap and invoice-hash replay protection |
| Arbitrary hidden dependencies | only one flat monthly pricing model supported; non-flat terms are out of scope |

## Non-goals

- Private offers, tax/FX calculations, financing, rebates, contingent discounts, bundled cross-product concessions.
- Universal legal interpretation, automatic retroactive credits/refunds, attested original publication timestamp.
- Full history of all provider offers or fairness when the provider hides some offers.
- Authorization to move real GEN from either party; the downstream settlement IC is responsible for its own funds and ambiguous transfer recovery.
- Live pricing continuous monitoring or a guarantee that every offer is captured.

## Verified deployment boundary

The current StudioNet proof is recorded in [`../DEPLOYMENT.md`](../DEPLOYMENT.md) and [`../artifacts/studionet_proof.json`](../artifacts/studionet_proof.json). It proves a finalized lower comparable offer, a finalized higher-price no-op, a finalized wrong-provider rejection, duplicate-offer protection, and InvoiceGate authorization/rejection paths. A weaker-support evaluation was observed as NONCOMPARABLE before its transaction became unavailable from the RPC, and a missing-source evaluation remained COMMITTING; neither is represented as finalized live evidence. The repository-controlled fixture limitation remains material.
