from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert payload

    for activity_name, details in payload.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert set(details.keys()) == {
            "description",
            "schedule",
            "max_participants",
            "participants",
        }
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_for_activity_returns_404_for_unknown_activity(client):
    response = client.post(
        f"/activities/{quote('Unknown Club', safe='')}/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_returns_400_for_duplicate_signup(client):
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": duplicate_email},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_unregister_from_activity_success(client):
    activity_name = "Robotics Club"
    email = "ryan@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_from_activity_returns_404_for_unknown_activity(client):
    response = client.delete(
        f"/activities/{quote('Unknown Club', safe='')}/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_returns_404_when_student_not_signed_up(client):
    activity_name = "Chess Club"
    email = "notenrolled@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}