from app import app, db
from models import SuspiciousAddress
from datetime import datetime

def init_suspicious_addresses():
    with app.app_context():
        # Check if address already exists
        existing = SuspiciousAddress.query.filter_by(
            address='1J1yr6QkaTji7zgVBSN9YnBK2eooTeqXeE'
        ).first()
        
        if not existing:
            # Add known hacker address
            suspicious_address = SuspiciousAddress(
                address='1J1yr6QkaTji7zgVBSN9YnBK2eooTeqXeE',
                cryptocurrency='BTC',
                reason='Known hacker address associated with multiple ransomware attacks',
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                risk_score=95
            )
            db.session.add(suspicious_address)
            db.session.commit()
            print("Added suspicious address to database.")
        else:
            print("Suspicious address already exists in database.")

if __name__ == "__main__":
    init_suspicious_addresses()
