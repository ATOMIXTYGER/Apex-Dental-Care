def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@clinic.com",
        "password": "Dental@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "admin"

def test_login_invalid_credentials(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@clinic.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"

def test_token_refresh(client):
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "dr.chen@clinic.com",
        "password": "Dental@123"
    })
    refresh_token = login_res.json()["refresh_token"]

    ref_res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert ref_res.status_code == 200
    ref_data = ref_res.json()
    assert "access_token" in ref_data
    assert "refresh_token" in ref_data

def test_get_current_user_profile(client, dentist_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {dentist_token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "dr.chen@clinic.com"
    assert res.json()["role"] == "dentist"
