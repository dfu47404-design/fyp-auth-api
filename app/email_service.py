# app/email_service.py - SIMPLIFIED
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Get environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "")
        
        logger.info("=" * 50)
        logger.info("EMAIL SERVICE INITIALIZATION")
        logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"Username: {'SET' if self.smtp_username else 'NOT SET'}")
        logger.info(f"Password: {'SET' if self.smtp_password else 'NOT SET'}")
        logger.info(f"From Email: {self.from_email}")
        logger.info("=" * 50)
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """
        Send password reset email with reset token
        """
        logger.info(f"🔐 Sending reset email to: {to_email}")
        logger.info(f"📧 Reset Token: {reset_token}")
        logger.info(f"👤 User: {user_name}")
        
        # If email not configured, just log and return success for development
        if not self.smtp_username or not self.smtp_password:
            logger.warning("⚠️ Email credentials not configured. Running in DEV MODE.")
            logger.warning(f"📧 TOKEN for {to_email}: {reset_token}")
            logger.warning(f"User would receive: Your reset code is {reset_token}")
            logger.warning("Set SMTP_USERNAME and SMTP_PASSWORD in .env to send real emails")
            return True
        
        try:
            # Create simple email
            subject = "Password Reset Code - Sure Step App"
            
            # Simple text email
            text_content = f"""
            Password Reset Request
            
            Hello {user_name},
            
            You requested a password reset for your Sure Step account.
            
            Your reset code is: {reset_token}
            
            This code will expire in 15 minutes.
            
            If you didn't request this, please ignore this email.
            
            Thanks,
            Sure Step Team
            """
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Attach text version
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            
            # Try to send email
            logger.info(f"📤 Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            logger.info("🔑 Logging in to SMTP server...")
            server.login(self.smtp_username, self.smtp_password)
            
            logger.info(f"📨 Sending email to {to_email}...")
            server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            logger.error(f"📧 Token for {to_email}: {reset_token}")  # Still log the token
            return False
    
    def get_configuration_status(self) -> dict:
        """Return email service configuration status"""
        return {
            "configured": bool(self.smtp_username and self.smtp_password),
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username[:3] + "***" if self.smtp_username else "NOT SET",
            "from_email": self.from_email,
        }


# Global instance
email_service = EmailService()