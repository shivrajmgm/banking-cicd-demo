import pytest
from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Reset DB state before each test
    db["user123"]["failed_attempts"] = 0
    db["user123"]["locked"] = False
    db["user123"]["balance"] = 150000.00
    db["user123"]["daily_transferred"] = 0
    with app.test_client() as test_client:
        yield test_client


# AC2: Invalid credentials message without saying which field is wrong
def test_login_invalid_credentials(client):
    res = client.post("/login", json={"user_id": "user123", "password": "wrongpassword"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid credentials"


# AC3: Account locked after 3 wrong attempts
def test_login_lockout(client):
    for _ in range(3):
        res = client.post("/login", json={"user_id": "user123", "password": "wrongpassword"})
    assert res.status_code == 403
    assert res.get_json()["error"] == "Account locked for 30 minutes"


# BANK-7: Check Balance is formatted correctly
def test_dashboard_balance(client):
    res = client.get("/dashboard/user123")
    assert res.status_code == 200   
    assert res.get_json()["balance"] == 150000.00


# AC2 (BANK-8): Reject transfer if insufficient balance
def test_transfer_insufficient_balance(client):
    res = client.post("/transfer", json={
        "user_id": "user123",
        "amount": 200000.00,
        "otp": "123456"
    })
    assert res.status_code == 400
    assert res.get_json()["error"] == "Insufficient balance"


# AC4 (BANK-8): Daily transfer limit of Rs. 1,00,000 applies
def test_transfer_daily_limit(client):
    res = client.post("/transfer", json={
        "user_id": "user123",
        "amount": 105000.00,
        "otp": "123456"
    })
    assert res.status_code == 400
    assert res.get_json()["error"] == "Daily limit of Rs. 1,00,000 exceeded"


# AC1 (BANK-10): Block card instantly with OTP
def test_block_card(client):
    res = client.post("/card/status", json={
        "user_id": "user123",
        "action": "Blocked",
        "otp": "123456"
    })
    assert res.status_code == 200
    assert db["user123"]["card_status"] == "Blocked"


