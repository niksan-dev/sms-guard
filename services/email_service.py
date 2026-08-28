import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_ADDRESS = os.getenv(
    "GMAIL_ADDRESS"
)

GMAIL_APP_PASSWORD = os.getenv(
    "GMAIL_APP_PASSWORD"
)

GMAIL_SENDER_NAME = os.getenv(
    "GMAIL_SENDER_NAME",
    "Security Management System"
)


# ============================================================
# SEND EMAIL
# ============================================================

def send_email_with_pdf(
    recipient_email,
    subject,
    body,
    pdf_data,
    pdf_filename
):

    try:

        # ----------------------------------------------------
        # VALIDATE CONFIGURATION
        # ----------------------------------------------------

        if not GMAIL_ADDRESS:

            return (
                False,
                "GMAIL_ADDRESS is not configured."
            )

        if not GMAIL_APP_PASSWORD:

            return (
                False,
                "GMAIL_APP_PASSWORD is not configured."
            )

        # ----------------------------------------------------
        # VALIDATE RECIPIENT
        # ----------------------------------------------------

        recipient_email = (
            str(recipient_email or "")
            .strip()
        )

        if not recipient_email:

            return (
                False,
                "Recipient email address is required."
            )

        # ----------------------------------------------------
        # CREATE EMAIL
        # ----------------------------------------------------

        message = EmailMessage()

        message["From"] = (
            f"{GMAIL_SENDER_NAME} "
            f"<{GMAIL_ADDRESS}>"
        )

        message["To"] = recipient_email

        message["Subject"] = subject

        message.set_content(body)

        # ----------------------------------------------------
        # ATTACH PDF
        # ----------------------------------------------------

        message.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=pdf_filename
        )

        # ----------------------------------------------------
        # CONNECT TO GMAIL
        # ----------------------------------------------------

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as smtp:

            smtp.ehlo()

            smtp.starttls()

            smtp.ehlo()

            smtp.login(
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD
            )

            smtp.send_message(
                message
            )

        return (
            True,
            "Email sent successfully."
        )

    except smtplib.SMTPAuthenticationError:

        return (
            False,
            "Gmail authentication failed. "
            "Check your Gmail address and App Password."
        )

    except smtplib.SMTPException as e:

        return (
            False,
            f"Gmail SMTP error: {str(e)}"
        )

    except Exception as e:

        return (
            False,
            f"Unable to send email: {str(e)}"
        )