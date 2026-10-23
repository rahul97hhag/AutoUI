"""JSON Schemas for the Recharge Plans API, used by `verify_schema`."""

ERROR_SCHEMA = {
    "type": "object",
    "required": ["error", "message"],
    "properties": {
        "error": {"type": "string"},
        "message": {"type": "string"},
    },
}

PLAN_SUMMARY_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "amount", "currency", "benefit_names"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": ["string", "null"]},
            "amount": {"type": "number"},
            "currency": {"type": "string"},
            "benefit_names": {"type": "array", "items": {"type": "string"}},
        },
    },
}

PLAN_DETAIL_SCHEMA = {
    "type": "object",
    "required": ["id", "amount", "currency", "benefits"],
    "properties": {
        "id": {"type": "integer"},
        "amount": {"type": "number"},
        "currency": {"type": "string"},
        "benefits": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "validity", "description"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                },
            },
        },
    },
}
