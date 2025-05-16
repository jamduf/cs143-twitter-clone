def test_create_user(app):
    with app.app_context():
        from project.models import User
        from project.extensions import db

        user = User(email="j@aol.com")
        db.session.add(user)
        db.session.commit()

        queried = User.query.filter_by(email="j@aol.com").first()
        assert queried is not None
