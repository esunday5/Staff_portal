"""empty message

Revision ID: 9add89615840
Revises: 
Create Date: 2024-12-09 19:38:40.663387

"""

from sqlalchemy.dialects import mysql
from alembic import op
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import mysql
from flask import Flask
from app import db
from flask import current_app as app
from models import (
    User, Role, Expense, CashAdvance, OpexCapexRetirement,
    PettyCashAdvance, PettyCashRetirement, StationaryRequest, Notification
)
from sqlalchemy import ForeignKey, Table, MetaData
from sqlalchemy.exc import OperationalError  # Import the exc submodule



# revision identifiers, used by Alembic.
revision = '9add89615840'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Check and create roles table
    if 'roles' not in inspector.get_table_names():
        op.create_table(
            'roles',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('name', sa.String(50), nullable=False, unique=True),
        )

    # Check and create departments table
    if 'departments' not in inspector.get_table_names():
        op.create_table(
            'departments',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('name', sa.String(50), nullable=False, unique=True),
        )

    # Check and create users table
    if 'users' not in inspector.get_table_names():
        op.create_table(
            'users',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('username', sa.String(100), nullable=False, unique=True),
            sa.Column('email', sa.String(100), nullable=False, unique=True),
            sa.Column('first_name', sa.String(100), nullable=False),
            sa.Column('last_name', sa.String(100), nullable=False),
            sa.Column('password', sa.String(255), nullable=False),
            sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id', ondelete='SET NULL')),
            sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id', ondelete='SET NULL')),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('email_verified', sa.Boolean, default=False),
            sa.Column('is_deleted', sa.Boolean, default=False),
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.TIMESTAMP, nullable=True, onupdate=sa.func.now()),
        )

    # Check and create statuses table
    if 'statuses' not in inspector.get_table_names():
        op.create_table(
            'statuses',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('name', sa.String(50), nullable=False, unique=True),
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.TIMESTAMP, nullable=True, onupdate=sa.func.now()),
        )

    # Check and create expenses table
    if 'expenses' not in inspector.get_table_names():
        op.create_table(
            'expenses',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('description', sa.String(255), nullable=False),
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('status_id', sa.Integer, sa.ForeignKey('statuses.id', ondelete='SET NULL')),
            sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
            sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id', ondelete='SET NULL')),
            sa.Column('management_approval_document', sa.String(255)),
            sa.Column('proforma_invoice_document', sa.String(255)),
            sa.Column('is_deleted', sa.Boolean, default=False),
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.TIMESTAMP, nullable=True, onupdate=sa.func.now()),
        )

    # Check and create 'cash_advance' table
    if 'cash_advance' not in inspector.get_table_names():
        op.create_table(
            'cash_advance',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('branch', sa.String(255), nullable=False),
            sa.Column('officer_id', sa.Integer, sa.ForeignKey('users.id', ondelete='SET NULL')),
            sa.Column('request_date', sa.Date, server_default=sa.func.current_date()),
            sa.Column('approval_date', sa.Date),
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('purpose', sa.Text, nullable=False),
            sa.Column('status', sa.String(50)),
            sa.Column('management_approval_doc', sa.LargeBinary),
            sa.Column('proforma_invoice', sa.LargeBinary),
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        )

    # Check if the table 'petty_cash_advance' exists
    if 'petty_cash_advance' not in inspector.get_table_names():
        op.create_table(
            'petty_cash_advance',
            sa.Column('id', sa.Integer, primary_key=True, nullable=False),
            sa.Column('branch', sa.String(255), nullable=False),
            sa.Column('officer_id', sa.Integer, sa.ForeignKey('users.id', ondelete='SET NULL')),
            sa.Column('request_date', sa.Date, server_default=sa.func.current_date()),
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('purpose', sa.Text),
            sa.Column('status', sa.String(50)),
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        )

    # Check if the table already exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'petty_cash_retirement'")).fetchone():
        # Create the table if it does not exist
        op.create_table(
            'petty_cash_retirement',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('branch', sa.String(length=255), nullable=False),
            sa.Column('officer_id', sa.Integer(), nullable=True),
            sa.Column('retirement_date', sa.Date(), server_default=sa.func.current_date(), nullable=True),
            sa.Column('retired_amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('receipt', sa.LargeBinary(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['officer_id'], ['users.id'], name='fk_officer_id', ondelete='SET NULL')
        )

    # Check if the table 'request_history' exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'request_history'")).fetchone():
        # Create the table only if it does not exist
        op.create_table(
            'request_history',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('request_id', sa.Integer(), nullable=False),
            sa.Column('change_type', sa.String(length=50), nullable=False),
            sa.Column('changed_by', sa.Integer(), nullable=True),
            sa.Column('change_timestamp', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
            sa.Column('previous_value', sa.JSON(), nullable=True),
            sa.Column('new_value', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['changed_by'], ['users.id'], name='fk_changed_by', ondelete='SET NULL')
        )

    # Check if the table 'transactions' exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'transactions'")).fetchone():
        # Create the table only if it does not exist
        op.create_table(
            'transactions',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('request_type', sa.String(length=50), nullable=False),
            sa.Column('request_id', sa.Integer(), nullable=False),
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('transaction_date', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=True)
        )


    # Check if the table 'stationary_request' exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'stationary_request'")).fetchone():
        # Create the table only if it does not exist
        op.create_table(
            'stationary_request',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('branch', sa.String(length=255), nullable=False),
            sa.Column('officer_id', sa.Integer(), nullable=True),
            sa.Column('request_date', sa.Date(), server_default=sa.func.current_date(), nullable=True),
            sa.Column('item_name', sa.String(length=255), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('justification', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['officer_id'], ['users.id'], name='fk_officer_id', ondelete='SET NULL')
        )

    # Check if the 'audit_logs' table exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'audit_logs'")).fetchone():
        op.create_table(
            'audit_logs',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('table_name', sa.String(length=50), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
            sa.Column('previous_value', sa.Text, nullable=True),
            sa.Column('new_value', sa.Text, nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )

    # Check if the 'notifications' table exists
    if not bind.execute(sa.text("SHOW TABLES LIKE 'notifications'")).fetchone():
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('notification_type', sa.String(length=50), nullable=False),
            sa.Column('is_read', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )

        # Create the branches table
    if 'branches' not in inspector.get_table_names():
        op.create_table(
            'branches',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('name', sa.String(255), nullable=False, unique=True),
        )

    # Create the notification_settings table
    if 'notification_settings' not in inspector.get_table_names():
        op.create_table(
            'notification_settings',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('notification_type', sa.String(50), nullable=False),
            sa.Column('is_enabled', sa.Boolean, nullable=False, default=True),
        )

    # Create the file_metadata table
    if 'file_metadata' not in inspector.get_table_names():
        op.create_table(
            'file_metadata',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('upload_id', sa.Integer, sa.ForeignKey('document_uploads.id', ondelete='CASCADE'), nullable=False),
            sa.Column('file_type', sa.String(50), nullable=True),
            sa.Column('file_size', sa.Integer, nullable=True),
        )

    # Create the expense_approval_workflow table
    if 'expense_approval_workflow' not in inspector.get_table_names():
        op.create_table(
            'expense_approval_workflow',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('expense_id', sa.Integer, sa.ForeignKey('expenses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('approver_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('approval_status', sa.String(50), nullable=False),
            sa.Column('approval_date', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        )

    # Create the flask_limiter table
    if 'flask_limiter' not in inspector.get_table_names():
        op.create_table(
            'flask_limiter',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('ip_address', sa.String(255), nullable=True),
            sa.Column('request_count', sa.Integer, nullable=True, default=0),
            sa.Column('last_request_time', sa.TIMESTAMP, server_default=sa.func.now(), nullable=True),
        )

    # Create the rate_limit table
    if 'rate_limit' not in inspector.get_table_names():
        op.create_table(
            'rate_limit',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('request_limit', sa.Integer, default=1000, nullable=False),
            sa.Column('reset_time', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        )

    # ### end Alembic commands ###


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Disable foreign key checks to avoid issues during table deletion
    op.execute("SET FOREIGN_KEY_CHECKS = 0")

    # List of tables to drop in reverse order of creation due to foreign key dependencies
    tables_to_drop = [
        "rate_limit",
        "flask_limiter",
        "expense_approval_workflow",
        "file_metadata",
        "notification_settings",
        "notifications",
        "audit_logs",
        "stationary_request",
        "transactions",
        "request_history",
        "petty_cash_retirement",
        "petty_cash_advance",
        "cash_advance",
        "expenses",
        "statuses",
        "users",
        "departments",
        "roles",
        "branches",
    ]

    for table in tables_to_drop:
        if table in inspector.get_table_names():
            try:
                op.drop_table(table)
            except Exception as e:
                print(f"Error dropping table {table}: {str(e)}")

    # Drop the stored procedure if it exists
    try:
        op.execute("DROP PROCEDURE IF EXISTS DropForeignKeyIfExists")
    except Exception as e:
        print(f"Could not drop stored procedure: {str(e)}")

    # Drop the trigger if it exists
    try:
        op.execute("DROP TRIGGER IF EXISTS trg_request_history_before_insert")
    except Exception as e:
        print(f"Could not drop trigger: {str(e)}")

    # Re-enable foreign key checks after operations are complete
    op.execute("SET FOREIGN_KEY_CHECKS = 1")

    # ### end Alembic commands ###
