import json
from datetime import datetime, timezone
import pytest

URL = "https://raw.githubusercontent.com/provider/official-offers/main/offers/offer-1.json"
PREFIX = "https://raw.githubusercontent.com/provider/official-offers/main/offers/"
T = 1791979200  # placeholder replaced by fixture time where relevant

def seconds(ts):
    return int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp())

def set_time(e,t="2026-10-14T12:00:00+00:00"):
    e.gl.message.raw.datetime=t

def propose(e,**overrides):
    params=dict(provider="provider",provider_key="provider-inc",source_prefix=PREFIX,currency="USD",
        scope="100 units of hosted project backups including full restores",tier="business",
        support="24/7 incident response within four hours",territory="Nigeria",
        exclusions="no additional restrictions beyond stated service maintenance windows",
        audience="all existing customers of business tier",quantity=100,term_months=12,
        unit_price_minor=100,setup_fee_minor=1000,recurring_fee_minor=200,end_at=seconds("2026-12-14T12:00:00+00:00"))
    params.update(overrides)
    return e.c.propose_covenant(**params)

def activate(e,cid):
    e.gl.message.sender_address="provider"
    e.c.ratify(cid)
    e.gl.message.sender_address="alice"

def document(e,offer_id="o-1",price=70,**overrides):
    data=dict(offer_id=offer_id,provider_key="provider-inc",currency="USD",
        scope="100 units of hosted project backups including full restores",tier="business",
        support="24/7 incident response within four hours",territory="Nigeria",
        exclusions="no additional restrictions beyond stated service maintenance windows",
        audience="all existing customers of business tier",billing_period="monthly",
        unit_price_minor=price,setup_fee_minor=1000,recurring_fee_minor=200,
        min_quantity=1,max_quantity=1000,min_term_months=1,max_term_months=24,
        published_at=seconds("2026-10-14T12:00:02+00:00"),
        valid_from=seconds("2026-10-14T12:00:01+00:00"),
        valid_until=seconds("2026-11-14T12:00:00+00:00"),public_offer=True)
    data.update(overrides)
    e.web.pages[URL] = json.dumps(data,sort_keys=True,separators=(",",":")).encode()
    return data

def ready(e):
    cid=propose(e)
    set_time(e,"2026-10-14T12:00:01+00:00")
    activate(e,cid)
    set_time(e,"2026-10-14T12:00:20+00:00")
    return cid

def assess(e,cid,url=URL):
    oid=e.c.submit_offer(cid,url)
    result=e.c.evaluate_offer(oid)
    return oid,result

def test_creation_is_draft_with_quote(env):
    cid=propose(env)
    got=env.c.get_covenant(cid)
    assert got["status"]==env.p.DRAFT
    assert got["original_total"]==1000+12*(100*100+200)
    assert got["best_total"]==got["original_total"]
    assert not env.c.is_quote_within_cap(cid,got["definition_hash"],1000)

def test_only_provider_may_ratify(env):
    cid=propose(env)
    with pytest.raises(Exception,match="named provider"):
        env.c.ratify(cid)
    activate(env,cid)
    with pytest.raises(Exception): env.c.ratify(cid)

def test_beneficiary_cancels_draft(env):
    cid=propose(env)
    env.c.cancel_draft(cid)
    assert env.c.get_covenant(cid)["status"]==env.p.CLOSED
    with pytest.raises(Exception):env.c.ratify(cid)

def test_provider_cannot_cancel_buyer_protection(env):
    cid=ready(env)
    env.gl.message.sender_address="provider"
    with pytest.raises(Exception):env.c.cancel_draft(cid)
    with pytest.raises(Exception):env.c.close_expired(cid)

def test_offer_lower_price_triggers(env):
    cid=ready(env)
    document(env)
    oid,status=assess(env,cid)
    assert status==env.p.TRIGGERED
    expected=1000+12*(70*100+200)
    assert env.c.get_offer(oid)["quoted_total"]==expected
    assert env.c.quote(cid)["effective_total"]==expected
    assert env.c.is_quote_within_cap(cid,env.c.get_covenant(cid)["definition_hash"],expected)
    assert not env.c.is_quote_within_cap(cid,env.c.get_covenant(cid)["definition_hash"],expected+1)
    assert not env.c.is_quote_within_cap(cid,"0"*64,expected)

@pytest.mark.parametrize("status", [404, 500, 302])
def test_non_success_http_status_never_triggers(env, status):
    cid=ready(env)
    document(env)
    raw=env.web.pages[URL]
    env.web.pages[URL]={"status":status,"body":raw}
    oid=env.c.submit_offer(cid,URL)
    assert env.c.evaluate_offer(oid)==env.p.PENDING
    assert env.c.quote(cid)["effective_total"]==env.c.quote(cid)["original_total"]
    assert env.c.evaluate_offer(oid)==env.p.PENDING
    assert env.c.evaluate_offer(oid)==env.p.SOURCE_UNAVAILABLE
    assert env.c.get_offer(oid)["status"]==env.p.SOURCE_UNAVAILABLE
    assert env.c.quote(cid)["effective_total"]==env.c.quote(cid)["original_total"]

def test_missing_http_status_never_triggers(env):
    cid=ready(env)
    document(env)
    raw=env.web.pages[URL]
    env.web.pages[URL]={"body":raw}
    oid,status=assess(env,cid)
    assert status==env.p.PENDING
    assert env.c.get_offer(oid)["attempts"]==1
    assert env.c.quote(cid)["effective_total"]==env.c.quote(cid)["original_total"]

def test_malformed_http_status_never_triggers(env):
    cid=ready(env)
    document(env)
    raw=env.web.pages[URL]
    env.web.pages[URL]={"status":"200","body":raw}
    oid,status=assess(env,cid)
    assert status==env.p.PENDING
    assert env.c.get_offer(oid)["attempts"]==1
    assert env.c.quote(cid)["effective_total"]==env.c.quote(cid)["original_total"]

def test_nonbetter_price_does_not_change_cap(env):
    cid=ready(env)
    document(env,price=120)
    _,status=assess(env,cid)
    assert status==env.p.NOT_BETTER
    assert env.c.quote(cid)["original_total"]==env.c.quote(cid)["effective_total"]

def test_equal_price_does_not_change_cap(env):
    cid=ready(env)
    document(env,price=100)
    _,status=assess(env,cid)
    assert status==env.p.NOT_BETTER
    assert env.c.quote(cid)["effective_total"]==env.c.quote(cid)["original_total"]

def test_no_unbounded_discount_below_zero(env):
    cid=ready(env)
    document(env,price=-3)
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_more_restrictive_dimension_fails(env):
    cid=ready(env)
    document(env)
    env.gl.nondet.exec_prompt=lambda *args,**kw:{"facets":{k:("FAIL" if k=="exclusions" else "PASS") for k in env.p.FACETS},"reason":"more restrictive"}
    _,status=assess(env,cid)
    assert status==env.p.NONCOMPARABLE
    assert env.c.quote(cid)["original_total"]==env.c.quote(cid)["effective_total"]

def test_uncertain_dimension_never_triggers(env):
    cid=ready(env); document(env)
    env.gl.nondet.exec_prompt=lambda *args,**kw:{"facets":{k:("UNCERTAIN" if k=="support" else "PASS") for k in env.p.FACETS},"reason":"ambiguous"}
    _,status=assess(env,cid)
    assert status==env.p.UNCERTAIN

def test_model_shape_failure_defaults_uncertain(env):
    cid=ready(env);document(env)
    env.gl.nondet.exec_prompt=lambda *args,**kw:{"random":"PASS"}
    _,status=assess(env,cid)
    assert status==env.p.UNCERTAIN

def test_ambiguous_fee_type_invalid(env):
    cid=ready(env);document(env,setup_fee_minor=True)
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_currency_mismatch_invalid(env):
    cid=ready(env);document(env,currency="EUR")
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_not_direct_public_offer_invalid(env):
    cid=ready(env);document(env,public_offer=False)
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_outside_term_mismatch_invalid(env):
    cid=ready(env);document(env,min_term_months=24)
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_volume_not_covered_invalid(env):
    cid=ready(env);document(env,max_quantity=50)
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_publication_before_ratification_invalid(env):
    cid=ready(env);document(env,published_at=seconds("2026-10-13T12:00:00+00:00"))
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_future_published_at_invalid(env):
    cid=ready(env);document(env,published_at=seconds("2026-10-20T12:00:00+00:00"))
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_bad_url_scope_fails(env):
    cid=ready(env)
    for url in ["http://provider/offers/1.json","https://raw.githubusercontent.com/attacker/repo/main/offers/x.json",PREFIX+"../evil.json",PREFIX+"fake.json?x=1",PREFIX+"fake.txt"]:
        with pytest.raises(Exception):env.c.submit_offer(cid,url)

def test_wrong_authoritative_path_rejected_without_other_url_markers(env):
    cid=ready(env)
    clean_wrong_path="https://raw.githubusercontent.com/attacker/official-offers/main/offers/offer.json"
    with pytest.raises(Exception):
        env.c.submit_offer(cid,clean_wrong_path)

def test_shared_host_root_prefix_rejected(env):
    with pytest.raises(Exception):propose(env,source_prefix="https://raw.githubusercontent.com/")

def test_lookalike_host_offer_rejected(env):
    cid = ready(env)
    with pytest.raises(Exception):
        env.c.submit_offer(cid, "https://raw.githubusercontent.com.attacker.com/provider/official-offers/main/offers/offer-1.json")

def test_bad_prefix_rejected(env):
    for url in ["https://localhost/offers/","https://user@provider.com/offers/","https://127.0.0.1/offers/","https://provider.com:8443/offers/","https://provider.com/../offers/"]:
        with pytest.raises(Exception):propose(env,source_prefix=url)

def test_duplicate_url_rejected(env):
    cid=ready(env);document(env)
    env.c.submit_offer(cid,URL)
    with pytest.raises(Exception):env.c.submit_offer(cid,URL)

def test_unavailable_bounded_retry(env):
    cid=ready(env)
    oid=env.c.submit_offer(cid,URL)
    for i in range(3):env.c.evaluate_offer(oid)
    assert env.c.get_offer(oid)["status"]==env.p.SOURCE_UNAVAILABLE
    with pytest.raises(Exception):env.c.evaluate_offer(oid)

def test_close_after_expiry(env):
    cid=ready(env)
    set_time(env,"2026-12-14T12:00:00+00:00")
    with pytest.raises(Exception):env.c.submit_offer(cid,URL)
    assert not env.c.quote(cid)["active"]
    env.c.close_expired(cid)
    assert env.c.get_covenant(cid)["status"]==env.p.CLOSED

def test_failed_source_does_not_trigger(env):
    cid=ready(env);env.web.pages[URL]=b"not json"
    oid,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE
    assert env.c.get_offer(oid)["source_digest"]
    assert env.c.quote(cid)["original_total"]==env.c.quote(cid)["effective_total"]

def test_invalid_unknown_json_fields_rejected(env):
    cid=ready(env)
    document(env,unknown="extra")
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE

def test_duplicate_json_keys_are_rejected(env):
    cid=ready(env)
    document(env)
    raw=env.web.pages[URL].decode()
    raw=raw.replace('"offer_id":"o-1"', '"offer_id":"o-1","offer_id":"o-2"', 1)
    env.web.pages[URL]=raw.encode()
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE
    assert "invalid source" in env.c.get_offer(1)["reason"]

def test_proposal_rejects_boolean_numeric_inputs(env):
    with pytest.raises(Exception, match="quantity"):
        propose(env, quantity=True)
    with pytest.raises(Exception, match="end time"):
        propose(env, end_at=True)

def test_second_lower_offer_monotonic(env):
    cid=ready(env);document(env,price=80)
    oid,status=assess(env,cid);assert status==env.p.TRIGGERED
    u2=PREFIX+"offer-2.json"
    data=document(env,offer_id="o-2",price=90)
    env.web.pages[u2]=env.web.pages[URL]
    _,status2=assess(env,cid,u2)
    assert status2==env.p.NOT_BETTER
    assert env.c.quote(cid)["best_offer_id"]==oid
    data["unit_price_minor"]=60
    data["offer_id"]="o-3"
    u3=PREFIX+"offer-3.json"
    env.web.pages[u3]=json.dumps(data).encode()
    oid3,status3=assess(env,cid,u3)
    assert status3==env.p.TRIGGERED
    assert env.c.quote(cid)["best_offer_id"]==oid3

def test_duplicate_provider_external_id_rejected(env):
    cid=ready(env);document(env)
    assess(env,cid)
    env.web.pages[PREFIX+"dup.json"]=env.web.pages[URL]
    oid=env.c.submit_offer(cid,PREFIX+"dup.json")
    with pytest.raises(Exception,match="duplicate provider offer identifier"):
        env.c.evaluate_offer(oid)

def test_validator_rejects_fabricated_leader_facet(env):
    cid=ready(env);document(env)
    original=env.gl.vm.run_nondet_unsafe
    def malicious(leader,validator):
        data=leader();data["facets"]["scope"]="FAIL"
        if not validator(env.gl.vm.Return(data)):
            raise ValueError("rejected fabricated leader")
        return data
    env.gl.vm.run_nondet_unsafe=malicious
    oid=env.c.submit_offer(cid,URL)
    with pytest.raises(ValueError,match="rejected fabricated leader"):
        env.c.evaluate_offer(oid)
    assert env.c.get_offer(oid)["attempts"]==0
    env.gl.vm.run_nondet_unsafe=original

def test_validator_rejects_forged_price(env):
    cid=ready(env);document(env)
    def malicious(leader,validator):
        data=leader();data["price"]+=1
        if not validator(env.gl.vm.Return(data)):
            raise ValueError("rejected forged price")
        return data
    env.gl.vm.run_nondet_unsafe=malicious
    oid=env.c.submit_offer(cid,URL)
    with pytest.raises(ValueError,match="rejected forged price"):
        env.c.evaluate_offer(oid)

@pytest.mark.parametrize("field,value", [
    ("source_digest", "0"*64),
    ("payload_digest", "f"*64),
    ("data", {"offer_id":"forged"}),
])
def test_validator_rejects_forged_material_observation(env,field,value):
    cid=ready(env);document(env)
    original=env.gl.vm.run_nondet_unsafe
    def malicious(leader,validator):
        data=leader();data[field]=value
        if not validator(env.gl.vm.Return(data)):
            raise ValueError("rejected forged material observation")
        return data
    env.gl.vm.run_nondet_unsafe=malicious
    oid=env.c.submit_offer(cid,URL)
    with pytest.raises(ValueError,match="rejected forged material observation"):
        env.c.evaluate_offer(oid)
    assert env.c.get_offer(oid)["attempts"]==0
    env.gl.vm.run_nondet_unsafe=original

def test_offer_limit(env):
    cid=ready(env)
    env.gl.message.sender_address="outsider"
    for i in range(env.p.MAX_OFFERS):
        env.c.submit_offer(cid,PREFIX+str(i)+".json")
    with pytest.raises(Exception,match="offer limit"):env.c.submit_offer(cid,PREFIX+"over.json")

def test_trusted_provider_reserve_survives_public_pool_exhaustion(env):
    cid=ready(env)
    env.gl.message.sender_address="outsider"
    for i in range(env.p.MAX_OFFERS):
        env.c.submit_offer(cid,PREFIX+"public-"+str(i)+".json")
    env.gl.message.sender_address="provider"
    oid=env.c.submit_offer(cid,PREFIX+"provider-reserved.json")
    got=env.c.get_covenant(cid)
    assert oid > env.p.MAX_OFFERS
    assert got["provider_reserved_count"] == 1
    assert got["offer_count"] == env.p.MAX_OFFERS + 1

def test_trusted_reserve_is_bounded(env):
    cid=ready(env)
    env.gl.message.sender_address="outsider"
    for i in range(env.p.MAX_OFFERS):
        env.c.submit_offer(cid,PREFIX+"pool-"+str(i)+".json")
    env.gl.message.sender_address="provider"
    for i in range(env.p.MAX_TRUSTED_RESERVED_OFFERS):
        env.c.submit_offer(cid,PREFIX+"provider-"+str(i)+".json")
    with pytest.raises(Exception, match="offer limit"):
        env.c.submit_offer(cid,PREFIX+"provider-over.json")

def test_buyer_cannot_increase_price_cap(env):
    cid=ready(env)
    document(env)
    assess(env,cid)
    assert env.c.quote(cid)["effective_total"]<env.c.quote(cid)["original_total"]
    assert not env.c.is_quote_within_cap(cid,env.c.get_covenant(cid)["definition_hash"],env.c.quote(cid)["original_total"])

def test_invalid_offer_url_can_be_retried_after_fix(env):
    cid=ready(env)
    env.web.pages[URL]=b"invalid"
    _,status=assess(env,cid)
    assert status==env.p.INVALID_SOURCE
    document(env)
    _,status2=assess(env,cid)
    assert status2==env.p.TRIGGERED
