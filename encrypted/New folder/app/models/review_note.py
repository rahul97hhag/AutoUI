from app.extensions import db


class ReviewNote(db.Model):
    __tablename__ = "review_notes"

    id = db.Column(db.Integer, primary_key=True)
    plan_amount = db.Column(db.Integer, nullable=True)
    plan_name = db.Column(db.String(255), nullable=True)
    data = db.Column(db.String(50), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    benefit_name = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text, nullable=False)
