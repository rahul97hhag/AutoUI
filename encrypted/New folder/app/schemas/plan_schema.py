from app.extensions import ma
from app.models.plan import Benefit, Plan


class BenefitSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Benefit
        load_instance = True
        exclude = ("plan_id",)


class PlanListSchema(ma.SQLAlchemyAutoSchema):
    benefit_names = ma.Method("get_benefit_names")

    class Meta:
        model = Plan
        load_instance = True

    def get_benefit_names(self, obj):
        return [benefit.name for benefit in obj.benefits]


class PlanDetailSchema(ma.SQLAlchemyAutoSchema):
    benefits = ma.Nested(BenefitSchema, many=True)

    class Meta:
        model = Plan
        load_instance = True


benefit_schema = BenefitSchema()
benefits_schema = BenefitSchema(many=True)
plan_list_schema = PlanListSchema(many=True)
plan_detail_schema = PlanDetailSchema()
