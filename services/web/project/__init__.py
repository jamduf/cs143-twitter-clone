# services/web/project/__init__.py

import os
from flask import Flask, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename
from project.extensions import db

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object("project.config.Config")

    if config_name == "testing":
        app.config.from_object("project.config.TestingConfig")
    elif config_name == "development":
        app.config.from_object("project.config.DevelopmentConfig")

    db.init_app(app)

    # 🧠 models are *imported only after* init_app
    with app.app_context():
        from project.models import User  # 👈 safe here

    @app.route("/")
    def hello_world():
        return jsonify(hello="world")

    @app.route("/static/<path:filename>")
    def staticfiles(filename):
        return send_from_directory(app.config["STATIC_FOLDER"], filename)

    @app.route("/api/users")
    def get_users():
        users = User.query.all()
        return jsonify([{"id": u.id, "email": u.email} for u in users])

    @app.route("/media/<path:filename>")
    def mediafiles(filename):
        return send_from_directory(app.config["MEDIA_FOLDER"], filename)
    
    @app.route("/register", methods=["POST"])
    def register():
        username = request.form.get("username")
        return f"Welcome {username}!"

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form.get("username")
        return f"Logout {username}"

    @app.route("/upload", methods=["GET", "POST"])
    def upload_file():
        if request.method == "POST":
            file = request.files["file"]
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
        return """
        <!doctype html>
        <title>upload new File</title>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file><input type=submit value=Upload>
        </form>
        """

    return app
