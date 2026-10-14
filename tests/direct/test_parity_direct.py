"""Pinned-SDK Direct Mode coverage for the Parity contract.

Direct Mode executes the real contract against the official GenLayer test
runtime.  It is not a substitute for multi-validator StudioNet evidence; the
validator-facing checks below use the SDK's captured validator callback.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone

import pytest


PARITY = "contracts/parity.py"
PREFIX = "https://offers.example.com/provider/"
URL = PREFIX + "offer-1.json"


def as_address(raw):
    from genlayer.py.types import Address
    return raw if isinstance(raw, Address) else Address(raw)


def ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def semantic_response(**overrides):
    facets = {name: "PASS" for name in ("scope", "tier", "support", "territory", "exclusions", "audience")}
    facets.update(overrides)
    return json.dumps({"facets": facets, "reason": "all bounded terms remain comparable"})


def offer_document(*, offer_id="offer-1", price=70, **overrides):
    data = {
        "offer_id": offer_id,
        "provider_key": "provider-inc",
        "currency": "USD",
        "scope": "100 units of hosted project backups including full restores",
        "tier": "business",
        "support": "24/7 incident response within four hours",
        "territory": "Nigeria",
        "exclusions": "no additional restrictions beyond stated maintenance windows",
        "audience": "all existing customers of business tier",
        "billing_period": "monthly",
        "unit_price_minor": price,
        "setup_fee_minor": 1000,
        "recurring_fee_minor": 200,
        "min_quantity": 1,
        "max_quantity": 1000,
        "min_term_months": 1,
        "max_term_months": 24,
        "published_at": ts("2026-10-14T12:00:02Z"),
        "valid_from": ts("2026-10-14T12:00:01Z"),
        "valid_until": ts("2026-11-14T12:00:00Z"),
        "public_offer": True,
    }
    data.update(overrides)
    return data


def install_offer(vm, url=URL, **kwargs):
    vm.mock_web(r"offers\.example\.com/provider/offer-[0-9]+\.json", {
        "status": 200,
        "body": json.dumps(offer_document(**kwargs), separators=(",", ":")),
    })
    vm.mock_llm(r"BASELINE_JSON=", semantic_response())


def deploy_ready(vm, deploy, beneficiary, provider):
    vm.warp("2026-10-14T12:00:00Z")
    contract = deploy(PARITY, sdk_version="v0.2.12")
    beneficiary = as_address(beneficiary)
    provider = as_address(provider)
    vm.sender = beneficiary
    cid = contract.propose_covenant(
        provider, "provider-inc", PREFIX, "USD",
        "100 units of hosted project backups including full restores",
        "business", "24/7 incident response within four hours", "Nigeria",
        "no additional restrictions beyond stated maintenance windows",
        "all existing customers of business tier", 100, 12, 100, 1000, 200,
        ts("2026-12-14T12:00:00Z"),
    )
    vm.warp("2026-10-14T12:00:01Z")
    vm.sender = provider
    contract.ratify(cid)
    vm.warp("2026-10-14T12:00:20Z")
    return contract, cid


@pytest.mark.direct
def test_direct_successful_comparable_offer(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    install_offer(direct_vm)
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    assert contract.evaluate_offer(oid) == 2  # TRIGGERED
    assert contract.quote(cid)["effective_total"] == 87400
    assert direct_vm.run_validator() is True


@pytest.mark.direct
def test_direct_unauthorized_ratification_and_immutable_definition(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp("2026-10-14T12:00:00Z")
    contract = direct_deploy(PARITY, sdk_version="v0.2.12")
    beneficiary = as_address(direct_alice)
    provider = as_address(direct_bob)
    unauthorized = as_address(direct_charlie)
    direct_vm.sender = beneficiary
    cid = contract.propose_covenant(
        provider, "provider-inc", PREFIX, "USD", "scope", "business", "support",
        "Nigeria", "none", "all customers", 100, 12, 100, 1000, 200,
        ts("2026-12-14T12:00:00Z"),
    )
    definition = contract.get_covenant(cid)["definition_hash"]
    direct_vm.sender = unauthorized
    with direct_vm.expect_revert("named provider"):
        contract.ratify(cid)
    direct_vm.sender = provider
    contract.ratify(cid)
    assert contract.get_covenant(cid)["definition_hash"] == definition


@pytest.mark.direct
def test_direct_malformed_source_fails_closed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_web(r"offer-1\.json", {"status": 200, "body": b"not json"})
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    assert contract.evaluate_offer(oid) == 7  # INVALID_SOURCE
    assert contract.quote(cid)["effective_total"] == 123400


@pytest.mark.direct
def test_direct_validator_rejects_fabricated_economic_observation(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    install_offer(direct_vm)
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    contract.evaluate_offer(oid)
    candidate = copy.deepcopy(direct_vm._captured_validators[-1][0])
    candidate["price"] = 1
    assert direct_vm.run_validator(leader_result=candidate) is False


@pytest.mark.direct
def test_direct_validator_rejects_source_digest_and_payload_tampering(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    install_offer(direct_vm)
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    contract.evaluate_offer(oid)
    original = direct_vm._captured_validators[-1][0]
    for field, value in (("source_digest", "0" * 64), ("payload_digest", "f" * 64), ("data", {"offer_id": "forged"})):
        candidate = copy.deepcopy(original)
        candidate[field] = value
        assert direct_vm.run_validator(leader_result=candidate) is False


@pytest.mark.direct
def test_direct_validator_rejects_missing_or_failed_facet(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    install_offer(direct_vm)
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    contract.evaluate_offer(oid)
    original = direct_vm._captured_validators[-1][0]
    for replacement in [
        {"scope": "PASS"},
        {name: ("FAIL" if name == "support" else "PASS") for name in ("scope", "tier", "support", "territory", "exclusions", "audience")},
    ]:
        candidate = copy.deepcopy(original)
        candidate["facets"] = replacement
        assert direct_vm.run_validator(leader_result=candidate) is False


@pytest.mark.direct
def test_direct_semantic_uncertainty_never_changes_cap(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_web(r"offer-1\.json", {"status": 200, "body": json.dumps(offer_document()).encode()})
    direct_vm.mock_llm(r"BASELINE_JSON=", semantic_response(support="UNCERTAIN"))
    direct_vm.sender = direct_alice
    oid = contract.submit_offer(cid, URL)
    assert contract.evaluate_offer(oid) == 5  # UNCERTAIN
    assert contract.quote(cid)["effective_total"] == 123400


@pytest.mark.direct
def test_direct_expired_covenant_closes_and_rejects_new_offer(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, cid = deploy_ready(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.warp("2026-12-14T12:00:01Z")
    with direct_vm.expect_revert("covenant not currently active"):
        contract.submit_offer(cid, URL)
    contract.close_expired(cid)
    assert contract.get_covenant(cid)["status"] == 3  # CLOSED
