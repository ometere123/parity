# Live validation checklist — ONLY Studionet 61999

These are **pending actions**, not completed proof. Never fill in a tx hash until the explorer confirms FINALIZED execution and an authoritative contract state readback.

## Prepare repo-local tools

From the extracted/checked-out repo root:

```powershell
npm install --no-audit --no-fund
node -p "require('./node_modules/genlayer/package.json').version"
# must say 0.39.1; global rc2 is irrelevant
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
genvm-lint lint contracts/parity.py
genvm-lint lint contracts/invoice_gate.py
genvm-lint download --version v0.2.12
genvm-lint validate contracts/parity.py
genvm-lint validate contracts/invoice_gate.py
python scripts/preflight.py
python scripts/deploy_studionet.py
```

`preflight.py` refuses any RPC whose `eth_chainId` is not `61999`. It must succeed before any write. All CLI operations must be repo-local (`npm exec --no -- genlayer ...` in PowerShell) and the stable network alias must be `studionet`. Do not run `genlayer up`, start Docker, use the preview, or use global CLI.

## Live contract lifecycle to capture

1. With **Wallet A** (beneficiary), deploy Parity; record address and finalized deployment tx. The owner of repo `ometere123/parity` is not automatically Wallet A.
2. Create a covenant with provider **Wallet B** and the exact public offer prefix `https://raw.githubusercontent.com/ometere123/parity/main/fixtures/live/`. Use currency USD (minor units), numeric quantity 100, 12 months, initial unit 100, setup 1000, recurring 200, expiration future. The `scope`, `tier`, `support`, `territory`, `exclusions`, `audience` strings should be identical between buyer baseline and cheaper offer for the first real network test to maximise consensus convergence.
3. With Wallet B, `ratify(covenant_id)`. Verify `status=ACTIVE`, `activated_at`, and immutable `definition_hash` via `get_covenant`.
4. **After** ratification, publish a truthful fixture under `fixtures/live/offer-001.json` by replacing the zero timestamps in `fixtures/OFFER_SCHEMA.json` with current Unix seconds (published_at >= actual `activated_at`, valid_from <= actual eval time, valid_until future), and set `provider_key` equal to the covenant's key. Wait for the raw GitHub URL to serve correct bytes reliably. This is a **self-controlled test fixture**, not proof of a real third-party commercial offer.
5. Anyone calls `submit_offer` with that exact raw URL, then `evaluate_offer`. Capture finalized receipts, source digest, all six actual facet codes and the new `best_total`. Failure to converge means investigate validator traces instead of claiming success.
6. Post a second authentic provider-issued record with a higher price; show its receipt `NOT_BETTER` and the best total unchanged. Change one material non-price facet with lower price and demonstrate `NONCOMPARABLE` or `UNCERTAIN` rather than an invalid discount.
7. Post an intentionally malformed/foreign-provider record under a distinct filename and show `INVALID_SOURCE` with no cap change; test missing/unavailable URL using a distinct filename and bounded retries.
8. Deploy the optional `contracts/invoice_gate.py` using repo-local CLI `deploy --contract contracts/invoice_gate.py --args <PARITY_ADDRESS> --rpc https://studio.genlayer.com/api`. Wait for finalized deployment. With beneficiary Wallet A authorize invoice amount equal to cap (pass), above cap (reject), reused invoice hash (reject), wrong wallet (reject), old covenant hash (reject). Never issue a real payment from this demonstration consumer.
9. Capture the exact deployed source via `genlayer code` or chain RPC, verify source hash matches committed file, full transaction lifecycle including FINALIZED, explorer URLs, and failing transaction evidence. Push proofs and README deployment section to the same repository. Don't label ACCEPTED or tx-submitted receipts as final.
10. Reviewer note should clearly say the system enforces a **participating consumer's price cap**, not automatic price discrimination monitoring or legal recourse.

## Tooling references

- Stable RPC: https://studio.genlayer.com/api
- Explorer: https://explorer-studio.genlayer.com
- Official chain ID: 61999
- Local CLI package: `genlayer@0.39.1`
- Semantic linter package: `genvm-linter==0.11.0`; SDK release target `v0.2.12` where available
- Testing suite: `genlayer-test==0.29.2` (official Direct Mode can be added separately after the SDK has installed)

## Evidence table (fill only with real proof)

| Proof | Status | Explorer / source |
|---|---|---|
| Parity stable 61999 deployment | PENDING | — |
| Ratified covenant final readback | PENDING | — |
| Lower public offer trigger | PENDING | — |
| Noncomparable cheap offer | PENDING | — |
| Higher offer no reduction reversal | PENDING | — |
| Invalid/unavailable source | PENDING | — |
| Consumer deployed and final pass/fail | PENDING | — |
| Exact source parity | PENDING | — |
