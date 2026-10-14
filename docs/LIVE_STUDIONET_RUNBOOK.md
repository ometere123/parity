# Live StudioNet runbook and evidence boundary

This runbook is for stable GenLayer StudioNet only. It is both reproducible procedure and a truthful boundary around the evidence already collected. An ACCEPTED receipt is not final: every write must reach `FINALIZED`, have a `MAJORITY_AGREE` result, have the intended execution result, and be followed by a canonical contract read.

## Fixed environment

```text
Network: studionet
Chain ID: 61999 (0xF22F)
RPC: https://studio.genlayer.com/api
CLI: repository-local genlayer@0.39.1
GenVM target: v0.2.12
Explorer: https://explorer-studio.genlayer.com
```

From the repository root on Windows:

```powershell
npm install --no-audit --no-fund
node -p "require('./node_modules/genlayer/package.json').version"
$env:Path="$PWD\.venv\Scripts;"+$env:Path
$env:PYTHONIOENCODING='utf-8'
python scripts/preflight.py
```

The preflight checks the local CLI package, pinned source headers, the exact live RPC chain ID and both contracts' lint/schema validation. Never use the global RC CLI, a dev/next network, chain 61997, Docker or a simulated receipt as live evidence.

## Reproduce the verified lifecycle

The final deployed addresses are:

```text
Parity:       0xA34c2aB4A6b8ca81A44F9012260B16268B88C47A
InvoiceGate:  0x4F4c6702491832986Ec6b95aFbD3389d0E6e0251
```

The observed run used three unlocked CLI accounts, recorded only by public address:

```text
beneficiary:  0x951e6B75530774fF82321a5ae54e14F778F0C855
provider:     0xB845a69860ba4CDf19CfDC5AfbAF2e20b6bE86b0
submitter:    0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7
```

1. Beneficiary proposes the frozen USD covenant: quantity `100`, term `12`, unit `100`, setup `1000`, recurring `200`, original total `123400`.
2. The named provider ratifies it. Read `get_covenant(1)` and verify `ACTIVE`, the provider key, source prefix and definition hash.
3. Submit the repository-controlled lower comparable fixture and evaluate it. Read `get_offer(1)` and `quote(1)`; the observed result was `TRIGGERED`, all six facets `PASS`, and `best_total=87400`.
4. Submit/evaluate the higher-price fixture. The observed result was `NOT_BETTER`; the cap stayed `87400`.
5. Submit/evaluate the wrong-provider fixture. The observed result was `INVALID_SOURCE` with no cap effect.
6. Submit the weaker-support fixture and duplicate the comparable URL only as separate negative checks. The weaker-support evaluation finalized as `NONCOMPARABLE` with `support=FAIL` and no cap effect. The duplicate reached a finalized contract error.
7. Submit the missing-source URL only for bounded retry testing. Its evaluation remained `COMMITTING` and is recorded as pending; do not treat it as a finalized source-unavailable proof.
8. Deploy InvoiceGate bound to the exact Parity address. Authorize an invoice at `87400` from the beneficiary, then verify finalized contract errors for amount `87401`, replay, wrong caller and invalid covenant hash.

All observed transaction hashes, finality labels, readbacks and limitations are in [`../DEPLOYMENT.md`](../DEPLOYMENT.md) and [`../artifacts/studionet_proof.json`](../artifacts/studionet_proof.json).

## Evidence table

| Proof | Status | Evidence |
|---|---|---|
| Parity deployment | FINALIZED / SUCCESS | `0xd07a4b2d5c421136bd7e4442158838f1d0aa4cbf5a69b18572c7acd196dff17b` |
| InvoiceGate deployment and binding | FINALIZED / SUCCESS | `0xc9da13b2f36e83b24e1d3e36f76cf0cd74f98ff022a9498ee39857e2e8184d31`; `get_parity_address()` exact match |
| Ratified covenant | FINALIZED / ACTIVE | proposal `0xaaec82...`; ratification `0xd58423...`; covenant `1` |
| Lower comparable offer | FINALIZED / TRIGGERED | evaluation `0x6c58c30ed0a530f9fb19847810a285f052862008e0f06c4b7525216946c28e13`; `123400 → 87400` |
| More expensive offer | FINALIZED / NOT_BETTER | evaluation `0xb4f593c0ea2e53a57319436edeeb12a13214e7de954d7d311d963194aa68f11d` |
| Wrong provider | FINALIZED / INVALID_SOURCE | evaluation `0x20ec5e65cf2b2cfec93892e0b4e2d979e7cd638ee6b2be7a5eeb07e010315f05` |
| Duplicate URL | FINALIZED / CONTRACT_ERROR | `0x063cccbf89d499345c51a1d96bf3dac28e83d5f0c80978d9bc8b1947df2f2179` |
| Weaker support | FINALIZED / NONCOMPARABLE | evaluation `0xcb064e8a750e272f37b7f523952960cc6c6cc69afc1e0f3bc36a697058e61e0f`; `support=FAIL`; no cap effect |
| Missing source/retry exhaustion | PENDING | `0xce94f1...` remained COMMITTING; no final claim |
| InvoiceGate at-cap authorization | FINALIZED / SUCCESS | `0xd0b92a165dbcbfc11cd1070ddebdeb754679fbc1f157acb80680bc6838c2a1b3`; canonical authorization readback |
| InvoiceGate negative checks | FINALIZED / CONTRACT_ERROR | above cap, replay, wrong caller and wrong hash; see `DEPLOYMENT.md` |

The repository-controlled fixture limitation, provider-source trust boundary and source-unavailability limitation are intentional and remain part of the security model.
