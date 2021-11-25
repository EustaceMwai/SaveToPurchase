import json
from datetime import datetime, timedelta

from flask import request, make_response, jsonify, Response
from sqlalchemy import and_, desc

from config import logger, c2b_utility_account_number
from . import app, db, models, bcrypt
from .decorators import token_required


@app.route('/get_customer_details', methods=['GET', 'POST'])
@token_required
def get_customer_details(current_user):
    data = request.get_json()
    logger.info("get_customer_details {}".format(data))

    try:

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data.get('username')) \
            .first()

        if user:

            customer_kyc = db.session.query(models.Entity_Kyc) \
                .filter_by(
                entity_owner_id=user.entity_id
            ) \
                .first()

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

            logger.info("get_customer_details response{}".format({
                "first_name": customer_kyc.first_name,
                "other_name": customer_kyc.other_names,
                "national_id": customer_kyc.document_number,
                "registration_date": customer_kyc.date_created,
                'id': user.id,
                'entity_id': user.entity_id,
                'username': user.user_name,
                'spending_account_number': spending_account.account_number,
                'spending_current_balance': spending_account.available_balance,
                'savings_account_number': savings_account.account_number,
                'savings_current_balance': savings_account.available_balance,

            }))

            return make_response(jsonify({
                "first_name": customer_kyc.first_name,
                "other_name": customer_kyc.other_names,
                "national_id": customer_kyc.document_number,
                "registration_date": customer_kyc.date_created,
                'id': user.id,
                'entity_id': user.entity_id,
                'username': user.user_name,
                'spending_account_number': spending_account.account_number,
                'spending_current_balance': spending_account.available_balance,
                'savings_account_number': savings_account.account_number,
                'savings_current_balance': savings_account.available_balance,

            }), 200)


        else:

            logger.info("get_customer_details response {}".format({
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


@app.route('/deposit_transactions', methods=['GET', 'POST'])
@token_required
def get_all_deposits(current_user):
    data = request.get_json()

    try:

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data.get('username')) \
            .first()

        if user:
            service = db.session.query(models.Services) \
                .filter_by(name="till_deposit") \
                .first()

            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

            date_object = datetime.combine(start_date, datetime.min.time())
            date2_object = datetime.combine(end_date, datetime.min.time()) + timedelta(hours=24)

            group = db.session.query(models.Transactions). \
                filter(and_(
                models.Transactions.service_id == service.id,
                models.Transactions.account_number == c2b_utility_account_number
            )
            ).filter(and_(
                models.Transactions.debit <= float(data['max_amount']),
                models.Transactions.debit >= float(data['min_amount']))).filter(and_(
                models.Transactions.date_created <= date2_object,
                models.Transactions.date_created >= date_object)).order_by(
                desc(
                    models.Transactions.date_created and
                    models.Transactions.id
                )
            )

            contributions = []
            total = 0.0
            total_deposit_charges = 0.0

            def myconverter(o):
                if isinstance(o, datetime):
                    return o.__str__()

            for contribution in group:
                total = total + contribution.debit
                total_deposit_charges = total_deposit_charges + contribution.credit
                contributions.append({
                    # 'name': contribution.group.group_name,
                    'master_transaction_id': contribution.master_transaction_id,
                    'transaction_id': contribution.transaction_id,
                    'description': contribution.description,
                    'debit': contribution.debit,
                    'credit': contribution.credit,
                    'bal_before': contribution.bal_before,
                    'bal_after': contribution.bal_after,
                    'date_created': contribution.date_created
                })
            # count = len(contributions) / 2

            # for dict_item in contributions:
            #     for key in dict_item:
            #         print(dict_item["master_transaction_id"])
            #
            #         group2 = db.session.query(models.Transactions).filter(and_(
            #         models.Transactions.transaction_id == dict_item["master_transaction_id"],
            #         models.Transactions.credit == dict_item["debit"]
            #     ))
            #
            # for x in group2:
            #     contributions.append({
            #         # 'name': contribution.group.group_name,
            #         'master_transaction_id': x.master_transaction_id,
            #         'transaction_id': x.transaction_id,
            #         'description': x.description,
            #         'debit': x.debit,
            #         'credit': x.credit,
            #         'bal_before': x.bal_before,
            #         'bal_after': x.bal_after,
            #         'date_created': x.date_created
            #     })

            return Response(json.dumps({
                'total': total,
                # 'count': count,
                'total_deposit_charges': total_deposit_charges,
                'statements': contributions

            }, default=myconverter), mimetype='application/json', status=200)

        else:

            return jsonify({

                "message": "User does not exist"
            })


    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("error {} occurred while retrieving airtime transactions".format(e))
        return make_response({
            "message": "Request Failed. Try again Later"
        }, 500)


@app.route('/customer_statements', methods=['GET', 'POST'])
@token_required
def get_statements(current_user):
    data = request.get_json()

    try:

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data.get('username')) \
            .first()

        if user:

            date_object = datetime.strptime(data['start_date'], '%Y-%m-%d')
            date2_object = datetime.strptime(data['end_date'], '%Y-%m-%d') + timedelta(hours=24)



            group = db.session.query(models.Transactions). \
                filter(models.Transactions.account_number == data.get('savings_account_number')). \
                filter(and_(
                models.Transactions.date_created <= date2_object,
                models.Transactions.date_created >= date_object)).order_by(desc(models.Transactions.date_created and
                                                                                models.Transactions.id))

            contributions = []

            def myconverter(o):
                if isinstance(o, datetime):
                    return o.__str__()

            for contribution in group:
                contributions.append({
                    # 'name': contribution.group.group_name,
                    'master_transaction_id': contribution.master_transaction_id,
                    'transaction_id': contribution.transaction_id,
                    'description': contribution.description,
                    'debit': contribution.debit,
                    'credit': contribution.credit,
                    'bal_before': contribution.bal_before,
                    'bal_after': contribution.bal_after,
                    'date_created': contribution.date_created
                })

            return Response(json.dumps({

                'statements': contributions

            }, default=myconverter), mimetype='application/json', status=200)

        else:

            return jsonify({

                "message": "User does not exist"
            })
    except Exception as e:

        logger.error("customer {} spending statements error {}".format(data.get('username'), e))
        return make_response({
            "message": "Request Failed. Try again Later"
        }, 500)



@app.route('/get_customer_items', methods=['GET', 'POST'])
@token_required
def customer_items(current_user):
    data = request.get_json()

    logger.info("customer_items {}".format(data))
    try:

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data.get('username')) \
            .first()

        if user:

            pending_aprovals = db.session.query(models.Items_Selected).filter(

                    models.Items_Selected.entity_user_id == user.id,

                ).all()

            approval_list = []

            approval_full = []



            if pending_aprovals:

                values_list = []

                for group in pending_aprovals:

                    pending_bal = float(group.price) - float(group.savings_made)
                    approval_list.append({
                        'item_id': group.id,
                        'inventory_id': group.inventory_id,
                        'price': group.price,
                        'savings_made': group.savings_made,
                        'pending_balance': pending_bal,

                        'date_requested': group.date_created
                    })

                    for index in range(len(approval_list)):
                        for key in approval_list[index]:

                            item = db.session.query(models.Items_Inventory) \
                                .get(group.inventory_id)

                            approval_full.append({

                                'id': approval_list[index]['item_id'],
                                'item_name': item.name,
                                'item_model': item.model,
                                'item_size': item.size,
                                'price': approval_list[index]['price'],
                                "savings_made": approval_list[index]['savings_made'],
                                "pending_balance": approval_list[index]['pending_balance'],
                                "date_requested": approval_list[index]['date_requested'],

                            })

                            values = {v['id']: v for v in approval_full}.values()
                            values_list = list(values)

                logger.info("customer_items {}".format({
                    "customer_items": values_list,
                }))

                return jsonify({
                    "customer_items": values_list,
                })



            else:
                logger.info("customer_items {}".format({
                    "customer_items": [],
                }))

                return jsonify({
                    "customer_items": []
                })

        else:
            logger.info("customer_items {}".format({
                "message": " User does not exist"
            }))
            return jsonify({
                "message": " User does not exist"
            })
    except Exception as e:
        logger.error("Error {} occurred as {} tried to get customer_items".format(e, data.get('username')))
        return make_response({
            "message": "Request Failed. Try again Later"
        }, 500)
