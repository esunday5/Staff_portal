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


# Expense Model with improved validations
class Expense(db.Model):
    __tablename__ = 'expenses'  # Add __tablename__
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = db.relationship('User', backref='expenses_created') 
    department = db.relationship('Department', backref='expenses')

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")
        return amount

    def __repr__(self):
        return f"<Expense(description={self.description}, amount={self.amount})>"

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    role = db.relationship('Role', back_populates='users')
    department = db.relationship('Department', back_populates='users')
    notifications = db.relationship('Notification', backref='user', lazy=True)
    expenses_created = db.relationship('Expense', backref='created_by_user', foreign_keys="[Expense.created_by]")

    def __init__(self, username, email, password, first_name, last_name, role_id=None, department_id=None):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role_id = role_id
        self.department_id = department_id
        self.set_password(password)

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


# Cash Advance Model
class CashAdvance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    management_board_approval_path = db.Column(db.String(255), nullable=True)
    proforma_invoice_path = db.Column(db.String(255), nullable=True)
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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<OpexCapexRetirement {self.payee_name}>'


# Petty Cash Advance Model
class PettyCashAdvance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    officer = db.relationship('User', backref='petty_cash_advances')


# Petty Cash Retirement Model
class PettyCashRetirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    items = db.Column(db.JSON, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by_user = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<StationaryRequest {self.branch}>'


# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


# Document Uploads Model (for tracking uploaded files)
class DocumentUploads(db.Model):
    __tablename__ = 'document_uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='documents')

    def __repr__(self):
        return f'<DocumentUpload {self.file_name}>'


# Transaction Model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

    user = db.relationship('User', backref='transactions') 

    def __repr__(self):
        return f"<Transaction {self.type}, Amount: {self.amount}>"


# Request History Model
class RequestHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False)  # E.g., 'cash advance', 'expense'
    status = db.Column(db.String(50), nullable=False)  # E.g., 'approved', 'pending'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='request_histories')

    def __repr__(self):
        return f"<RequestHistory {self.request_type}, Status: {self.status}>"


# Notification Settings Model
class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    sms_notifications_enabled = db.Column(db.Boolean, default=False)
    push_notifications_enabled = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='notification_settings') 

    def __repr__(self):
        return f"<NotificationSettings User ID: {self.user_id}>"


# File Metadata Model
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


# Expense Approval Workflow Model
class ExpenseApprovalWorkflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Removed expense_id as it's no longer needed
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(50), default='Pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Remove the expense relationship
    # expense = db.relationship('Expense', backref='approval_workflow') 
    officer = db.relationship('User', foreign_keys=[officer_id], backref='expense_workflows_officer')
    supervisor = db.relationship('User', foreign_keys=[supervisor_id], backref='expense_workflows_supervisor')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='expense_workflows_reviewer') 
    approver = db.relationship('User', foreign_keys=[approver_id], backref='expense_workflows_approver')

    def __repr__(self):
        # Remove the expense_id from the representation 
        return f"<ExpenseApprovalWorkflow Officer ID: {self.officer_id}, Status: {self.status}>"


# Audit Log Model
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)  # Description of the action performed
    entity_type = db.Column(db.String(100), nullable=False)  # E.g., 'User', 'Expense', etc.
    entity_id = db.Column(db.Integer, nullable=True)  # ID of the affected entity (if applicable)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp of the action

    # Relationship to the user who performed the action
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f"<AuditLog Action: {self.action}, Entity: {self.entity_type}, Performed By: {self.performed_by}>"

    def to_dict(self):
        """Convert the AuditLog instance to a dictionary for easy serialization."""
        return {
            "id": self.id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "performed_by": self.performed_by,
            "performed_at": self.performed_at.isoformat()
        }


# Event listener to automatically set timestamps
@event.listens_for(Expense, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()