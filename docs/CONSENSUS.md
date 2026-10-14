# Consensus boundary

Parity's deterministic boundary is established before semantic comparison:
the beneficiary proposes an immutable covenant, the named provider ratifies
it, and the exact HTTPS URL prefix, provider key, currency, quantity, term,
publication/validity bounds and fee fields are stored in the covenant
definition hash.

## Source observation

The leader and every validator independently call gl.nondet.web.get for the
same submitted URL. A response is eligible only when the pinned runtime
reports an integer HTTP status in the successful 2xx range. Missing,
malformed, 3xx, 4xx, 5xx and network-failure responses are unavailable
evidence. The accepted body is hashed, parsed as strict UTF-8 JSON and checked
against the source prefix, provider identity, schema, timestamps, quantity,
term, currency, billing period and deterministic integer price formula.

Validators independently reproduce the source digest, canonical payload
digest, normalized economic fields, calculated total and all six semantic
facet states. A leader cannot lower the cap by reporting a fabricated price,
source, payload, identity or facet. Natural-language rationale is explanatory
provenance and is not required to be byte-identical; the economic fields and
six bounded PASS/FAIL/UNCERTAIN outcomes are the decision boundary.

The six facets are scope, tier, support, territory, exclusions and audience. A
price-cap trigger requires all six to be PASS and the deterministically
calculated total to be strictly below the current best. Any FAIL, UNCERTAIN,
source mismatch, malformed structure, stale timestamp or failed fetch produces
no economic reduction.

## Economic state

Contract code, not the model, calculates:

~~~text
setup_fee_minor + term_months * (quantity * unit_price_minor + recurring_fee_minor)
~~~

The cap is monotonic: best_total(new) < best_total(old) <= original_total for
every trigger. A more expensive or materially weaker offer is recorded without
changing the cap. The final current deployment demonstrated a comparable
trigger from 123400 to 87400, a finalized NOT_BETTER result at 147400, and a
finalized weaker-support NONCOMPARABLE result with no cap effect.

## Trust boundaries

Provider-wallet ratification is an authorization decision, not cryptographic
proof that the provider owns the DNS name or repository. published_at is
declared by the source and bounded by consensus time; it is not an attested
historical publication timestamp. Repository-hosted fixtures prove the
contract path and are not independent commercial-market evidence. Parity does
not discover hidden offers, charge customers, escrow funds or issue refunds.

Prompt-injection text remains data inside a bounded semantic prompt. It cannot
call a transfer, amend covenant state or choose numeric economics. The
security and source-authentication limitations are documented in
THREAT_MODEL.md, and finalized current evidence is in DEPLOYMENT.md.
