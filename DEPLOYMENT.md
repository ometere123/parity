# Parity — StudioNet deployment and evidence

This file separates the current deployments from the superseded deployment. A
transaction is evidence of a successful state change only when its receipt is
`FINALIZED`, its consensus result is `MAJORITY_AGREE`, its execution result is
`SUCCESS`, and the canonical state readback confirms the expected result.

## Current network and toolchain

| Item | Value |
|---|---|
| Network | GenLayer StudioNet / `studionet` |
| Chain ID | `61999` (`0xF22F`) |
| RPC | `https://studio.genlayer.com/api` |
| Explorer | `https://explorer-studio.genlayer.com` |
| Local CLI | `genlayer@0.39.1` |
| GenVM target | `v0.2.12` |
| GenVM linter | `genvm-linter==0.11.0` |
| Official test package | `genlayer-test==0.29.2` |

The repository preflight queried `eth_chainId` from the exact RPC and returned
`0xF22F`. It also verified the repository-local CLI and both contract lint and
semantic validation commands.

## Final local verification

- Offline suite: 66 passed.
- Official Direct Mode suite: 12 passed.
- Security mutation suite: 12/12 critical mutants killed.
- Parity AST lint: 3/3; InvoiceGate AST lint: 3/3.
- Parity and InvoiceGate GenVM v0.2.12 semantic validation: passed.
- Python compilation: passed.
- Repository-local CLI and live chain guard: 0.39.1 and chain 61999.

## Current deployments

The current Parity deployment contains the HTTP-response-status guard. The
current InvoiceGate deployment contains the GenVM-compatible constructor
address normalization and is bound to the current Parity address.

| Contract | Address | Deployment transaction | Finality/result | Deployment source commit | Git source SHA-256 / bytes |
|---|---|---|---|---|---|
| Parity | [`0xda1BAE7241c7595893e3AE85952AD91588653B33`](https://explorer-studio.genlayer.com/address/0xda1BAE7241c7595893e3AE85952AD91588653B33) | [`0xc6e109402af4a295ac5c2aa247ba7058273030743c66714a88b6476c30da0327`](https://explorer-studio.genlayer.com/tx/0xc6e109402af4a295ac5c2aa247ba7058273030743c66714a88b6476c30da0327) | FINALIZED / MAJORITY_AGREE / SUCCESS | `c6c84d48077680d3fc6936542c73d08b96c3fd64` | `B41909870003925A23A754FE2DF1A1B92EB557A97CC314A99347D7E54BBBBDDA` / 29221 LF bytes |
| ParityInvoiceGate | [`0x0Fe103558b5990a2254aB711b8bf080AA3D980F0`](https://explorer-studio.genlayer.com/address/0x0Fe103558b5990a2254aB711b8bf080AA3D980F0) | [`0xab52a709b366456aa54e325316e3ef4f47dc0d67d789ed4db56158c17a3ca68d`](https://explorer-studio.genlayer.com/tx/0xab52a709b366456aa54e325316e3ef4f47dc0d67d789ed4db56158c17a3ca68d) | FINALIZED / MAJORITY_AGREE / SUCCESS | `bbea164a12262a7d1408e62079c100a3d00bcebd` | `6AC2D5726BFF83D17808FC05190C6FFD87DE8B5781F68E679EF822A62FE20232` / 4463 LF bytes |

The stable CLI `code` readback matched the deployed source content after the
CLI's omitted terminal newline was restored. The RPC retrieval hashes without
that terminal newline are Parity
`2B99DADE7DD2C431DC19B31ABB244441AB6F804F8BC441E7F10AA10327191FFB`
(29220 bytes) and InvoiceGate
`DDC8EF0FF16B3A23C7B2EF629857CC530FFE33AD541522F6A771249539775B53`
(4462 bytes). The Windows worktree hashes are line-ending dependent; the Git
content hashes above are the stable source-parity identifiers.

`get_parity_address()` on the current InvoiceGate returned exactly
`0xda1BAE7241c7595893e3AE85952AD91588653B33`.

## Current live covenant and offer evidence

Public test accounts, recorded by address only:

- beneficiary (`walletA`): `0x951e6B75530774fF82321a5ae54e14F778F0C855`
- named provider (`walletB`): `0xB845a69860ba4CDf19CfDC5AfbAF2e20b6bE86b0`
- permissionless submitter/evaluator (`praest-deployer`): `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`

The current covenant uses USD minor units, quantity `100`, term `12`, unit
price `100`, setup `1000`, recurring `200`, and original total `123400`.
Its source prefix is:

`https://raw.githubusercontent.com/ometere123/parity/main/fixtures/live/`

| Action | Transaction | Finality/result | Canonical readback |
|---|---|---|---|
| `propose_covenant` | [`0x6d857a073359e649f2477414b1d8028e46c681752ce42df069363870caa95dcf`](https://explorer-studio.genlayer.com/tx/0x6d857a073359e649f2477414b1d8028e46c681752ce42df069363870caa95dcf) | FINALIZED / MAJORITY_AGREE / SUCCESS | covenant `1`, DRAFT |
| `ratify(1)` | [`0x709b46869bdb27a4c07137cfe5a9bce575535d84e71673b7172d76a879424101`](https://explorer-studio.genlayer.com/tx/0x709b46869bdb27a4c07137cfe5a9bce575535d84e71673b7172d76a879424101) | FINALIZED / MAJORITY_AGREE / SUCCESS | ACTIVE; definition hash `60aea77b4f55cbe9e3cef26472ecdd568f2e6f48ec2d518d0db5015b1e555f4c` |
| submit comparable offer `parity-final-comparable-007` | [`0xa10e53794220bb7f4de80693c489255ab7841e9209c53eab5685e733f14cc08e`](https://explorer-studio.genlayer.com/tx/0xa10e53794220bb7f4de80693c489255ab7841e9209c53eab5685e733f14cc08e) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `3` |
| evaluate offer `3` | [`0x9b46e26961aff612f640a8c89c9c924f69911ef07e45eec45d41122929f9d5c5`](https://explorer-studio.genlayer.com/tx/0x9b46e26961aff612f640a8c89c9c924f69911ef07e45eec45d41122929f9d5c5) | FINALIZED / MAJORITY_AGREE / SUCCESS | `TRIGGERED`; all six facets `PASS`; `123400 → 87400` |
| submit more-expensive offer `parity-final-more-expensive-008` | [`0x057a061cc2c43024fdfe7dbe102b7b508c8759a11ab3e1666da2e7fabd739a85`](https://explorer-studio.genlayer.com/tx/0x057a061cc2c43024fdfe7dbe102b7b508c8759a11ab3e1666da2e7fabd739a85) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `4` |
| evaluate offer `4` | [`0x76d4350928f36fddf554266b0f4ed0bc987c26a81f75147f8ee9945629ea8736`](https://explorer-studio.genlayer.com/tx/0x76d4350928f36fddf554266b0f4ed0bc987c26a81f75147f8ee9945629ea8736) | FINALIZED / MAJORITY_AGREE / SUCCESS | `NOT_BETTER`; quoted `147400`; cap remains `87400` |
| submit weaker-support offer `parity-final-weaker-support-009` | [`0xea1d6f7c7b0b9583ddeae908d5630b9a0a5601bdb5632b5e01f7d9509cc7332b`](https://explorer-studio.genlayer.com/tx/0xea1d6f7c7b0b9583ddeae908d5630b9a0a5601bdb5632b5e01f7d9509cc7332b) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `5` |
| evaluate offer `5` | [`0xe64b6f48af1cd1568fe659fa7ae1fcf292c36fac4ec7cff40909c3875e173fe6`](https://explorer-studio.genlayer.com/tx/0xe64b6f48af1cd1568fe659fa7ae1fcf292c36fac4ec7cff40909c3875e173fe6) | FINALIZED / MAJORITY_AGREE / SUCCESS | `NONCOMPARABLE`; `support=FAIL`; quoted `75400`; no cap effect |

The final `get_covenant(1)` readback is ACTIVE with `best_offer_id=3`,
`best_total=87400`, `original_total=123400`, and `offer_count=5`.
The final offer `3` source digest is
`0849983919102537eecbc5bb408c8cdb6d30e45626dda1090b80c48653cbca15`.
Offer `4` source digest is
`6e003ba89cc5305d4aa99439dc499d567e1b170900212446c9cf4cef2459710e`.
Offer `5` source digest is
`9a77f2cfe1f6d5ba4a63ae5767d78421aaf1b747990e004984d0ee58acf2ad5d`.

An earlier final-deployment submission of the cached, pre-correction offer-004
fixture evaluated as `UNCERTAIN` and did not change the cap. It is not used as
the comparable proof; the uniquely addressed offer-007 fixture is the current
positive evidence.

## Current InvoiceGate evidence

The authorized invoice hash is
`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`.

| Attempt | Transaction | Finality/result | Readback |
|---|---|---|---|
| authorize at cap `87400` | [`0x9c9b980e81dcf5eced2eff9c64286253a1714508989bba31d1ca33932664ae4d`](https://explorer-studio.genlayer.com/tx/0x9c9b980e81dcf5eced2eff9c64286253a1714508989bba31d1ca33932664ae4d) | FINALIZED / MAJORITY_AGREE / SUCCESS | `was_authorized=true`; beneficiary walletA; amount `87400`; currency USD |
| above cap `87401` | [`0x3317d7e3965a42d4ed32aef9a29ee6ad53969c01fd277f16d2a03c5b83555b45`](https://explorer-studio.genlayer.com/tx/0x3317d7e3965a42d4ed32aef9a29ee6ad53969c01fd277f16d2a03c5b83555b45) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: invoice exceeds active parity quote or hash is stale` |
| replay | [`0x8ae310a08b2d3009f63f4582da7ce432fa7edf895744abe760a3cab7e229d4aa`](https://explorer-studio.genlayer.com/tx/0x8ae310a08b2d3009f63f4582da7ce432fa7edf895744abe760a3cab7e229d4aa) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: invoice already authorized` |
| wrong caller walletB | [`0x94e95d1974fba74275ec4e2f2999fccb560fc3a844629c99c96cc55a141afbea`](https://explorer-studio.genlayer.com/tx/0x94e95d1974fba74275ec4e2f2999fccb560fc3a844629c99c96cc55a141afbea) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: only protected beneficiary can authorize` |
| malformed all-zero hash | [`0xeab13df50a50d21764641f4b1ed97b4256e38d87d74ecc708c575b42452c0992`](https://explorer-studio.genlayer.com/tx/0xeab13df50a50d21764641f4b1ed97b4256e38d87d74ecc708c575b42452c0992) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: covenant hash is invalid` |
| valid-format stale hash | [`0xce108e1c6f18c34ddb13ec526c19124b2f3e6cb5933561b6180bacbe2f51886c`](https://explorer-studio.genlayer.com/tx/0xce108e1c6f18c34ddb13ec5261b6180bacbe2f51886c) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: invoice exceeds active parity quote or hash is stale` |

`get_parity_address()` returned the exact current Parity address, and
`get_authorization()` returned covenant `1`, the current definition hash,
amount `87400`, beneficiary walletA and currency USD. InvoiceGate does not
transfer GEN; it records a beneficiary-authorized invoice only when the
current Parity quote and immutable covenant hash permit it.

## Superseded deployment and historical evidence

The following deployment predates the HTTP-status correction and is not current
evidence:

| Contract | Address | Deployment transaction | Source commit | Source SHA-256 |
|---|---|---|---|---|
| Parity | `0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A` | `0xd07a4b2d5c421136bd7e4442158838f1d0aa4cbf5a69b18572c7acd196dff17b` | `41fc1f17ff910028f6c17cae17120edd57b9169f` | `3ec8ceca6b72d55ac727b00eaca350a980f08f05a5f0990bf0b74846f7553445` |
| InvoiceGate | `0x4F4c6702491832986Ec6b95aFbD3389d0E6e0251` | `0xc9da13b2f36e83b24e1d3e36f76cf0cd74f98ff022a9498ee39857e2e8184d31` | `41fc1f17ff910028f6c17cae17120edd57b9169f` | `f3ad9cc8a9ad68778d30a7f67e932710ffc5f9c326100071eb0d4cadf44fa70a` |

Historical covenant/evaluation and Gate transactions remain available in the
repository history and were not relabeled as current. The older comparable,
higher-price, weaker-support, wrong-provider, missing-source, duplicate and
InvoiceGate transaction hashes are retained in the earlier deployment record
for audit continuity.

## Limitations and failed attempts

- Repository-controlled fixture documents demonstrate the protocol but are not independent commercial-market proof.
- Provider ratification binds a wallet to a URL prefix; it is not cryptographic proof of DNS or GitHub ownership.
- `published_at` is source-declared, not an independently attested publication timestamp.
- Parity does not discover every offer, charge customers, escrow funds or refund invoices.
- A valid HTTP status authenticates transport success, not the truth of provider statements. Missing, malformed, non-2xx and network-failure responses cannot trigger a cap change.
- The first malformed final Gate deployment attempts finalized with contract errors and are excluded from current deployment evidence; only the deployment above is bound to current Parity.
