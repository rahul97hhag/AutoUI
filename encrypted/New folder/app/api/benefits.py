from flask import jsonify

from app.api import api_bp
from app.schemas.review_note_schema import review_notes_schema
from app.services import plan_service, review_note_service


@api_bp.route("/benefits/<int:benefit_id>/review-notes", methods=["GET"])
def get_review_notes_for_benefit(benefit_id):
    benefit = plan_service.get_benefit_by_id(benefit_id)
    if benefit is None:
        return jsonify(error="not_found", message="Benefit not found"), 404
    notes = review_note_service.get_review_notes_for_benefit_name(benefit.name)
    return jsonify(review_notes_schema.dump(notes)), 200
