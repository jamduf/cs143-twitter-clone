# services/web/project/__init__.py

import os
from flask import Flask, jsonify, send_from_directory, request, render_template, url_for, session, redirect
from project.extensions import db
from datetime import datetime
from sqlalchemy import text

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object("project.config.Config")
    app.secret_key = "dev"

    if config_name == "testing":
        app.config.from_object("project.config.TestingConfig")
    elif config_name == "development":
        app.config.from_object("project.config.DevelopmentConfig")

    db.init_app(app)

    # 🧠 models are *imported only after* init_app
    with app.app_context():
        from project.models import User, Message  # 👈 safe here

    @app.route("/")
    def index():
        page = request.args.get("page", 1, type=int)
        per_page = 20

        messages = (
            db.session.query(Message, User.username)
            .join(User, Message.user_id == User.id)
            .order_by(Message.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return render_template("index.html", messages=messages)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("index"))

        error = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("index"))
            else:
                error = "Invalid username or password."

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/create_account", methods=["GET", "POST"])
    def create_account():
        if session.get("user_id"):
            return redirect(url_for("index"))

        error = None

        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm = request.form["confirm"]

            if password != confirm:
                error = "Passwords do not match!"
            elif User.query.filter((User.email == email) | (User.username == username)).first():
                error = "Email or username already exists!"
            else:
                new_user = User(email=email, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                session["user_id"] = new_user.id
                return redirect(url_for("index"))

        return render_template("create_account.html", error=error)

    @app.route("/create_message", methods=["GET", "POST"])
    def create_message():
        if "user_id" not in session:
            return redirect(url_for("login"))

        error = None
        if request.method == "POST":
            content = request.form.get("content", "").strip()

            if not content:
                error = "Message cannot be empty."
            else:
                new_message = Message(
                    user_id=session["user_id"],
                    content=content,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_message)
                db.session.commit()
                return redirect(url_for("index"))

        return render_template("create_message.html", error=error)

    @app.route("/search")
    def search():
        query = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = 20

        if not query:
            return render_template("search.html", messages=[], query=query, page=page, has_next=False, has_prev=False, suggestions=[])

        offset = (page - 1) * per_page

        # Primary full-text search
        stmt = text("""
            SELECT
                m.id,
                ts_headline('simple', m.content, plainto_tsquery('simple', :query)) AS highlighted,
                m.created_at,
                u.username
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE to_tsvector('simple', m.content) @@ plainto_tsquery('simple', :query)
            ORDER BY ts_rank_cd(to_tsvector('simple', m.content), plainto_tsquery('simple', :query)) DESC
            LIMIT :limit OFFSET :offset
        """)

        count_stmt = text("""
            SELECT COUNT(*) FROM messages
            WHERE to_tsvector('simple', content) @@ plainto_tsquery('simple', :query)
        """)

        with db.engine.connect() as conn:
            result = conn.execute(stmt, {"query": query, "limit": per_page, "offset": offset})
            messages = result.fetchall()
            total = conn.execute(count_stmt, {"query": query}).scalar()

            # If no results, use trigram for spelling suggestions
            suggestions = []
            if total == 0 and len(query) >= 3:
                suggest_stmt = text("""
                    SELECT DISTINCT content, similarity(content, :query) AS sim
                    FROM messages
                    WHERE content % :query
                    ORDER BY sim DESC
                    LIMIT 5
                    """)
                suggest_results = conn.execute(suggest_stmt, {"query": query}).fetchall()
                suggestions = [row[0] for row in suggest_results]

        return render_template("search.html", messages=messages, query=query, page=page,
                            has_next=(page * per_page) < total,
                            has_prev=page > 1,
                            suggestions=suggestions)


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
