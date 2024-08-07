import os

from flask import Flask, render_template, request, redirect


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'calendar_app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template("index.html", pageTitle="Dashboard", pageCss="homeStyle")

    @app.route('/account')
    def account():
        return render_template("auth.html", pageTitle="Register", pageCss="authStyle")

    @app.route('/register', methods=["POST"])
    def register():
        if not request.form.get("firstName"):
            return "FFFFU"
        # if not request.form.get("password") === request.form.get("confirmPassword"):
        #     return "Passwords do not match"
        return redirect("/")

    from . import db
    db.init_app(app)

    return app
