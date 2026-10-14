# Parity — StudioNet submission record

Parity is a contract-only GenLayer most-favoured-terms primitive. A beneficiary freezes a covenant, the named provider ratifies it, and any participant can submit a provider-source JSON offer. GenLayer validators independently fetch and assess the six non-price dimensions; deterministic contract code owns identity, timestamps, quantity, term, integer arithmetic and monotonic cap enforcement.

## Current verified state

- Network: GenLayer StudioNet, chain `61999`
- RPC: `https://studio.genlayer.com/api`
- CLI: repository-local `genlayer@0.39.1`
- Parity: `0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A`
- InvoiceGate: `0x4F4c6702491832986Ec6b95aFbD3389d0E6e0251`, bound readback `0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A`
- Contract source commit: `41fc1f17ff910028f6c17cae17120edd57b9169f`
- Parity source SHA-256: `3ec8ceca6b72d55ac727b00eaca350a980f08f05a5f0990bf0b74846f7553445`
- InvoiceGate source SHA-256: `f3ad9cc8a9ad68778d30a7f67e932710ffc5f9c326100071eb0d4cadf44fa70a`

Both deployed source responses matched the corresponding local files byte-for-byte. Deployment transaction and live evidence details are in [`DEPLOYMENT.md`](DEPLOYMENT.md) and the machine-readable record [`artifacts/studionet_proof.json`](artifacts/studionet_proof.json).

## Automated verification

The completed local run recorded:

| Check | Result |
|---|---:|
| Offline Python tests | `57 passed` |
| Official Direct Mode | `8 passed` |
| Security mutation suite | `12/12 killed` |
| Parity GenVM lint | `3/3` |
| InvoiceGate GenVM lint | `3/3` |
| Parity semantic validation | passed |
| InvoiceGate semantic validation | passed |
| Python compilation | passed |
| CLI guard / live chain guard | passed (`0.39.1`, `61999`) |

## Finalized live economic proof

Wallet A proposed covenant `1` using USD minor units, quantity `100`, term `12`, unit `100`, setup `1000`, recurring `200`, and total `123400`. Wallet B ratified it. The comparable public fixture reduced the finalized quote to `87400`; `get_covenant(1)` and `quote(1)` read back `best_offer_id=1`, `best_total=87400`, `active=true`.

The same deployment also has finalized readbacks for a higher-price `NOT_BETTER` offer, a cheaper but weaker-support `NONCOMPARABLE` offer (`support=FAIL`, no economic effect), an `INVALID_SOURCE` wrong-provider offer, and the missing-source offer (`INVALID_SOURCE`, no economic effect). These limits are stated explicitly in `DEPLOYMENT.md`.

## Cross-contract proof

The deployed InvoiceGate authorized one invoice at the exact current cap (`87400`) for the covenant beneficiary. Finalized contract-error attempts proved that an amount above the cap, a replayed invoice hash, a non-beneficiary caller and an invalid covenant hash do not create authorization records. InvoiceGate is an authorization gate, not an escrow or payment processor.

## Reproduction and honest scope

Use the commands in [`docs/LIVE_STUDIONET_RUNBOOK.md`](docs/LIVE_STUDIONET_RUNBOOK.md). Do not treat an ACCEPTED receipt as final: wait for `FINALIZED`, check `MAJORITY_AGREE`, check execution success, and then read canonical state. The raw fixture files under [`fixtures/live`](fixtures/live) are repository-controlled test evidence rather than independent commercial-market evidence.

Remaining limitations are not hidden: provider ratification is not domain-ownership proof; the protocol cannot prove catalogue completeness or undisclosed terms; and HTTP/public-source availability can change.
