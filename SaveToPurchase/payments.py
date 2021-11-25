from flask import request, jsonify, make_response
from datetime import datetime

from sqlalchemy import and_

from config import logger, c2b_utility_name, c2b_utility_account_number
from . import app, db, models, save_to_purchase
from .decorators import token_required


@app.route('/deposits', methods=['POST'])
@token_required
def deposit(current_user):
    data = request.get_json()
    logger.info("deposit request {}".format(data))
    try:

        entity_user = db.session.query(models.Entity_Users) \
            .filter_by(user_name=data['msisdn']) \
            .first()

        if entity_user:

            user_kyc = db.session.query(models.Entity_Kyc) \
                .filter_by(entity_owner_id=entity_user.entity_id) \
                .first()

            group = db.session.query(models.Items_Inventory). \
                filter(
                and_(
                    models.Items_Inventory.name == data.get('item_name'),
                    models.Items_Inventory.model == data.get('item_model'),
                    models.Items_Inventory.size == data.get('item_size')
                )
            ).first()

            if group:

                # check if user is paying for an existing item

                reference_number = save_to_purchase.get_random_string(8)
                # token = save_to_purchase.sam_token()

                # nilipie.make_deposit(msisdn=data['msisdn'], amount=str(data['amount']), account=data.get('entity_acc_number'),
                #                      token=token,
                #                      reference=reference_number)

                stk_request = models.STK_Results(
                    transaction_id=None,
                    msisdn=data['msisdn'],
                    amount=str(data['amount']),
                    account=data.get('entity_acc_number'),
                    item_inventory_id=group.id,
                    name=None,
                    description=None, reference=reference_number, status=None,
                    stk_status="unprocessed", created_at=datetime.now()
                )

                db.session.add(stk_request)
                db.session.commit()

                save_to_purchase.process_stk_results(
                    transaction_id="PJ{}".format(stk_request.reference),
                    name=user_kyc.first_name,
                    reference=stk_request.reference
                )
                logger.info("deposit request {}".format({
                    "message": "Stk sent successful"
                }))
                return jsonify({
                    "message": "Stk sent successful"
                })
            else:
                return make_response({
                    "message": "Product Not found"
                }, 405)
        else:
            return make_response({
                "message": "User does not exist!"
            }, 409)
    except Exception as e:
        logger.error('deposit error: {} as {} tried to make a deposit'.format(str(e), data['msisdn']))

        return make_response({
            "message": "Transaction Failed. Try again Later"
        }, 500)


@app.route('/stk_deposits', methods=['POST'])
def receive_stk_results():
    data = request.json
    logger.info("receive_stk_results {}".format(data))
    try:

        user = db.session.query(models.STK_Results) \
            .filter_by(reference=data['reference']) \
            .first()

        if data['status'] == "success":
            user.transaction_id = data['transaction_id'],
            user.name = data['name']
            user.description = data['description']
            user.status = data['status']

            master_trans_id = save_to_purchase.generate_master_id(12)

            entity_user = db.session.query(models.Entity_Users) \
                .filter_by(user_name=user.msisdn) \
                .first()

            if entity_user:
                account = db.session.query(models.Entity_Account).filter(
                    and_(
                        models.Entity_Account.entity_id == entity_user.entity_id,

                        models.Entity_Account.description == "1"
                    )).first()

                depositing_account = db.session.query(models.AccountTypes).filter(
                    and_(
                        models.AccountTypes.account_name == c2b_utility_name,

                        models.AccountTypes.account_number == c2b_utility_account_number
                    )).first()

                global_account = db.session.query(models.Global_Charts_OF_Accounts) \
                    .get(depositing_account.global_id)

                account_type = db.session.query(models.AccountTypes) \
                    .get(account.accounts_type_id)

                global_account2 = db.session.query(models.Global_Charts_OF_Accounts) \
                    .get(account_type.global_id)

                service = db.session.query(models.Services) \
                    .filter_by(name="till_deposit") \
                    .first()

                nilipie_service_tariff = db.session.query(models.TariffCharges).filter(
                    and_(
                        service.id == models.TariffCharges.service_id,

                        float(user.amount) >= models.TariffCharges.min_amount,
                        float(user.amount) <= models.TariffCharges.max_amount
                    )).first()

                tariff_incurred = nilipie_service_tariff.charges * float(user.amount)

                transaction_expense = db.session.query(models.AccountTypes).filter(
                    and_(
                        models.AccountTypes.account_name == "transaction_charges_expense",

                        models.AccountTypes.account_number == "1550021"
                    )).first()

                global_account3 = db.session.query(models.Global_Charts_OF_Accounts) \
                    .get(transaction_expense.global_id)

                payable_transaction_charge = db.session.query(models.AccountTypes).filter(
                    and_(
                        models.AccountTypes.account_name == "payable_transaction_charges",

                        models.AccountTypes.account_number == "200567512"
                    )).first()

                bulk_sms_expense_account = db.session.query(models.AccountTypes).filter(
                    and_(
                        models.AccountTypes.account_name == "bulk_sms_expenses",

                        models.AccountTypes.account_number == "100629281"
                    )).first()

                bulk_sms_expense_global = db.session.query(models.Global_Charts_OF_Accounts) \
                    .get(bulk_sms_expense_account.global_id)

                bulk_sms_inventory_account = db.session.query(models.AccountTypes).filter(
                    and_(
                        models.AccountTypes.account_name == "mobipesa_bulksms",

                        models.AccountTypes.account_number == "2456854"
                    )).first()

                bulk_sms_inventory_global = db.session.query(models.Global_Charts_OF_Accounts) \
                    .get(bulk_sms_inventory_account.global_id)

                transaction_id = save_to_purchase.get_random_string(16)
                transaction_id2 = save_to_purchase.get_random_string(16)
                transaction_id3 = save_to_purchase.get_random_string(16)
                transaction_id5 = save_to_purchase.get_random_string(16)

                # debit bank account

                print(user.transaction_id)
                nilipie_transactions = models.Transactions(master_transaction_id=master_trans_id,
                                                           transaction_id=transaction_id,
                                                           account_number=depositing_account.account_number,
                                                           service_id=service.id,

                                                           description="Receive Deposit From Customer"
                                                                       " {} Transaction ID {}".format(
                                                               user.msisdn,
                                                               data['transaction_id']),
                                                           debit=user.amount,
                                                           credit=0,
                                                           bal_before=depositing_account.available_amount,
                                                           bal_after=depositing_account.available_amount + float(
                                                               user.amount),
                                                           transaction_status='active', date_created=datetime.now())

                db.session.add(nilipie_transactions)

                depositing_account.available_amount = depositing_account.available_amount + float(
                    user.amount)
                db.session.merge(depositing_account)

                global_account.total_amount = global_account.total_amount + float(user.amount)
                db.session.merge(global_account)

                transactions = models.Transactions(master_transaction_id=master_trans_id,
                                                   transaction_id=transaction_id,
                                                   account_number=account.account_number,
                                                   service_id=service.id,

                                                   description="Deposit from Mpesa to Davis.",
                                                   debit=0,
                                                   credit=user.amount,
                                                   bal_before=account.available_balance,
                                                   bal_after=account.available_balance + float(
                                                       user.amount),
                                                   transaction_status='active', date_created=datetime.now())

                db.session.add(transactions)

                account.available_balance = account.available_balance + float(user.amount)
                account_type.available_amount = account_type.available_amount + float(user.amount)

                global_account2.total_amount = global_account2.total_amount + float(user.amount)
                db.session.merge(account)
                db.session.merge(account_type)
                db.session.merge(global_account2)

                # transaction charges

                # debit expense

                transaction_charge = models.Transactions(
                    master_transaction_id=master_trans_id,
                    transaction_id=transaction_id2,
                    account_number="1550021",
                    service_id=service.id,

                    description="Transaction Charge expense to Financial Institution "
                                "with Transaction ID {} ".format(data['transaction_id']),
                    debit=tariff_incurred,
                    credit=0, bal_before=transaction_expense.available_amount,
                    bal_after=transaction_expense.available_amount + tariff_incurred,
                    transaction_status='active',
                    date_created=datetime.now())

                db.session.add(transaction_charge)
                transaction_expense.available_amount = transaction_charge.bal_after
                db.session.merge(transaction_expense)
                global_account3.total_amount = global_account3.total_amount - tariff_incurred
                db.session.merge(global_account3)

                # credit payable

                fs_transaction_charge = models.Transactions(
                    master_transaction_id=master_trans_id,
                    transaction_id=transaction_id2,
                    account_number="200567512",
                    service_id=service.id,

                    description="Credit Transaction Charge Payable to "
                                "Financial Institution  with Transaction ID {}".format(
                        data['transaction_id']),
                    debit=0,
                    credit=tariff_incurred,
                    bal_before=payable_transaction_charge.available_amount,
                    bal_after=payable_transaction_charge.available_amount + tariff_incurred,
                    transaction_status='active',
                    date_created=datetime.now())

                db.session.add(fs_transaction_charge)
                payable_transaction_charge.available_amount = fs_transaction_charge.bal_after
                db.session.merge(payable_transaction_charge)

                # debit payable

                fs_transaction_charge_pay = models.Transactions(
                    master_transaction_id=master_trans_id,
                    transaction_id=transaction_id3,
                    account_number="200567512",
                    service_id=service.id,

                    description="Pay Transaction charge to Financial "
                                "Institution Transaction ID {}".format(data['transaction_id']),
                    debit=-tariff_incurred,
                    credit=0, bal_before=payable_transaction_charge.available_amount,
                    bal_after=payable_transaction_charge.available_amount - tariff_incurred,
                    transaction_status='active',
                    date_created=datetime.now())

                db.session.add(fs_transaction_charge_pay)
                payable_transaction_charge.available_amount = fs_transaction_charge_pay.bal_after
                db.session.merge(payable_transaction_charge)

                # credit fs

                credit_fs_account = models.Transactions(
                    master_transaction_id=master_trans_id,
                    transaction_id=transaction_id3,
                    account_number=depositing_account.account_number,
                    service_id=service.id,

                    description="Transaction Charge incurred to "
                                "financial institution Transaction ID {} "
                                "MSISDN depositing {}".format(data['transaction_id'],
                                                              user.msisdn),
                    debit=0,
                    credit=-tariff_incurred, bal_before=depositing_account.available_amount,
                    bal_after=depositing_account.available_amount - tariff_incurred,
                    transaction_status='active',
                    date_created=datetime.now())

                db.session.add(credit_fs_account)
                depositing_account.available_amount = credit_fs_account.bal_after
                db.session.merge(depositing_account)

                global_account.total_amount = global_account.total_amount - tariff_incurred
                db.session.merge(global_account)

                # # notification charge
                #
                # notification_expense = models.Transactions(master_transaction_id=master_trans_id,
                #                                            transaction_id=transaction_id5,
                #                                            account_number="100629281",
                #                                            service_id=service.id,
                #                                            description="Notification Expense to MSISDN {} "
                #                                                        "and Transaction ID {}".format(
                #                                                user.msisdn,
                #                                                user.transaction_id),
                #                                            debit=0.12,
                #                                            credit=0,
                #                                            bal_before=bulk_sms_expense_account.available_amount,
                #                                            bal_after=bulk_sms_expense_account.available_amount + 0.12,
                #                                            transaction_status='active',
                #                                            date_created=datetime.now())
                # db.session.add(notification_expense)
                # bulk_sms_expense_account.available_amount = notification_expense.bal_after
                # db.session.merge(bulk_sms_expense_account)
                #
                # bulk_sms_expense_global.total_amount = bulk_sms_expense_global.total_amount - 0.12
                # db.session.merge(bulk_sms_expense_global)
                #
                # # credit bulk sms inventory
                #
                # credit_bulk_sms = models.Transactions(master_transaction_id=master_trans_id,
                #                                       transaction_id=transaction_id5,
                #                                       account_number="2456854",
                #                                       service_id=service.id,
                #
                #                                       description="Credit Bulk Sms sent to {} "
                #                                                   "Transaction ID {}".format(
                #                                           user.msisdn,
                #                                           user.transaction_id),
                #                                       debit=0,
                #                                       credit=-0.12,
                #                                       bal_before=bulk_sms_inventory_account.available_amount,
                #                                       bal_after=bulk_sms_inventory_account.available_amount - 0.12,
                #                                       transaction_status='active',
                #                                       date_created=datetime.now())
                # db.session.add(credit_bulk_sms)
                #
                # bulk_sms_inventory_account.available_amount = credit_bulk_sms.bal_after
                # db.session.merge(bulk_sms_inventory_account)
                #
                # bulk_sms_inventory_global.total_amount = bulk_sms_inventory_global.total_amount - 0.12
                # db.session.merge(bulk_sms_inventory_global)

                user.status = "processed"

                db.session.flush()

                # check if its an existing

                group = db.session.query(models.Items_Selected). \
                    filter(
                    and_(
                        models.Items_Selected.entity_user_id == entity_user.id,
                        models.Items_Selected.inventory_id == user.item_inventory_id,

                    )
                ).first()

                if group:

                    user_item = db.session.query(models.Items_Inventory).get(user.item_inventory_id)

                    if float(user.amount) + group.savings_made >= group.price:
                        group.savings_made = group.price

                        group.payment_status = "completed"
                        group.end_date = datetime.now()

                        db.session.flush()
                        db.session.commit()

                        # nofity user payment is complete

                        save_to_purchase.sendMessage(
                            phone_number=user.msisdn,
                            text="{} CONFIRMED.\nYou have deposited Ksh. {:,.2f} to Davis and Shirtliff "
                                 "For Purchase of {} Model {}.\nYou have reached your target of Ksh. {:,.2f}.\n"
                                 "Your payment is complete\n"
                                 "You can now collect your Item at one of our stores"
                                .format(master_trans_id,
                                        float(user.amount),
                                        user_item.name,
                                        user_item.model,
                                        user_item.price
                                        )
                        )
                    else:

                        group.savings_made = models.Items_Selected.savings_made + user.amount

                        db.session.flush()
                        db.session.commit()

                        # notify user of payment and remaining amount
                        pending_bal = group.price - group.savings_made

                        save_to_purchase.sendMessage(
                            phone_number=user.msisdn,
                            text="{} CONFIRMED.\nYou have deposited Ksh. {:,.2f} to Davis and Shirtliff "
                                 "For Purchase of {} Model {}.\nYour Pending Balance is Ksh. {:,.2f}.\n"
                                 "Your Wallet Balance is Ksh. {:,.2f}".format(master_trans_id,
                                                                              float(user.amount),
                                                                              user_item.name,
                                                                              user_item.model,
                                                                              pending_bal,
                                                                              account.available_balance
                                                                              )
                        )

                else:

                    user_item = db.session.query(models.Items_Inventory).get(user.item_inventory_id)

                    if float(user.amount) >= user_item.price:

                        selected_item = models.Items_Selected(
                            entity_account_id=account.id,
                            entity_user_id=entity_user.id,
                            inventory_id=user.item_inventory_id,
                            price=user_item.price,
                            savings_made=user_item.price,
                            payment_status="completed",
                            date_created=datetime.now(),
                            end_date=datetime.now()

                        )

                        db.session.add(selected_item)
                        db.session.commit()

                        # notify user

                        save_to_purchase.sendMessage(
                            phone_number=user.msisdn,
                            text="{} CONFIRMED.\nYou have deposited Ksh. {:,.2f} to Davis and Shirtliff "
                                 "For Purchase of {} Model {}.\nYou have reached your target of Ksh. {:,.2f}.\n"
                                 "Your payment is complete\n"
                                 "You can now collect your Item at one of our stores"
                                .format(master_trans_id,
                                        float(user.amount),
                                        user_item.name,
                                        user_item.model,
                                        user_item.price))


                    else:
                        selected_item = models.Items_Selected(
                            entity_account_id=account.id,
                            entity_user_id=entity_user.id,
                            inventory_id=user.item_inventory_id,
                            price=user_item.price,
                            savings_made=float(user.amount),
                            payment_status="inprogress",
                            date_created=datetime.now()

                        )

                        db.session.add(selected_item)
                        db.session.commit()


                        # nofity user

                        pending_bal = user_item.price - float(user.amount)

                        save_to_purchase.sendMessage(
                            phone_number=user.msisdn,
                            text="{} CONFIRMED.\nYou have deposited Ksh. {:,.2f} to Davis and Shirtliff "
                                 "For Purchase of {} Model {}.\nYour Pending Balance is Ksh. {:,.2f}.\n"
                                 "Your Wallet Balance is Ksh. {:,.2f}".format(master_trans_id,
                                                                              float(user.amount),
                                                                              user_item.name,
                                                                              user_item.model,
                                                                              pending_bal,
                                                                              account.available_balance
                                                                              ))

                # phone_number = user.msisdn
                # text = texts['wallet_update_success'][entity_user.language.name].format(master_trans_id,
                #                                                                         float(
                #                                                                             process_nilipie_deposits.amount),
                #                                                                         current_date,
                #                                                                         current_time,
                #
                #                                                                         float(
                #                                                                             account.available_balance))
                #
                # nilipie.send_nilipie_message(phone_number, text)

                logger.info("process_verified_deposits response {}".format(
                    {"transactions_id": transactions.transaction_id, "description": transactions.description,
                     "amount_deposited": user.amount, "current_balance": account.available_balance,
                     "created_at": transactions.date_created,
                     "message": "success", }))
                return jsonify(
                    {"transactions_id": transactions.transaction_id, "description": transactions.description,
                     "amount_deposited": user.amount, "current_balance": account.available_balance,
                     "created_at": transactions.date_created,
                     "message": "success", })



        else:
            user.transaction_id = data['transaction_id'],
            user.name = data['name']
            user.status = data['status']

            db.session.merge(user)
            db.session.commit()

        logger.info("receive_stk_results {}".format({
            "message": "Transaction was a success"}
        ))

        return jsonify({
            "message": "Transaction was a success"
        })
    except Exception as e:
        logger.error('deposit error: {}'.format(str(e)))
        logger.error(e, exc_info=True)

        return make_response({
            "message": "Transaction Failed. Try again Later"
        }, 500)
