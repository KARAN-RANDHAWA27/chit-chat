import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

smtp_server = os.getenv('EMAIL_HOST')
port = int(os.getenv('EMAIL_PORT'))
sender_email = os.getenv('EMAIL_HOST_USER')
password = os.getenv('EMAIL_HOST_PASSWORD')

receiver_email = "karandeeprandhawa27@gmail.com"  # Replace with your personal email for testing
message = MIMEMultipart("alternative")
message["Subject"] = "Test email from Python"
message["From"] = sender_email
message["To"] = receiver_email

text = "This is a test email sent from Python."
part1 = MIMEText(text, "plain")
message.attach(part1)

try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("Test email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")
finally:
    server.quit()
