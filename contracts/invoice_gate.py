# v0.2.12
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Optional minimal contract-only consumer for proving enforceable Parity quotations.

Not an escrow/payment processor. An actual settlement contract should consume
this eligibility check and perform its own atomic settlement and replay checks.
"""
from genlayer import *
from dataclasses import dataclass

@gl.contract_interface
class IParity:
    class View:
        def get_covenant(self, covenant_id: u256) -> dict: ...
        def is_quote_within_cap(self, covenant_id: u256, expected_hash: str, total_minor: u256) -> bool: ...

@allow_storage
@dataclass
class AuthorizedInvoice:
    beneficiary: Address
    covenant_id: u256
    covenant_hash: str
    amount_minor: u256
    currency: str

class InvoiceAuthorized(gl.Event):
    def __init__(self, invoice_hash: str, covenant_id: u256, /, **blob): ...

class ParityInvoiceGate(gl.Contract):
    parity_address: Address
    consumed: TreeMap[str, AuthorizedInvoice]
    authorized_count: u256

    def __init__(self, parity_address: Address):
        # The CLI/runtime may deliver constructor addresses as strings even
        # when the annotated argument is Address.  Normalize before writing
        # the typed storage slot; storing the raw string is a finalized
        # deployment-time contract error in GenVM v0.2.12.
        if not isinstance(parity_address, Address):
            raw_address = str(parity_address)
            # CLI address# arguments arrive in the VM without the optional
            # 0x marker, while Address accepts hex only with that marker.
            if (len(raw_address) == 40 and
                all(ch in "0123456789abcdefABCDEF" for ch in raw_address)):
                raw_address = "0x" + raw_address
            parity_address = Address(raw_address)
        self.parity_address=parity_address
        self.authorized_count=u256(0)

    @gl.public.write
    def authorize_invoice(self, covenant_id: u256, expected_hash: str, invoice_hash: str, amount_minor: u256) -> None:
        key = str(invoice_hash).lower().strip()
        if len(key)!=64 or any(c not in "0123456789abcdef" for c in key):
            raise gl.vm.UserError("GATE: invoice_hash must be 64 lowercase hex chars")
        if (not isinstance(expected_hash, str) or len(expected_hash)!=64 or
            any(c not in "0123456789abcdef" for c in expected_hash)):
            raise gl.vm.UserError("GATE: covenant hash is invalid")
        if (isinstance(amount_minor, bool) or not isinstance(amount_minor, int) or
            int(amount_minor) <= 0):
            raise gl.vm.UserError("GATE: invoice amount must be a positive integer")
        if key in self.consumed:
            raise gl.vm.UserError("GATE: invoice already authorized")
        parity = IParity(self.parity_address)
        covenant = parity.view().get_covenant(covenant_id)
        if str(covenant["beneficiary"]) != str(gl.message.sender_address):
            raise gl.vm.UserError("GATE: only protected beneficiary can authorize")
        if not parity.view().is_quote_within_cap(covenant_id, expected_hash, amount_minor):
            raise gl.vm.UserError("GATE: invoice exceeds active parity quote or hash is stale")
        self.consumed[key] = AuthorizedInvoice(
            beneficiary=gl.message.sender_address,
            covenant_id=covenant_id,
            covenant_hash=expected_hash,
            amount_minor=amount_minor,
            currency=str(covenant["currency"]),
        )
        self.authorized_count=u256(int(self.authorized_count)+1)
        InvoiceAuthorized(key, covenant_id, amount_minor=amount_minor).emit()

    @gl.public.view
    def was_authorized(self, invoice_hash: str) -> bool:
        return str(invoice_hash).strip().lower() in self.consumed

    @gl.public.view
    def get_authorization(self, invoice_hash: str) -> dict:
        record = self.consumed.get(str(invoice_hash).strip().lower())
        if record is None:
            raise gl.vm.UserError("GATE: unknown invoice")
        return {"beneficiary": str(record.beneficiary), "covenant_id": int(record.covenant_id),
                "covenant_hash": str(record.covenant_hash), "amount_minor": int(record.amount_minor),
                "currency": str(record.currency)}

    @gl.public.view
    def get_parity_address(self) -> str:
        """Return the immutable Parity address used by this gate."""
        return str(self.parity_address)
