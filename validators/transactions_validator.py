def withdraw_validation(data):
    required_fields = [
        "type",
        "from_account_id",
        "amount",
        "description",
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


def deposit_validation(data):
    required_fields = [
        "type",
        "to_account_id",
        "amount",
        "description",
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


def transfer_validation(data):
    required_fields = [
        "type",
        "from_account_id",
        "to_account_id",
        "amount",
        "description",
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
