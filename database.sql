-- Drop the procedure for foreign key check after running it once
DROP PROCEDURE IF EXISTS DropForeignKeyIfExists;

DELIMITER $$
CREATE PROCEDURE DropForeignKeyIfExists(
    IN tbl_name VARCHAR(255),
    IN fk_constraint_name VARCHAR(255)
)
BEGIN
    DECLARE constraint_exists INT;

    SET constraint_exists = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                             WHERE TABLE_NAME = tbl_name
                             AND CONSTRAINT_NAME = fk_constraint_name);

    IF constraint_exists > 0 THEN
        ALTER TABLE tbl_name DROP FOREIGN KEY fk_constraint_name;
    END IF;
END $$
DELIMITER ;

-- Database Setup
USE ekondo_db;

-- Disable foreign key checks to avoid errors during table modifications
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables if any to avoid conflicts
DROP TABLE IF EXISTS users, roles, departments, branches, statuses, expenses, cash_advance, opex_capex_retirement, 
    petty_cash_advance, petty_cash_retirement, stationary_request, audit_log, document_uploads, notifications, 
    transactions, request_history, notification_settings, file_metadata, expense_approval_workflow, flask_limiter, rate_limit; 

-- Enable foreign key checks again
SET FOREIGN_KEY_CHECKS = 1;

-- Create the branches table
CREATE TABLE branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Insert default branches
INSERT INTO branches (name) VALUES
    ('Head Office'),
    ('Corporate'),
    ('Effio-Ette'),
    ('Chamley'),
    ('Ekpo-Abasi'),
    ('Etim-Edem'),
    ('Watt'),
    ('Ika Ika'),
    ('Ikang'),
    ('Ikot Nakanda'),
    ('Mile 8'),
    ('Oban'),
    ('Odukpani'),
    ('Uyanga'),
    ('Ugep'),
    ('Obubra'),
    ('Ikom'),
    ('Ogoja');

-- Create the roles table
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Insert default roles
INSERT INTO roles (name) VALUES
    ('officer'),
    ('approver'),
    ('reviewer'),
    ('supervisor'),
    ('admin'),
    ('super_admin');

-- Create departments table
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    branch_id INT,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Insert default departments
INSERT INTO departments (name, branch_id) VALUES
    ('HR/Admin', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Account', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Risk/Compliance', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('IT', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Audit', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Funds Transfer', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Credit', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Recovery', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('E-Business', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Legal', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Strategic Branding / Communication', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Business Development', (SELECT id FROM branches WHERE name = 'Head Office')),
    ('Managing Director', (SELECT id FROM branches WHERE name = 'Head Office'));

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INT,
    department_id INT,
    branch_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Insert users with assigned roles
INSERT INTO users (first_name, last_name, username, email, password, role_id, branch_id, department_id) VALUES
    ('Hyacinth', 'Sunday', 'hyman', 'hyacinth.sunday@ekondomfbank.com', '11229012', (SELECT id FROM roles WHERE name = 'officer'), (SELECT id FROM branches WHERE name = 'Head Office'), (SELECT id FROM departments WHERE name = 'IT')),
    ('Ekuere', 'Akpan', 'ekuere', 'ekuere.akpan@ekondomfbank.com', '11223344', (SELECT id FROM roles WHERE name = 'approver'), (SELECT id FROM branches WHERE name = 'Head Office'), (SELECT id FROM departments WHERE name = 'Managing Director')),
    ('Henry', 'Ikpeme', 'henzie', 'henry.etim@ekondomfbank.com', '22446688', (SELECT id FROM roles WHERE name = 'reviewer'), (SELECT id FROM branches WHERE name = 'Head Office'), (SELECT id FROM departments WHERE name = 'Risk/Compliance')),
    ('Ubong', 'Wilson', 'wilson', 'ubong.wilson@ekondomfbank.com', '44556677', (SELECT id FROM roles WHERE name = 'supervisor'), (SELECT id FROM branches WHERE name = 'Head Office'), (SELECT id FROM departments WHERE name = 'IT')),
    ('Emmanuel', 'Sunday', 'emmanate', 'emmyblaq3@gmail.com', 'admin@it', (SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM branches WHERE name = 'Head Office'), (SELECT id FROM departments WHERE name = 'IT'));

-- Verify insertion
SELECT * FROM users;

-- Table for statuses
CREATE TABLE statuses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table for expenses
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status_id INT,
    created_by INT NOT NULL,
    department_id INT,
    branch_id INT,
    management_approval_document VARCHAR(255),
    proforma_invoice_document VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (status_id) REFERENCES statuses(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Table for cash advances
CREATE TABLE cash_advance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    officer_id INT,
    request_date DATE DEFAULT (CURRENT_DATE),
    approval_date DATE,
    amount NUMERIC(10, 2) NOT NULL,
    purpose TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    management_approval_doc BLOB,
    proforma_invoice BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Table for OPEX/CAPEX/RETIREMENT
CREATE TABLE opex_capex_retirement (
    id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT,  -- Remove NOT NULL here
    department_id INT,
    payee_name VARCHAR(100) NOT NULL,
    payee_account_number VARCHAR(20) NOT NULL,
    invoice_amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    cash_advance DECIMAL(10, 2) DEFAULT 0,
    refund_reimbursement DECIMAL(10, 2) DEFAULT 0,
    less_what DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    receipt_filename VARCHAR(255),
    officer_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,  -- This is allowed now
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- Table for petty cash advances
CREATE TABLE petty_cash_advance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT, -- Allow NULL values here
    officer_id INT,
    request_date DATE DEFAULT (CURRENT_DATE),
    amount NUMERIC(10, 2) NOT NULL,
    purpose TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL -- Set to NULL on delete
);

-- Table for petty cash retirements
CREATE TABLE petty_cash_retirement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT, -- Allow NULL values here
    officer_id INT,
    retirement_date DATE DEFAULT (CURRENT_DATE),
    amount NUMERIC(10, 2) NOT NULL,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL -- Set to NULL on delete
);

-- Table for stationary requests
CREATE TABLE stationary_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NULL,  -- Allow NULL values for branch_id
    officer_id INT,
    request_date DATE DEFAULT (CURRENT_DATE),
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    justification TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Table for audit logs
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    previous_value TEXT,
    new_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table for document uploads
CREATE TABLE document_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table for notifications
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Transaction management table
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_type VARCHAR(50) NOT NULL,
    request_id INT NOT NULL, 
    amount DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',
    CHECK (request_type IN ('expense', 'cash_advance')), 
    CONSTRAINT fk_transactions_expense 
        FOREIGN KEY (request_id) 
        REFERENCES expenses(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_transactions_cash_advance 
        FOREIGN KEY (request_id) 
        REFERENCES cash_advance(id) 
        ON DELETE CASCADE 
);

-- History/versioning table for request updates 
CREATE TABLE request_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL, 
    change_type VARCHAR(50) NOT NULL,
    changed_by INT, 
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    previous_value JSON,
    new_value JSON,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

DELIMITER $$
CREATE TRIGGER trg_request_history_before_insert
BEFORE INSERT ON request_history
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT 1 FROM expenses WHERE id = NEW.request_id) 
       AND NOT EXISTS (SELECT 1 FROM cash_advance WHERE id = NEW.request_id) 
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid request_id. Must exist in expenses, cash_advance, or other relevant tables.';
    END IF;
END $$
DELIMITER ;

-- Notification settings table
CREATE TABLE notification_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- File metadata table for document uploads
CREATE TABLE file_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    upload_id INT NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    FOREIGN KEY (upload_id) REFERENCES document_uploads(id) ON DELETE CASCADE
);

-- Expense approval workflow table
CREATE TABLE expense_approval_workflow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    expense_id INT NOT NULL,
    approver_id INT NOT NULL,
    approval_status VARCHAR(50) NOT NULL,
    approval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Flask rate limiter table for request limiting
CREATE TABLE flask_limiter (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    ip_address VARCHAR(255),
    request_count INT DEFAULT 0,
    last_request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Rate limit data for users
CREATE TABLE rate_limit (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    request_limit INT DEFAULT 1000,
    reset_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

