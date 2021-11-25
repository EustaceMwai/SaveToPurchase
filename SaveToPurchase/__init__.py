from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from .helpers import SaveToPurchase


app = Flask(__name__)

app.config.from_object('config')


bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
save_to_purchase = SaveToPurchase()

from . import (
        models, index, registration, payments, portal, ussd, ussdmenus,
        customer_details

)


# save_to_Purchase = Nilipie()