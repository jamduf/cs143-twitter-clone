def test_register_and_login(client):
    res = client.post("/register", data={"username": "james", "password": "pass"}, follow_redirects=True)
    assert b"Welcome" in res.data

    res = client.post("/login", data={"username": "james", "password": "pass"}, follow_redirects=True)
    assert b"Logout" in res.data
