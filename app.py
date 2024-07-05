import os

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_DATABASE")

from flask import Flask
from dotenv import load_dotenv
from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker

from db import db
from flask_migrate import Migrate
from models.users import UserModel
from models.accounts import AccountModel
from models.transactions import TransactionModel

from controllers.users import user_routes
from controllers.accounts import account_routes
from controllers.transactions import transaction_routes

from flask_login import LoginManager

from flasgger import Swagger

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{username}:{password}@{host}/{database}"
)

app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False  # Sessions are not permanent
app.config["PERMANENT_SESSION_LIFETIME"] = 600


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

app.register_blueprint(user_routes)
app.register_blueprint(account_routes)
app.register_blueprint(transaction_routes)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    try:
        return s.query(UserModel).get(int(user_id))
    finally:
        s.close()


@app.route("/")
def hello_world():

    return "Hello World"
