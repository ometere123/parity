#!/usr/bin/env python3
"""Run the bounded security-critical mutation set in isolated temp copies.

This is intentionally a small, reproducible mutation harness rather than a
claim of whole-repository mutation coverage.  Every mutant is a single exact
source substitution and must be killed by the named regression selection.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "parity.py"

MUTANTS = [
    ("allow_equal_price_trigger", "return TRIGGERED if offered < current else NOT_BETTER", "return TRIGGERED if offered <= current else NOT_BETTER", "test_equal_price_does_not_change_cap"),
    ("ignore_failed_facet", "if any(facets[key] == \"FAIL\" for key in FACETS):", "if False and any(facets[key] == \"FAIL\" for key in FACETS):", "test_more_restrictive_dimension_fails"),
    ("treat_uncertain_as_pass", "if any(facets[key] == \"UNCERTAIN\" for key in FACETS):", "if False and any(facets[key] == \"UNCERTAIN\" for key in FACETS):", "test_uncertain_dimension_never_triggers"),
    ("trust_leader_source_digest", "if lead.get(\"source_digest\") != own.get(\"source_digest\"):", "if False and lead.get(\"source_digest\") != own.get(\"source_digest\"):", "test_validator_rejects_forged_material_observation"),
    ("trust_leader_payload_digest", "if lead.get(\"payload_digest\") != own.get(\"payload_digest\") or lead.get(\"price\") != own.get(\"price\"):", "if lead.get(\"price\") != own.get(\"price\"):", "test_validator_rejects_forged_material_observation"),
    ("trust_leader_data", "if lead.get(\"data\") != own.get(\"data\"):", "if False and lead.get(\"data\") != own.get(\"data\"):", "test_validator_rejects_forged_material_observation"),
    ("allow_unauthorized_ratification", "gl.message.sender_address != c.provider", "False", "test_only_provider_may_ratify"),
    ("ignore_prefix_binding", "not s.startswith(prefix)", "False", "test_wrong_authoritative_path_rejected_without_other_url_markers"),
    ("ignore_quantity_coverage", "data[\"min_quantity\"] > baseline[\"quantity\"] or data[\"max_quantity\"] < baseline[\"quantity\"]", "False", "test_volume_not_covered_invalid"),
    ("ignore_publication_window", "data[\"published_at\"] < baseline[\"activated_at\"] or data[\"published_at\"] > ts", "False", "test_publication_before_ratification_invalid"),
    ("disable_offer_replay", "if int(self.url_seen.get(unique) or 0) != 0:", "if False and int(self.url_seen.get(unique) or 0) != 0:", "test_duplicate_url_rejected"),
    ("allow_cap_increase", "if status == TRIGGERED:", "if status in (TRIGGERED, NOT_BETTER):", "test_nonbetter_price_does_not_change_cap"),
]


def main() -> int:
    killed = 0
    failures: list[str] = []
    original = SOURCE.read_text(encoding="utf-8")
    for name, needle, replacement, selection in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="parity-mutant-") as tmp:
            mutated = Path(tmp) / "parity.py"
            count = original.count(needle)
            if count != 1:
                failures.append(f"{name}: expected one source match, got {count}")
                continue
            mutated.write_text(original.replace(needle, replacement, 1), encoding="utf-8")
            env = os.environ.copy()
            env["PARITY_CONTRACT_PATH"] = str(mutated)
            cmd = [sys.executable, "-m", "pytest", "tests/test_parity.py", "-q", "-k", selection]
            result = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
            if result.returncode != 0:
                killed += 1
                print(f"KILLED {name}")
            else:
                failures.append(f"SURVIVED {name}\n{result.stdout}{result.stderr}")
                print(f"SURVIVED {name}")
    total = len(MUTANTS)
    print(f"Mutation result: {killed}/{total} killed")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
