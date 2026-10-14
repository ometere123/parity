"""Deterministic offline harness; NOT a substitute for GenVM Direct Mode or Studionet."""
import sys
import types
import hashlib
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

class Storage(dict):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls
    def get_or_insert_default(self, key):
        if key not in self:
            self[key] = types.SimpleNamespace()
        return self[key]

class MockEvent:
    def emit(self):
        return None
class MockReturn:
    def __init__(self, calldata):
        self.calldata = calldata
class MockWeb:
    def __init__(self):
        self.pages = {}
    def get(self, url):
        if url not in self.pages:
            raise OSError("unavailable")
        value = self.pages[url]
        if isinstance(value, Exception):
            raise value
        return types.SimpleNamespace(body=value)

@pytest.fixture
def env(monkeypatch):
    gm = types.ModuleType("genlayer")
    gm.__dict__.update({"u256":int,"u32":int,"u8":int,"Address":str,"TreeMap":Storage,"allow_storage":lambda cls:cls,
                        "Keccak256": lambda b:hashlib.sha3_256(b)})
    class UserError(Exception): pass
    class Vm:
        Return = MockReturn
        @staticmethod
        def run_nondet_unsafe(leader, validator):
            data = leader()
            if not validator(MockReturn(data)):
                raise ValueError("leader-validator disagreement")
            return data
    Vm.UserError = UserError
    web = MockWeb()
    genlayer = types.SimpleNamespace(
        Contract=object,
        Event=MockEvent,
        public=types.SimpleNamespace(view=lambda fn:fn,write=lambda fn:fn),
        contract_interface=lambda cls:cls,
        vm=Vm,
        message=types.SimpleNamespace(sender_address="alice",raw=types.SimpleNamespace(datetime="2026-10-14T12:00:00+00:00")),
        nondet=types.SimpleNamespace(web=web,exec_prompt=lambda prompt,response_format="json":{
            "facets":{k:"PASS" for k in ("scope","tier","support","territory","exclusions","audience")},
            "reason":"offer retains all protected qualitative dimensions"
        }),
    )
    gm.gl = genlayer
    monkeypatch.setitem(sys.modules,"genlayer",gm)
    spec = importlib.util.spec_from_file_location("parity_contract",ROOT/"contracts"/"parity.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules,"parity_contract",module)
    spec.loader.exec_module(module)
    contract = module.Parity()
    contract.covenants, contract.offers, contract.url_seen, contract.external_seen = Storage(),Storage(),Storage(),Storage()
    return types.SimpleNamespace(p=module,c=contract,gl=genlayer,web=web)
