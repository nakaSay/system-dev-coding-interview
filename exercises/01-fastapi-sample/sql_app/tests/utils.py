def create_users_and_items(client, test_users, item_titles, item_descriptions):
    user_ids = []
    user_tokens = []
    for i, user in enumerate(test_users):
        response = client.post("/users/", json=user)
        data = response.json()
        db_user = data["db_user"]
        user_id = db_user["id"]
        user_ids.append(user_id)
        token = data["x_api_token"]
        user_tokens.append(token)

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/users/{user_id}/items/",
            headers=headers,
            json={"title": item_titles[i], "description": item_descriptions[i]},
        )
    return user_ids, user_tokens