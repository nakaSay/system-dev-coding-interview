from . import utils

test_users = [
        {"email": "deadpool@example.com", "password": "chimichangas4life"},
        {"email": "deadpoo2@example.com", "password": "chimichangas4life2"},
    ]
item_titles = ["test_title", "test_title2"]
item_descriptions = ["test_description", "test_description2"]

# ユーザー登録&取得
def test_create_user(test_db, client):
    test_user = test_users[0]
    response = client.post(
        "/users/",
        json=test_user,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    db_user = data["db_user"]
    assert db_user["email"] == test_user["email"]
    assert "id" in db_user
    user_id = db_user["id"]
    token = data["x_api_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["id"] == user_id

# 認証
def test_authenticate_user(test_db, client):
    user_ids, user_tokens = utils.create_users_and_items(client, test_users, item_titles, item_descriptions)

    ind = 0
    user_id = user_ids[ind]
    token = user_tokens[ind]

    # 正常系
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200, response.text

    # 異常系（トークンあり）
    headers = {"Authorization": f"Bearer fake"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 401, response.text

    # 異常系（トークンなし）
    headers = {"Authorization": f""}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 403, response.text

# ユーザーリスト取得
def test_read_users(test_db, client):
    user_ids, user_tokens = utils.create_users_and_items(client, test_users, item_titles, item_descriptions)

    headers = {"Authorization": f"Bearer {user_tokens[0]}"}
    response = client.get(
        "/users/",
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    data = data[:len(item_titles)]
    for i, user in enumerate(data):
        assert user["email"] == test_users[i]["email"]
        assert user["id"] == user_ids[i]

# タスク作成
def test_create_items(test_db, client):
    user_ids, user_tokens = utils.create_users_and_items(client, test_users, item_titles, item_descriptions)
    ind = 0
    user_id = user_ids[ind]
    title = item_titles[ind]
    descriptions = item_descriptions[ind]
    headers = {"Authorization": f"Bearer {user_tokens[ind]}"}
    response = client.post(
        f"/users/{user_ids[ind]}/items/", 
        headers=headers,
        json={"title": title, "description": descriptions},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == title
    assert data["description"] == descriptions
    assert data["owner_id"] == user_id

# タスクリスト取得
def test_get_items(test_db, client):
    user_ids, user_tokens = utils.create_users_and_items(client, test_users, item_titles, item_descriptions)

    headers = {"Authorization": f"Bearer {user_tokens[0]}"}
    response = client.get("/items/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    data = data[:len(item_titles)]
    for i, item in enumerate(data):
        assert item["title"] == item_titles[i]
        assert item["description"] == item_descriptions[i]
        assert item["owner_id"] == user_ids[i]

# タスク取得
def test_get_item(test_db, client):
    user_ids, user_tokens = utils.create_users_and_items(client, test_users, item_titles, item_descriptions)

    ind = 1
    headers = {"Authorization": f"Bearer {user_tokens[ind]}"}
    response = client.get("/me/items/", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["title"] == item_titles[ind]
    assert data[0]["description"] == item_descriptions[ind]
    assert data[0]["owner_id"] == user_ids[ind]
