from pathlib import Path
import sys
from fastapi.testclient import TestClient

# ensure src on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure not present
    resp = client.get("/activities")
    before = resp.json()
    all_participants = []
    for v in before.values():
        all_participants.extend(v.get("participants", []))
    assert email not in all_participants

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # check present
    resp = client.get("/activities")
    after = resp.json()
    assert email in after[activity]["participants"]

    # unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # check removed
    resp = client.get("/activities")
    final = resp.json()
    assert email not in final[activity]["participants"]


def test_signup_already_registered():
    # alex@mergington.edu already signed up in the initial data
    resp = client.post("/activities/Tennis%20Club/signup?email=alex@mergington.edu")
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()
