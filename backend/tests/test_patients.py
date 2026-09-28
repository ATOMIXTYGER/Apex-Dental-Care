def test_list_patients(client, receptionist_token):
    res = client.get("/api/v1/patients", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] >= 15
    assert len(data["items"]) > 0

def test_search_patients(client, receptionist_token):
    res = client.get("/api/v1/patients?search=Aarav", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(p["first_name"] == "Aarav" for p in items)

def test_create_patient(client, receptionist_token):
    payload = {
        "first_name": "Kunal",
        "last_name": "Sharma",
        "date_of_birth": "1990-01-11",
        "gender": "Male",
        "phone": "+91 98765 99999",
        "email": "kunal.sharma@example.in",
        "address": "57 MG Road, Bengaluru 560001",
        "blood_group": "A+",
        "medical_history": {
            "allergies": "None",
            "medical_conditions": "None",
            "bleeding_disorders": False
        },
        "dental_history": {
            "chief_complaint": "Regular cleaning",
            "brushing_frequency": "Twice daily"
        }
    }
    res = client.post("/api/v1/patients", json=payload, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["first_name"] == "Kunal"
    assert data["patient_code"].startswith("P-")
    assert data["medical_history"]["allergies"] == "None"

def test_get_patient_timeline(client, dentist_token):
    # Patient 1 has appointments, visits, prescriptions
    res = client.get("/api/v1/patients/1/timeline", headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 200
    timeline = res.json()
    assert isinstance(timeline, list)
    assert len(timeline) > 0
