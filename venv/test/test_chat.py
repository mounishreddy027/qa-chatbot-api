import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_llm_success():
    with patch("app.llm.get_answer") as mock:
        mock.return_value = {
            "success": True,
            "answer": "This is a test answer",
            "model": "models/gemini-1.5-flash"
        }
        yield mock

@pytest.fixture
def mock_llm_failure():
    with patch("app.llm.get_answer") as mock:
        mock.return_value = {
            "success": False,
            "error": "API error",
            "answer": "I encountered an error processing your request."
        }
        yield mock

@pytest.fixture
def mock_history_success():
    with patch("app.chat.get_history", AsyncMock(return_value=[
        {"id": 1, "question": "Q1", "answer": "A1", "timestamp": "2025-05-09T10:00:00"}
    ])):
        yield

@pytest.fixture
def mock_add_to_history_success():
    with patch("app.chat.add_to_history", AsyncMock(return_value=True)):
        yield

@pytest.fixture
def mock_add_to_history_failure():
    with patch("app.chat.add_to_history", AsyncMock(return_value=False)):
        yield


# ----------- Health Check -----------

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ----------- /ask endpoint -----------

def test_ask_question_success(mock_llm_success, mock_add_to_history_success):
    response = client.post("/ask", json={"question": "What is AI?"})
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["answer"] == "This is a test answer"
    assert data["question"] == "What is AI?"

def test_ask_question_llm_error(mock_llm_failure, mock_add_to_history_success):
    response = client.post("/ask", json={"question": "What is AI?"})
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "error" in data
    assert data["answer"] == "I encountered an error processing your request."

def test_ask_question_db_failure(mock_llm_success, mock_add_to_history_failure):
    response = client.post("/ask", json={"question": "What is AI?"})
    assert response.status_code == 200  # Still succeeds despite DB issue


# ----------- Input validation -----------

@pytest.mark.parametrize("bad_question", ["", " " * 5, "x" * 501])
def test_invalid_question_input(bad_question):
    response = client.post("/ask", json={"question": bad_question})
    assert response.status_code == 422


# ----------- /history endpoint -----------

def test_get_history_success(mock_history_success):
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1

def test_invalid_history_limit():
    response = client.get("/history?limit=-5")
    assert response.status_code == 400
    assert "Limit must be between" in response.json()["detail"]

def test_history_retrieval_error():
    with patch("app.chat.get_history", AsyncMock(side_effect=Exception("DB Error"))):
        response = client.get("/history")
        assert response.status_code == 500
        assert "Failed to retrieve" in response.json()["detail"]
