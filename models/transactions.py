from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class TransactionModel(db.Model):
    __tablename__ = "transactions"

    id = mapped_column(Integer, primary_key=True)
    from_account_id = mapped_column(Integer, ForeignKey("accounts.id"), nullable=True)
    to_account_id = mapped_column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = mapped_column(Numeric(10, 2))
    type = mapped_column(String(255))
    description = mapped_column(String(255))
    created_at = mapped_column(DateTime, default=gmt_plus_7_now)

    from_account = relationship(
        "AccountModel",
        foreign_keys=[from_account_id],
        back_populates="transactions_from_account",
    )
    to_account = relationship(
        "AccountModel",
        foreign_keys=[to_account_id],
        back_populates="transactions_to_account",
    )

    def to_dictionaries(self):
        return {
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
        }
