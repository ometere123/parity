#!/usr/bin/env python3
"""Strict Studionet 61999 + repo-local CLI 0.39.1 guard. No keys touched."""
from __future__ import annotations
import json
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RPC = "https://studio.genlayer.com/api"
EXPECTED_CHAIN = 61999
EXPECTED_CLI = "0.39.1"
SDK_HEADER = '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'


def fail(detail: str):
    raise SystemExit("PREFLIGHT FAILED: " + detail)


def check_local_cli() -> None:
    pkg = ROOT / "node_modules" / "genlayer" / "package.json"
    if not pkg.is_file():
        fail("local node_modules/genlayer missing. Run npm install in this repository (never npm -g).")
    got = json.loads(pkg.read_text(encoding="utf-8")).get("version")
    if got != EXPECTED_CLI:
        fail(f"repository-local genlayer must be {EXPECTED_CLI}, got {got!r}")
    print(f"OK: repository-local CLI {got}")


def check_contracts() -> None:
    for name in ("parity.py", "invoice_gate.py"):
        path = ROOT / "contracts" / name
        source = path.read_text(encoding="utf-8")
        # StudioNet requires the runner version comment before the dependency
        # manifest. Keep the exact pinned dependency, but allow that required
        # two-line header shape for both contracts.
        if SDK_HEADER not in {line.strip() for line in source.splitlines()[:3]}:
            fail(f"{name}: pinned stable py-genlayer dependency header differs")
        compile(source, str(path), "exec")
    cfg = (ROOT / "gltest.config.yaml").read_text()
    if "https://studio.genlayer.com/api" not in cfg or "default: studionet" not in cfg:
        fail("incorrect gltest stable endpoint/preset")
    print("OK: stable SDK header and Studionet-only config")


def check_rpc() -> None:
    payload = json.dumps({"jsonrpc":"2.0","id":23,"method":"eth_chainId","params":[]}).encode("utf-8")
    req = urllib.request.Request(
        RPC,
        data=payload,
        headers={
            "Content-Type": "application/json",
            # StudioNet's gateway rejects urllib's default request identity.
            # This remains a read-only chain guard; it does not alter the RPC.
            "User-Agent": "parity-preflight/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as rsp:
            obj=json.loads(rsp.read(8192).decode("utf-8"))
        raw = obj["result"]
        chain_id=int(raw,16) if isinstance(raw,str) and raw.startswith("0x") else int(raw)
    except Exception as e:
        fail("cannot independently verify chain ID from stable RPC: " + str(e))
    if chain_id != EXPECTED_CHAIN:
        fail(f"RPC returned chain {chain_id}; refusing transactions (expected {EXPECTED_CHAIN})")
    print(f"OK: live RPC chain ID {chain_id} at {RPC}")


def check_lint() -> None:
    tool=shutil.which("genvm-lint")
    if not tool:
        fail("genvm-lint missing. Install requirements-dev.txt into a Python virtual environment")
    lint_env = os.environ.copy()
    # The linter emits a check-mark on success; keep the guard usable on
    # Windows installations whose inherited console still uses cp1252.
    lint_env.setdefault("PYTHONIOENCODING", "utf-8")
    # Validation must use the stable runtime targeted by this repository,
    # even if a newer artifact happens to be cached on the developer machine.
    lint_env["GENVM_VERSION"] = "v0.2.12"
    for name in ("parity.py", "invoice_gate.py"):
        path=ROOT/"contracts"/name
        for command in ("lint", "validate"):
            print("Running", tool, command, path, flush=True)
            result=subprocess.run([tool,command,str(path)],cwd=ROOT,check=False,env=lint_env)
            if result.returncode:
                fail(f"genvm-lint {command} failed for {name} (exit {result.returncode})")


def main():
    offline = "--offline" in sys.argv[1:]
    check_contracts()
    check_local_cli()
    if not offline:
        check_rpc()
        check_lint()
    print("PREFLIGHT PASSED" + (" (offline toolchain + syntax ONLY)" if offline else " (RPC + SDK lint)"))

if __name__ == "__main__":
    main()
