def create_account_validation(data):
    required_fields = [
        "account_type",
        "account_number",
        "balance",
    ]

    for field in required_fields:
        if field not in data:
            raise Exception(
                f"Field '{field}' is not provided!"
            )  # Inform which field is not provided
        if not data[field]:
            raise Exception(
                f"Field '{field}' value is not provided!"
            )  # Inform which field value is not provided


def update_account_validation(data):
    required_fields = [
        "account_type",
    ]

    for field in required_fields:
        if field not in data:
            raise Exception(
                f"Field '{field}' is not provided!"
            )  # Inform which field is not provided
        if not data[field]:
            raise Exception(
                f"Field '{field}' value is not provided!"
            )  # Inform which field value is not provided
