def test_list_plans(client):
    response = client.get("/api/plans")
    assert response.status_code == 200
    plans = response.get_json()
    assert len(plans) == 57
    assert "benefit_names" in plans[0]


def test_get_plan_with_benefits(client):
    response = client.get("/api/plans/1")
    assert response.status_code == 200
    plan = response.get_json()
    assert plan["name"] == "30GB + Top OTTs"
    assert len(plan["benefits"]) == 5
    assert plan["benefits"][0]["name"] == "Prime Video Mobile Edition"


def test_get_plan_not_found(client):
    response = client.get("/api/plans/9999")
    assert response.status_code == 404


def test_review_notes_for_benefit(client):
    benefits_response = client.get("/api/plans/39")
    benefits = benefits_response.get_json()["benefits"]
    adobe_benefit = next(b for b in benefits if b["name"] == "Adobe Express Premium")

    response = client.get(f"/api/benefits/{adobe_benefit['id']}/review-notes")
    assert response.status_code == 200
    notes = response.get_json()
    assert len(notes) > 0
    assert all(note["benefit_name"] == "Adobe Express Premium" for note in notes)


def test_review_notes_for_benefit_not_found(client):
    response = client.get("/api/benefits/9999/review-notes")
    assert response.status_code == 404
