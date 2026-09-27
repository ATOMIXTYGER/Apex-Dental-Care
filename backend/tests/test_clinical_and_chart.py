from datetime import date

def test_create_visit_examination(client, dentist_token):
    payload = {
        "patient_id": 2,
        "dentist_id": 1,
        "visit_date": date.today().isoformat(),
        "vitals_blood_pressure": "120/80",
        "vitals_pulse": 72,
        "chief_complaint": "Mild bleeding gums",
        "oral_findings": "Marginal gingivitis, no bone loss",
        "gum_condition": "Gingivitis",
        "hygiene_index": "Fair",
        "diagnosis": "Generalized gingivitis",
        "clinical_notes": "Ultrasonic scaling performed."
    }
    res = client.post("/api/v1/visits", json=payload, headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["diagnosis"] == "Generalized gingivitis"
    assert data["patient_name"] is not None

def test_fdi_dental_chart_retrieval(client, dentist_token):
    res = client.get("/api/v1/dental-chart/1", headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "teeth" in data
    assert len(data["teeth"]) == 32 # All 32 permanent teeth accounted for
    assert "history" in data

def test_fdi_dental_chart_tooth_update(client, dentist_token):
    payload = {
        "tooth_number": 26,
        "condition": "filled",
        "severity": "mild",
        "surfaces": "MOD",
        "notes": "Composite restoration placed."
    }
    res = client.post("/api/v1/dental-chart/1/tooth", json=payload, headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["tooth_number"] == 26
    assert data["current_condition"] == "filled"
    assert data["surfaces"] == "MOD"

    # Check history
    hist_res = client.get("/api/v1/dental-chart/1/tooth/26/history", headers={"Authorization": f"Bearer {dentist_token}"})
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert len(hist) > 0
    assert hist[0]["condition"] == "filled"

def test_fdi_invalid_tooth_number(client, dentist_token):
    # Tooth 99 is invalid in FDI notation
    payload = {
        "tooth_number": 99,
        "condition": "caries"
    }
    res = client.post("/api/v1/dental-chart/1/tooth", json=payload, headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 422 # Pydantic validation error
