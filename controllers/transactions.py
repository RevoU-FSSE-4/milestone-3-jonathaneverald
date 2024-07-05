from flask import Blueprint, request
from flasgger import swag_from

from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.accounts import AccountModel
from models.transactions import TransactionModel
from flask_login import login_required, current_user
from sqlalchemy import select, update
from validators.transactions_validator import (
    withdraw_validation,
    deposit_validation,
    transfer_validation,
)
import decimal

transaction_routes = Blueprint("transaction_routes", __name__)


@transaction_routes.route("/transactions", methods=["GET"])
@swag_from("docs/transactions/transaction_show.yml")
@login_required
def transaction_show():
    Session = sessionmaker(connection)
    s = Session()

    try:
        current_user_id = current_user.id
        # Retrieve all Account IDs for the current user
        account_query = select(AccountModel.id).where(
            AccountModel.user_id == current_user_id
        )
        account_result = s.execute(account_query)
        account_ids = [row[0] for row in account_result]
        if not account_ids:
            return {"message": "No accounts found for the current user."}, 404

        # Retrieve all Transactions for the retrieved Account IDs
        transaction_query = select(TransactionModel).where(
            (TransactionModel.from_account_id.in_(account_ids))
            | (TransactionModel.to_account_id.in_(account_ids))
        )

        result = s.execute(transaction_query)
        transactions = []
        for row in result.scalars():
            transactions.append(
                {
                    "id": row.id,
                    "from_account_id": row.from_account_id,
                    "to_account_id": row.to_account_id,
                    "amount": row.amount,
                    "type": row.type,
                    "description": row.description,
                }
            )

    except Exception as e:
        s.rollback()
        return {"message": f"Show Transactions Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Show Transactions by " + current_user.username,
        "transactions": transactions,
    }, 200


@transaction_routes.route("/transactions/<id>", methods=["GET"])
@swag_from("docs/transactions/transaction_show_by_id.yml")
@login_required
def transaction_show_by_id(id):
    Session = sessionmaker(connection)
    s = Session()

    try:
        current_user_id = current_user.id
        # Retrieve all Account IDs for the current user
        account_query = select(AccountModel.id).where(
            AccountModel.user_id == current_user_id
        )
        account_result = s.execute(account_query)
        account_ids = [row[0] for row in account_result]
        if not account_ids:
            return {"message": "No accounts found for the current user."}, 404

        # Retrieve transaction by ID
        transaction_query = select(TransactionModel).where(TransactionModel.id == id)
        transaction_result = s.execute(transaction_query).scalar_one_or_none()

        if not transaction_result:
            return {"message": "Transaction not found."}, 404

        # Checking authorization
        if (
            transaction_result.from_account_id not in account_ids
            and transaction_result.to_account_id not in account_ids
        ):
            return {"message": "You are not Authorized to view this transaction!"}, 403

        result = {
            "id": transaction_result.id,
            "from_account_id": transaction_result.from_account_id,
            "to_account_id": transaction_result.to_account_id,
            "amount": transaction_result.amount,
            "type": transaction_result.type,
            "description": transaction_result.description,
        }

    except Exception as e:
        s.rollback()
        return {"message": f"Show Transaction by ID Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Show Transaction by " + current_user.username,
        "transaction": result,
    }, 200


@transaction_routes.route("/transactions", methods=["POST"])
@swag_from("docs/transactions/transaction_create.yml")
@login_required
def transaction_create():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        data = request.form.to_dict()
        current_user_id = current_user.id

        # Retrieve input data
        type = request.form.get("type")
        amount = float(request.form.get("amount"))
        from_account_id = request.form.get("from_account_id")
        to_account_id = request.form.get("to_account_id")
        description = request.form.get("description")

        if not type or not amount:
            return {"message": "Transaction type and amount are required."}, 400

        # Ensure the amount is positive
        amount = decimal.Decimal(amount)
        if amount <= 0:
            return {"message": "Transaction amount must be positive."}, 400

        # Validate account ownership
        account_query = select(AccountModel.id, AccountModel.balance).where(
            AccountModel.user_id == current_user_id
        )
        account_result = s.execute(account_query)
        user_accounts = {row[0]: row[1] for row in account_result}

        # Check ownership and handle transaction types
        if type == "Withdraw":
            withdraw_validation(data)
            if not from_account_id or int(from_account_id) not in user_accounts:
                return {
                    "message": "Invalid from_account_id or account does not belong to the user."
                }, 403

            if user_accounts[int(from_account_id)] < amount:
                return {"message": "Insufficient funds for withdrawal."}, 400

            # Update balance
            new_balance = user_accounts[int(from_account_id)] - amount
            s.execute(
                update(AccountModel)
                .where(AccountModel.id == int(from_account_id))
                .values(balance=new_balance)
            )

        elif type == "Deposit":
            deposit_validation(data)
            if not to_account_id or int(to_account_id) not in user_accounts:
                return {
                    "message": "Invalid to_account_id or account does not belong to the user."
                }, 403

            # Update balance
            new_balance = user_accounts[int(to_account_id)] + amount
            s.execute(
                update(AccountModel)
                .where(AccountModel.id == int(to_account_id))
                .values(balance=new_balance)
            )

        elif type == "Transfer":
            transfer_validation(data)
            if (
                not from_account_id
                or not to_account_id
                or int(from_account_id) not in user_accounts
                or int(to_account_id) not in user_accounts
            ):
                return {
                    "message": "Invalid from_account_id or to_account_id, or accounts do not belong to the user."
                }, 403

            if user_accounts[int(from_account_id)] < amount:
                return {"message": "Insufficient funds for transfer."}, 400

            # Update balances
            new_from_balance = user_accounts[int(from_account_id)] - amount
            new_to_balance = user_accounts[int(to_account_id)] + amount
            s.execute(
                update(AccountModel)
                .where(AccountModel.id == int(from_account_id))
                .values(balance=new_from_balance)
            )
            s.execute(
                update(AccountModel)
                .where(AccountModel.id == int(to_account_id))
                .values(balance=new_to_balance)
            )
        else:
            return {
                "message": "Invalid transaction type. Must be 'Withdraw', 'Deposit', or 'Transfer'."
            }, 400

        new_transaction = TransactionModel(
            from_account_id=from_account_id if from_account_id else None,
            to_account_id=to_account_id if to_account_id else None,
            amount=amount,
            type=type,
            description=description,
        )
        s.add(new_transaction)
        s.commit()

    except Exception as e:
        s.rollback()
        return {"message": f"Create Transaction Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {"message": "Create Transaction Success!"}, 200
