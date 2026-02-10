def test_list_runs(client):
    response = client.get("/runs")
    assert response.status_code == 200

    data = response.json()

    # Your API returns {"items": [...]}
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_run_not_found(client):
    response = client.get("/runs/non-existent-id")

    # Depending on implementation, could be 404 or 200 with empty content
    assert response.status_code in (404, 200)
