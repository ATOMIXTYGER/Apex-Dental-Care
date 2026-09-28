# Online Payment Gateway Integration Guide

This document details the architecture, configuration, security model, and operational procedures for the online payment gateway integrated into the **Apex Dental Care** Smart Dental Clinic Management System.

---

## 1. Architecture Overview

The payment system follows a decoupled, provider-agnostic design. The clinic's database remains the **sole source of truth** for all invoice balances and payment records. No payment is marked `SUCCESS` without server-side cryptographic signature validation.

```
                      +-----------------------------+
                      |   Frontend (React / Vite)   |
                      +--------------+--------------+
                                     |
              1. Click "Pay Online"  |  3. Razorpay SDK Modal /
                 (Full or Partial)   |     Sandbox Simulator
                                     v
+-------------------------------------------------------------------------+
|                         Backend (FastAPI)                               |
|                                                                         |
|  [POST /api/v1/billing/invoices/{id}/payments/order]                    |
|    - Validates invoice exists, payable, balance > 0                     |
|    - Prevents overpayment / negative balances (Decimal precision)        |
|    - Idempotency check via idempotency_key                              |
|    - Generates Gateway Order via BasePaymentProvider                    |
|    - Creates Payment record with status="PENDING"                       |
|                                                                         |
|  [POST /api/v1/billing/payments/verify]                                 |
|    - Server-side cryptographic HMAC-SHA256 signature verification       |
|    - Atomic DB transaction: row lock, status=SUCCESS, balance recalc    |
|    - Creates structured AUDIT log entry                                 |
|    - Returns verified payment details                                   |
|                                                                         |
|  [POST /api/v1/billing/webhooks/{provider}]                            |
|    - Validates X-Razorpay-Signature over raw request bytes              |
|    - Idempotent deduplication via payment_webhook_events table          |
|    - Asynchronously reconciles pending payments                         |
+------------------------------------+------------------------------------+
                                     |
                         Provider Abstraction Layer
                                     |
            +------------------------+------------------------+
            |                                                 |
+-----------v-----------+                         +-----------v-----------+
|    RazorpayProvider   |                         |  MockPaymentProvider  |
|  (Official API v1     |                         |  (Offline Dev / CI    |
|   HMAC-SHA256 crypto) |                         |   Zero-dependency)    |
+-----------------------+                         +-----------------------+
```

---

## 2. Payment Lifecycle & Status Model

Payments transition through a strict finite state machine:

| Status | Description |
| :--- | :--- |
| `PENDING` | Order created on gateway; awaiting patient authorization and capture. |
| `SUCCESS` | Cryptographically verified server-side via HMAC-SHA256; invoice balance credited. |
| `FAILED` | Payment failed or signature verification failed; invoice balance untouched. |
| `REFUNDED` | Full payment refunded by an authorized Administrator; invoice balance restored. |
| `PARTIALLY_REFUNDED` | Partial refund processed; invoice balance credited back proportionately. |

### Invoice Payment Status Derivation
Invoice status is never manually edited; it is derived from real database transactions:
$$\text{paid\_amount} = \sum_{\text{SUCCESS}} \text{payment.amount}$$
$$\text{balance} = \text{invoice.total} - \text{paid\_amount}$$
- $\text{paid\_amount} = 0 \implies \textbf{UNPAID}$
- $0 < \text{paid\_amount} < \text{total} \implies \textbf{PARTIALLY\_PAID}$
- $\text{paid\_amount} \ge \text{total} \implies \textbf{PAID}$

---

## 3. Configuration & Environment Variables

Configure the gateway in your `.env` file:

```ini
# Gateway Selection: "razorpay" for production/sandbox, "mock" for zero-dependency offline dev/CI
PAYMENT_PROVIDER=razorpay

# Mode: "test" (Sandbox) or "live" (Production)
PAYMENT_MODE=test

# Razorpay Credentials (from https://dashboard.razorpay.com/#/accesskeys)
PAYMENT_KEY_ID=rzp_test_placeholder_key_id
PAYMENT_KEY_SECRET=rzp_test_placeholder_key_secret

# Webhook Secret (configured in Razorpay Webhooks dashboard)
PAYMENT_WEBHOOK_SECRET=rzp_test_webhook_secret_key

# Transaction Currency
PAYMENT_CURRENCY=INR

# Redirection URLs
PAYMENT_SUCCESS_URL=https://clinic.example.com/billing
PAYMENT_FAILURE_URL=https://clinic.example.com/billing
```

> [!CAUTION]
> Never put `PAYMENT_KEY_SECRET` or `PAYMENT_WEBHOOK_SECRET` in frontend code, Git commits, or Vite environment variables (`VITE_*`). Only `key_id` is public.

---

## 4. API Reference

All payment endpoints are located under `/api/v1/billing`:

### 1. Create Payment Order
`POST /api/v1/billing/invoices/{invoice_id}/payments/order`
- **RBAC**: `admin`, `receptionist`
- **Request Body**:
  ```json
  {
    "amount": 5000.00,
    "idempotency_key": "ord-101-1727500000000"
  }
  ```
  *(If `amount` is omitted, defaults to the exact outstanding invoice balance).*
- **Response**: `200 OK`
  ```json
  {
    "internal_payment_id": 42,
    "order_id": "order_M123abcXYZ",
    "amount": 5000.00,
    "currency": "INR",
    "key_id": "rzp_test_...",
    "provider": "razorpay",
    "status": "PENDING",
    "clinic_name": "Apex Dental Care",
    "patient_name": "Rajesh Kumar",
    "patient_email": "rajesh@example.com",
    "patient_phone": "+919876543210"
  }
  ```

### 2. Verify Payment (Cryptographic Server-Side)
`POST /api/v1/billing/payments/verify`
- **RBAC**: `admin`, `receptionist`
- **Request Body**:
  ```json
  {
    "internal_payment_id": 42,
    "provider_order_id": "order_M123abcXYZ",
    "provider_payment_id": "pay_P456defUVW",
    "provider_signature": "9b12a34...",
    "invoice_id": 101
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "success": true,
    "payment_id": 42,
    "invoice_id": 101,
    "invoice_status": "partially_paid",
    "amount": 5000.00,
    "balance_remaining": 2000.00,
    "transaction_reference": "pay_P456defUVW",
    "message": "Payment verified and credited successfully."
  }
  ```

### 3. Webhook Listener
`POST /api/v1/billing/webhooks/{provider}`
- **Authentication**: Raw HMAC signature verification via header `X-Razorpay-Signature` against `PAYMENT_WEBHOOK_SECRET`.
- **Supported Events**: `payment.captured`, `payment.failed`, `order.paid`.
- **Idempotency**: All processed `event_id`s are recorded in `payment_webhook_events`. Repeated deliveries are acknowledged with `200 OK` without re-crediting the invoice.

### 4. Download Official Payment Receipt (PDF)
`GET /api/v1/billing/payments/{payment_id}/receipt`
- **RBAC**: `admin`, `receptionist`, `dentist`
- **Response**: Formatted PDF document containing clinic letterhead, receipt number, patient details, payment breakdown, remaining balance, and authorized signature block.

### 5. Reconcile Payment
`POST /api/v1/billing/payments/{payment_id}/reconcile`
- **RBAC**: `admin`, `receptionist`
- Queries the gateway API directly to verify state for any stuck `PENDING` payment and reconciles the database.

### 6. Process Refund
`POST /api/v1/billing/payments/{payment_id}/refund`
- **RBAC**: `admin` only
- Initiates gateway refund and updates internal ledger.

---

## 5. Security & Fraud Protection

| Attack Vector | Defense Mechanism |
| :--- | :--- |
| **Amount Tampering** | Backend calculates outstanding balance directly from database; client-requested amounts exceeding balance or $\le 0$ are rejected with HTTP 400. |
| **Invoice / Payment IDOR** | Backend verifies user permissions, validates that the payment transaction strictly matches the invoice ID, and confirms the gateway order mapping. |
| **Fake Success Callbacks** | Frontend callbacks are **never** trusted as proof of payment. Payment status is only updated after server-side cryptographic HMAC-SHA256 signature verification (`hmac.compare_digest`). |
| **Fake Webhooks** | Raw request bytes are verified against `PAYMENT_WEBHOOK_SECRET` before parsing JSON. Unsigned or invalid requests are rejected with HTTP 400. |
| **Replay Attacks** | Unique `event_id` constraint on `payment_webhook_events` ensures every webhook event is processed at most once. |
| **Double Payment Race** | Database updates use atomic transactions with row-level locking (`with_for_update`) to prevent concurrent payments from overpaying an invoice. |
| **Credential Leakage** | Secrets are isolated to backend `.env`. They are never logged, never returned in API responses, and never bundled in the frontend. |

---

## 6. Local Setup & Testing

### Running Tests
Execute the full test suite covering mock provider, Razorpay cryptographic signature verification, partial payments, IDOR, webhooks, and receipts:

```bash
# Backend Pytest Suite (43 tests)
cd backend
.\venv\Scripts\activate
pytest -v

# Frontend Vitest Suite (9 tests)
cd ../frontend
npm test -- --run

# Production Build Verification
npm run build
```

### Switching to Live Razorpay Credentials
1. Create a Razorpay account at [https://razorpay.com](https://razorpay.com).
2. Generate API Keys in **Settings > API Keys**.
3. Set in your production `.env`:
   ```ini
   PAYMENT_PROVIDER=razorpay
   PAYMENT_MODE=live
   PAYMENT_KEY_ID=rzp_live_your_actual_key
   PAYMENT_KEY_SECRET=your_actual_live_secret
   PAYMENT_WEBHOOK_SECRET=your_webhook_secret
   ```
4. Set up a Webhook in the Razorpay Dashboard pointing to:
   `https://your-domain.com/api/v1/billing/webhooks/razorpay`
   Select events: `payment.captured`, `payment.failed`, `order.paid`.
