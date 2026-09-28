from datetime import date, timedelta


def test_list_appointments(client, receptionist_token):
    res = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) > 0

def test_create_appointment_and_conflict_detection(client, receptionist_token):
    target_date = (date.today() + timedelta(days=20)).isoformat()

    # 1. Schedule appointment 10:00 - 10:45 with dentist 1
    res1 = client.post("/api/v1/appointments", json={
        "patient_id": 1,
        "dentist_id": 1,
        "appointment_type_id": 1,
        "appointment_date": target_date,
        "start_time": "10:00:00",
        "end_time": "10:45:00",
        "reason": "Test Consultation"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res1.status_code == 201

    # 2. Try booking overlapping appointment with SAME dentist (10:15 - 11:00)
    res2 = client.post("/api/v1/appointments", json={
        "patient_id": 2,
        "dentist_id": 1,
        "appointment_type_id": 1,
        "appointment_date": target_date,
        "start_time": "10:15:00",
        "end_time": "11:00:00",
        "reason": "Conflicting Consultation"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res2.status_code == 409
    assert res2.json()["error"]["code"] == "APPOINTMENT_CONFLICT"

def test_update_appointment_status(client, receptionist_token):
    # Schedule and cancel
    target_date = (date.today() + timedelta(days=22)).isoformat()
    res = client.post("/api/v1/appointments", json={
        "patient_id": 2,
        "dentist_id": 2,
        "appointment_date": target_date,
        "start_time": "14:00:00",
        "end_time": "14:30:00",
        "reason": "Status Test"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert res.status_code == 201
    appt_id = res.json()["id"]

    patch_res = client.patch(f"/api/v1/appointments/{appt_id}/status", json={
        "status": "cancelled",
        "cancellation_reason": "Patient requested reschedule"
    }, headers={"Authorization": f"Bearer {receptionist_token}"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "cancelled"
    assert patch_res.json()["cancellation_reason"] == "Patient requested reschedule"
