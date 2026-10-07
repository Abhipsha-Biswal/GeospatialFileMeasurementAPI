from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Geospatial File Measurement API"


def test_invalid_extension():
    response = client.post(
        "/api/files/",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
