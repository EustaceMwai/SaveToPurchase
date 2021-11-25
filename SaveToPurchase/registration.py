import json

from flask import Blueprint, jsonify, request, make_response, Response, flash

from datetime import datetime, timedelta
from sqlalchemy import exc, and_
import jwt

from config import logger, SECRET_KEY
from . import (

    models,
    app,
    db,

    bcrypt, save_to_purchase,

)


@app.route('/register', methods=['POST'])
def registration():
    data = request.get_json()
    logger.info("registration request{}".format(data))

    try:
        if data.get('msisdn').isdigit() and len(data.get('msisdn')) == 12:

            member = db.session.query(models.Entity_Users) \
                .filter_by(user_name=data['msisdn']) \
                .first()
            if not member:

                phone_number = data['msisdn']

                account_no = save_to_purchase.generate_random_spending()
                account_no2 = save_to_purchase.generate_random_savings()

                password = data.get('password')
                entity_type = db.session.query(models.EntityTypes) \
                    .filter_by(name=data['entity_type']) \
                    .first()
                entity = models.Entity(name=data['first_name'], entity_type=entity_type.id, entity_status="active",
                                       date_created=datetime.now())
                db.session.add(entity)

                db.session.flush()

                entity_user = models.Entity_Users(user_name=data['msisdn'],
                                                  password=bcrypt.generate_password_hash(password),
                                                  entity_id=entity.id, user_type_id=2, user_status="active",
                                                  language=data['language'],
                                                  date_created=datetime.now())
                db.session.add(entity_user)
                db.session.flush()

                document_type = db.session.query(models.Document_Types) \
                    .filter_by(name=data['document_type']) \
                    .first()

                entity_kyc = models.Entity_Kyc(first_name=data['first_name'], other_names=data['other_names'],
                                               description=data['description'], document_id=document_type.id,
                                               document_number=data['document_number'], active_status="active",
                                               entity_owner_id=entity.id,
                                               country="KE",

                                               date_created=datetime.now())

                db.session.add(entity_kyc)
                db.session.flush()

                # entity_kyc_location = models.Kyc_Location(kyc_id=entity_kyc.id, residential_address=data['address'],
                #                                           state=data['city'], kyc_status="active",
                #                                           date_created=datetime.now())
                #
                # db.session.add(entity_kyc_location)
                currency = db.session.query(models.Currencies) \
                    .filter_by(currency_name=data['currency']) \
                    .first()

                account_type = db.session.query(models.AccountTypes) \
                    .filter_by(account_name="customer_wallets") \
                    .first()

                spending_account = models.Entity_Account(description="spending",
                                                         account_number=account_no, available_balance=0,
                                                         accounts_type_id=account_type.id,
                                                         currency_id=currency.id, entity_id=entity.id,
                                                         active_status="active",
                                                         date_created=datetime.now())
                db.session.add(spending_account)
                savings_account = models.Entity_Account(description="savings",
                                                        account_number=account_no2, available_balance=0,
                                                        accounts_type_id=account_type.id,
                                                        currency_id=currency.id, entity_id=entity.id,
                                                        active_status="active",
                                                        date_created=datetime.now())
                db.session.add(savings_account)

                token = jwt.encode({'id': entity_user.id, 'exp': datetime.utcnow() + timedelta(hours=12)},
                                   SECRET_KEY)

                db.session.commit()

                logger.info("Registration success for {}".format(phone_number))

                logger.info("ussd_register response {}".format({"name": entity.name,
                                                                "other names": entity_kyc.other_names,
                                                                "created_at": entity_kyc.date_created,
                                                                "message": "success", 'token': token.decode('UTF-8')}))

                return jsonify(
                    {"name": entity.name,
                     "other names": entity_kyc.other_names, "created_at": entity_kyc.date_created,
                     "message": "success", 'token': token.decode('UTF-8')})

            else:
                logger.info("ussd_register {}".format({
                    'User already exists. Please Log in.'
                }))
                return make_response('User already exists. Please Log in.', 202)
        else:
            return make_response(
                {
                    "message": "Invalid PhoneNumber"
                }, 401
            )

    except Exception as e:
        logger.info(e, exc_info=True)
        logger.info("error {} occurred username {} during registration".format(e, data.get('username')))

        return make_response({
            "message": "Registration Failed!. Try again Later"
        }, 500)

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    logger.info("login {}".format(auth))

    try:

        logger.info("{} attempt to login".format(auth.get('username')))

        if not auth or not auth.get('username') or not auth.get('password'):
            logger.info("login {}".format('Why Could not verify',
                                          401,
                                          {'WWW-Authenticate': 'Basic realm ="Login required !!"'}))
            return make_response(
                'Why Could not verify',
                401,
                {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
            )

        user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=auth.get('username')) \
            .first()

        if not user:
            # returns 401 if user does not exist
            logger.info("login {}".format('USER DOES NOT EXIST',
                                          403,
                                          {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}))
            return make_response(
                'USER DOES NOT EXIST',
                403,
                {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
            )

        if bcrypt.check_password_hash(user.password, auth.get('password')):

            user_kyc = db.session.query(models.Entity_Kyc) \
                .filter_by(entity_owner_id=user.entity_id) \
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


            # generates the JWT Token
            token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(hours=12)},
                               app.config['SECRET_KEY'])


            logger.info("{} login successful".format(auth.get('username')))

            logger.info("login {}".format({'token': token.decode('UTF-8'),
                                          'id': user.id,

                                          'entity_id': user.entity_id,
                                          'username': user.user_name,
                                          'first_name': user_kyc.first_name,
                                          'other_names': user_kyc.other_names,
                                          'description': user_kyc.description,
                                          'document_number': user_kyc.document_number,
                                          'spending_account_number': spending_account.account_number,
                                          'spending_current_balance': spending_account.available_balance,
                                          'savings_account_number': savings_account.account_number,
                                          'savings_current_balance': savings_account.available_balance
                                          }))

            return make_response(jsonify({'token': token.decode('UTF-8'),
                                          'id': user.id,

                                          'entity_id': user.entity_id,
                                          'username': user.user_name,
                                          'first_name': user_kyc.first_name,
                                          'other_names': user_kyc.other_names,
                                          'description': user_kyc.description,
                                          'document_number': user_kyc.document_number,
                                          'spending_account_number': spending_account.account_number,
                                          'spending_current_balance': spending_account.available_balance,
                                          'savings_account_number': savings_account.account_number,
                                          'savings_current_balance': savings_account.available_balance
                                          }), 201)


            # returns 403 if password is wrong
        logger.info("{} login failed".format(auth.get('username')))
        logger.info("login {}".format('Invalid Login',
                                      409,
                                      {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}))
        return make_response(
            'Invalid Login',
            409,
            {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
        )

    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info("error {} occurred username {}".format(e, auth.get('username')))
        return make_response(
            {
                "message": "Login Failed. Try Again Later"
            }, 500

        )
