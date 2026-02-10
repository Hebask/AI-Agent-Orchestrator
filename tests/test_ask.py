def test_ask_basic(client):
    payload = {"message": "Hello"}

    response = client.post("/ask", json=payload)
    assert response.status_code == 200

    data = response.json()

    # With mocked Ollama, final agent returns reply
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
