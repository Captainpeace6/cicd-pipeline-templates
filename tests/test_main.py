from fastapi.testclient import TestClient

from app.main import _ITEMS, app

client = TestClient(app)


def setup_function():
    _ITEMS.clear()


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version_reads_env(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    monkeypatch.setenv("GIT_SHA", "abc123")
    body = client.get("/version").json()
    assert body["version"] == "1.2.3"
    assert body["commit"] == "abc123"


def test_create_and_get_item():
    r = client.post("/items", json={"name": "hoodie", "quantity": 12})
    assert r.status_code == 201
    item = r.json()
    assert item == {"id": 1, "name": "hoodie", "quantity": 12}
    assert client.get("/items/1").json() == item
    assert client.get("/items").json() == [item]


def test_missing_item_is_404():
    assert client.get("/items/99").status_code == 404


def test_rejects_negative_quantity():
    r = client.post("/items", json={"name": "tee", "quantity": -1})
    assert r.status_code == 422
