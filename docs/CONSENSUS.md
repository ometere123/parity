# Consensus argument

**Problem:** two different public service offers can have a lower headline price while offering a weaker product, more restrictive exclusions, narrower eligible customers, or longer commitments. Any one party choosing whether an offer is "equivalent" would have an incentive to bias the result.

**Deterministic boundary:** beneficiary/proposer and named provider wallet ratify an immutable baseline, price arithmetic, quantity/term/currency and public source path. The evaluator parses a *strict* UTF-8 JSON public offer. Numeric and objective eligibility fields are checked programmatically before semantic consensus. The only nondeterminism is public source acquisition and bounded interpretation of exactly six qualitative facets.

**Leader:** fetch the exact URL with `gl.nondet.web.get`, hash the exact bytes with Keccak256, parse the strict JSON, reject mismatched identity or ineligible term/volume/timestamps, compute normalized full-term minor-unit price, and ask the model for `PASS/FAIL/UNCERTAIN` on each of `scope`, `tier`, `support`, `territory`, `exclusions`, `audience`.

**Validators:** each independently fetches, hashes, parses, recomputes objective price and re-runs its own semantic judgment. Accepting a leader's output requires exact agreement on *the downloaded source digest, normalized source payload digest, payload data, calculated price and all six material semantic facet states*. The reason string may differ and is not part of the economic decision. Merely correct JSON shape is never enough.

**Economic state:** compare the consensus-backed outcome to the *current best* verified total using pure integer arithmetic. A trigger requires all six facets PASS and a strictly lower amount; otherwise it only creates an audit receipt. The invariant `best_total(new) <= best_total(old) <= original_total` follows by construction.

**Consensus availability:** two validators may see different HTTP snapshots or interpret a subtle term differently. Rejecting equivocation may cause a rotation or an inconclusive result rather than a trigger. This is a deliberate fail-closed tradeoff. The final StudioNet run reached finalized agreement for the comparable trigger, the higher-price no-op, and the invalid-source path; the weaker-support and missing-source attempts are documented separately where their finality/readback boundary was not complete.

**Prompt injection:** all supplier statements are enclosed as JSON data in a narrow prompt with instruction-in-data warnings. Semantic validation is limited to the fixed facet set; remote text cannot instruct a GEN transfer or alter state directly. The Direct Mode adversarial suite covers malformed, dishonest and conflicting leader/validator observations; live source-controlled fixtures demonstrate the economic boundary but are not independent provider-market evidence.
