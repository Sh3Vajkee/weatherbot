from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text

from db.base import Base


class CallsCount(Base):
    __tablename__ = "callscount"

    id = Column(Integer, primary_key=True)
    day_calls = Column(BigInteger, default=0)
    month_calls = Column(BigInteger, default=0)
    daily = Column(Integer, default=0)
