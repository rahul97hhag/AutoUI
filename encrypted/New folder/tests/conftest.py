import pytest

from app import create_app
from app.extensions import db
from scripts.seed_data import seed


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        seed()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
