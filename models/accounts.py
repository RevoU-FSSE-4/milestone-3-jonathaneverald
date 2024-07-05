from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class AccountModel(db.Model):
    __tablename__ = "accounts"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    account_type = mapped_column(String(255))
    account_number = mapped_column(String(255), unique=True)
    balance = mapped_column(Numeric(10, 2))
    created_at = mapped_column(DateTime, default=gmt_plus_7_now)
    updated_at = mapped_column(
        DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now
    )
    # user = relationship("UserModel", back_populates="accounts")
    # transactions = relationship("TransactionModel", back_populates="account")

    transactions_from_account = db.relationship(
        "TransactionModel",
        foreign_keys="TransactionModel.from_account_id",
        # backref="from_account",
        back_populates="from_account",
        lazy=True,
    )
    transactions_to_account = db.relationship(
        "TransactionModel",
        foreign_keys="TransactionModel.to_account_id",
        # backref="to_account",
        back_populates="to_account",
        lazy=True,
    )

    def to_dictionaries(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_type": self.account_type,
            "account_number": self.account_number,
            "balance": self.balance,
        }
