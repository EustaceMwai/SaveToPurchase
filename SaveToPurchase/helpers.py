import json
import random
import string
from datetime import datetime, timedelta

import jwt
import requests

from config import ussd_url_test, SECRET_KEY
from . import models


class SaveToPurchase:
    @staticmethod
    def generate_random_spending():
        acc_no = random.randrange(6000000000, 9999999999)
        return acc_no

    @staticmethod
    def generate_random_savings():
        acc_no = random.randrange(1000000000, 5999999999)
        return acc_no

    @staticmethod
    def generate_master_id(length):
        # With combination of lower and upper case
        trans_id = ''.join(random.choice(string.ascii_uppercase) for i in range(length))
        # print random string

        return trans_id

    @staticmethod
    def get_random_string(length):
        # With combination of lower and upper case

        trans_id = ''.join(random.choice(string.ascii_letters) for i in range(length))
        # print random string

        return trans_id

    @staticmethod
    def process_stk_results(transaction_id, name, reference):
        endpoint = "{}/stk_deposits".format(ussd_url_test)
        headers = {"Content-Type": "application/json"}

        response_data = requests.post(
            endpoint,
            json={
                "transaction_id": transaction_id,
                "account": "test",
                "name": name,
                "description": "The service request is processed successfully.",
                "reference": reference,
                "status": "success"

            }, headers=headers, verify=False)
        print("response is ", response_data.text)

        return response_data.json()

    @staticmethod
    def send_save_to_purchase_message(phone_number, text):
        url = "https://sms.onfonmedia.co.ke"

        payload = {
            "SenderId": "OnfonInfo",
            "MessageParameters": [
                {
                    "Number": phone_number,
                    "Text": text,
                }
            ],
            "ApiKey": "80oGEibQEFzf37KcXRqKt36jtg2K7WgaGlZgc/sCxIQ=",
            "ClientId": "811a6c43-7f28-4c27-8fc6-f1b5c54d3a3e"
        }

        headers = {
            'Content-Type': "application/json",
            'AccessKey': "SW9ibWmBMNzJ6r4oZRr5GgyvhGpxkAnY",
        }
        # logging.info(json.dumps(payload))
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers, verify=True)



        return response

    @staticmethod
    def sendMessage(phone_number, text):
        url = "https://api.onfonmedia.co.ke/v1/sms/SendBulkSMS"

        payload = {
            "SenderId": "22141",
            "MessageParameters": [
                {
                    "Number": phone_number,
                    "Text": text
                }
            ],
            "ApiKey": "eGh/LkniEmyaruyee6aQYCNbvdYwx6sUNr6CsSkORWM=",
            "ClientId": "e74f0df8-c70a-46c1-b400-dd346ab84be2"
        }

        headers = {
            'Content-Type': "application/json",
            'AccessKey': "2MJcjwjwOFMTAFep4iYV4jzMWybkxlXg",
        }
        # logging.info(json.dumps(payload))
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers, verify=True)
        print(json.dumps(payload))

        print(response.text)

    @staticmethod
    def log_ussd_session(db, sessionId, serviceCode, msisdn, ussdString, level):
        user = models.USSD_SESSION_LOGS(sessionId=sessionId,
                                        serviceCode=serviceCode,
                                        msisdn=msisdn,
                                        ussdString=ussdString,
                                        level=level)

        db.session.add(user)

        db.session.commit()

    @staticmethod
    def get_user_accounts(msisdn, token):
        endpoint = "{}/get_customer_accounts".format(ussd_url_test)

        headers = {"x-access-token": token, "Content-Type": "application/json"}

        response_data = requests.post(
            endpoint,
            json={
                "username": msisdn,

            }, headers=headers, verify=False)
        print("response is ", response_data.text)

        return response_data.json()

    @staticmethod
    def auth_token(db, phone_number):
        current_user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=phone_number) \
            .first()

        token = jwt.encode({'id': current_user.id, 'exp': datetime.utcnow() + timedelta(hours=12)},
                           SECRET_KEY)

        return token.decode('UTF-8')

