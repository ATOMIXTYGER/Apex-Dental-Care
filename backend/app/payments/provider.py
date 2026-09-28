from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class PaymentOrderResult:
    order_id: str
    amount: Decimal
    currency: str
    key_id: str
    provider: str
    receipt: str
    notes: dict[str, Any] = field(default_factory=dict)
    raw_response: dict[str, Any] = field(default_factory=dict)

@dataclass
class PaymentVerificationResult:
    is_valid: bool
    order_id: str
    payment_id: str
    signature: str
    error_message: str | None = None

@dataclass
class PaymentDetailsResult:
    payment_id: str
    order_id: str | None
    amount: Decimal
    currency: str
    status: str # captured, authorized, failed, refunded
    method: str | None # upi, card, netbanking, etc.
    email: str | None = None
    contact: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)

@dataclass
class RefundResult:
    refund_id: str
    payment_id: str
    amount: Decimal
    currency: str
    status: str # processed, pending, failed
    notes: dict[str, Any] = field(default_factory=dict)
    raw_response: dict[str, Any] = field(default_factory=dict)

class BasePaymentProvider(ABC):
    """
    Abstract Payment Provider Interface.
    Enforces decoupling between billing business logic and specific payment gateways (Razorpay, Stripe, Cashfree, etc.).
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of the provider."""

    @property
    @abstractmethod
    def public_key_id(self) -> str:
        """Public key safe to expose to client frontend for checkout initialization."""

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        notes: dict[str, Any] | None = None
    ) -> PaymentOrderResult:
        """Create a payment order/session on the gateway."""

    @abstractmethod
    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> PaymentVerificationResult:
        """Cryptographically verify payment success callback signature from checkout."""

    @abstractmethod
    def verify_webhook_signature(
        self,
        raw_body: bytes,
        signature_header: str
    ) -> bool:
        """Cryptographically verify webhook notification signature against raw request body."""

    @abstractmethod
    def get_payment_details(
        self,
        provider_payment_id: str
    ) -> PaymentDetailsResult:
        """Fetch status and metadata of a payment directly from provider."""

    @abstractmethod
    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Decimal,
        notes: dict[str, Any] | None = None
    ) -> RefundResult:
        """Initiate full or partial refund on the payment."""
