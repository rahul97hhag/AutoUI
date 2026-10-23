from flask import jsonify

from app.api import api_bp
from app.schemas.plan_schema import plan_detail_schema, plan_list_schema
from app.services import plan_service


@api_bp.route("/plans", methods=["GET"])
def list_plans():
    plans = plan_service.get_all_plans()
    return jsonify(plan_list_schema.dump(plans)), 200


@api_bp.route("/plans/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    plan = plan_service.get_plan_by_id(plan_id)
    if plan is None:
        return jsonify(error="not_found", message="Plan not found"), 404
    return jsonify(plan_detail_schema.dump(plan)), 200
