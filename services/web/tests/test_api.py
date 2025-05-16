def test_api_get_users(client):
    res = client.get("/api/users")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
