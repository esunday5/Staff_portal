from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, DecimalField, TextAreaField,
    SubmitField, FloatField, BooleanField, DateField, FileField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError
)
from datetime import datetime
from models import Role, Department  # Ensure correct model imports

# User Registration Form
class UserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role_id = SelectField('Role', choices=[(1, 'Admin'), (2, 'Officer')], coerce=int)
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# User Login Form
class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Cash Advance Form
class CashAdvanceForm(FlaskForm):
    branch = StringField('Branch', validators=[DataRequired()])
    department = StringField('Department', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=255)])
    purpose = StringField('Purpose', validators=[DataRequired()])
    advance_amount = FloatField('Advance Amount', validators=[DataRequired()])
    date_incurred = DateField('Date Incurred', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Cash Advance')

# Cash Advance Form with Document Uploads
class CashAdvanceWithDocumentsForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    amount = DecimalField('Amount', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    management_approval_document = FileField('Management/Board Approval Document')
    proforma_invoice_document = FileField('Proforma Invoice Document')
    submit = SubmitField('Submit')

# OPEX/CAPEX/Retirement Form
class OpexCapexRetirementForm(FlaskForm):
    branch = SelectField('Branch', choices=[('Branch A', 'Branch A'), ('Branch B', 'Branch B'), ('Head Office', 'Head Office')], validators=[DataRequired()])
    department = StringField('Department', validators=[Optional()])
    payee_name = StringField('Payee Name', validators=[DataRequired()])
    payee_account_number = StringField('Payee Account Number', validators=[DataRequired()])
    invoice_amount = DecimalField('Invoice Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    cash_advance = BooleanField('Cash Advance')
    refund_reimbursement = BooleanField('Refund/Reimbursement')
    less_what = DecimalField('Less What', validators=[Optional()])
    total_amount = DecimalField('Total Amount', validators=[DataRequired()])
    receipt = FileField('Upload Receipt', validators=[Optional()])
    submit = SubmitField('Submit OPEX/CAPEX Request')

# Petty Cash Advance Form
class PettyCashAdvanceForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    items = TextAreaField('Items', validators=[DataRequired(), Length(max=500)])
    total_amount = DecimalField('Total Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit Petty Cash Advance')

# Petty Cash Retirement Form
class PettyCashRetirementForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    items = TextAreaField('Items', validators=[DataRequired(), Length(max=500)])
    total_amount = DecimalField('Total Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit Petty Cash Retirement')

# Stationary Request Form
class StationaryRequestForm(FlaskForm):
    branch = StringField('Branch', validators=[DataRequired(), Length(max=100)])
    items = TextAreaField('Items', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Request Stationery')

# Login Form (for main site login)
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Register Form (for main site registration)
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[], validators=[DataRequired()])
    department = SelectField('Department', choices=[], validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]
        self.department.choices = [(department.id, department.name) for department in Department.query.all()]
