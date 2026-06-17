import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from io import BytesIO

logger = logging.getLogger(__name__)


def _build_email_message(pdf_buffer: BytesIO, recipient_email: str, industry: str) -> MIMEMultipart:
    message = MIMEMultipart()
    message["From"] = os.getenv("EMAIL_SENDER")
    message["To"] = recipient_email
    message["Subject"] = f"Competitor Analysis Report for {industry}"

    pdf_buffer.seek(0)
    attachment = MIMEApplication(pdf_buffer.read(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename="competitor_analysis_report.pdf")
    message.attach(attachment)
    return message


def send_email_with_pdf(pdf_buffer: BytesIO, recipient_email: str, industry: str) -> None:
    """Send the PDF report as an email attachment.

    Args:
        pdf_buffer: Rendered PDF as a BytesIO object
        recipient_email: Destination email address
        industry: Industry label used in the email subject line
    """
    logger.info(f"Sending email to {recipient_email}")
    message = _build_email_message(pdf_buffer, recipient_email, industry)
    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(message)
        logger.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise RuntimeError(f"Failed to send email: {e}") from e
