from models import User, Role, Branch, Department, Notification, AuditLog
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_caching import Cache
from PIL import Image
import pdf2image
import os
from flask_mail import Message  
from extensions import db, mail  # Import db from extensions.py
from models import User  # Only import models you need
from flask import request, jsonify


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize caching (assuming cache configuration is done elsewhere)
cache = Cache()

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_image(pdf_path, output_folder='converted_images'):
    """Convert a PDF to an image and save it."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    try:
        images = pdf2image.convert_from_path(pdf_path)
        image_path = os.path.join(output_folder, os.path.basename(pdf_path).replace(".pdf", ".jpg"))
        images[0].save(image_path, 'JPEG')
        return image_path
    except Exception as e:
        logging.error(f"Error converting PDF to image: {e}")
        raise

def resize_image(image_path, max_size=(800, 800)):
    """Resize an image to a maximum size while maintaining aspect ratio."""
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size)
        img.save(image_path)
    except Exception as e:
        logging.error(f"Error resizing image: {e}")
        raise


def send_email(subject, recipients, body):
    """Send an email notification."""
    try:
        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")


def get_role_id_by_name(role_name):
    """Fetch the role ID based on the role name."""
    role = Role.query.filter_by(name=role_name).first()
    return role.id if role else None


@cache.cached(timeout=60, key_prefix='supervisor_by_department')
def get_supervisor(department_id):
    """Fetch the supervisor for a given department.

    Args:
        department_id (int): The ID of the department.

    Returns:
        User: The supervisor User object or None if not found.
    """
    try:
        SUPERVISOR_ROLE_ID = get_role_id_by_name('Supervisor')
        supervisor = User.query.filter_by(department_id=department_id, role_id=SUPERVISOR_ROLE_ID).first()
        if supervisor:
            logging.info(f"Supervisor found for department {department_id}: {supervisor.username}")
        else:
            logging.warning(f"No supervisor found for department {department_id}.")
        return supervisor
    except SQLAlchemyError as e:
        logging.error(f"Error fetching supervisor for department {department_id}: {e}")
        return None

def send_notification(user_id, message, notification_type='email'):
    """Send a notification to the user.

    Args:
        user_id (int): The ID of the user to notify.
        message (str): The message content.
        notification_type (str): The type of notification ('email', 'sms', 'in-app').
    """
    user = User.query.get(user_id)
    if user is None:
        logging.error(f"User with ID {user_id} not found. Notification not sent.")
        return

    try:
        if notification_type == 'email':
            subject = "Important Notification"
            # Implement email sending logic using Flask-Mail or similar
            logging.info(f"Email sent to {user.email}: {message}")
        elif notification_type == 'sms':
            logging.info(f"SMS sent to {user.phone_number}: {message}")  # Assuming phone_number exists in User
        elif notification_type == 'in-app':
            logging.info(f"In-app notification sent to {user.username}: {message}")
        else:
            logging.warning(f"Unknown notification type: {notification_type}. No action taken.")
    except Exception as e:
        logging.error(f"Failed to send notification to user {user_id}: {e}")

def get_role_id_by_name(role_name):
    """Fetch role ID by role name.

    Args:
        role_name (str): The name of the role.

    Returns:
        int: The ID of the role or None if not found.
    """
    role = Role.query.filter_by(name=role_name).first()
    return role.id if role else None

def get_officer_role_id():
    """Fetch the Officer role ID."""
    return get_role_id_by_name('Officer')

def get_supervisor_role_id():
    """Fetch the Supervisor role ID."""
    return get_role_id_by_name('Supervisor')

def get_reviewer_role_id():
    """Fetch the Reviewer role ID."""
    return get_role_id_by_name('Reviewer')

def get_approver_role_id():
    """Fetch the Approver role ID."""
    return get_role_id_by_name('Approver')

def get_admin_role_id():
    """Fetch the Admin role ID."""
    return get_role_id_by_name('Admin')

def get_super_admin_role_id():
    """Fetch the Super Admin role ID."""
    return get_role_id_by_name('Super Admin')

def convert_pdf_to_image_v2(pdf_path):
    """Convert PDF to images and return paths of the images.""" 
    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = f'uploads/page_{i + 1}.png'  # Save each page as a PNG
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

def populate_branches_and_departments():
    """Populate branches and departments into the database."""
    # Add branches
    branches = [
        "Corporate Branch", "Effio-Ette Branch", "Chamley Branch", "Ekpo-Abasi Branch",
        "Etim-Edem Branch", "Watt Branch", "Ika Ika Branch", "Ikang Branch", "Ikot Nakanda Branch",
        "Mile 8 Branch", "Oban Branch", "Odukpani Branch", "Uyanga Branch", "Ugep Branch", 
        "Obubra Branch", "Ikom Branch", "Ogoja Branch", "HeadOffice Branch"
    ]

    for branch_name in branches:
        branch = Branch(name=branch_name)
        db.session.add(branch)
    
    db.session.commit()

    # Add departments for Head Office
    head_office = Branch.query.filter_by(name="HeadOffice Branch").first()

    if head_office:
        departments = [
            "HR/Admin", "Account", "Risk/Compliance", "IT", "Audit", "Fund transfer", 
            "Credit", "Recovery", "E-Business", "Legal", "Strategic Branding/Communications"
        ]

        for department_name in departments:
            department = Department(name=department_name, branch_id=head_office.id)
            db.session.add(department)

        db.session.commit()

def validate_json(required_fields):
    """Validate incoming JSON payloads."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    return data