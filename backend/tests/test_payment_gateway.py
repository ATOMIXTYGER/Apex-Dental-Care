import hmac
import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal
import pytest

from app.config import settings

def _generate_signature(order_id: str, payment_id: str, secret: str = settings.PAYMENT_KEY_SECRET) -> str:
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def _generate_webhook_signature(raw_body: bytes, secret: str = settings.PAYMENT_WEBHOOK_SECRET) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

def create_sample_invoice(client, token, total_amount=1000.00):
    due = (date.today() + timedelta(days=14)).isoformat()
    res = client.post("/api/v1/billing/invoices", json={
        "patient_id": 1,
        "due_date": due,
        "discount": 0.00,
        "tax": 0.00,
        "items": [{"description": "Dental Root Canal", "unit_price": total_amount, "quantity": 1}]
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    return res.json()["id"]

# =========================================================================
# Order Creation Tests
# =========================================================================

def test_create_payment_order_default_balance(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 2500.00)

    res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert "order_id" in data
    assert data["order_id"].startswith("order_")
    assert float(data["amount"]) == 2500.00
    assert data["currency"] == "INR"
    assert data["key_id"] == settings.PAYMENT_KEY_ID
    assert data["invoice_id"] == inv_id
    assert "patient_name" in data

def test_create_payment_order_custom_partial_amount(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 3000.00)

    res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "amount": 1000.00
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert float(data["amount"]) == 1000.00

def test_create_payment_order_overpayment_rejected(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1000.00)

    res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "amount": 1500.00
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "OVERPAYMENT_NOT_ALLOWED"

def test_create_payment_order_zero_amount_rejected(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1000.00)

    res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "amount": 0.00
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code in (400, 422)

def test_create_payment_order_idempotency(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1200.00)
    key = "idem-order-test-uuid-999"

    res1 = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "idempotency_key": key
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res1.status_code == 201
    order1 = res1.json()

    # Second identical request
    res2 = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "idempotency_key": key
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res2.status_code == 201
    order2 = res2.json()

    assert order1["order_id"] == order2["order_id"]
    assert order1["internal_payment_id"] == order2["internal_payment_id"]

# =========================================================================
# Payment Verification Tests
# =========================================================================

def test_payment_verification_success_and_balance_update(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 4000.00)

    # 1. Create order
    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={
        "amount": 4000.00
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["order_id"]
    internal_pid = order_data["internal_payment_id"]

    # 2. Simulate valid signature from Razorpay checkout
    provider_pay_id = "pay_test_987654321"
    valid_sig = _generate_signature(order_id, provider_pay_id)

    verify_res = client.post("/api/v1/billing/payments/verify", json={
        "internal_payment_id": internal_pid,
        "provider_order_id": order_id,
        "provider_payment_id": provider_pay_id,
        "provider_signature": valid_sig,
        "invoice_id": inv_id
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["success"] is True
    assert float(v_data["balance_remaining"]) == 0.00
    assert "receipt_url" in v_data

    # 3. Check invoice status becomes paid
    inv_check = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert inv_check.status_code == 200
    inv = inv_check.json()
    assert inv["status"] == "paid"
    assert float(inv["paid_amount"]) == 4000.00
    assert float(inv["balance"]) == 0.00

def test_payment_verification_tampered_signature_rejected(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1500.00)

    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert order_res.status_code == 201
    order_data = order_res.json()

    # Pass malicious/tampered signature
    verify_res = client.post("/api/v1/billing/payments/verify", json={
        "internal_payment_id": order_data["internal_payment_id"],
        "provider_order_id": order_data["order_id"],
        "provider_payment_id": "pay_fake_11111",
        "provider_signature": "tampered_fake_signature_hex_value",
        "invoice_id": inv_id
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert verify_res.status_code == 400
    assert verify_res.json()["error"]["code"] == "INVALID_SIGNATURE"

    # Invoice balance must remain untouched
    inv_check = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert float(inv_check.json()["balance"]) == 1500.00

def test_payment_verification_mismatched_invoice_idor_rejected(client, receptionist_token):
    inv_id1 = create_sample_invoice(client, receptionist_token, 1000.00)
    inv_id2 = create_sample_invoice(client, receptionist_token, 2000.00)

    order_res = client.post(f"/api/v1/billing/invoices/{inv_id1}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    order_data = order_res.json()

    valid_sig = _generate_signature(order_data["order_id"], "pay_sample_123")

    # Attempt to verify payment belonging to inv_id1 against inv_id2
    verify_res = client.post("/api/v1/billing/payments/verify", json={
        "internal_payment_id": order_data["internal_payment_id"],
        "provider_order_id": order_data["order_id"],
        "provider_payment_id": "pay_sample_123",
        "provider_signature": valid_sig,
        "invoice_id": inv_id2 # Mismatch!
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert verify_res.status_code == 400
    assert verify_res.json()["error"]["code"] == "INVOICE_MISMATCH"

def test_payment_verification_idempotency_prevents_double_credit(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1000.00)

    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    order_data = order_res.json()
    valid_sig = _generate_signature(order_data["order_id"], "pay_idem_123")

    payload = {
        "internal_payment_id": order_data["internal_payment_id"],
        "provider_order_id": order_data["order_id"],
        "provider_payment_id": "pay_idem_123",
        "provider_signature": valid_sig,
        "invoice_id": inv_id
    }

    # First verification
    v1 = client.post("/api/v1/billing/payments/verify", json=payload, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert v1.status_code == 200

    # Repeated verification must succeed idempotently without decrementing balance twice!
    v2 = client.post("/api/v1/billing/payments/verify", json=payload, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert v2.status_code == 200

    inv_check = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert float(inv_check.json()["paid_amount"]) == 1000.00 # Not 2000!

# =========================================================================
# Webhook Tests
# =========================================================================

def test_webhook_payment_captured_updates_invoice(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 5000.00)

    # Create order
    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", json={"amount": 5000.00}, headers={"Authorization": f"Bearer {receptionist_token}"})
    order_id = order_res.json()["order_id"]

    # Construct webhook event
    event_payload = {
        "id": "evt_test_captured_001",
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_webhook_cap_123",
                    "order_id": order_id,
                    "amount": 500000,
                    "currency": "INR",
                    "status": "captured"
                }
            }
        }
    }
    raw_body = json.dumps(event_payload).encode("utf-8")
    sig = _generate_webhook_signature(raw_body)

    wh_res = client.post(
        "/api/v1/billing/webhooks/razorpay",
        content=raw_body,
        headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"}
    )
    assert wh_res.status_code == 200
    assert wh_res.json()["status"] == "success"

    # Confirm invoice became paid
    inv = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"}).json()
    assert inv["status"] == "paid"
    assert float(inv["balance"]) == 0.00

def test_webhook_invalid_signature_rejected(client):
    body = b'{"event": "payment.captured"}'
    res = client.post(
        "/api/v1/billing/webhooks/razorpay",
        content=body,
        headers={"X-Razorpay-Signature": "invalid_sig_123", "Content-Type": "application/json"}
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"

def test_webhook_idempotency_prevents_duplicate_processing(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1000.00)
    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    order_id = order_res.json()["order_id"]

    event_payload = {
        "id": "evt_unique_idem_999",
        "event": "payment.captured",
        "payload": {"payment": {"entity": {"id": "pay_wh_idem", "order_id": order_id, "amount": 100000}}}
    }
    raw = json.dumps(event_payload).encode("utf-8")
    sig = _generate_webhook_signature(raw)

    res1 = client.post("/api/v1/billing/webhooks/razorpay", content=raw, headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"})
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"

    # Second arrival of same webhook
    res2 = client.post("/api/v1/billing/webhooks/razorpay", content=raw, headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"})
    assert res2.status_code == 200
    assert res2.json()["status"] == "already_processed"

# =========================================================================
# Receipt PDF & Reconcile & Refund Tests
# =========================================================================

def test_payment_receipt_pdf_download(client, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 800.00)
    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    odata = order_res.json()

    # Complete payment
    sig = _generate_signature(odata["order_id"], "pay_receipt_test")
    client.post("/api/v1/billing/payments/verify", json={
        "internal_payment_id": odata["internal_payment_id"],
        "provider_order_id": odata["order_id"],
        "provider_payment_id": "pay_receipt_test",
        "provider_signature": sig,
        "invoice_id": inv_id
    }, headers={"Authorization": f"Bearer {receptionist_token}"})

    # Download receipt PDF
    rcpt_res = client.get(f"/api/v1/billing/payments/{odata['internal_payment_id']}/receipt", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert rcpt_res.status_code == 200
    assert rcpt_res.headers["content-type"] == "application/pdf"
    assert rcpt_res.content.startswith(b"%PDF")

def test_admin_refund_workflow_and_rbac(client, admin_token, receptionist_token):
    inv_id = create_sample_invoice(client, receptionist_token, 1000.00)
    order_res = client.post(f"/api/v1/billing/invoices/{inv_id}/payments/order", headers={"Authorization": f"Bearer {receptionist_token}"})
    odata = order_res.json()
    pid = odata["internal_payment_id"]

    sig = _generate_signature(odata["order_id"], "pay_rfnd_test")
    client.post("/api/v1/billing/payments/verify", json={
        "internal_payment_id": pid,
        "provider_order_id": odata["order_id"],
        "provider_payment_id": "pay_rfnd_test",
        "provider_signature": sig,
        "invoice_id": inv_id
    }, headers={"Authorization": f"Bearer {receptionist_token}"})

    # 1. Receptionist attempted refund -> Forbidden (403)
    rec_res = client.post(f"/api/v1/billing/payments/{pid}/refund", json={"amount": 500.00}, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert rec_res.status_code == 403

    # 2. Admin refund -> Success (200)
    admin_res = client.post(f"/api/v1/billing/payments/{pid}/refund", json={"amount": 500.00, "reason": "Patient requested partial cancellation"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200
    assert admin_res.json()["status"] == "refunded"

    # 3. Check invoice balance adjusted back
    inv = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"}).json()
    assert float(inv["balance"]) == 500.00
    assert inv["status"] == "partially_paid"
