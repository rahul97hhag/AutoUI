from app.models.review_note import ReviewNote


def get_all_review_notes():
    return ReviewNote.query.order_by(ReviewNote.id).all()


def get_review_notes_for_benefit_name(benefit_name):
    pattern = f"%{benefit_name}%"
    return ReviewNote.query.filter(ReviewNote.benefit_name.ilike(pattern)).all()
