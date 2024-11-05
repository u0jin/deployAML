from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app import db

class SuspiciousAddress(db.Model):
    __tablename__ = 'suspicious_addresses'

    id = Column(Integer, primary_key=True)
    address = Column(String(80), unique=True, nullable=False)
    cryptocurrency = Column(String(10), nullable=False)
    reason = Column(String(255), nullable=True)
    risk_score = Column(Integer, nullable=True)
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)

    def __init__(self, address, cryptocurrency, reason, first_seen, last_seen, risk_score):
        self.address = address
        self.cryptocurrency = cryptocurrency
        self.reason = reason
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.risk_score = risk_score

    def __repr__(self):
        return f'<SuspiciousAddress {self.address}>'

class AddressCheck(db.Model):
    __tablename__ = 'address_checks'  # 테이블 이름이 지정되지 않았을 경우 이름을 지정합니다.

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    check_date = Column(DateTime, default=datetime.utcnow)
    result = Column(db.Boolean, default=False)

    def __init__(self, address, result):
        self.address = address
        self.result = result

    def __repr__(self):
        return f'<AddressCheck {self.address}>'