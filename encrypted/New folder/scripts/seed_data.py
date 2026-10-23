import json
import os

from app.extensions import db
from app.models.plan import Benefit, Plan
from app.models.review_note import ReviewNote

TESTDATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "testdata"
)


def _load_json(filename):
    path = os.path.join(TESTDATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_plans():
    for entry in _load_json("Airtel_Recharge_Plans_With_Benefits.json"):
        details = entry["details"]
        plan = Plan(
            name=entry.get("planName"),
            plan_type=details.get("planType"),
            mobile_number=details.get("mobileNumber"),
            amount=details["amount"]["value"],
            currency=details["amount"]["currency"],
            amount_payable=details.get("amountPayable", {}).get("value"),
            amount_payable_currency=details.get("amountPayable", {}).get("currency"),
            pack_type=details.get("packType"),
            data=details.get("data"),
            talktime=details.get("talktime"),
            duration=details.get("duration"),
        )
        for benefit in details.get("benefits", []):
            plan.benefits.append(
                Benefit(
                    name=benefit["name"],
                    validity=benefit.get("validity"),
                    description=benefit.get("description"),
                )
            )
        db.session.add(plan)
    db.session.commit()


def load_review_notes():
    payload = _load_json("Airtel_Recharge_Plans_Benefit_Review.json")
    for note in payload.get("reviewNotes", []):
        db.session.add(
            ReviewNote(
                plan_amount=note.get("planAmount"),
                plan_name=note.get("planName"),
                data=note.get("data"),
                duration=note.get("duration"),
                benefit_name=note.get("benefitName"),
                note=note.get("note"),
            )
        )
    db.session.commit()


def seed(reset=False):
    if reset:
        db.drop_all()
    db.create_all()

    if Plan.query.first() is None:
        load_plans()
    if ReviewNote.query.first() is None:
        load_review_notes()

    return {
        "plans": Plan.query.count(),
        "benefits": Benefit.query.count(),
        "review_notes": ReviewNote.query.count(),
    }


if __name__ == "__main__":
    from app import create_app

    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        counts = seed()
        print(f"Seeded: {counts}")
