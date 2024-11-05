import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from utils import get_address_info, get_detailed_transactions, create_transaction_flow_visualization
from flask_cors import CORS

Base = declarative_base()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "your-secret-key-here"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///local.db"  # Use local database for development
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize and configure the database
db = SQLAlchemy(model_class=Base)
db.init_app(app)

with app.app_context():
    import models  # Defining and creating models within the app context
    db.create_all()

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/address/<string:address>')
def address_info(address):
    from models import SuspiciousAddress
    address_info = SuspiciousAddress.query.filter_by(address=address).first()
    if not address_info:
        return "Address not found", 404

    # Fetch additional information using utilities
    address_data = get_address_info(address)
    transactions = get_detailed_transactions(address)
    transaction_viz = None
    if transactions:
        transaction_viz = create_transaction_flow_visualization(transactions, address)

    return render_template(
        'result.html',
        address=address,
        address_info=address_data,
        transaction_viz=transaction_viz,
        suspicious=address_info
    )

@app.route('/check_address', methods=['POST'])
def check_address():
    address = request.form.get('address')
    return redirect(url_for('address_info', address=address))

@app.route('/report_address', methods=['GET', 'POST'])
def report_address():
    if request.method == 'POST':
        address = request.form.get('address')
        flash('Address reported successfully', 'success')
        return redirect(url_for('home'))
    return render_template('report.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)