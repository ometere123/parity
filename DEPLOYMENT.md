# Parity — verified StudioNet deployment

This record contains only observed StudioNet 61999 results. `FINALIZED` below means the GenLayer transaction reached FINALIZED with a MAJORITY_AGREE result; contract-error transactions are recorded as rejected execution, not as successful state changes.

## Network and toolchain

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

The chain guard queried `eth_chainId` from the exact RPC and returned `0xF22F`. The local CLI package and executable both reported `0.39.1`.

## Deployed contracts

The contract source commit is `41fc1f17ff910028f6c17cae17120edd57b9169f`. Later commits changed fixtures and documentation only; the deployed contract files remain byte-identical to that source commit.

| Contract | Address | Deployment transaction | Finality/result | Source bytes | SHA-256 |
|---|---|---|---|---:|---|
| Parity | [`0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A`](https://explorer-studio.genlayer.com/address/0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A) | [`0xd07a4b2d5c421136bd7e4442158838f1d0aa4cbf5a69b18572c7acd196dff17b`](https://explorer-studio.genlayer.com/tx/0xd07a4b2d5c421136bd7e4442158838f1d0aa4cbf5a69b18572c7acd196dff17b) | FINALIZED / MAJORITY_AGREE / SUCCESS | 29349 | `3ec8ceca6b72d55ac727b00eaca350a980f08f05a5f0990bf0b74846f7553445` |
| ParityInvoiceGate | [`0x4F4c6702491832986Ec6b95aFbD3389d0E6e0251`](https://explorer-studio.genlayer.com/address/0x4F4c6702491832986Ec6b95aFbD3389d0E6e0251) | [`0xc9da13b2f36e83b24e1d3e36f76cf0cd74f98ff022a9498ee39857e2e8184d31`](https://explorer-studio.genlayer.com/tx/0xc9da13b2f36e83b24e1d3e36f76cf0cd74f98ff022a9498ee39857e2e8184d31) | FINALIZED / MAJORITY_AGREE / SUCCESS | 3796 | `f3ad9cc8a9ad68778d30a7f67e932710ffc5f9c326100071eb0d4cadf44fa70a` |

Retrieved contract source from the RPC matched the local files byte-for-byte. `get_parity_address()` on the deployed InvoiceGate returned the exact Parity address above.

## Covenant and offer lifecycle

The live fixture prefix was ratified after covenant creation:

`https://raw.githubusercontent.com/ometere123/parity/main/fixtures/live/`

Wallets are public test accounts only:

- beneficiary: `0x951e6B75530774fF82321a5ae54e14F778F0C855` (`walletA`)
- named provider: `0xB845a69860ba4CDf19CfDC5AfbAF2e20b6bE86b0` (`walletB`)
- permissionless submitter/evaluator: `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7` (`praest-deployer`)

| Action | Transaction | Finality/result | Readback |
|---|---|---|---|
| `propose_covenant` | [`0xaaec82ca61b0c9d178d07101aef50dff7c1eeaa2d7ed148724132ac9f140aa61`](https://explorer-studio.genlayer.com/tx/0xaaec82ca61b0c9d178d07101aef50dff7c1eeaa2d7ed148724132ac9f140aa61) | FINALIZED / MAJORITY_AGREE / SUCCESS | covenant `1`, DRAFT |
| `ratify(1)` | [`0xd58423bc90290dee265456bf554d072cf6114ca8815fe89e57dd1a278d1d12f2`](https://explorer-studio.genlayer.com/tx/0xd58423bc90290dee265456bf554d072cf6114ca8815fe89e57dd1a278d1d12f2) | FINALIZED / MAJORITY_AGREE / SUCCESS | ACTIVE; definition hash `d2f8190db5fba97e3f313c643fc7ec13c7cfe6dc82c1230dd2433151901028f3` |
| submit comparable offer 1 | [`0x5b285b2d92f716512414319a99d90de21c1ba9d6fff9db2d65416fd81ad87334`](https://explorer-studio.genlayer.com/tx/0x5b285b2d92f716512414319a99d90de21c1ba9d6fff9db2d65416fd81ad87334) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `1` |
| evaluate offer 1 | [`0x6c58c30ed0a530f9fb19847810a285f052862008e0f06c4b7525216946c28e13`](https://explorer-studio.genlayer.com/tx/0x6c58c30ed0a530f9fb19847810a285f052862008e0f06c4b7525216946c28e13) | FINALIZED / MAJORITY_AGREE / SUCCESS | TRIGGERED; all six facets PASS; total `123400 → 87400` |
| submit more-expensive offer 2 | [`0x897d11724157f4f5dece8acf1817fe9b7b2d01a541b6ca8b44a62a22ac229894`](https://explorer-studio.genlayer.com/tx/0x897d11724157f4f5dece8acf1817fe9b7b2d01a541b6ca8b44a62a22ac229894) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `2` |
| evaluate offer 2 | [`0xb4f593c0ea2e53a57319436edeeb12a13214e7de954d7d311d963194aa68f11d`](https://explorer-studio.genlayer.com/tx/0xb4f593c0ea2e53a57319436edeeb12a13214e7de954d7d311d963194aa68f11d) | FINALIZED / MAJORITY_AGREE / SUCCESS | NOT_BETTER; quoted `147400`; best remains `87400` |
| submit weaker-support offer 3 | [`0xf652f82391e9d11773b491ae81488fd2a8419e473918ce4f1ed374a71207e23c`](https://explorer-studio.genlayer.com/tx/0xf652f82391e9d11773b491ae81488fd2a8419e473918ce4f1ed374a71207e23c) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `3` |
| evaluate offer 3 | [`0xcb064e8a750e272f37b7f523952960cc6c6cc69afc1e0f3bc36a697058e61e0f`](https://explorer-studio.genlayer.com/tx/0xcb064e8a750e272f37b7f523952960cc6c6cc69afc1e0f3bc36a697058e61e0f) | **Not counted as final evidence** | A non-final state read observed NONCOMPARABLE with `support=FAIL`, but the RPC later stopped returning this transaction by hash; no FINALIZED claim is made. |
| submit wrong-provider offer 4 | [`0x2d3291f8350e2cbeceadd1ba2265a43d8865b4281f7d357fe6a896933d68bde8`](https://explorer-studio.genlayer.com/tx/0x2d3291f8350e2cbeceadd1ba2265a43d8865b4281f7d357fe6a896933d68bde8) | FINALIZED / MAJORITY_AGREE / SUCCESS | offer `4` |
| evaluate offer 4 | [`0x20ec5e65cf2b2cfec93892e0b4e2d979e7cd638ee6b2be7a5eeb07e010315f05`](https://explorer-studio.genlayer.com/tx/0x20ec5e65cf2b2cfec93892e0b4e2d979e7cd638ee6b2be7a5eeb07e010315f05) | FINALIZED / MAJORITY_AGREE / SUCCESS | INVALID_SOURCE; no economic effect |
| duplicate offer 1 URL | [`0x063cccbf89d499345c51a1d96bf3dac28e83d5f0c80978d9bc8b1947df2f2179`](https://explorer-studio.genlayer.com/tx/0x063cccbf89d499345c51a1d96bf3dac28e83d5f0c80978d9bc8b1947df2f2179) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `PARITY: duplicate offer URL`; no new offer |

Final `get_covenant(1)` readback was ACTIVE, `best_offer_id=1`, `original_total=123400`, `best_total=87400`, and `offer_count=5`. `quote(1)` returned `active=true`, `effective_total=87400` and the same definition hash.

The source-unavailable fixture submission finalized as offer `5` and remained PENDING. Its evaluation transaction [`0xce94f1cea08c67c8c931eb31e2b37f1cb272080fbfff3bfc3a3f2e26d1cdd08f`](https://explorer-studio.genlayer.com/tx/0xce94f1cea08c67c8c931eb31e2b37f1cb272080fbfff3bfc3a3f2e26d1cdd08f) remained `COMMITTING`; the CLI wait timed out and it is not presented as finalized source-unavailability evidence.

## InvoiceGate cross-contract evidence

The successful at-cap authorization used invoice hash `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` and amount `87400`. `get_authorization` returned beneficiary walletA, covenant `1`, the live definition hash, amount `87400`, and currency USD.

| Attempt | Transaction | Finality/result | Readback |
|---|---|---|---|
| authorize at cap | [`0xd0b92a165dbcbfc11cd1070ddebdeb754679fbc1f157acb80680bc6838c2a1b3`](https://explorer-studio.genlayer.com/tx/0xd0b92a165dbcbfc11cd1070ddeb754679fbc1f157acb80680bc6838c2a1b3) | FINALIZED / MAJORITY_AGREE / SUCCESS | authorized; amount `87400` |
| authorize above cap `87401` | [`0xcaf39227a3e6310a3b712412f8835d6357d7aae89bd2679845fa6dd378ef024d`](https://explorer-studio.genlayer.com/tx/0xcaf39227a3e6310a3b712412f8835d6357d7aae89bd2679845fa6dd378ef024d) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: invoice exceeds active parity quote or hash is stale`; `was_authorized` false |
| replay same invoice hash | [`0x82fb1fe9d9232cadec792b11169d393a81c6e32573345a534caaffa1c0d33e6f`](https://explorer-studio.genlayer.com/tx/0x82fb1fe9d9232cadec792b11169d393a81c6e32573345a534caaffa1c0d33e6f) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: invoice already authorized` |
| wrong caller walletB | [`0xec464a7c3b9bc40878d31181e729915e385049f1288f37a55a023469b89592b6`](https://explorer-studio.genlayer.com/tx/0xec464a7c3b9bc40878d31181e729915e385049f1288f37a55a023469b89592b6) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: only protected beneficiary can authorize`; `was_authorized` false |
| wrong definition hash | [`0x3d509537989a17e20224f779f812145251effa50dea908475932d169d6abedf3`](https://explorer-studio.genlayer.com/tx/0x3d509537989a17e20224f779f812145251effa50dea908475932d169d6abedf3) | FINALIZED / MAJORITY_AGREE / CONTRACT_ERROR | `GATE: covenant hash is invalid`; `was_authorized` false |

InvoiceGate does not transfer GEN. It records a beneficiary-authorized invoice only when the current Parity quote and immutable covenant hash permit it.

## Limitations and non-final attempts

- The fixture documents are controlled by this repository. They demonstrate the protocol, not independent provider-market adoption.
- Provider ratification binds a wallet to a URL prefix; it is not cryptographic proof of domain ownership.
- Parity does not discover every offer, charge customers, escrow funds or refund invoices.
- The malformed first deployment attempt (`0xfcdc6d5a0e955c0dbf4ecd612ae78b3525dadabeda8e367ae0a036540c115d23`) finalized with `invalid_contract` and is excluded from current deployment evidence.
- The source-unavailable evaluation above remains pending/non-final. No fabricated finalized result is recorded.
