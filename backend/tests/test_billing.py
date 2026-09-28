from datetime import date, timedelta


def test_invoice_creation_and_balance(client, receptionist_token):
    due = (date.today() + timedelta(days=14)).isoformat()
    payload = {
        "patient_id": 2,
        "due_date": due,
        "discount": 10.00,
        "tax": 0.00,
        "notes": "Testing invoice",
        "items": [
            {"description": "Dental Scaling", "unit_price": 90.00, "quantity": 1},
            {"description": "Fluoride Application", "unit_price": 40.00, "quantity": 1}
        ]
    }
    res = client.post("/api/v1/billing/invoices", json=payload, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert float(data["subtotal"]) == 130.00
    assert float(data["discount"]) == 10.00
    assert float(data["total"]) == 120.00
    assert float(data["balance"]) == 120.00
    assert data["status"] == "unpaid"

def test_payment_recording_and_overpayment_prevention(client, receptionist_token):
    # Create invoice for $100
    due = (date.today() + timedelta(days=7)).isoformat()
    inv_res = client.post("/api/v1/billing/invoices", json={
        "patient_id": 2,
        "due_date": due,
        "items": [{"description": "Dental Care", "unit_price": 100.00, "quantity": 1}]
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert inv_res.status_code == 201
    inv_id = inv_res.json()["id"]

    # 1. Attempt overpayment of $150
    over_res = client.post("/api/v1/billing/payments", json={
        "invoice_id": inv_id,
        "amount": 150.00,
        "payment_method": "card"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert over_res.status_code == 400
    assert over_res.json()["error"]["code"] == "OVERPAYMENT_NOT_ALLOWED"

    # 2. Record valid partial payment of $40
    pay1_res = client.post("/api/v1/billing/payments", json={
        "invoice_id": inv_id,
        "amount": 40.00,
        "payment_method": "cash"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert pay1_res.status_code == 201

    # Check invoice balance
    inv_check = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert inv_check.status_code == 200
    assert float(inv_check.json()["paid_amount"]) == 40.00
    assert float(inv_check.json()["balance"]) == 60.00
    assert inv_check.json()["status"] == "partially_paid"

    # 3. Pay remaining balance $60
    pay2_res = client.post("/api/v1/billing/payments", json={
        "invoice_id": inv_id,
        "amount": 60.00,
        "payment_method": "upi"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert pay2_res.status_code == 201

    # Check invoice status becomes paid
    inv_final = client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert inv_final.status_code == 200
    assert float(inv_final.json()["balance"]) == 0.00
    assert inv_final.json()["status"] == "paid"

def test_invoice_pdf_download(client, receptionist_token):
    res = client.get("/api/v1/billing/invoices/1/pdf", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
