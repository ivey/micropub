
from flask import Flask, render_template, session
from flask_session import Session
from datetime import timedelta
from config import ME, TOKEN_ENDPOINT
import os

def create_app():
    app = Flask(__name__)

    # set secret key
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
    app.config['TOKEN_ENDPOINT'] = TOKEN_ENDPOINT
    app.config['ME'] = "https://"+ME
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['SESSION_TYPE'] = "filesystem"

    # set maximum lifetime for session
    app.permanent_session_lifetime = timedelta(days=120)

    app.config.from_object(__name__)

    sess = Session()
    sess.init_app(app)

    from server.micropub import micropub as micropub_blueprint

    app.register_blueprint(micropub_blueprint)

    from client import client as client_blueprint

    app.register_blueprint(client_blueprint)

    from auth.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    @app.errorhandler(400)
    def request_error(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="400", title="Bad request error", user=user, me=me), 400

    @app.errorhandler(405)
    def method_not_allowed(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="405", title="Method not allowed error", user=user, me=me), 405

    @app.errorhandler(404)
    def page_not_found(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="404", title="Page not found error", user=user, me=me), 404

    @app.errorhandler(500)
    def server_error(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="500", title="Server error", user=user, me=me), 500

    return app

create_app()