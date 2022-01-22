from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_moment import Moment
from config import Config
# from fyyur.models import db


app = Flask(__name__)
# moment = Moment(app)

app.config.from_object(Config)
db = SQLAlchemy(app)
# db.init_app(app)

migrate = Migrate(app, db)


# Avoid circulation
from fyyur import routes



