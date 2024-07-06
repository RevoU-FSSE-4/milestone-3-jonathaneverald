from flask import Blueprint, request
from flasgger import swag_from

from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.accounts import AccountModel
from flask_login import login_required, current_user
from sqlalchemy import select
from validators.accounts_validator import (
    create_account_validation,
    update_account_validation,
)

account_routes = Blueprint("account_routes", __name__)


@account_routes.route("/accounts", methods=["GET"])
@login_required
@swag_from("docs/accounts/account_show.yml")
def account_show():
    Session = sessionmaker(connection)
    s = Session()

    try:
        account_query = select(AccountModel)
        current_user_id = current_user.id
        account_query = account_query.where(AccountModel.user_id == current_user_id)

        search_keyword = request.args.get("query")
        if search_keyword != None:
            account_query = account_query.where(
                AccountModel.account_type.like(f"%{search_keyword}%")
            )

        result = s.execute(account_query)
        accounts = []
        for row in result.scalars():
            accounts.append(
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "account_type": row.account_type,
                    "account_number": row.account_number,
                    "balance": row.balance,
                }
            )
    except Exception as e:
        s.rollback()
        return {"message": f"Show Accounts Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Show Accounts by " + current_user.username,
        "accounts": accounts,
    }, 200


@account_routes.route("/accounts/<id>", methods=["GET"])
@login_required
@swag_from("docs/accounts/account_show_by_id.yml")
def account_show_by_id(id):
    Session = sessionmaker(connection)
    s = Session()

    try:
        account_query = s.query(AccountModel).filter(AccountModel.id == id).first()
        if account_query is None:
            return {"message": "Account not found!"}, 404

        current_user_id = current_user.id
        if account_query.user_id != current_user_id:
            return {"message": "You are not authorized to view this account!"}, 403

        result = {
            "id": account_query.id,
            "user_id": account_query.user_id,
            "account_type": account_query.account_type,
            "account_number": account_query.account_number,
            "balance": account_query.balance,
        }
    except Exception as e:
        s.rollback()
        return {"message": f"Show Account by ID Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Show Account by " + current_user.username,
        "account": result,
    }, 200


@account_routes.route("/accounts", methods=["POST"])
@login_required
@swag_from("docs/accounts/account_create.yml")
def account_create():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        data = request.form.to_dict()
        create_account_validation(data)

        # Check if the account number already exists
        existing_account = (
            s.query(AccountModel)
            .filter(AccountModel.account_number == request.form["account_number"])
            .first()
        )
        if existing_account:
            return {
                "message": "Account Number already exists!"
            }, 400  # Return a 400 status code for client error

        new_account = AccountModel(
            user_id=current_user.id,
            account_type=request.form["account_type"],
            account_number=request.form["account_number"],
            balance=request.form["balance"],
        )
        s.add(new_account)
        s.commit()

    except Exception as e:
        s.rollback()
        return {"message": f"Create Account Failed! {str(e)}"}, 500
    finally:
        s.close()

    return {"message": "Create Account Success!"}, 200


@account_routes.route("/accounts/<id>", methods=["PUT"])
@login_required
@swag_from("docs/accounts/account_update.yml")
def account_update(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    try:
        data = request.form.to_dict()
        update_account_validation(data)

        account = s.query(AccountModel).filter(AccountModel.id == id).first()
        if account is None:
            return {"message": "Account not found"}, 404

        current_user_id = current_user.id
        if account.user_id != current_user_id:
            return {"message": "You are not authorized to update this account!"}, 403

        account.account_type = request.form["account_type"]
        s.commit()

        result = {
            "id": account.id,
            "user_id": account.user_id,
            "account_type": account.account_type,
            "account_number": account.account_number,
            "balance": account.balance,
        }
    except Exception as e:
        s.rollback()
        return {"message": f"Failed to Update Account! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Update Account by " + current_user.username,
        "updated_account": result,
    }, 200


@account_routes.route("/accounts/<id>", methods=["DELETE"])
@login_required
@swag_from("docs/accounts/account_delete.yml")
def account_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    try:
        account = s.query(AccountModel).filter(AccountModel.id == id).first()
        if account is None:
            return {"message": "Account not found"}, 404

        current_user_id = current_user.id
        if account.user_id != current_user_id:
            return {"message": "You are not authorized to delete this account!"}, 403

        s.delete(account)
        result = {
            "id": account.id,
            "user_id": account.user_id,
            "account_type": account.account_type,
            "account_number": account.account_number,
            "balance": account.balance,
        }
        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": f"Failed to Delete Account! {str(e)}"}, 500
    finally:
        s.close()

    return {
        "message": "Success Delete Account by " + current_user.username,
        "deleted_account": result,
    }, 200
