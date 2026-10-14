# Parity — source-backed most-favoured-terms primitive

**Contract-only. No frontend. Studionet stable chain `61999`, RPC `https://studio.genlayer.com/api`, local `genlayer@0.39.1`.**

Parity turns an agreed most-favoured-terms covenant into a machine-readable, monotonically non-increasing price cap when an authentic, publicly published, **materially comparable** provider offer is independently verified by GenLayer consensus. The core invariant is simple:

> No later public offer may lower the protected beneficiary's entitlement unless every frozen non-price dimension remains no worse, the source is pinned to a provider-ratified authoritative URL prefix, and deterministic price normalization proves it is cheaper.

Unlike a generic LLM price comparator, Parity separates **semantic quality** from **numeric economics**. A model cannot propose a new price or amend the covenant; numeric prices and fees are extracted as integers from provider-published strict JSON. Six semantic quality dimensions are independently re-evaluated by validators. Contract state only ever decreases the beneficiary's maximum eligible cost.

## What it does — and what it does not

A buyer proposes a bounded covenant with a supplier. The supplier ratifies the buyer's exact baseline, including authoritative source prefix, currency, service scope, tier, support, territory, exclusions, beneficiary audience, purchase quantity, term duration, setup/recurring fees, and expiry. This creates an immutable covenant hash. Anyone can submit a provider-official JSON offer hosted under the ratified **full URL path prefix**. A validator-safe nondeterministic operation fetches the bytes, computes a content digest, checks mandatory schema and provenance limits, normalizes the full-term price *deterministically*, and compares six material non-price facets under independent consensus. Only a strictly cheaper, all-PASS offer reduces the active price cap. A subsequent, worse offer cannot raise it.

The optional `ParityInvoiceGate` is another **contract-only** IC demonstrating enforcement. It refuses a protected beneficiary's invoice authorization if the exact covenant hash is wrong, the quote is expired, the charge exceeds the current cap, or the invoice hash was consumed already.

**Parity does not charge, refund, custody, transfer, automatically discover, or independently authenticate all commercial offers.** The supplier wallet ratifies the web-source prefix but no wallet-to-domain cryptographic proof is claimed. A contract cannot prove completeness of the supplier's entire commercial sales catalogue, private discounts, or the veracity of undisclosed commercial terms. A provider can still withhold an offer; this primitive only makes **observed, ratified-source offers** actionable. It is not legal advice or evidence that all customers receive the same deal.

## Contract architecture

```text
Beneficiary creates DRAFT covenant -- frozen baseline & provider-approved source path
           |
     named Provider wallet ratifies
           v
       ACTIVE covenant (immutable definition hash)
           |
       anyone submits candidate URL inside exact allowed prefix
           |
       independent validator fetch of actual official JSON
           |-- source mismatch/bad terms/unavailable --> no price effect
           v
  deterministic: provider ID, currency, published/valid time, volume, duration,
                 fees, decimal-free integer full-term amount
           |
   GenLayer consensus: scope, tier, support, territory, exclusions, audience
           |-- FAIL/UNCERTAIN --> no price effect
           v
   deterministic: better than best verified eligible total?
           |-- NO --> audit record, unchanged cap
           v
     new best offer ID + monotonically reduced cap
           |
   optional downstream InvoiceGate refuses charges exceeding cap
```

### Core invariants

1. **Bilateral consent:** The buyer authors a frozen initial covenant; only its named supplier may activate it.
2. **Source authority is narrow:** HTTPS, public DNS, mandatory ratified *non-root path prefix*, no URL credentials/port/query/fragment/traversal. Shared hosts must pin `/owner/repo/...`, not just `raw.githubusercontent.com`.
3. **Source bytes are independently reproduced:** validators independently fetch, hash and re-parse the public payload. A single LLM result is not proof of origin or availability.
4. **Economic truth is deterministic:** quantity, exact currency, integer price and fees, published/valid windows and term/volume coverage are validated in Python; no LLM arithmetic or price suggestion.
5. **Material validator agreement:** exact agreement across six semantic facet states, payload digest, downloaded bytes digest and calculated total. A merely shape-valid output fails.
6. **Uncertain or stale evidence is not a discount:** any FAIL or UNCERTAIN facet cannot trigger; source fetch failures have bounded retries.
7. **Monotonic cap:** `best_total` may only decrease for active covenants; neither buyer nor provider can manually overwrite it.
8. **History and replay:** every candidate gets a receipt, duplicated URLs are blocked while active/assessed, external offer IDs are unique, and the consumer enforces one-use invoice hashes.
9. **No provider unilateral cancellation of a live covenant:** draft cancellation belongs to the buyer and an active record closes only after its immutable expiry.
10. **No hidden financial side effect:** a trigger changes a price-cap entitlement, not funds. Economic settlement is the downstream integrator's responsibility.

### Normalization formula

For the protected quantity `Q` and exact protected term `M` in whole months:

```text
total_minor = one_time_setup_fee_minor + M * (Q * unit_price_minor + recurring_fee_minor)
```

A later offer is objectively eligible only if it covers `Q` and `M` under the same currency/monthly billing basis, explicitly states all three monetary components, is currently valid, and its publication timestamp lies between activation and the current consensus transaction. This deliberately excludes many real-world discount structures (tiered progressive pricing, deferred credits, tax changes, contingent rebates, usage-based pricing and different currencies). Those should be separate versioned models, not guessed by AI.

All amounts are **minor currency units** (for example, USD cents), not GEN and not floating-point numbers.

### API

| Method | Caller | Purpose |
|---|---|---|
| `propose_covenant(...)` | beneficiary | freeze the full baseline and named supplier |
| `ratify(covenant_id)` | named supplier | activate exact buyer-authored covenant |
| `cancel_draft(covenant_id)` | beneficiary | cancel unratified agreement |
| `submit_offer(covenant_id, url)` | anyone | commit official-source candidate |
| `evaluate_offer(offer_id)` | anyone | independent source re-observation + semantic consensus |
| `close_expired(covenant_id)` | anyone | close after immutable expiry |
| `get_covenant(id)`, `get_offer(id)` | anyone | audit source and decision states |
| `quote(covenant_id)` | anyone | current beneficiary-specific price cap and hash |
| `is_quote_within_cap(id, hash, amount)` | any consumer IC | guarded, version-pinned quote eligibility |

Covenant `DRAFT=1`, `ACTIVE=2`, `CLOSED=3`.
Offer `PENDING=1`, `TRIGGERED=2`, `NOT_BETTER=3`, `NONCOMPARABLE=4`, `UNCERTAIN=5`, `SOURCE_UNAVAILABLE=6`, `INVALID_SOURCE=7`.

## Official offer document

See [`fixtures/OFFER_SCHEMA.json`](fixtures/OFFER_SCHEMA.json). Every field is required and **unknown fields are rejected**, to prevent omitted or reinterpreted financial conditions. Values must come from a JSON document published at the URL approved by both parties. `public_offer` must be the JSON boolean `true`; `published_at`, `valid_from`, and `valid_until` are Unix timestamps. `published_at` must not predate covenant activation. Quantity and term ranges must include the protected reference quantity and term.

The official JSON `scope`, `tier`, `support`, `territory`, `exclusions`, `audience` are treated as **hostile data** by the LLM prompt. The evaluator returns only six PASS/FAIL/UNCERTAIN values and a short rationale. Provider identity and source prefix are fixed in the contract, not decided by an LLM.

## Reproducible development — no globally installed CLI

The PC's globally installed `0.40.0rc2` must never be used for this repo. From the repo root:

```bash
npm install --no-audit --no-fund
node -p "require('./node_modules/genlayer/package.json').version"  # MUST show 0.39.1
python -m venv .venv
# activate venv (Windows PowerShell: .venv\Scripts\Activate.ps1)
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/preflight.py
python scripts/deploy_studionet.py
```

If Python's venv is unavailable, install test dependencies into the currently selected Python environment. `preflight.py` checks the **repo-local** CLI package, the pinned SDK headers, live `eth_chainId==61999` from the exact stable RPC, and SDK semantic lint on both contracts. It aborts deployment on network ambiguity, SDK validation failure, or untrusted local CLI version.

**Do not deploy until preflight passes.** Never run bare global `genlayer`; use the repo-local CLI binary or `npm exec --no -- genlayer` from the repo root. No Docker is required to deploy to hosted Studionet.

Current network reference: [GenLayer Networks](https://docs.genlayer.com/developers/networks), [CLI v0.39.1](https://docs.genlayer.com/api-references/genlayer-cli), [GenVM Linter](https://docs.genlayer.com/api-references/genlayer-linter).

## Verified development and StudioNet proof

The current verification run recorded:

- `57` offline Python tests (`python -m pytest tests -q`);
- `8` official Direct Mode tests (`python -m pytest tests/direct -q`);
- `12/12` security-critical mutation checks killed;
- GenVM lint: `3/3` checks passed for each contract;
- GenVM semantic validation passed for both contracts;
- repository-local CLI `genlayer@0.39.1` and Python `genvm-linter==0.11.0`, `genlayer-test==0.29.2`.

The final contracts are deployed on stable StudioNet (`61999`) and their retrieved source bytes match the committed contract files exactly. A live covenant, provider ratification, comparable lower offer, non-triggering/invalid offer records and InvoiceGate authorization/rejection paths are recorded in [`DEPLOYMENT.md`](DEPLOYMENT.md), [`SUBMISSION.md`](SUBMISSION.md) and [`artifacts/studionet_proof.json`](artifacts/studionet_proof.json).

The live offer documents are repository-controlled fixtures for reproducible protocol evidence; they are not independent proof of third-party pricing or complete market discovery. Source-unavailable evaluation was attempted but remained in `COMMITTING` and is recorded as pending rather than presented as finalized evidence.

See [`docs/LIVE_STUDIONET_RUNBOOK.md`](docs/LIVE_STUDIONET_RUNBOOK.md), [`docs/CONSENSUS.md`](docs/CONSENSUS.md) and [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Intended reuse

A subscription agreement, API marketplace, data supplier, service contract, or DAO purchasing policy can pin a Parity covenant hash and refuse invoices above the current agreed cap, **without trusting one party's textual interpretation**. The source publisher may be the provider's website or repository, subject to the explicit limitations above. Other contracts can consume `is_quote_within_cap()` without inheriting Parity's prompts.
