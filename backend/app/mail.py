import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class EmailConfig:
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@example.com")
    DEV_MODE: bool = os.getenv("DEV_MODE", "1") == "1"

async def send_mail(
    to: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
):
    """
    Send an email using SMTP in PROD or log in DEV.
    
    Args:
        to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional)
        cc: Carbon copy recipients (optional)
        bcc: Blind carbon copy recipients (optional)
    """
    config = EmailConfig()
    
    if config.DEV_MODE or not config.SMTP_HOST:
        logger.info(f"DEV MODE: Email would be sent")
        logger.info(f"To: {to}")
        if cc:
            logger.info(f"CC: {', '.join(cc)}")
        if bcc:
            logger.info(f"BCC: {', '.join(bcc)}")
        logger.info(f"Subject: {subject}")
        logger.info(f"HTML Content: {html_content[:100]}...")
        if text_content:
            logger.info(f"Text Content: {text_content[:100]}...")
        return
    
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.MAIL_FROM
        msg["To"] = to
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)
        
        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.sendmail(config.MAIL_FROM, recipients, msg.as_string())
            
        logger.info(f"Email sent to {to}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise
