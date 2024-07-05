from flask import Blueprint, request, jsonify

from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.users import UserModel
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from validators.users_validator import register_update_validation, login_validation
from flasgger import swag_from

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/register", methods=["POST"])
@swag_from("docs/users/user_register.yml")
def user_register():
    Session = sessionmaker(bind=connection)
    s = Session()

    s.begin()
    try:
        data = (
            request.form.to_dict()
        )  # Convert ImmutableMultiDict to a regular dictionary
        register_update_validation(data)  # Validate the input data

        # Check if the username or email already exists
        existing_user = (
            s.query(UserModel)
            .filter(
                (UserModel.username == request.form["username"])
                | (UserModel.email == request.form["email"])
            )
            .first()
        )

        if existing_user:
            return (
                jsonify({"message": "Username or Email already exists!"}),
                400,
            )  # Return a 400 status code for client error

        new_user = UserModel(
            username=request.form["username"],
            email=request.form["email"],
        )

        new_user.set_password(request.form["password"])

        s.add(new_user)
        s.commit()
    except Exception as e:
        s.rollback()
        return jsonify({"message": f"Register Failed! {str(e)}"}), 500
    finally:
        s.close()

    return jsonify({"message": "Register Success!"}), 200


@user_routes.route("/login", methods=["POST"])
@swag_from("docs/users/user_login.yml")
def user_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        data = request.form.to_dict()
        login_validation(data)

        email = request.form["email"]
        user = s.query(UserModel).filter(UserModel.email == email).first()

        if user == None:
            return jsonify({"message": "User not found"}), 403

        if not user.check_password(request.form["password"]):
            return jsonify({"message": "Invalid password"}), 403

        # Proceed to login
        login_user(user)

        # Get Session ID
        session_id = request.cookies.get("session")

        return jsonify({"session_id": session_id, "message": "Login Success"}), 200

    except Exception as e:
        s.rollback()
        return jsonify({"message": f"Login Failed! {str(e)}"}), 500
    finally:
        s.close()


@user_routes.route("/users/me", methods=["GET"])
@swag_from("docs/users/user_profile.yml")
@login_required
def user_profile():
    user_profile = current_user.email
    Session = sessionmaker(connection)
    s = Session()

    try:
        user = s.query(UserModel).filter(UserModel.email == user_profile).first()
        if user is None:
            return jsonify({"message": "User not found!"}), 404

        result = {"id": user.id, "username": user.username, "email": user.email}

    except Exception as e:
        s.rollback()
        return {"message": f"Failed to Show Profile! {str(e)}"}, 500
    finally:
        s.close()

    return (
        jsonify(
            {
                "message": "Success Show Profile by " + current_user.username,
                "profile": result,
            }
        ),
        200,
    )


@user_routes.route("/users/me", methods=["PUT"])
@swag_from("docs/users/user_update_profile.yml")
@login_required
def user_update_profile():
    user_profile = current_user.email
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        data = request.form.to_dict()
        register_update_validation(data)

        user = s.query(UserModel).filter(UserModel.email == user_profile).first()
        if user is None:
            return jsonify({"message": "User not found!"}), 404

        # Check if the username or email already exists
        existing_user = (
            s.query(UserModel)
            .filter(
                (UserModel.username == request.form["username"])
                | (UserModel.email == request.form["email"])
            )
            .first()
        )
        if existing_user:
            return (
                jsonify({"message": "Username or Email already exists!"}),
                400,
            )  # Return a 400 status code for client error

        user.username = request.form["username"]
        user.email = request.form["email"]
        user.set_password(request.form["password"])
        s.commit()

        result = {"id": user.id, "username": user.username, "email": user.email}

    except Exception as e:
        s.rollback()
        return jsonify({"message": f"Failed to Update Profile! {str(e)}"}), 500
    finally:
        s.close()

    return (
        jsonify(
            {
                "message": "Success Update Profile by " + current_user.username,
                "updated_profile": result,
            }
        ),
        200,
    )


@user_routes.route("/logout", methods=["GET"])
@swag_from("docs/users/user_logout.yml")
@login_required
def user_logout():
    logout_user()
    return jsonify({"message": "Success logout"})
