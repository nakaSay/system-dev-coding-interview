def test_create_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    db_user = data["db_user"]
    assert db_user["email"] == "deadpool@example.com"
    assert "id" in db_user
    user_id = db_user["id"]

    token = data["x_api_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 正常系
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id

    # 異常系（トークンあり）
    headers = {"Authorization": f"Bearer fake"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 401, response.text

    # 異常系（トークンなし）
    headers = {"Authorization": f""}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 403, response.text