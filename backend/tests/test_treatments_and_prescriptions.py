from decimal import Decimal

def test_create_treatment_plan_and_items(client, dentist_token):
    payload = {
        "patient_id": 2,
        "dentist_id": 1,
        "title": "Periodontal & Restoration Therapy",
        "notes": "Full mouth scaling and single filling",
        "treatments": [
            {
                "procedure_name": "Dental Prophylaxis & Scaling",
                "estimated_cost": 90.00,
                "notes": "Complete scaling"
            },
            {
                "procedure_name": "Composite Resin Filling (1-2 surfaces)",
                "tooth_number": 36,
                "estimated_cost": 120.00,
                "notes": "Occlusal filling"
            }
        ]
    }
    res = client.post("/api/v1/treatments/plans", json=payload, headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert float(data["estimated_total"]) == 210.00
    assert len(data["treatments"]) == 2

def test_create_prescription_and_generate_pdf(client, dentist_token):
    payload = {
        "patient_id": 2,
        "dentist_id": 1,
        "diagnosis_summary": "Post-scaling oral hygiene regimen",
        "general_instructions": "Rinse twice daily",
        "items": [
            {
                "medicine_name": "Chlorhexidine 0.2% Mouthwash",
                "dosage": "15 ml",
                "frequency": "Twice daily",
                "duration": "7 days",
                "timing": "After Meals",
                "instructions": "Do not rinse with water immediately after"
            }
        ]
    }
    res = client.post("/api/v1/prescriptions", json=payload, headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 201
    rx_data = res.json()
    rx_id = rx_data["id"]
    assert rx_data["prescription_number"].startswith("RX-")

    # Test PDF generation endpoint
    pdf_res = client.get(f"/api/v1/prescriptions/{rx_id}/pdf", headers={"Authorization": f"Bearer {dentist_token}"})
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 500 # Valid PDF bytes
    assert pdf_res.content.startswith(b"%PDF")
