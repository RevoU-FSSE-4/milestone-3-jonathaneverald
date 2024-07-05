import re


def register_update_validation(data):
    required_fields = [
        "username",
        "email",
        "password",
    ]

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Define the email regex pattern

    for field in required_fields:
        if field not in data:
            raise Exception(
                f"Field '{field}' is not provided!"
            )  # Inform which field is not provided
        if not data[field]:
            raise Exception(
                f"Field '{field}' value is not provided!"
            )  # Inform which field value is not provided

        # Check if the email is valid
        if field == "email" and not re.match(email_regex, data[field]):
            raise Exception(
                "Invalid email address!"
            )  # Raise an exception if the email is invalid


def login_validation(data):
    required_fields = [
        "email",
        "password",
    ]

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Define the email regex pattern

    for field in required_fields:
        if field not in data:
            raise Exception(
                f"Field '{field}' is not provided!"
            )  # Inform which field is not provided
        if not data[field]:
            raise Exception(
                f"Field '{field}' value is not provided!"
            )  # Inform which field value is not provided

        # Check if the email is valid
        if field == "email" and not re.match(email_regex, data[field]):
            raise Exception(
                "Invalid email address!"
            )  # Raise an exception if the email is invalid
