"""Deterministic offline harness; NOT a substitute for GenVM Direct Mode or Studionet."""
import sys
import types
import hashlib
import importlib.util
import os
from datetime import datetime, timezone
from pathlib import Path
import pytest


if sys.platform == "win32":
    # genlayer-test 0.29.2 keeps a duplicated temporary stdin handle open on
    # Windows and reports WinError 32 when unlinking it.  The descriptor has
    # already been installed successfully; keep this compatibility shim
    # limited to that cleanup error so all other runner failures remain fatal.
    from gltest.direct import loader as _direct_loader

    _original_inject_message = _direct_loader._inject_message_to_fd0

    def _windows_safe_inject_message(vm):
        try:
            _original_inject_message(vm)
        except PermissionError as exc:
            if getattr(exc, "winerror", None) != 32:
                raise

    _direct_loader._inject_message_to_fd0 = _windows_safe_inject_message


# genlayer-test 0.29.2 does not refresh message_raw.datetime when a Direct
# Mode VM clock is warped, although the contract reads that raw message in the
# stable v0.2.12 runtime.  Keep the test clock and raw message synchronized.
try:
    from gltest.direct import vm as _direct_vm_module

    _original_warp = _direct_vm_module.VMContext.warp

    def _warp_with_raw_message(self, timestamp):
        _original_warp(self, timestamp)
        gl_module = sys.modules.get("genlayer.gl")
        raw_message = getattr(gl_module, "message_raw", None) if gl_module else None
        if isinstance(raw_message, dict):
            raw_message["datetime"] = timestamp

    _direct_vm_module.VMContext.warp = _warp_with_raw_message
except ImportError:
    # Offline-only environments do not install the official runner.
    pass

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
        if isinstance(value, dict):
            attrs = {}
            if "status" in value:
                attrs["status"] = value["status"]
            if "body" in value:
                attrs["body"] = value["body"]
            return types.SimpleNamespace(**attrs)
        return types.SimpleNamespace(status=200, body=value)

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
    contract_path = Path(os.environ.get("PARITY_CONTRACT_PATH", str(ROOT/"contracts"/"parity.py")))
    spec = importlib.util.spec_from_file_location("parity_contract",contract_path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules,"parity_contract",module)
    spec.loader.exec_module(module)
    contract = module.Parity()
    contract.covenants, contract.offers, contract.url_seen, contract.external_seen = Storage(),Storage(),Storage(),Storage()
    return types.SimpleNamespace(p=module,c=contract,gl=genlayer,web=web)
