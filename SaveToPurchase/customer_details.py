import json
from datetime import datetime, timedelta

from flask import request, jsonify, make_response, Response
from sqlalchemy import and_, desc

from SaveToPurchase import app, db, models, save_to_purchase
from SaveToPurchase.decorators import token_required
from config import logger


@app.route('/get_customer_accounts', methods=['GET', 'POST'])
@token_required
def get_customer_accounts(current_user):
    data = request.get_json()
    logger.info("get_customer_accounts {}".format(data))

    try:

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data.get('username')) \
            .first()

        if user:
            spending_account = db.session.query(models.Entity_Account).filter(
                and_(
                    models.Entity_Account.entity_id == user.entity_id,

                    models.Entity_Account.description == "0"
                )).first()

            savings_account = db.session.query(models.Entity_Account).filter(
                and_(
                    models.Entity_Account.entity_id == user.entity_id,

                    models.Entity_Account.description == "1"
                )).first()

            logger.info("get_customer_accounts {}".format({
                'id': user.id,
                'entity_id': user.entity_id,
                'username': user.user_name,
                'spending_account_number': spending_account.account_number,
                'spending_current_balance': spending_account.available_balance,
                'savings_account_number': savings_account.account_number,
                'savings_current_balance': savings_account.available_balance,

            }))

            return make_response(jsonify({
                'id': user.id,
                'entity_id': user.entity_id,
                'username': user.user_name,
                'spending_account_number': spending_account.account_number,
                'spending_current_balance': spending_account.available_balance,
                'savings_account_number': savings_account.account_number,
                'savings_current_balance': savings_account.available_balance,

            }), 200)


        else:

            logger.info("get_customer_accounts {}".format({
                "message": " User does not exist"
            }))

            return jsonify({
                "message": " User does not exist"
            })
    except Exception as e:
        logger.error("Error {} occurred as {} tried to get customer accounts".format(e, data.get('username')))
        return make_response({
            "message": "Request Failed. Try again Later"
        }, 500)
