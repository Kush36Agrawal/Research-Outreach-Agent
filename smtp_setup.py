import os
import dotenv
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

dotenv.load_dotenv()

csv_file = 'final_df.csv'  # Path to your CSV file
email_data = pd.read_csv(csv_file)

# Gmail SMTP server details
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Replace with your email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to_email, subject, message, from_email=EMAIL_ADDRESS):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Connect to the Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to your Gmail account
            server.send_message(msg)  # Send the email
        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

for index, row in email_data.iterrows():
    subject = row['Email Body'].split("\n")[0].replace("Subject:", "").strip()
    recipient_name = row['Professor Name']
    # recipient_email = row['Email Address']
    recipient_email = os.getenv("Your_Email")
    body_start_index = row['Email Body'].find("\n") + 1
    message = row['Email Body'][body_start_index:].strip()
    send_email(recipient_email, subject, message)