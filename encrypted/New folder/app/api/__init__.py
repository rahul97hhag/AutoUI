from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api import health  # noqa: E402,F401
from app.api import plans  # noqa: E402,F401
from app.api import benefits  # noqa: E402,F401
