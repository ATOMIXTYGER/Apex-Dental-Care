from app.config import settings
from app.payments.provider import BasePaymentProvider
from app.payments.razorpay_provider import RazorpayProvider
from app.payments.mock_provider import MockSandboxProvider

_provider_instance: BasePaymentProvider | None = None

def get_payment_provider(override_name: str | None = None) -> BasePaymentProvider:
    """
    Factory function to retrieve the configured payment provider.
    Enables zero-downtime provider switching via configuration.
    """
    provider_name = (override_name or settings.PAYMENT_PROVIDER).lower()
    if provider_name == "mock":
        return MockSandboxProvider()
    elif provider_name == "razorpay":
        return RazorpayProvider()
    else:
        # Default fallback to Razorpay provider
        return RazorpayProvider()
