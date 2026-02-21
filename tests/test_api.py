import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_simple_equation():
    response = client.post("/api/solve", json={"equation": "2x + 5 = 15"})
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "x"
    assert data["numeric_solution"] == 5.0

def test_implicit_multiplication():
    response = client.post("/api/solve", json={"equation": "3y - 9 = 0"})
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "y"
    assert data["numeric_solution"] == 3.0

def test_other_variable():
    response = client.post("/api/solve", json={"equation": "2*a + 4 = 10"})
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "a"
    assert data["numeric_solution"] == 3.0

def test_no_solution():
    # Technically 0 = 5 has no solution
    response = client.post("/api/solve", json={"equation": "5 = 10"})
    # The logic returns HTTPException(status_code=400, detail="Keine Variable in der Gleichung gefunden.")
    assert response.status_code == 400
    assert "Keine Variable" in response.json()["detail"]

def test_multiple_variables_error():
    response = client.post("/api/solve", json={"equation": "x + y = 10"})
    assert response.status_code == 400
    assert "eine Variable" in response.json()["detail"]

def test_non_linear_error():
    response = client.post("/api/solve", json={"equation": "x^2 - 4 = 0"})
    assert response.status_code == 400
    assert "nur lineare gleichungen" in response.json()["detail"].lower()

def test_invalid_format():
    response = client.post("/api/solve", json={"equation": "abc"})
    assert response.status_code == 400
    assert "muss ein '=' Zeichen enthalten" in response.json()["detail"]
