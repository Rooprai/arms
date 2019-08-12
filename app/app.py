import os
import flask
from datetime import timedelta

from sessionManager import SessionManager

user_details = {}

def create_app(test_config=None):
    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = '1234'
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=10)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

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

    # # a simple page that says hello
    # @app.route('/')
    # def hello():
    #     return flask.render_template('index.html')

    # @app.route('/login', methods=["GET", "POST"])
    # def login():
    #     if flask.request.method == "GET":
    #         msg = 'Hello flask'
    #     elif flask.request.method == "POST":
    #         msg = str(flask.request.form) + "<br/> Hello flask"
    #     return msg
    #     # return flask.render_template('login.html')

    # @app.route('/loginuser', methods=["POST"])
    # def test():
    #     # print(flask.request.json)
    #     formdata = flask.request.form
    #     print(formdata)
    #     return flask.redirect('/login', code=307), 201
    #     # return formdata

    @app.route('/')
    def index():
        title = "Home"

        page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <p>{msg}</p>
            <ul>
                <li><a href="/{url}">{url_tag}</a></li>
                <li><a href="/view">View Profile</a></li>
            </ul>
        </body>
        </html>
        """
        if flask.session.get('token') in user_details:
            url = "logout"
            msg = "Welcome {}!".format(flask.session['token'])
        else:
            url = "login"
            msg = "Please Login!"

        index_page = page.format(title=title,
                                 msg=msg, 
                                 url=url, url_tag=url.capitalize())

        return index_page

    @app.route('/login')
    def login():
        title = "LogIn"
        page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <form action="/loginuser" method="post">
                <label>Username: <input type="text" name="username"></label><br/><br/>
                <label>password: <input type="password" name="password"></label><br/><br/>
                <button>Login</button>
            </form>
        </body>
        </html>
        """
        return page.format(title=title)

    @app.route('/loginuser', methods=["POST"])
    def loginuser():

        page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <h3>User {username} is not Registered, Fill up the details below!</h3>
            <form action="/register" method="post">
                <label>Full Name:<input type="text" name="fullname"></label><br/><br/>
                <label>State<input type="text" name="state"></label><br/><br/>
                <label>Username:<input type="text" name="username"></label><br/><br/>
                <label>password:<input type="password" name="password"></label><br/><br/>
                <button>Register</button>
            </form>
        </body>
        </html>
        """

        token_id = flask.request.form['username']

        if token_id not in user_details:
            return page.format(title="404", username=token_id)

        flask.session['token'] = token_id
        # flask.session.permanent = True
        return flask.redirect('/')

    @app.route('/logout')
    def logoutuser():
        flask.session.pop('token', None)
        return flask.redirect('/')

    @app.route('/register', methods=["POST"])
    def register():
        user_info = {}
        user_info["username"] = flask.request.form["username"]
        user_info["fullname"] = flask.request.form["fullname"]
        user_info["state"] = flask.request.form["state"]
        user_info["password"] = flask.request.form["password"]
        user_info["posts"] = []

        if user_info["username"] in user_details:
            return "User already exists!"

        user_details.update({user_info["username"]: user_info})
        flask.session['token'] = user_info["username"]

        return flask.redirect('/view')


    @app.route('/view',  methods=["GET", "POST"])
    def view():
        from pprint import pprint
        pprint(user_details)
        print
        user_info = user_details.get(flask.session["token"])
        page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{fullname}</title>
        </head>
        <body>
            <h3>Welcome {fullname}! <a href="/logout">Logout</a> </h3>
            <form action="/view" method="post">
                <input type="text" name="newpost">
                <button>New Post</button>
            </form>
            <br/><br/>
            {posts}
        </body>
        </html>
        """
        if flask.request.method == "POST":
            newpost = flask.request.form["newpost"]
            user_info["posts"].insert(0, newpost)

        if not user_info["posts"]:
            posts = "You don't have any posts yet!<br/><br/>"

        else: 
            posts = "<br/><br/>".join(user_info["posts"])

        user_details.update({user_info["username"]: user_info})

        return page.format(fullname=user_info["fullname"],
                            posts=posts)


    return app

