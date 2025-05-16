# services/web/manage.py

from flask.cli import FlaskGroup
from sqlalchemy import text
from project import create_app
from project.extensions import db  # Import db from extensions module

app = create_app()
cli = FlaskGroup(app)

# ✅ Import models after app and db are ready
with app.app_context():
    from project.models import User

@cli.command("create_db")
def create_db():
    # Manually drop tables in dependency-safe order using CASCADE
    db.session.execute(text("DROP TABLE IF EXISTS urls CASCADE"))
    db.session.execute(text("DROP TABLE IF EXISTS tweets CASCADE"))
    db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    db.session.commit()

    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    user1 = User(email="michael@mherman.org", username="michael")
    db.session.add(user1)
    db.session.commit()

    msg = Message(user_id=user1.id, content="Hello world!")
    db.session.add(msg)
    db.session.commit()

if __name__ == "__main__":
    cli()
