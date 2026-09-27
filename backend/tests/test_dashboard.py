def test_dashboard_summary_metrics(client, admin_token):
    res = client.get("/api/v1/dashboard/summary?period=30d", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_patients" in data
    assert data["total_patients"] >= 15
    assert "today_appointments" in data
    assert "total_revenue" in data
    assert float(data["total_revenue"]) > 0
    assert "outstanding_payments" in data

def test_dashboard_analytics_charts(client, admin_token):
    res = client.get("/api/v1/dashboard/analytics?days=30", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "appointments_by_status" in data
    assert len(data["appointments_by_status"]) > 0
    assert "treatments_by_procedure" in data
    assert "revenue_trend" in data
    assert "patients_trend" in data

def test_health_endpoints(client):
    liveness = client.get("/health")
    assert liveness.status_code == 200
    assert liveness.json()["status"] == "ok"

    readiness = client.get("/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"
