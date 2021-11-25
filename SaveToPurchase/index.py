import json
from datetime import datetime

from flask import request, jsonify, make_response
from sqlalchemy import and_

from config import logger
from . import app, db, models


@app.route('/add_document_types', methods=['POST'])
def add_document_types():
    data = request.get_json()

    try:
        document = models.Document_Types(name=data['name'], description=data['description'],
                                         document_status="active", date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.name, "description": document.description,
             "created_at": document.date_created,
             "message": "success", })

    except Exception as e:
        logger.error("error {} in document_types".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"
        })


@app.route('/add_user_types', methods=['POST'])
def add_user_types():
    data = request.get_json()

    try:
        document = models.UserTypes(user_type=data['user_type'], active_status="active", date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.user_type, "created_at": document.date_created,
             "message": "success", })


    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("error {} in add_user_types".format(e))

        return make_response({
            "message": "Request Failed. Try Again Later!"
        }, 500)


@app.route('/add_entity_types', methods=['POST'])
def add_entity_types():
    data = request.get_json()

    try:

        document = models.EntityTypes(name=data['name'], active_status="active", date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return json.dumps(
            {"name": document.name,
             "status": document.active_status, "created_at": document.date_created,
             "message": "success", })


    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("error {} in add_entity_types".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"
        })


@app.route('/add_global_account', methods=['POST'])
def add_global_account():
    data = request.get_json()

    try:

        document = models.Global_Charts_OF_Accounts(account_type=data['account_type'],
                                                    account_classification=data['account_classification'],
                                                    total_amount=0,
                                                    global_status="active", date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.account_type,
             "classification": document.account_classification, "created_at": document.date_created,
             "message": "success", })


    except Exception as e:
        logger.error("error {} in add_global_account".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"
        })


@app.route('/create_account_type', methods=['POST'])
def create_account_type():
    data = request.get_json()

    try:

        global_account = db.session.query(models.Global_Charts_OF_Accounts) \
            .filter_by(account_type=data.get('category')) \
            .first()

        document = models.AccountTypes(
            account_name=data['name'], account_number=data['account_number'],
            available_amount=0,
            global_id=global_account.id,
            created_by=data['created_by'],
            account_type_status="active",
            date_created=datetime.now()
        )
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.account_name,
             "account_number": document.account_number, "created_at": document.date_created,
             "message": "success", })


    except Exception as e:
        logger.error("error {} in create_account_type".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"
        })


@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    data = request.get_json()

    try:

        group = db.session.query(models.Items_Inventory). \
            filter(
            and_(
                models.Items_Inventory.name == data.get('item_name'),
                models.Items_Inventory.model == data.get('item_model'),
                models.Items_Inventory.size == data.get('item_size')
            )
        ).first()
        if not group:

            document = models.Items_Inventory(
                name=data.get('item_name'),
                model=data.get('item_model'),
                size=data.get('item_size'),
                price=data.get('price'),
                inventory_status="active",
                date_created=datetime.now()

            )
            db.session.add(document)
            db.session.commit()

            return jsonify(
                {"name": document.name,
                 "price": document.price, "created_at": document.date_created,
                 "message": "success", })
        else:
            return make_response({
                "message": "Item already exists!"
            }, 409)


    except Exception as e:
        logger.error("error {} in create_account_type".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"
        })


@app.route('/add_currency', methods=['POST'])
def add_currency():
    data = request.get_json()

    try:
        document = models.Currencies(currency_name=data['currency_name'], country=data['country'],
                                     currency_status="active",
                                     date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.currency_name, "description": document.country,
             "status": str(document.currency_status), "created_at": document.date_created,
             "message": "success", })


    except Exception as e:
        logger.error("error {} in add_currency".format(e))
        return make_response({

            "message": "Request Failed. Try Again Later!"

        })


@app.route('/create_service', methods=['POST'])
# @token_required
def add_service():
    data = request.get_json()

    try:
        document = models.Services(name=data['service'], description=data['description'], service_status='active',
                                   date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"name": document.name, "description": document.description,
             "created_at": document.date_created,
             "message": "success", })

    except Exception as e:
        logger.error("error {} in add_service".format(e))
        return make_response({

            "message": "Request Failed. Try Again Later!"

        })


@app.route('/create_tariff_charge', methods=['POST'])
# @token_required
def add_tariff_charge():
    data = request.get_json()

    try:
        tariff = db.session.query(models.Services).filter_by(
            name=data['tariff']
        ).one()

        document = models.TariffCharges(min_amount=data['min_amount'], max_amount=data['max_amount'],
                                        charges=data['charges'], service_id=tariff.id, tariff_status='active',
                                        date_created=datetime.now())
        db.session.add(document)
        db.session.commit()

        return jsonify(
            {"tariff": tariff.name, "min_amount": document.min_amount,
             "max_amount": document.max_amount, "charges": document.charges, "date_created": document.date_created,
             "message": "success", })

    except Exception as e:
        logger.error("error {} in create_tariff_charge".format(e))
        return make_response({
            "message": "Request Failed. Try Again Later!"

        })