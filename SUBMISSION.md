# Parity — StudioNet submission record

Parity is a contract-only GenLayer most-favoured-terms primitive. A
beneficiary freezes a covenant, the named provider ratifies it, and public
source offers are independently fetched and semantically compared before
deterministic contract code can lower the beneficiary's price cap.

## Current verified deployment

- Network: GenLayer StudioNet, chain `61999`
- RPC: `https://studio.genlayer.com/api`
- CLI: repository-local `genlayer@0.39.1`
- Parity: [`0xda1BAE7241c7595893e3AE85952AD91588653B33`](https://explorer-studio.genlayer.com/address/0xda1BAE7241c7595893e3AE85952AD91588653B33)
- InvoiceGate: [`0x0Fe103558b5990a2254aB711b8bf080AA3D980F0`](https://explorer-studio.genlayer.com/address/0x0Fe103558b5990a2254aB711b8bf080AA3D980F0)
- InvoiceGate `get_parity_address()` readback: `0xda1BAE7241c7595893e3AE85952AD91588653B33`
- Parity deployment: [`0xc6e109402af4a295ac5c2aa247ba7058273030743c66714a88b6476c30da0327`](https://explorer-studio.genlayer.com/tx/0xc6e109402af4a295ac5c2aa247ba7058273030743c66714a88b6476c30da0327)
- InvoiceGate deployment: [`0xab52a709b366456aa54e325316e3ef4f47dc0d67d789ed4db56158c17a3ca68d`](https://explorer-studio.genlayer.com/tx/0xab52a709b366456aa54e325316e3ef4f47dc0d67d789ed4db56158c17a3ca68d)
- Parity deployment source commit: `c6c84d48077680d3fc6936542c73d08b96c3fd64`
- InvoiceGate deployment source commit: `bbea164a12262a7d1408e62079c100a3d00bcebd`
- Stable Git-content SHA-256: Parity `B41909870003925A23A754FE2DF1A1B92EB557A97CC314A99347D7E54BBBBDDA`; InvoiceGate `6AC2D5726BFF83D17808FC05190C6FFD87DE8B5781F68E679EF822A62FE20232`

Both deployment receipts are FINALIZED / MAJORITY_AGREE / SUCCESS. The stable
CLI source readback matches the deployed source content after accounting for
the CLI's omitted terminal newline and the Windows checkout's line endings.

## Automated verification

The authoritative commands and final counts are recorded after the final run
in the CI-linked verification record. The required checks are:

- offline Python suite;
- official Direct Mode suite;
- security mutation suite;
- GenVM AST lint and semantic validation for both contracts;
- Python compilation and exact chain/CLI preflight.

The repository never treats `ACCEPTED` as final and never treats a simulated
receipt as live evidence.

## Finalized live economic proof

WalletA proposed covenant `1` with original total `123400` minor USD units;
walletB ratified it. On the final Parity deployment, offer `3` was a genuine
lower comparable fixture and finalized `TRIGGERED` with all six facets PASS,
reducing the cap to `87400`. Offer `4` finalized `NOT_BETTER` at `147400`
and offer `5` finalized `NONCOMPARABLE` because support was weaker; neither
raised or reduced the cap. The final canonical readback is ACTIVE,
`best_offer_id=3`, `best_total=87400`, `original_total=123400`,
`offer_count=5`.

The complete hashes and explorer links are in [`DEPLOYMENT.md`](DEPLOYMENT.md)
and [`artifacts/studionet_proof.json`](artifacts/studionet_proof.json).

## Cross-contract proof

The final InvoiceGate authorized one invoice for the beneficiary at exactly
`87400` using the current covenant definition hash. Finalized contract-error
receipts prove that an amount above the cap, a replayed invoice hash, a
non-beneficiary caller, a malformed hash and a valid-format stale hash do not
create authorization records. InvoiceGate is an authorization gate, not an
escrow or payment processor.

## Trust boundaries and limits

Provider-wallet ratification is not cryptographic domain ownership. The
provider-declared publication time is not an independently authenticated
timestamp. The raw offer fixtures are repository-controlled test evidence, not
independent commercial-market evidence. Parity cannot prove catalogue
completeness or undisclosed offers, and it does not charge, refund, custody or
transfer customer funds.

See [`docs/LIVE_STUDIONET_RUNBOOK.md`](docs/LIVE_STUDIONET_RUNBOOK.md),
[`docs/CONSENSUS.md`](docs/CONSENSUS.md) and
[`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) for reproduction and security
boundaries.
