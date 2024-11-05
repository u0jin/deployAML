from flask import render_template, request, flash, json, redirect, url_for
from app import app, db
from models import SuspiciousAddress, AddressCheck
from utils import (
    is_valid_btc_address, 
    get_address_info, 
    sanitize_address, 
    get_detailed_transactions,
    create_transaction_flow_visualization
)
from datetime import datetime

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_address():
    address = sanitize_address(request.form.get('address', ''))
    
    if not address:
        flash('Please enter an address', 'danger')
        return render_template('index.html')
    
    if not is_valid_btc_address(address):
        flash('Invalid Bitcoin address format', 'danger')
        return render_template('index.html')

    # Check local database
    suspicious = SuspiciousAddress.query.filter_by(address=address).first()
    
    # Get blockchain info
    address_info = get_address_info(address)
    
    # Get transaction flow data
    transactions = get_detailed_transactions(address)
    transaction_viz = None
    if transactions:
        transaction_viz = create_transaction_flow_visualization(transactions, address)
    
    # Record the check
    check = AddressCheck(address=address, result=bool(suspicious))
    db.session.add(check)
    db.session.commit()
    
    return render_template('result.html',
                         address=address,
                         suspicious=suspicious,
                         address_info=address_info,
                         transaction_viz=transaction_viz)

@app.route('/report', methods=['GET', 'POST'])
def report_address():
    if request.method == 'POST':
        address = sanitize_address(request.form.get('address', ''))
        reason = request.form.get('reason', '').strip()
        risk_score = request.form.get('risk_score', type=int)
        
        if not address or not reason or not risk_score:
            flash('All fields are required', 'danger')
            return render_template('report.html', address=address)
        
        if not is_valid_btc_address(address):
            flash('Invalid Bitcoin address format', 'danger')
            return render_template('report.html', address=address)
            
        if not (0 <= risk_score <= 100):
            flash('Risk score must be between 0 and 100', 'danger')
            return render_template('report.html', address=address)
            
        # Check if address is already reported
        existing = SuspiciousAddress.query.filter_by(address=address).first()
        if existing:
            flash('This address has already been reported', 'warning')
            return redirect(url_for('check_address', address=address))
            
        # Create new suspicious address report
        now = datetime.utcnow()
        suspicious = SuspiciousAddress(
            address=address,
            cryptocurrency='BTC',
            reason=reason,
            first_seen=now,
            last_seen=now,
            risk_score=risk_score
        )
        
        try:
            db.session.add(suspicious)
            db.session.commit()
            flash('Address reported successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error reporting address. Please try again.', 'danger')
            return render_template('report.html', address=address)
            
    address = request.args.get('address', '')
    return render_template('report.html', address=address)
