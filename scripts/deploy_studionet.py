#!/usr/bin/env python3
"""Deploy Parity and optional InvoiceGate only to verified chain 61999.

Uses the user's ALREADY CONFIGURED/unlocked CLI account. Never reads, prints,
or creates a private key; never falls back to the globally installed CLI.
"""
from __future__ import annotations
import pathlib
import subprocess
import sys
import os

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ["npm","exec","--no","--","genlayer"] if os.name=="nt" else [str(ROOT/"node_modules"/".bin"/"genlayer")]


def run(args: list[str]):
    print("+", " ".join(args), flush=True)
    subprocess.run(args,cwd=ROOT,check=True)


def main():
    run([sys.executable,str(ROOT/"scripts"/"preflight.py")])
    run(CLI + ["network","set","studionet"])
    run(CLI + ["network","info"])
    run(CLI + ["account","show"])
    print("Deploying contract-only Parity to VERIFIED Studionet RPC (chain 61999)",flush=True)
    run(CLI + ["deploy","--contract",str(ROOT/"contracts"/"parity.py"),"--rpc","https://studio.genlayer.com/api"])
    print("NOTE: save the returned address and finalized receipt; then deploy optional invoice_gate.py with --args <parity_address> after Parity finalizes.",flush=True)

if __name__=="__main__":
    main()
