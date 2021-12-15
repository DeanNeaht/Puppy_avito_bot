from sqlalchemy import Column, Integer, BigInteger, VARCHAR, ForeignKey, BOOLEAN, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(VARCHAR(length=255))
    full_name = Column(VARCHAR(255))
    is_send = Column(BOOLEAN, default=True, nullable=False)

    def __repr__(self):
        return f"User_id:{self.user_id}"
