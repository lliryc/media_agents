import smtplib
import os
import dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import logging_init

# Initialize logger
logger = logging.getLogger(__name__)

# Load env vars
dotenv.load_dotenv()

# Init smtp params
smtp_host = str(os.getenv('SMTP_SERVER'))
smtp_port = int(os.getenv('SMTP_PORT_SSL'))
smtp_user = str(os.getenv('SMTP_USER'))
smtp_password = str(os.getenv('SMTP_PASSWORD'))
def send_email(subject, html_body, txt_body, recipients):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ', '.join(recipients)

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(html_body, 'html')
    part1 = MIMEText(txt_body, 'plain')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    for recipient in recipients:
        try:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp_server:
               smtp_server.login(smtp_user, smtp_password)
               smtp_server.sendmail(smtp_user, recipient, msg.as_string())
        except Exception as ex:
            logger.error('Error: sending email')
            logger.error(ex)
        logger.info("Message with subject")

