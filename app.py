from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import traceback

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Serve static files (index.html)
app.static_folder = 'static'
app.static_url_path = '/'

# Gmail SMTP configuration
GMAIL_USER = os.getenv('GMAIL_USER', 'selvavishnug25@gmail.com')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD','fbnm osfr usod sdvy')
ADMIN_EMAIL = 'selvavishnug25@gmail.com'

if not GMAIL_APP_PASSWORD:
    logger.error("GMAIL_APP_PASSWORD environment variable is not set")
    raise ValueError("GMAIL_APP_PASSWORD environment variable is not set")

@app.route('/')
def serve_index():
    logger.debug("Serving index.html")
    return app.send_static_file('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    logger.debug("Received request to /send-email")
    try:
        # Get form data
        name = request.form.get('name')
        user_email = request.form.get('_email')
        message = request.form.get('message')

        logger.debug(f"Form data: name={name}, email={user_email}, message={message}")

        if not all([name, user_email, message]):
            logger.warning("Missing required fields in form submission")
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate email format (basic check)
        if '@' not in user_email or '.' not in user_email:
            logger.warning(f"Invalid email format: {user_email}")
            return jsonify({'error': 'Invalid email format'}), 400

        # Create email for user (auto-reply)
        user_msg = MIMEMultipart()
        user_msg['From'] = GMAIL_USER
        user_msg['To'] = user_email
        user_msg['Subject'] = 'Thanks for contacting Selva Vishnu'
        user_body = f"Hi {name},\n\nThank you for connecting with me! I will get back to you soon.\n\n– Selva Vishnu"
        user_msg.attach(MIMEText(user_body, 'plain'))

        # Create email for admin (notification)
        admin_msg = MIMEMultipart()
        admin_msg['From'] = GMAIL_USER
        admin_msg['To'] = ADMIN_EMAIL
        admin_msg['Subject'] = f'New Contact Form Submission from {name}'
        admin_body = f"Name: {name}\nEmail: {user_email}\nMessage: {message}"
        admin_msg.attach(MIMEText(admin_body, 'plain'))

        # Connect to Gmail SMTP server
        logger.debug("Connecting to Gmail SMTP server")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            logger.debug("SMTP login successful")
            server.send_message(user_msg)
            server.send_message(admin_msg)
            logger.info(f"Emails sent to {user_email} and {ADMIN_EMAIL}")

        return jsonify({'message': 'Email sent successfully'}), 200

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Authentication failed. Please contact the administrator.'}), 401
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)