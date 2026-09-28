from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PaymentOrderResult:
    order_id: str
    amount: Decimal
    currency: str
    key_id: str
    provider: str
    receipt: str
    notes: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PaymentVerificationResult:
    is_valid: bool
    order_id: str
    payment_id: str
    signature: str
    error_message: Optional[str] = None

@dataclass
class PaymentDetailsResult:
    payment_id: str
    order_id: Optional[str]
    amount: Decimal
    currency: str
    status: str # captured, authorized, failed, refunded
    method: Optional[str] # upi, card, netbanking, etc.
    email: Optional[str] = None
    contact: Optional[str] = None
    error_code: Optional[str] = None
    error_description: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RefundResult:
    refund_id: str
    payment_id: str
    amount: Decimal
    currency: str
    status: str # processed, pending, failed
    notes: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)

class BasePaymentProvider(ABC):
    """
    Abstract Payment Provider Interface.
    Enforces decoupling between billing business logic and specific payment gateways (Razorpay, Stripe, Cashfree, etc.).
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of the provider."""
        pass

    @property
    @abstractmethod
    def public_key_id(self) -> str:
        """Public key safe to expose to client frontend for checkout initialization."""
        pass

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        receipt: str,
        notes: Optional[Dict[str, Any]] = None
    ) -> PaymentOrderResult:
        """Create a payment order/session on the gateway."""
        pass

    @abstractmethod
    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> PaymentVerificationResult:
        """Cryptographically verify payment success callback signature from checkout."""
        pass

    @abstractmethod
    def verify_webhook_signature(
        self,
        raw_body: bytes,
        signature_header: str
    ) -> bool:
        """Cryptographically verify webhook notification signature against raw request body."""
        pass

    @abstractmethod
    def get_payment_details(
        self,
        provider_payment_id: str
    ) -> PaymentDetailsResult:
        """Fetch status and metadata of a payment directly from provider."""
        pass

    @abstractmethod
    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Decimal,
        notes: Optional[Dict[str, Any]] = None
    ) -> RefundResult:
        """Initiate full or partial refund on the payment."""
        pass
