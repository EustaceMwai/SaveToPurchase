from flask import request, make_response

from SaveToPurchase import app, db, models, save_to_purchase
from SaveToPurchase.ussdmenus import home_page_menu, unregistered_home_page_menu
from config import logger, ussd_session_live, ussd_code_live, ussd_msisdn_live, ussd_text_live


@app.route('/api/ussd', methods=['POST'])
def ussd_callback():
    data = request.get_json()
    logger.info("Ussd callback request{}".format(data))

    user = db.session.query(models.Entity_Users) \
        .filter_by(user_name=data.get('msisdn')) \
        .first()

    session_id = data.get(ussd_session_live, None)
    serviceCode = data.get(ussd_code_live, None)
    phoneNumber = data.get(ussd_msisdn_live, None)

    if user:

        if user:

            text = data.get(ussd_text_live, "")
            last_text = text.split("*")[-1:][0]
            # identify = "i"
            logger.info("text{}".format(text))
            user_phone = phoneNumber

            # user_account = nilipie.get_user_accounts(msisdn=user_phone,
            #                                          token=nilipie.auth_token(db, phone_number=user_phone))

        else:
            unregistered_text = data.get(ussd_text_live, "")
            last_unregistered_text = unregistered_text.split("*")[-1:][0]

    logger.info("session_id{}".format(session_id))
    logger.info("serviceCode{}".format(serviceCode))
    logger.info("phoneNumber{}".format(phoneNumber))

    similar_session = db.session.query(models.USSD_SESSION_LOGS) \
        .filter_by(sessionId=session_id) \
        .first()

    if user:

        if not similar_session:
            save_to_purchase.log_ussd_session(db,
                                              sessionId=session_id,
                                              serviceCode=serviceCode,
                                              msisdn=phoneNumber,
                                              ussdString=text,
                                              level='')

        menu_text = ""

        # serve menus based on text
        if last_text == "":
            user_account = save_to_purchase.get_user_accounts(msisdn=user_phone,
                                                     token=save_to_purchase.auth_token(db, phone_number=user_phone))

            menu_text = home_page_menu.format()

        # elif last_text == "1" and similar_session.ussdString == "":


    if not user:

        similar_session = db.session.query(models.USSD_SESSION_LOGS) \
            .filter_by(sessionId=session_id) \
            .first()

        print(similar_session)

        if not similar_session:
            save_to_purchase.log_ussd_session(db,
                                     sessionId=session_id,
                                     serviceCode=serviceCode,
                                     msisdn=phoneNumber,
                                     ussdString=unregistered_text,
                                     level='')

        menu_text = ""

        user_phone = phoneNumber
        similar_session = db.session.query(models.USSD_SESSION_LOGS) \
            .filter_by(sessionId=session_id) \
            .first()
        print("similar session at this level {}".format(similar_session))

        if last_unregistered_text == "" and similar_session.ussdString == "":
            menu_text = unregistered_home_page_menu


    resp = make_response(menu_text, 200)
    resp.headers['Content-Type'] = "application/json"
    return resp
