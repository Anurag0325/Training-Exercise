import psycopg2
import csv
from flask import Flask, jsonify, request, send_file
from models import *
from flask_cors import CORS
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.security import generate_password_hash
import jwt
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SECRET_KEY'] = "anuragiitmadras"

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#     'DATABASE_URL')  # Use full URL from Render
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


db.init_app(app)


# def create_database():
# connection = psycopg2.connect(
#     user="postgres", password="warcraft2503", host="127.0.0.1", port="5432")
# connection.autocommit = True
# cursor = connection.cursor()
# try:
#     cursor.execute("CREATE DATABASE my_database")
#     print("Database created successfully")
# except psycopg2.errors.DuplicateDatabase:
#     print("Database already exists")
# finally:
#     cursor.close()
#     connection.close()


def insert_dummy_data():
    colleagues_data = [
        {"name": "Alice Johnson", "email": "22dp1000105@ds.study.iitm.ac.in",
            "department": "IT", "designation": "Analyst"},
        {"name": "Anurag Kumar", "email": "akanuragkumar75@gmail.com",
            "department": "Developer", "designation": "Developer"},
        {"name": "Sethi", "email": "tech@kvqaindia.com",
            "department": "Developer", "designation": "Developer"},
        {"name": "Ritika", "email": "training@kvqaindia.com",
            "department": "Leadership", "designation": "CTO"},
        # {"name": "Lav Kaushik", "email": "lav@kvqaindia.com",
        #     "department": "Leadership", "designation": "CEO"},
        # {"name": "Krishna Chaudhari", "email": "krishna.chaudhari@riaadvisory.com",
        #     "department": "Internal IT and Cloud Ops", "designation": "Associate Consultant"},
        # {"name": "Krishna Chaudhari GMAIL", "email": "krish.chaudhari2018@gmail.com",
        #     "department": "Internal IT and Cloud Ops", "designation": "Associate Consultant"},
        # {"name": "Jibin Sebastian", "email": "jibin.sebastian@riaadvisory.com",
        #     "department": "Operations", "designation": "Consultant - Admin"},
        # {"name": "Salman Ansari", "email": "salman.ansari@riaadvisory.com",
        #     "department": "Internal IT and Cloud Ops", "designation": "Director - CISO"},
        # {"name": "Deepak Nichani", "email": "deepak.nichani@riaadvisory.com",
        #     "department": "Operations", "designation": "Senior Consultant - Admin"},
        # {"name": "Suraj Kamble", "email": "suraj.kambale@riaadvisory.com",
        #     "department": "Developer", "designation": "Consultant"},
        # {"name": "Eva Adams", "email": "eva.adams@bing.com", "designation": "HR"},
    ]

    # colleagues = [Colleagues(name=data['name'], email=data['email'],
    #                          designation=data['designation']) for data in colleagues_data]

    for data in colleagues_data:
        existing_colleague = Colleagues.query.filter_by(
            email=data['email']).first()
        if not existing_colleague:  # Only insert if email doesn't exist
            colleague = Colleagues(
                name=data['name'], email=data['email'], department=data['department'], designation=data['designation'])
            db.session.add(colleague)

    questions_data = [
        {
        "question_text": "What is the most common method of cyberattack?",
        "options": [
            "Phishing",
            "Ransomware",
            "Man-in-the-middle attack",
            "SQL Injection"
        ],
        "answer": "Phishing"
    },
    {
        "question_text": "What should you do if you receive an email from an unknown sender asking for personal information?",
        "options": [
            "Respond with your details",
            "Open any attached files",
            "Report it and delete the email",
            "Click the link to check if it's legitimate"
        ],
        "answer": "Report it and delete the email"
    },
    {
        "question_text": "What does the term 'Malware' refer to?",
        "options": [
            "Legitimate software",
            "Software designed to disrupt, damage, or gain unauthorized access",
            "Software to improve performance",
            "A type of firewall"
        ],
        "answer": "Software designed to disrupt, damage, or gain unauthorized access"
    },
    {
        "question_text": "Which of the following is an example of a strong password?",
        "options": [
            "password123",
            "john123",
            "P@55w0rd_2025!",
            "abc123"
        ],
        "answer": "P@55w0rd_2025!"
    },
    {
        "question_text": "Which of the following best describes two-factor authentication (2FA)?",
        "options": [
            "Using two passwords",
            "A combination of something you know and something you have",
            "Using multiple usernames",
            "A tool for system encryption"
        ],
        "answer": "A combination of something you know and something you have"
    },
    {
        "question_text": "What is phishing?",
        "options": [
            "A type of malware",
            "The act of stealing data through fraudulent emails or websites",
            "A method to secure a network",
            "A strong password protection technique"
        ],
        "answer": "The act of stealing data through fraudulent emails or websites"
    },
    {
        "question_text": "Which of these is NOT a good cybersecurity practice?",
        "options": [
            "Using a different password for each account",
            "Sharing your password with friends",
            "Enabling 2FA",
            "Regularly updating software"
        ],
        "answer": "Sharing your password with friends"
    },
    {
        "question_text": "What is a firewall used for?",
        "options": [
            "To monitor website traffic",
            "To detect viruses",
            "To prevent unauthorized access to or from a private network",
            "To encrypt emails"
        ],
        "answer": "To prevent unauthorized access to or from a private network"
    },
    {
        "question_text": "What does 'Pharming' refer to?",
        "options": [
            "A type of phishing attack involving fraudulent websites",
            "A software update",
            "A tool for hacking passwords",
            "Using two-factor authentication"
        ],
        "answer": "A type of phishing attack involving fraudulent websites"
    },
    {
        "question_text": "What is the primary purpose of antivirus software?",
        "options": [
            "To improve computer speed",
            "To remove malware",
            "To encrypt communications",
            "To create backups"
        ],
        "answer": "To remove malware"
    },
    {
        "question_text": "What should you do if you encounter suspicious activity on your work computer?",
        "options": [
            "Ignore it and continue working",
            "Notify IT or your security team immediately",
            "Attempt to fix it yourself",
            "Disconnect the computer from the internet"
        ],
        "answer": "Notify IT or your security team immediately"
    },
    {
        "question_text": "Which of the following is NOT a sign that your computer might be infected with malware?",
        "options": [
            "Slower system performance",
            "Unexpected pop-up ads",
            "Increased battery life",
            "Unusual or unfamiliar programs running"
        ],
        "answer": "Increased battery life"
    },
    {
        "question_text": "Which of these is a good practice for keeping personal data safe online?",
        "options": [
            "Use public Wi-Fi for sensitive transactions",
            "Share passwords with trusted colleagues",
            "Use strong, unique passwords for different accounts",
            "Keep the same password across all websites"
        ],
        "answer": "Use strong, unique passwords for different accounts"
    },
    {
        "question_text": "What is a VPN used for?",
        "options": [
            "To enhance computer performance",
            "To encrypt and secure your internet connection",
            "To check for system updates",
            "To manage user accounts"
        ],
        "answer": "To encrypt and secure your internet connection"
    },
    {
        "question_text": "What is the purpose of software updates?",
        "options": [
            "To add new features",
            "To improve the aesthetic appearance",
            "To patch vulnerabilities and fix security issues",
            "To remove unwanted files"
        ],
        "answer": "To patch vulnerabilities and fix security issues"
    },
    {
        "question_text": "Which of the following is a recommended method for protecting sensitive information on a mobile device?",
        "options": [
            "Using a simple PIN code",
            "Not locking the device at all",
            "Installing security apps and using strong passwords",
            "Sharing your password with others"
        ],
        "answer": "Installing security apps and using strong passwords"
    },
    {
        "question_text": "Which of these is an example of social engineering?",
        "options": [
            "Sending emails that appear to come from trusted sources to trick users into revealing personal information",
            "Writing complex code to hack into a system",
            "Using antivirus software to detect malware",
            "Encrypting data for secure storage"
        ],
        "answer": "Sending emails that appear to come from trusted sources to trick users into revealing personal information"
    },
    {
        "question_text": "What is ransomware?",
        "options": [
            "A type of phishing attack",
            "A software that encrypts files and demands payment for decryption",
            "A tool for creating backups",
            "A password management application"
        ],
        "answer": "A software that encrypts files and demands payment for decryption"
    },
    {
        "question_text": "Which of the following is NOT a security risk when using public Wi-Fi?",
        "options": [
            "Hackers can intercept your data",
            "Personal information can be accessed",
            "Secure connections may be made available",
            "Malware can be spread easily"
        ],
        "answer": "Secure connections may be made available"
    },
    {
        "question_text": "What is the primary purpose of encryption?",
        "options": [
            "To improve data speed",
            "To make data unreadable to unauthorized users",
            "To create backups of data",
            "To provide access control"
        ],
        "answer": "To make data unreadable to unauthorized users"
    },
    {
        "question_text": "Which of the following is a feature of a strong password?",
        "options": [
            "It contains your name",
            "It is a combination of letters, numbers, and symbols",
            "It is short and easy to remember",
            "It is the same for every account"
        ],
        "answer": "It is a combination of letters, numbers, and symbols"
    },
    {
        "question_text": "What is a secure way to dispose of sensitive information on your computer?",
        "options": [
            "Delete it and move it to the recycle bin",
            "Delete it and wipe the disk using software tools",
            "Copy it to a USB drive and dispose of the drive",
            "Leave it as it is and sell the device"
        ],
        "answer": "Delete it and wipe the disk using software tools"
    },
    {
        "question_text": "What does 'phishing' usually attempt to steal?",
        "options": [
            "Software licenses",
            "Personal and financial information",
            "Operating system updates",
            "System performance data"
        ],
        "answer": "Personal and financial information"
    },
    {
        "question_text": "What should you do if you suspect that your password has been compromised?",
        "options": [
            "Ignore it, and continue using the account",
            "Change your password immediately",
            "Tell a friend to reset the password for you",
            "Re-enter the password repeatedly"
        ],
        "answer": "Change your password immediately"
    },
    {
        "question_text": "Which of these should you NOT click on in an email or text message?",
        "options": [
            "Links from trusted senders",
            "Unexpected links or attachments from unknown sources",
            "Links with a reputable domain",
            "Links to well-known websites"
        ],
        "answer": "Unexpected links or attachments from unknown sources"
    }
    ]

    for data in questions_data:
        existing_question = Questions.query.filter_by(
            question_text=data['question_text']).first()
        if not existing_question:
            question = Questions(question_text=data['question_text'],
                                 options=data['options'], answer=data['answer'])
            db.session.add(question)

    users_data = [
        {"email": "tech@kvqaindia.com",
            "username": "tech@kvqaindia", "password": "asdfgh"}
    ]

    for data in users_data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if not existing_user:  # Only insert if email doesn't exist
            user = User(email=data['email'], username=data['username'])
            user.set_password(data['password'])  # Hash the password
            db.session.add(user)

    db.session.commit()


with app.app_context():
    # create_database()
    db.create_all()
    insert_dummy_data()


class EmailTemplate:
    def __init__(self, template_file):

        with open(template_file, 'r') as file:
            self.template = file.read()

    def generate_email(self, sender_name, sender_email, recipient_name, subject):

        email_content = self.template
        email_content = email_content.replace('{{sender_name}}', sender_name)
        email_content = email_content.replace('{{sender_email}}', sender_email)
        email_content = email_content.replace(
            '{{recipient_name}}', recipient_name)
        email_content = email_content.replace('{{subject}}', subject)

        email_content = email_content.replace('\n', '<br>')
        email_content = email_content.replace('\n\n', '</p><p>')
        email_content = f"<p>{email_content}</p>"

        return email_content


@app.route('/')
def home():
    return 'Hello World'


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'message': 'User with this email or username already exists!'}), 409

    new_user = User(email=email, username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    credentials = request.json  # Get JSON data from the request
    username = credentials.get('username')
    password = credentials.get('password')

    user = User.query.filter_by(
        username=username).first()  # Query user by username

    # Verify if user exists and check password
    if user and user.check_password(password):
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)  # Correct usage here
        }
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"message": "Login Successful", "access_token": token}), 200

    return jsonify({"message": "Invalid username or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    # JWT is stateless, just inform the client to delete the token
    return jsonify({"message": "Logged out successfully"}), 200


emailed_candidates = []


# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     request_data = request.json
#     selected_department = request_data.get('department')

#     if not selected_department:
#         return jsonify({'error': 'No department selected'}), 400

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

#     if selected_department == 'HR':
#         with open(os.path.join(templates_dir, 'hr_email_template.html')) as f:
#             email_template = f.read()
#         action_name = "Update Payroll Information"
#         email_subject = "Important: Update Your Payroll Information for Q4"
#     elif selected_department == 'Accounts':
#         with open(os.path.join(templates_dir, 'accounts_email_template.html')) as f:
#             email_template = f.read()
#         action_name = "Update Credentials"
#         email_subject = "Reminder: Update Your Credentials for Compliance"
#     # else:
#     #     with open(os.path.join(templates_dir, 'email_template.html')) as f:
#     #         email_template = f.read()
#     #     action_name = "Complete Action"
#     #     email_subject = "Action Required: Complete Task"  # Default subject

#     colleagues = Colleagues.query.all()

#     from_email = "akanuragkumar4@gmail.com"
#     password = "ibairoljmhkjmqah"

#     for colleague in colleagues:
#         # tracking_link = f"https://phishing-mail-application.onrender.com/phishing_test/{colleague.id}"
#         tracking_link = f"https://phishing-mail-frontend.vercel.app/phishing_test/{colleague.id}"
#         # tracking_link = f"http://localhost:8080/phishing_test/{colleague.id}"

#         print(f"Generated tracking link for {colleague.name}: {tracking_link}")

#         to_email = colleague.email
#         msg = MIMEMultipart('related')
#         msg['Subject'] = email_subject
#         msg['From'] = from_email
#         msg['To'] = to_email

#         body = email_template.replace("{{recipient_name}}", colleague.name)
#         body = body.replace("{{action_link}}", tracking_link)
#         body = body.replace("{{action_name}}", action_name)
#         body = body.replace("{{email_subject}}", email_subject)

#         html_content = f"""
#         <html>
#             <body>
#                 {body}
#                 <p>Best regards,</p>
#                 <img src="cid:signature_image" alt="Company Signature" />
#             </body>
#         </html>
#         """
#         msg.attach(MIMEText(html_content, 'html'))

#         signature_image_path = os.path.join('templates', 'Capture.JPG')
#         with open(signature_image_path, 'rb') as img_file:
#             img = MIMEImage(img_file.read())
#             img.add_header('Content-ID', '<signature_image>')
#             msg.attach(img)

#         try:
#             with smtplib.SMTP('smtp.gmail.com', 587) as server:
#                 server.starttls()
#                 server.login(from_email, password)
#                 server.send_message(msg)
#             print(f"Email sent to {colleague.email}")

#             emailed_candidates.append({
#                 'name': colleague.name,
#                 'email': colleague.email,
#                 'designation': colleague.designation
#             })
#             print("Emailed candidates list after sending:", emailed_candidates)

#         except Exception as e:
#             print(f"Failed to send email to {colleague.email}: {str(e)}")

#     return jsonify({'message': 'Phishing emails sent to colleagues.'})

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    global emailed_candidates
    emailed_candidates = []

    # request_data = request.json
    # selected_department = request_data.get('department')

    # if not selected_department:
    #     return jsonify({'error': 'No department selected'}), 400

    # templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    # signature_image_path = ''

    # if selected_department == 'HR, Information Security, Training and TMG':
    #     with open(os.path.join(templates_dir, 'hr_email_template.html')) as f:
    #         email_template = f.read()
    #     action_name = "Update Payroll Information"
    #     email_subject = "Update Your Payroll Information for Q4"
    #     # signature_image_path = os.path.join('templates', 'hr_signature.jpeg')

    # elif selected_department == 'Sales and Marketing, Finance, Admin':
    #     with open(os.path.join(templates_dir, 'accounts_email_template.html')) as f:
    #         email_template = f.read()
    #     action_name = "Update Credentials"
    #     email_subject = "Update Your Credentials for Compliance"
    #     # signature_image_path = os.path.join(
    #     #     'templates', 'sales_signature.jpeg')

    # elif selected_department == 'Developer and Product Development':
    #     with open(os.path.join(templates_dir, 'developer_template.html')) as f:
    #         email_template = f.read()
    #         action_name = "Download Security Patch"
    #         email_subject = "Security Patch Deployment for Development Tools"
    #         # signature_image_path = os.path.join(
    #         #     'templates', 'product_development_signature.jpeg')

    # elif selected_department == 'Leadership':
    #     with open(os.path.join(templates_dir, 'leadership_template.html')) as f:
    #         email_template = f.read()
    #         action_name = "Review Strategic Plan"
    #         email_subject = "Strategic Plan Review for Q4 - Action Required"
            # signature_image_path = os.path.join(
            #     'templates', 'leadership_signature.jpeg')
    # else:
    #     with open(os.path.join(templates_dir, 'email_template.html')) as f:
    #         email_template = f.read()
    #     action_name = "Complete Action"
    #     email_subject = "Action Required: Complete Task"  # Default subject

    colleagues = Colleagues.query.all()

    # from_email = "akanuragkumar4@gmail.com"
    # password = "ibairoljmhkjmqah"

    from_email = os.getenv('Email_Username')
    password = os.getenv('Password')
    action_name = "Exam Link"
    email_subject = "Attend Training Exam"

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

    with open(os.path.join(templates_dir, 'training_email_template.html')) as f:
        email_template = f.read()

    for colleague in colleagues:
        # tracking_link = f"https://phishing-mail-application.onrender.com/phishing_test/{colleague.id}"
        # tracking_link = f"https://phishing-mail-frontend.vercel.app/phishing_test/{colleague.id}"
        # tracking_link = f"https://phishing-mail-frontend-updated.vercel.app/phishing_test/{colleague.id}"
        tracking_link = f"https://training-exercise.vercel.app/phishing_test/{colleague.id}"
        # tracking_link = f"http://localhost:8080/phishing_test/{colleague.id}"

        print(f"Generated tracking link for {colleague.name}: {tracking_link}")

        to_email = colleague.email
        msg = MIMEMultipart('related')
        msg['Subject'] = email_subject
        msg['From'] = from_email
        msg['To'] = to_email

        body = email_template.replace("{{recipient_name}}", colleague.name)
        body = body.replace("{{action_link}}", tracking_link)
        body = body.replace("{{action_name}}", action_name)
        body = body.replace("{{email_subject}}", email_subject)

        html_content = f"""
        <html>
            <body>
                {body}
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        # signature_image_path = os.path.join('templates', 'Capture.JPG')
        # with open(signature_image_path, 'rb') as img_file:
        #     img = MIMEImage(img_file.read())
        #     img.add_header('Content-ID', '<signature_image>')
        #     msg.attach(img)

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
            print(f"Email sent to {colleague.email}")

            emailed_candidates.append({
                'name': colleague.name,
                'email': colleague.email,
                'designation': colleague.designation
            })
            print("Emailed candidates list after sending:", emailed_candidates)

        except Exception as e:
            print(f"Failed to send email to {colleague.email}: {str(e)}")

    return jsonify({'message': 'Phishing emails sent to colleagues.'})

    # Batch size for email sending
#     batch_size = 50
#     for i in range(0, len(colleagues), batch_size):
#         # Create a batch of up to 50 colleagues
#         batch = colleagues[i:i + batch_size]
#         for colleague in batch:
#             tracking_link = f"https://phishing-mail-frontend-updated.vercel.app/phishing_test/{colleague.id}"
#             to_email = colleague.email
#             msg = MIMEMultipart('related')
#             msg['Subject'] = email_subject
#             msg['From'] = from_email
#             msg['To'] = to_email

#             body = email_template.replace("{{recipient_name}}", colleague.name)
#             body = body.replace("{{action_link}}", tracking_link)
#             body = body.replace("{{action_name}}", action_name)
#             body = body.replace("{{email_subject}}", email_subject)

#             html_content = f"""
#             <html>
#                 <body>
#                     {body}
#                     <img src="cid:signature_image" alt="Company Signature" />
#                 </body>
#             </html>
#             """
#             msg.attach(MIMEText(html_content, 'html'))

#             # Attach the signature image
#             with open(signature_image_path, 'rb') as img_file:
#                 img = MIMEImage(img_file.read())
#                 img.add_header('Content-ID', '<signature_image>')
#                 msg.attach(img)

#             # Send the email
#             try:
#                 with smtplib.SMTP('smtp.gmail.com', 587) as server:
#                     server.starttls()
#                     server.login(from_email, password)
#                     server.send_message(msg)
#                 print(f"Email sent to {colleague.email}")

#                 emailed_candidates.append({
#                     'name': colleague.name,
#                     'email': colleague.email,
#                     'designation': colleague.designation
#                 })
#                 print("Emailed candidates list after sending:", emailed_candidates)

#             except Exception as e:
#                 print(f"Failed to send email to {colleague.email}: {str(e)}")

#     return jsonify({'message': 'Phishing emails sent to colleagues.'})


@app.route('/phishing_test/<int:colleague_id>', methods=['GET'])
def phishing_test(colleague_id):
    print(f'Phishing test accessed for colleague ID: {colleague_id}')

    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    return jsonify({'message': 'Tracking link accessed successfully', 'colleague_id': colleague_id})
    # return redirect(f'https://kvphishing.netlify.app/phishing_test/{colleague_id}')


@app.route('/generate_emailed_candidates_report', methods=['GET', 'POST'])
def generate_emailed_candidates_report():
    global emailed_candidates

    if not emailed_candidates:
        print("No candidates in emailed_candidates:",
              emailed_candidates)
        return jsonify({'error': 'No successfully emailed candidates.'}), 400

    print("Generating CSV for:", emailed_candidates)

    try:
        csv_file_path = "emailed_candidates_report.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'email', 'department', 'designation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(emailed_candidates)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/users')
def users():
    user = Colleagues.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'department': u.department, 'designation': u.designation} for u in user])


@app.route('/phising_click/<int:colleague_id>', methods=['POST'])
def phising_click(colleague_id):
    print(f'Received request for colleague ID: {colleague_id}')
    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    if report:
        report.clicked = True
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
    db.session.commit()

    candidate_data = {
        'id': colleague.id,
        'name': colleague.name,
        'email': colleague.email,
        'department': colleague.department,
        'designation': colleague.designation
    }

    return jsonify({'message': 'Click recorded', 'candidate': candidate_data})


@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Reports.query.all()
    report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                    'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'completion_date': r.completion_date} for r in reports]
    return jsonify(report_data)


@app.route('/phishing_opened/<int:colleague_id>', methods=['GET'])
def phishing_opened(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    print(
        f'Processing click for colleague ID: {colleague_id} | Existing report: {report}')

    if report:
        report.clicked = True
        print(f'Updated existing report for ID {colleague_id} to clicked=True')
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
        print(f'Created new report for ID {colleague_id} with clicked=True')

    db.session.commit()
    return jsonify({'message': 'Thank you for participating in our phishing awareness program.', 'showPopup': True})


# def evaluate_answers(submitted_answers):
#     questions = Questions.query.all()
#     correct_answers = [str(q.answer).strip().lower()
#                        for q in questions]
#     score = 0
#     total_questions = len(correct_answers)

#     for i, submitted_answer in enumerate(submitted_answers):
#         if i < total_questions:
#             submitted_answer = str(submitted_answer).strip().lower()
#             correct_answer = correct_answers[i]

#             print(
#                 f"Comparing submitted: '{submitted_answer}' with correct: '{correct_answer}'")

#             if submitted_answer == correct_answer:
#                 score += 1

#     return (score / total_questions) * 100 if total_questions > 0 else 0


def evaluate_answers(submitted_answers, correct_answers, questions):
    score = 0
    total_questions = len(questions)

    for i, submitted_answer in enumerate(submitted_answers):
        question_id = questions[i]['id']  # Get the question ID
        correct_answer = correct_answers.get(question_id, None)

        if correct_answer:
            # Normalize and compare answers
            submitted_answer = str(submitted_answer).strip().lower()
            correct_answer = str(correct_answer).strip().lower()

            print(
                f"Comparing submitted: '{submitted_answer}' with correct: '{correct_answer}'")

            if submitted_answer == correct_answer:
                score += 1

    return (score / total_questions) * 100 if total_questions > 0 else 0


# @app.route('/submit_answers/<int:colleague_id>', methods=['POST'])
# def submit_answers(colleague_id):
#     data = request.get_json()
#     report = Reports.query.filter_by(colleague_id=colleague_id).first()

#     if report and report.clicked:
#         report.answered = True
#         report.answers = data['answers']
#         report.score = evaluate_answers(data['answers'])
#         db.session.commit()

#         return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

#     return jsonify({'error': 'User did not click the phishing link.'}), 400


# @app.route('/submit_answers/<int:colleague_id>', methods=['POST'])
# def submit_answers(colleague_id):
#     data = request.get_json()
#     report = Reports.query.filter_by(colleague_id=colleague_id).first()

#     if report and report.clicked:
#         report.answered = True
#         report.answers = data['answers']
#         report.score = evaluate_answers(data['answers'])
#         report.status = "Completed" if report.score >= 70 else "Pending"
#         db.session.commit()

#         study_material_link = f"https://phishing-mail-frontend-updated.vercel.app/study-material/{colleague_id}"

#         if report.score >= 70:
#             subject = "Congratulations on Completing the Training Program!"
#             body = f"Dear {report.colleague.name},\n\nYou have successfully completed the training program with a score of {report.score}%."
#         else:
#             subject = "Reattempt the Training Program"
#             body = f"Dear {report.colleague.name},\n\nUnfortunately, you did not pass the training program. Please reattempt it by following the link provided:\n\n<a href=\"{study_material_link}\">Reattempt</a>\n\nScore: {report.score}%."

#         # Call `send_result_email` with the colleague's email, subject, and body
#         send_result_email(report.colleague.email, subject, body)

#         return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

#     return jsonify({'error': 'User did not click the phishing link.'}), 400


# @app.route('/submit_answers/<int:colleague_id>', methods=['POST'])
# def submit_answers(colleague_id):
#     data = request.get_json()
#     report = Reports.query.filter_by(colleague_id=colleague_id).first()

#     if report and report.clicked:
#         report.answered = True
#         report.answers = data['answers']
#         report.score = evaluate_answers(data['answers'])
#         report.status = "Completed" if report.score >= 70 else "Pending"
#         report.completion_date = datetime.now()
#         db.session.commit()

#         study_material_link = f"https://phishing-mail-frontend-updated.vercel.app/study-material/{colleague_id}"

#         if report.score >= 70:
#             subject = "Congratulations on Completing the Training Program!"
#             body = f"Dear {report.colleague.name},\n\nYou have successfully completed the training program with a score of {report.score}%."
#         else:
#             subject = "Reattempt the Training Program"
#             body = f"""Dear {report.colleague.name},<br><br>
#                     Unfortunately, you did not pass the training program. Please reattempt it by following the link provided:<br><br>
#                     <a href="{study_material_link}">Reattempt</a><br><br>
#                     Score: {report.score}%."""

#         send_result_email(report.colleague.email, subject, body)

#         return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

#     return jsonify({'error': 'User did not click the phishing link.'}), 400


@app.route('/submit_answers/<int:colleague_id>', methods=['POST'])
def submit_answers(colleague_id):
    data = request.get_json()
    report = Reports.query.filter_by(colleague_id=colleague_id).first()

    if report and report.clicked:
        report.answered = True
        report.answers = data['answers']

        # We need to store the correct answers with the corresponding question IDs
        correct_answers = {question['id']: question['answer']
                           for question in data['questions']}  # Using the received questions with answers

        # Evaluate the score using the submitted answers and the corresponding correct answers
        report.score = evaluate_answers(
            data['answers'], correct_answers, data['questions'])
        print(report.score)
        report.status = "Completed" if report.score >= 70 else "Pending"
        report.completion_date = datetime.now()
        db.session.commit()

        # study_material_link = f"https://phishing-mail-frontend-updated.vercel.app/study-material/{colleague_id}"
        study_material_link = f"http://localhost:8080/study-material/{colleague_id}"

        if report.score >= 70:
            subject = "Congratulations on Completing the Training Program!"
            body = f"Dear {report.colleague.name},\n\nYou have successfully completed the training program with a score of {report.score}%."
        else:
            subject = "Reattempt the Training Program"
            body = f"""Dear {report.colleague.name},<br><br>
                    Unfortunately, you did not pass the training program. Please reattempt it by following the link provided:<br><br>
                    <a href="{study_material_link}">Reattempt</a><br><br>
                    Score: {report.score}%."""

        send_result_email(report.colleague.email, subject, body)

        return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

    return jsonify({'error': 'User did not click the phishing link.'}), 400


@app.route('/generate_reports', methods=['GET', 'POST'])
def generate_reports():
    try:
        reports = Reports.query.all()
        report_data = []

        for report in reports:
            colleague = Colleagues.query.get(report.colleague_id)
            report_entry = {
                'Colleague Name': colleague.name,
                'Colleague Email': colleague.email,
                'Department': colleague.department,
                'Designation': colleague.designation,
                'Link Clicked': 'Yes' if report.clicked else 'No',
                # 'Answered': report.answered,
                'Score': report.score,
                'Status': report.status,
                'Completion Date': report.completion_date.strftime('%Y-%m-%d') if report.completion_date else None,
            }
            report_data.append(report_entry)

        csv_file_path = "candidate_reports.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Colleague Name', 'Colleague Email', 'Department',
                          'Designation', 'Link Clicked', 'Score',
                          'Status', 'Completion Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in report_data:
                writer.writerow(data)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_report/<int:colleague_id>', methods=['GET'])
def download_report(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    colleague = Colleagues.query.get(colleague_id)

    if not report or not colleague:
        return jsonify({'error': 'Report or colleague not found.'}), 404

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 770, "Phishing Awareness Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 740, f"Report for: {colleague.name}")
    pdf.drawString(100, 720, f"Email: {colleague.email}")
    pdf.drawString(100, 700, f"Department: {colleague.department}")

    pdf.setLineWidth(1)
    pdf.line(100, 690, 500, 690)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 670, "Phishing Email Status:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, 650, f"Clicked: {'Yes' if report.clicked else 'No'}")
    pdf.drawString(120, 630, f"Answered: {'Yes' if report.answered else 'No'}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 600, "Answers Provided:")

    pdf.setFont("Helvetica", 12)
    y_position = 580
    if report.answers:
        for i, answer in enumerate(report.answers, start=1):
            pdf.drawString(120, y_position, f"Q{i}: {answer}")
            y_position -= 20
    else:
        pdf.drawString(120, y_position, "No answers submitted")
        y_position -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, y_position - 20, "Overall Performance:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, y_position - 40,
                   f"Score: {report.score if report.score else 0}")

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(100, 50, "Generated on: " +
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=f'report_{colleague_id}.pdf', mimetype='application/pdf')


@app.route('/upload_colleagues_data', methods=['POST'])
def upload_colleagues_data():
    try:
        db.session.query(Colleagues).delete()

        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                colleague = Colleagues(
                    name=row['Full Name'],
                    email=row['Work Email'],
                    department=row['Department'],
                    designation=row['Job Title']
                )
                db.session.add(colleague)

            db.session.commit()
            return jsonify({'message': 'Data uploaded successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format. Please upload an .xlsx file.'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error processing file: {str(e)}'}), 500


@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([{
        'id': question.id,
        'question_text': question.question_text,
        'options': question.options,
        'answer': question.answer
    } for question in questions])


@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        return jsonify({
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'answer': question.answer
        })
    return jsonify({'error': 'Question not found!'}), 404


@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    new_question = Questions(
        question_text=data['question_text'],
        options=data['options'],
        answer=data['answer']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added!', 'id': new_question.id}), 201


@app.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    print(f"Updating question ID: {question_id}")
    data = request.json
    print(f"Received data: {data}")

    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    question.question_text = data['question_text']
    question.options = data['options']
    question.answer = data['answer']
    db.session.commit()
    return jsonify({'message': 'Question updated!'})


@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted!'})


@app.route('/download_certificate/<int:colleague_id>')
def download_certificate(colleague_id):
    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return abort(404)

    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    if not report:
        return abort(404)

    score = report.score

    pdf_path = f"certificate_{colleague.name.replace(' ', '_')}.pdf"

    if not os.path.exists('certificates'):
        os.makedirs('certificates')

    if not os.path.exists(pdf_path):
        generate_certificate(colleague.name, score)

    if not os.path.exists(pdf_path):
        return abort(404)

    return send_file(pdf_path, as_attachment=True)


def generate_certificate(candidate_name, score):
    candidate_name_safe = candidate_name.replace(" ", "_")
    pdf_file_path = f"certificate_{candidate_name_safe}.pdf"

    document = SimpleDocTemplate(pdf_file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    title = Paragraph("Certificate of Completion", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 20))

    name = Paragraph(
        f"This certifies that <b>{candidate_name}</b>", styles['Normal'])
    content.append(name)
    content.append(Spacer(1, 20))

    score_paragraph = Paragraph(
        f"Has successfully completed the quiz with a score of <b>{score}%</b>.", styles['Normal'])
    content.append(score_paragraph)
    content.append(Spacer(1, 20))

    footer = Paragraph("Thank you for your participation!", styles['Normal'])
    content.append(footer)

    document.build(content)
    print(f"Generated PDF at: {pdf_file_path}")


# @app.route('/update_report_status/<int:colleague_id>', methods=['POST'])
# def update_report_status(colleague_id):
#     data = request.get_json()
#     status = data.get('status')

#     report = Reports.query.filter_by(colleague_id=colleague_id).first()
#     if report:
#         report.status = status
#         db.session.commit()
#         return jsonify({'message': 'Status updated successfully'}), 200
#     else:
#         return jsonify({'message': 'Report not found'}), 404


@app.route('/update_report_status/<colleague_id>', methods=['POST'])
def update_report_status(colleague_id):
    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    try:
        # Log the incoming data
        print(
            f"Updating report for colleague_id: {colleague_id} with score: {score}")

        # Fetch the report for the given colleague_id
        report = Reports.query.filter_by(colleague_id=colleague_id).first()

        if report:
            report.score = score
            db.session.commit()
            return jsonify({'message': 'Score updated successfully'})
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        print(f"Error updating report: {e}")  # Log the error to console
        return jsonify({'error': str(e)}), 500


@app.route('/send_result_email', methods=['POST'])
def send_result_email():
    data = request.get_json()

    colleague_email = data.get('colleague_id')
    subject = data.get('subject')
    body = data.get('body')

    if colleague_email and subject and body:
        send_result_email(colleague_email, subject, body)
        return jsonify({'message': 'Email sent successfully.'}), 200
    else:
        return jsonify({'error': 'Missing required fields.'}), 400


def send_result_email(colleague_email, subject, body):

    from_email = os.getenv('Email_Username')
    password = os.getenv('Password')


    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = colleague_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, colleague_email, msg.as_string())
        print(f"Email sent to {colleague_email}")

    except Exception as e:
        print(f"Failed to send email to {colleague_email}: {str(e)}")


@app.route('/send_reminder/<int:report_id>', methods=['POST'])
def send_reminder(report_id):
    report = Reports.query.get(report_id)
    if report:

        if report.status in ['Pending', 'Training Completed']:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            from_email = os.getenv('Email_Username')
            password = os.getenv('Password')

            colleague_email = report.colleague.email
            colleague_id = report.colleague_id

            # study_material_link = f"https://phishing-mail-frontend-updated.vercel.app/study-material/{colleague_id}"
            study_material_link = f"http://localhost:8080/study-material/{colleague_id}"

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = colleague_email
            msg['Subject'] = "Reminder: Complete Your Training"

            # body = f"Dear {report.colleague.name},\n\nThis is a reminder to complete your training."

            body = f"""
            Dear {report.colleague.name},<br><br>
            This is a reminder to complete your training.<br><br>
            Please click the link below to access the study material:<br>
            <a href="{study_material_link}">Study Material</a><br><br>
            """
            msg.attach(MIMEText(body, 'html'))

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(from_email, password)
                    server.send_message(msg)
                return jsonify({"message": "Reminder email sent successfully!"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"message": "Status is not Pending or Training Completed."}), 400
    else:
        return jsonify({"message": "Report not found."}), 404


@app.route('/get_random_questions', methods=['GET'])
def get_random_questions():
    try:
        # Fetch 10 random questions from the database
        questions = Questions.query.order_by(func.random()).limit(10).all()
        questions_data = [{
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'answer': question.answer
        } for question in questions]

        return jsonify({'questions': questions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_all_reports', methods=['GET'])
def get_all_reports():
    try:
        reports = Reports.query.all()
        report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                        'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'completion_date': r.completion_date} for r in reports]
        return jsonify({'reports': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
