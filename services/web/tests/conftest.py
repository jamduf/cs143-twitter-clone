# services/web/tests/conftest.py

import pytest
from project import create_app, db

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        from project.models import User  # 👈 move import here
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
