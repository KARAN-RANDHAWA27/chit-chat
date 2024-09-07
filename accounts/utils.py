from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_otp_email(user):
    subject = 'Verify Your Chit Chat Account'
    html_message = render_to_string('accounts/email/otp_email.html', {'user': user, 'otp': user.otp})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    print(f"Sending OTP email to {to_email}")  # Add this line

    try:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        print("Email sent successfully")  # Add this line
    except Exception as e:
        print(f"Error sending email: {str(e)}")  # Add this line