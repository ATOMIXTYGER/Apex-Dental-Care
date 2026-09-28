import hashlib
import hmac
import secrets
from decimal import Decimal
from typing import Any

from app.payments.provider import (
    BasePaymentProvider,
    PaymentDetailsResult,
    PaymentOrderResult,
    PaymentVerificationResult,
    RefundResult,
)


class MockSandboxProvider(BasePaymentProvider):
    """
    Mock sandbox payment provider for isolated testing, contract tests,
    and environments without external internet connectivity.
    """

    def __init__(self, key_id: str = "mock_key_test_123", secret: str = "mock_secret_test_456"):
        self._key_id = key_id
        self._secret = secret

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def public_key_id(self) -> str:
        return self._key_id

    def create_order(
        self,
        amount: Decimal,
        currency: str = "INR",
        receipt: str = "",
        notes: dict[str, Any] | None = None
    ) -> PaymentOrderResult:
        order_id = f"order_mock_{secrets.token_hex(8)}"
        return PaymentOrderResult(
            order_id=order_id,
            amount=amount,
            currency=currency,
            key_id=self._key_id,
            provider=self.provider_name,
            receipt=receipt or f"rcpt_{secrets.token_hex(4)}",
            notes=notes or {},
            raw_response={"id": order_id, "amount": int(amount * 100), "status": "created"}
        )

    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> PaymentVerificationResult:
        if signature.startswith("invalid_"):
            return PaymentVerificationResult(
                is_valid=False,
                order_id=order_id,
                payment_id=payment_id,
                signature=signature,
                error_message="Simulated signature invalid."
            )

        msg = f"{order_id}|{payment_id}".encode()
        expected_sig = hmac.new(self._secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

        # In mock provider, either exact HMAC match or standard mock signature prefix is accepted
        is_valid = (signature == expected_sig) or signature.startswith("sig_valid_")
        return PaymentVerificationResult(
            is_valid=is_valid,
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            error_message=None if is_valid else "Signature does not match expected digest."
        )

    def verify_webhook_signature(
        self,
        raw_body: bytes,
        signature_header: str
    ) -> bool:
        if signature_header.startswith("invalid_"):
            return False
        expected_sig = hmac.new(self._secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        return (signature_header == expected_sig) or signature_header.startswith("wh_valid_")

    def get_payment_details(
        self,
        provider_payment_id: str
    ) -> PaymentDetailsResult:
        return PaymentDetailsResult(
            payment_id=provider_payment_id,
            order_id="order_mock_sample",
            amount=Decimal("100.00"),
            currency="INR",
            status="captured",
            method="upi",
            raw_response={"simulated": True}
        )

    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Decimal,
        notes: dict[str, Any] | None = None
    ) -> RefundResult:
        refund_id = f"rfnd_mock_{secrets.token_hex(8)}"
        return RefundResult(
            refund_id=refund_id,
            payment_id=provider_payment_id,
            amount=amount,
            currency="INR",
            status="processed",
            notes=notes or {},
            raw_response={"id": refund_id, "amount": int(amount * 100), "status": "processed"}
        )
