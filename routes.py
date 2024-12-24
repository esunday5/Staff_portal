from flask import Blueprint, jsonify, request
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from extensions import db, csrf, limiter, mail
from models import (
    User, CashAdvance, OpexCapexRetirement, PettyCashAdvance, 
    PettyCashRetirement, StationaryRequest, Notification, Role
)
from werkzeug.utils import secure_filename
from utils import send_email, get_role_id_by_name
from utils import convert_pdf_to_image, allowed_file, resize_image, populate_branches_and_departments  # Import utility functions
# Import forms
from forms import (
    UserRegistrationForm,
    UserLoginForm,
    CashAdvanceForm,
    OpexCapexRetirementForm,
    PettyCashAdvanceForm,
    PettyCashRetirementForm,
    StationaryRequestForm
)
# Import additional modules
from PIL import Image
import os
import logging

def send_email(subject, recipients, body):
    """Send an email notification."""
    try:
        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

# Blueprints
main_blueprint = Blueprint('main', __name__)
auth_blueprint = Blueprint('auth', __name__)

# Home Route
@main_blueprint.route('/')
def home():
    return jsonify({"message": "Welcome to the Expense Management System!"})

# Login API
@auth_blueprint.route('/login', methods=['POST'])
@csrf.exempt  # Disable CSRF for testing purposes (remove in production)
def login_user_api():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be 'application/json'"}), 415

    data = request.get_json()
    login_input = data.get('login')  # Can be username or email
    password = data.get('password')
    if password and login_input:
        return jsonify({"Login successful"})

    if not login_input or not password:
        return jsonify({"error": "Login and password are required"}), 400

    user = User.query.filter((User.username == login_input) | (User.email == login_input)).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user": {"username": user.username, "email": user.email, "role": user.role.name}
        }), 200
    return jsonify({"error": "Invalid login credentials"}), 401

# Petty Cash Advance API
@main_blueprint.route('/petty_cash_advance', methods=['POST'])
@csrf.exempt  # Disable CSRF for testing purposes (remove in production)
def petty_cash_advance():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be 'application/json'"}), 415

    data = request.get_json()
    branch = data.get('branch')
    department = data.get('department')
    name = data.get('name')
    account = data.get('account')
    items = data.get('items')
    description = data.get('description')
    total_amount = data.get('total_amount')

    if not all([branch, department, name, account, items, description, total_amount]):
        return jsonify({"error": "All fields are required"}), 400

    petty_cash = PettyCashAdvance(
        officer_id=1,  # Replace this with current_user.id if using Flask-Login
        branch=branch,
        department=department,
        name=name,
        account=account,
        items=items,
        description=description,
        total_amount=total_amount,
        status="Pending"
    )
    db.session.add(petty_cash)
    db.session.commit()

    # Notify supervisor
    supervisor = User.query.filter_by(role_id=get_role_id_by_name('Supervisor')).first()
    if supervisor:
        send_email(
            "New Petty Cash Advance Request",
            [supervisor.email],
            f"A new petty cash advance request has been raised by {name}."
        )

    return jsonify({"message": "Petty cash advance request submitted successfully!", "id": petty_cash.id}), 201


# Petty Cash Retirement Request
@main_blueprint.route('/petty_cash_retirement', methods=['POST'])
@login_required
@csrf.exempt
def petty_cash_retirement():
    data = request.form
    branch = data.get('branch')
    name = data.get('name')
    items = data.get('items')
    amount = data.get('amount')
    department = data.get('department')
    account = data.get('account')
    description = data.get('description')
    total_amount = data.get('total_amount')
    receipt = request.files.get('receipt')

    if not all([branch, name, items, amount, department, account, description, total_amount, receipt]):
        return jsonify({"error": "All fields and receipt are required"}), 400

    receipt_path = f"uploads/receipts/{receipt.filename}"
    receipt.save(receipt_path)

    petty_cash_ret = PettyCashRetirement(
        officer_id=current_user.id,
        branch=branch,
        name=name,
        items=items,
        amount=amount,
        department=department,
        account=account,
        description=description,
        total_amount=total_amount,
        status="Pending"
    )
    db.session.add(petty_cash_ret)
    db.session.commit()

    supervisor = User.query.filter_by(role_id=get_role_id_by_name('Supervisor'), department_id=current_user.department_id).first()
    if supervisor:
        send_email(
            "New Petty Cash Retirement Request",
            [supervisor.email],
            f"A new petty cash retirement request has been raised by {current_user.username}."
        )

    return jsonify({"message": "Petty cash retirement request submitted successfully!", "id": petty_cash_ret.id}), 201

# Cash Advance Request
@main_blueprint.route('/cash_advance', methods=['POST'])
@csrf.exempt
def cash_advance_request():
    # Check if the form data exists
    if not request.form or not request.files:
        return jsonify({"error": "Form data or files missing"}), 400

    data = request.form
    branch = data.get('branch')
    department = data.get('department')
    name = data.get('name')
    account = data.get('account')
    invoice_amount = data.get('invoice_amount')
    cash_advance = data.get('cash_advance')
    narration = data.get('narration')   
    less_what = data.get('less_what')
    amount = data.get('amount')
    management_board_approval = request.files.get('management_board_approval')
    proforma_invoice = request.files.get('proforma_invoice')

    if not all([branch, department, name, account, invoice_amount, cash_advance, narration, less_what, amount, management_board_approval, proforma_invoice]):
        return jsonify({"error": "All fields and required documents are mandatory"}), 400

    approval_path = f"uploads/docs/{management_board_approval.filename}"
    invoice_path = f"uploads/docs/{proforma_invoice.filename}"
    management_board_approval.save(approval_path)
    proforma_invoice.save(invoice_path)

    cash_advance = CashAdvance(
        officer_id=current_user.id,
        branch=branch,
        department=department,
        name=name,
        account=account,
        invoice_amount=invoice_amount,
        cash_advance=cash_advance,
        narration=narration,
        less_what=less_what,
        amount=amount,
        status="Pending"
    )
    db.session.add(cash_advance)
    db.session.commit()

    supervisor = User.query.filter_by(role_id=get_role_id_by_name('Supervisor'), department_id=current_user.department_id).first()
    if supervisor:
        send_email(
            "New Cash Advance Request",
            [supervisor.email],
            f"A new cash advance request has been raised by {current_user.username}."
        )

    return jsonify({"message": "Cash advance request submitted successfully!", "id": cash_advance.id}), 201

# OPEX/CAPEX Retirement Request
@main_blueprint.route('/opex_capex_retirement', methods=['POST'])
@login_required
@csrf.exempt
def opex_capex_retirement():
    data = request.form
    branch = data.get('branch')
    department = data.get('department')
    name = data.get('name')
    account = data.get('account')
    invoice_amount = data.get('invoice_amount')
    cash_advance = data.get('cash_advance')
    narration = data.get('narration')
    refund_reimbursement = data.get('refund_reimbursement')
    less_what = data.get('less_what')
    amount = data.get('amount')
    receipt = request.files.get('receipt')

    if not all([branch, department, name, account, invoice_amount, cash_advance, narration, refund_reimbursement, less_what, amount, receipt]):
        return jsonify({"error": "All fields and receipt are required"}), 400

    receipt_path = f"uploads/receipts/{receipt.filename}"
    receipt.save(receipt_path)

    opex_retirement = OpexCapexRetirement(
        officer_id=current_user.id,
        branch=branch,
        department=department,
        name=name,
        account=account,
        invoice_amount=invoice_amount,
        cash_advance=cash_advance,
        narration=narration,
        refund_reimbursement=refund_reimbursement,
        less_what=less_what,
        amount=amount,
        status="Pending"
    )
    db.session.add(opex_retirement)
    db.session.commit()

    supervisor = User.query.filter_by(role_id=get_role_id_by_name('Supervisor'), department_id=current_user.department_id).first()
    if supervisor:
        send_email(
            "New OPEX/CAPEX Retirement Request",
            [supervisor.email],
            f"A new OPEX/CAPEX retirement request has been raised by {current_user.username}."
        )

    return jsonify({"message": "OPEX/CAPEX retirement request submitted successfully!", "id": opex_retirement.id}), 201

# Stationery Request
@main_blueprint.route('/stationery_request', methods=['POST'])
@login_required
@csrf.exempt
def stationery_request():
    data = request.get_json()
    branch = data.get('branch')
    department = data.get('department')
    description = data.get('description')
    quantity = data.get('quantity')
    items = data.get('items')

    if not all([branch, department, description, quantity, items]):
        return jsonify({"error": "All fields are required"}), 400

    stationery = StationaryRequest(
        officer_id=current_user.id,
        branch=branch,
        department=department,
        description=description,
        quantity=quantity,
        items=items,
        status="Pending"
    )
    db.session.add(stationery)
    db.session.commit()

    supervisor = User.query.filter_by(role_id=get_role_id_by_name('Supervisor'), department_id=current_user.department_id).first()
    if supervisor:
        send_email(
            "New Stationery Request",
            [supervisor.email],
            f"A new stationery request has been raised by {current_user.username}."
        )

    return jsonify({"message": "Stationery request submitted successfully!", "id": stationery.id}), 201

# Notifications API
@main_blueprint.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return jsonify([notification.to_dict() for notification in notifications])

# Error Handlers
@main_blueprint.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

@main_blueprint.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

# Helper Functions
def get_role_id_by_name(role_name):
    role = Role.query.filter_by(name=role_name).first()
    return role.id if role else None

# Users API
@auth_blueprint.route('/users', methods=['GET'])
@login_required
def get_all_users():
    """Get all registered users. Accessible by Admin/Super Admin."""
    if current_user.role.name not in ['Admin', 'Super Admin']:
        return jsonify({"error": "Unauthorized access"}), 403

    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@auth_blueprint.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_details(user_id):
    """Get details of a specific user."""
    if current_user.role.name not in ['Admin', 'Super Admin']:
        return jsonify({"error": "Unauthorized access"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# Review Request API
@main_blueprint.route('/review_requests', methods=['GET'])
@login_required
def review_requests():
    """Get all requests for review based on user role."""
    if current_user.role.name not in ['Supervisor', 'Reviewer', 'Approver']:
        return jsonify({"error": "Unauthorized access"}), 403

    requests = []
    if current_user.role.name == 'Supervisor':
        requests = CashAdvance.query.filter_by(status="Pending", department_id=current_user.department_id).all()
    elif current_user.role.name == 'Reviewer':
        requests = OpexCapexRetirement.query.filter_by(status="Pending", department_id=current_user.department_id).all()
    elif current_user.role.name == 'Approver':
        requests = PettyCashAdvance.query.filter_by(status="Pending").all()

    return jsonify([req.to_dict() for req in requests]), 200


@main_blueprint.route('/review_requests/<int:request_id>', methods=['PUT'])
@login_required
def update_request_status(request_id):
    """Update the status of a request."""
    if current_user.role.name not in ['Supervisor', 'Reviewer', 'Approver']:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    new_status = data.get('status')

    if not new_status or new_status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    request_to_review = None
    if current_user.role.name == 'Supervisor':
        request_to_review = CashAdvance.query.get(request_id)
    elif current_user.role.name == 'Reviewer':
        request_to_review = OpexCapexRetirement.query.get(request_id)
    elif current_user.role.name == 'Approver':
        request_to_review = PettyCashAdvance.query.get(request_id)

    if not request_to_review:
        return jsonify({"error": "Request not found"}), 404

    request_to_review.status = new_status
    db.session.commit()

    # Notify the requester about the status update
    requester = User.query.get(request_to_review.officer_id)
    if requester:
        send_email(
            "Request Status Updated",
            [requester.email],
            f"Your request (ID: {request_id}) has been {new_status} by {current_user.role.name}."
        )

    return jsonify({"message": f"Request ID {request_id} has been updated to {new_status}."}), 200
