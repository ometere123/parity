import importlib.util
from pathlib import Path
import types
import pytest
from conftest import Storage
from test_parity import ready,document,assess

ROOT=Path(__file__).resolve().parents[1]

def gate_fixture(env):
    spec=importlib.util.spec_from_file_location("parity_invoice_gate",ROOT/"contracts"/"invoice_gate.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    contract=mod.ParityInvoiceGate("parity-contract")
    contract.consumed=Storage()
    class ParityBridge:
        def __init__(self, _address): pass
        def view(self): return self
        def get_covenant(self, cid): return env.c.get_covenant(cid)
        def is_quote_within_cap(self, cid,hash_,amount): return env.c.is_quote_within_cap(cid,hash_,amount)
    mod.IParity=ParityBridge
    return mod,contract

def test_authorized_invoice_replay_proof(env):
    cid=ready(env);document(env);assess(env,cid)
    h=env.c.get_covenant(cid)["definition_hash"]
    price=env.c.quote(cid)["effective_total"]
    _,gate=gate_fixture(env)
    action="1"*64
    gate.authorize_invoice(cid,h,action,price)
    assert gate.was_authorized(action)
    assert gate.get_authorization(action)["amount_minor"]==price
    with pytest.raises(Exception,match="already authorized"):
        gate.authorize_invoice(cid,h,action,price)

def test_invoice_over_cap_rejected(env):
    cid=ready(env);document(env);assess(env,cid)
    h=env.c.get_covenant(cid)["definition_hash"]
    _,gate=gate_fixture(env)
    with pytest.raises(Exception,match="exceeds"):
        gate.authorize_invoice(cid,h,"2"*64,env.c.quote(cid)["effective_total"]+1)

def test_wrong_beneficiary_rejected(env):
    cid=ready(env)
    h=env.c.get_covenant(cid)["definition_hash"]
    _,gate=gate_fixture(env)
    env.gl.message.sender_address="mallory"
    with pytest.raises(Exception,match="only protected beneficiary"):
        gate.authorize_invoice(cid,h,"3"*64,500)

def test_invalid_hash_and_expected_hash(env):
    cid=ready(env)
    h=env.c.get_covenant(cid)["definition_hash"]
    _,gate=gate_fixture(env)
    with pytest.raises(Exception,match="invoice_hash"):
        gate.authorize_invoice(cid,h,"bad",10)
    with pytest.raises(Exception,match="hash is invalid"):
        gate.authorize_invoice(cid,"bad","a"*64,10)
    with pytest.raises(Exception,match="exceeds"):
        gate.authorize_invoice(cid,"f"*64,"a"*64,10)

def test_consumer_refuses_draft_or_expired(env):
    from test_parity import propose,set_time
    cid=propose(env)
    h=env.c.get_covenant(cid)["definition_hash"]
    _,gate=gate_fixture(env)
    with pytest.raises(Exception,match="exceeds"):
        gate.authorize_invoice(cid,h,"b"*64,1)
    from test_parity import activate
    set_time(env,"2026-10-14T12:00:01+00:00")
    activate(env,cid)
    set_time(env,"2026-12-14T12:00:00+00:00")
    with pytest.raises(Exception,match="exceeds"):
        gate.authorize_invoice(cid,h,"b"*64,1)

def test_consumer_exposes_bound_parity_address(env):
    mod,gate=gate_fixture(env)
    assert gate.get_parity_address()=="parity-contract"

def test_consumer_rejects_nonpositive_or_boolean_amount(env):
    cid=ready(env)
    h=env.c.get_covenant(cid)["definition_hash"]
    _,gate=gate_fixture(env)
    with pytest.raises(Exception,match="positive integer"):
        gate.authorize_invoice(cid,h,"c"*64,0)
    with pytest.raises(Exception,match="positive integer"):
        gate.authorize_invoice(cid,h,"d"*64,True)
