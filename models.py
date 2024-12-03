import enum
import re
from datetime import datetime
from sqlalchemy import Enum, event
from sqlalchemy.orm import validates
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Define status enum for Expense
class ExpenseStatus(enum.Enum):
    PENDING = 'Pending'
    RETURNED_TO_OFFICER = 'Returned to Officer'
    AUTHORIZED_BY_SUPERVISOR = 'Authorized by Supervisor'
    REVIEWED_BY_REVIEWER = 'Reviewed by Reviewer'
    APPROVED_BY_APPROVER = 'Approved by Approver'
    PAYMENT_REQUESTED = 'Payment Requested'


# Branch Model
class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Branch {self.name}>"


# Department Model for Head Office
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch', backref=db.backref('departments', lazy=True))

    def __init__(self, name, branch_id):
        self.name = name
        self.branch_id = branch_id

    def __repr__(self):
        return f"<Department {self.name}>"
    
    
# Role Model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f"<Role {self.name}>"


# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    role = db.relationship('Role', back_populates='users')
    department = db.relationship('Department', back_populates='users')

    def __repr__(self):
        return f"<User {self.username}>"

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        return email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    created_by_user = db.relationship('User', foreign_keys=[created_by])
    department = db.relationship('Department', backref='expenses')

    def __repr__(self):
        return f"<Expense {self.description}, Amount: {self.amount}>"

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount


# Cash Advance Model
class CashAdvance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    officer = db.relationship('User', backref='cash_advances')


# OPEX/CAPEX Retirement Model
class OpexCapexRetirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    payee_name = db.Column(db.String(100), nullable=False)
    payee_account_number = db.Column(db.String(20), nullable=False)
    invoice_amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<OpexCapexRetirement {self.payee_name}>'


# Petty Cash Advance Model
class PettyCashAdvance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<PettyCashAdvance {self.branch}>'


# Petty Cash Retirement Model
class PettyCashRetirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<PettyCashRetirement {self.branch}>'


# Stationary Request Model
class StationaryRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<StationaryRequest {self.branch}>'


# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f"<Notification {self.message}>"


# Document Uploads Model (for tracking uploaded files)
class DocumentUploads(db.Model):
    __tablename__ = 'document_uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # e.g., PDF, Image
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Correct foreign key reference
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    uploader = db.relationship('User', backref='documents')

    def __repr__(self):
        return f"<DocumentUploads {self.file_name}, Uploaded By: {self.uploaded_by}>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='transactions')

    def __repr__(self):
        return f"<Transaction {self.type}, Amount: {self.amount}>"

class RequestHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)  # E.g., 'cash advance', 'expense'
    status = db.Column(db.String(50), nullable=False)  # E.g., 'approved', 'pending'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='request_histories')

    def __repr__(self):
        return f"<RequestHistory {self.request_type}, Status: {self.status}>"

class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    sms_notifications_enabled = db.Column(db.Boolean, default=False)
    push_notifications_enabled = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='notification_settings')

    def __repr__(self):
        return f"<NotificationSettings User ID: {self.user_id}>"

class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # In bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    document_id = db.Column(db.Integer, db.ForeignKey('document_uploads.id'))

    document = db.relationship('DocumentUploads', backref='file_metadata')

    def __repr__(self):
        return f"<FileMetadata {self.file_name}, Size: {self.file_size} bytes>"


class ExpenseApprovalWorkflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(50), default='Pending')  # Workflow status (e.g. Pending, Approved)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    expense = db.relationship('Expense', backref='approval_workflow')
    officer = db.relationship('User', foreign_keys=[officer_id], backref='expense_workflows_officer')
    supervisor = db.relationship('User', foreign_keys=[supervisor_id], backref='expense_workflows_supervisor')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='expense_workflows_reviewer')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='expense_workflows_approver')

    def __repr__(self):
        return f"<ExpenseApprovalWorkflow Expense ID: {self.expense_id}, Status: {self.status}>"


# Audit Log Model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    performed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.action}>"


# Event listener to automatically set timestamps
@event.listens_for(Expense, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()