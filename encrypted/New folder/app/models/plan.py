from app.extensions import db


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    plan_type = db.Column(db.String(50), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="INR")
    amount_payable = db.Column(db.Integer, nullable=True)
    amount_payable_currency = db.Column(db.String(10), nullable=True)
    pack_type = db.Column(db.String(100), nullable=True)
    data = db.Column(db.String(50), nullable=True)
    talktime = db.Column(db.String(50), nullable=True)
    duration = db.Column(db.String(50), nullable=True)

    benefits = db.relationship(
        "Benefit", backref="plan", cascade="all, delete-orphan", lazy="select"
    )


class Benefit(db.Model):
    __tablename__ = "benefits"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    validity = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
