
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_POOL_RECYCLE = 10
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/save_to_purchase'

SECRET_KEY = "thisissecret"

import logging

logger = logging.getLogger("SAVE_TO_PURCHASE")
logger.setLevel(logging.INFO)
hdlr = logging.FileHandler("save_to_purchase.log")

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s ')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)


ussd_url_test = "http://127.0.0.1:5000"
# ussd_url_live = "https://www.nilipie.ml"

c2b_utility_name = "mpesa_c2b_utility"
c2b_utility_account_number = "4558892000"


ussd_session_live = "sessionId"
ussd_code_live = "serviceCode"
ussd_msisdn_live = "msisdn"
ussd_text_live = "ussdString"