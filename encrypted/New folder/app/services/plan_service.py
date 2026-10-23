from app.extensions import db
from app.models.plan import Benefit, Plan


def get_all_plans():
    return Plan.query.order_by(Plan.id).all()


def get_plan_by_id(plan_id):
    return db.session.get(Plan, plan_id)


def get_benefit_by_id(benefit_id):
    return db.session.get(Benefit, benefit_id)
