# Live StudioNet runbook

This runbook uses stable GenLayer StudioNet only. An ACCEPTED receipt is not
final: every write must reach FINALIZED, have a MAJORITY_AGREE result, have the
intended execution result, and be followed by a canonical contract read.

## Fixed environment

~~~text
Network: studionet
Chain ID: 61999 (0xF22F)
RPC: https://studio.genlayer.com/api
CLI: repository-local genlayer@0.39.1
GenVM target: v0.2.12
Explorer: https://explorer-studio.genlayer.com
~~~

From the repository root on Windows:

~~~powershell
npm install --no-audit --no-fund
node -p "require('./node_modules/genlayer/package.json').version"
$env:Path="$PWD\.venv\Scripts;"+$env:Path
$env:PYTHONIOENCODING='utf-8'
python scripts/preflight.py
~~~

The preflight checks the local CLI package, pinned source headers, live
eth_chainId=61999 from the exact stable RPC and SDK lint/schema validation on
both contracts. Never use the global RC CLI, a dev/next network, chain 61997,
Docker or a simulated receipt as live evidence.

## Current deployed addresses

~~~text
Parity:       0xda1BAE7241c7595893e3AE85952AD91588653B33
InvoiceGate:  0x0Fe103558b5990a2254aB711b8bf080AA3D980F0
~~~

The current InvoiceGate is bound to Parity by construction. Confirm with
get_parity_address before using it.

## Reproduce the current economic proof

Use three unlocked accounts, recording public addresses only:

~~~text
beneficiary:  0x951e6B75530774fF82321a5ae54e14F778F0C855
provider:     0xB845a69860ba4CDf19CfDC5AfbAF2e20b6bE86b0
submitter:    0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7
~~~

1. Propose the frozen USD covenant and wait for FINALIZED.
2. Ratify it from the named provider and read get_covenant(1), confirming ACTIVE
   and definition hash
   60aea77b4f55cbe9e3cef26472ecdd568f2e6f48ec2d518d0db5015b1e555f4c.
3. Submit and evaluate offer-007-final-comparable.json. Confirm TRIGGERED,
   all six facets PASS and best_total=87400.
4. Submit and evaluate offer-008-final-more-expensive.json. Confirm NOT_BETTER,
   quoted_total=147400 and unchanged best_total.
5. Submit and evaluate offer-009-final-weaker-support.json. Confirm
   NONCOMPARABLE, support=FAIL and unchanged best_total.
6. Read get_covenant(1) again. The current final readback is ACTIVE,
   best_offer_id=3, best_total=87400, original_total=123400 and offer_count=5.
7. From the beneficiary authorize a fresh invoice at 87400 through InvoiceGate.
   Read was_authorized and get_authorization.
8. Verify finalized contract-error receipts for above-cap amount 87401, invoice
   replay, wrong beneficiary, malformed covenant hash and valid-format stale
   covenant hash. Confirm no rejected invoice was stored.

Every current transaction hash, receipt result, source digest and readback is
in DEPLOYMENT.md and artifacts/studionet_proof.json.

## Evidence table

| Proof | Status | Current transaction or readback |
|---|---|---|
| Parity deployment | FINALIZED / SUCCESS | 0xc6e109402af4a295ac5c2aa247ba7058273030743c66714a88b6476c30da0327 |
| InvoiceGate deployment/binding | FINALIZED / SUCCESS | 0xab52a709b366456aa54e325316e3ef4f47dc0d67d789ed4db56158c17a3ca68d; get_parity_address exact match |
| Ratified covenant | FINALIZED / ACTIVE | proposal 0x6d857a073359e649f2477414b1d8028e46c681752ce42df069363870caa95dcf; ratification 0x709b46869bdb27a4c07137cfe5a9bce575535d84e71673b7172d76a879424101 |
| Comparable offer | FINALIZED / TRIGGERED | evaluation 0x9b46e26961aff612f640a8c89c9c924f69911ef07e45eec45d41122929f9d5c5; 123400 -> 87400 |
| More expensive offer | FINALIZED / NOT_BETTER | evaluation 0x76d4350928f36fddf554266b0f4ed0bc987c26a81f75147f8ee9945629ea8736 |
| Weaker support | FINALIZED / NONCOMPARABLE | evaluation 0xe64b6f48af1cd1568fe659fa7ae1fcf292c36fac4ec7cff40909c3875e173fe6 |
| InvoiceGate at-cap authorization | FINALIZED / SUCCESS | 0x9c9b980e81dcf5eced2eff9c64286253a1714508989bba31d1ca33932664ae4d |
| InvoiceGate negative checks | FINALIZED / CONTRACT_ERROR | listed individually in DEPLOYMENT.md |

The fixture documents are repository-controlled test evidence, not independent
commercial-market evidence. Provider ratification is not domain ownership proof
and Parity is not an escrow or payment processor.
