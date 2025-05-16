# services/web/manage.py

from flask.cli import FlaskGroup
from project import create_app
from project.extensions import db  # Import db from extensions module

app = create_app()
cli = FlaskGroup(app)

# ✅ Import User *after* app is created and db is initialized
with app.app_context():
    from project.models import User

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="michael@mherman.org"))
    db.session.commit()

if __name__ == "__main__":
    cli()
