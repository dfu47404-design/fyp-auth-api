# app/email_service.py - UPDATED FOR PORT 465 SSL
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Get environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))  # Changed default to 465
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "")
        
        logger.info("=" * 60)
        logger.info("📧 EMAIL SERVICE - PORT 465 SSL VERSION")
        logger.info(f"🔧 SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"🔐 Using SSL on port: {self.smtp_port}")
        logger.info(f"👤 Username: {'SET' if self.smtp_username else 'NOT SET'}")
        logger.info(f"📤 From Email: {self.from_email}")
        logger.info("=" * 60)
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """
        Send password reset email with reset token using SSL on port 465
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 STARTING EMAIL SEND (SSL Port 465)")
        logger.info(f"📧 To: {to_email}")
        logger.info(f"🔢 Token: {reset_token}")
        logger.info(f"👤 User: {user_name}")
        logger.info(f"{'='*60}")
        
        # Check credentials
        if not self.smtp_username or not self.smtp_password:
            logger.error("❌ SMTP credentials not configured!")
            logger.info(f"📝 Token for debugging: {reset_token}")
            return False
        
        try:
            # Create email content
            subject = "Password Reset Code - Sure Step App"
            
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
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            
            # 🔄 CRITICAL CHANGE: Use SMTP_SSL for port 465
            logger.info(f"🔗 Connecting with SSL to: {self.smtp_server}:{self.smtp_port}")
            
            # Method 1: Simple SMTP_SSL (recommended for Gmail)
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context, timeout=30)
            
            logger.info("✅ SSL Connection established")
            
            # Login (no need for starttls with SMTP_SSL)
            logger.info(f"🔑 Logging in as: {self.smtp_username}")
            server.login(self.smtp_username, self.smtp_password)
            logger.info("✅ Login successful")
            
            # Send email
            logger.info(f"📨 Sending email to {to_email}...")
            server.sendmail(self.from_email, [to_email], msg.as_string())
            logger.info("✅ Email sent to server")
            
            # Quit
            server.quit()
            logger.info("✅ Connection closed")
            
            logger.info(f"🎉 EMAIL SENT SUCCESSFULLY to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as auth_error:
            logger.error(f"❌ SMTP AUTHENTICATION FAILED: {auth_error}")
            logger.error("🔑 This usually means:")
            logger.error("1. Wrong password (use 16-char App Password)")
            logger.error("2. 2FA not enabled or app password incorrect")
            logger.error(f"📝 Token for {to_email}: {reset_token}")
            return False
            
        except ConnectionRefusedError as conn_error:
            logger.error(f"❌ CONNECTION REFUSED: {conn_error}")
            logger.error("🌐 Port 465 is also blocked by Render Free tier")
            logger.error("💡 Try SendGrid or upgrade to paid plan")
            logger.error(f"📝 Token for {to_email}: {reset_token}")
            return False
            
        except Exception as e:
            logger.error(f"❌ UNEXPECTED ERROR: {type(e).__name__}")
            logger.error(f"📝 Message: {str(e)}")
            logger.error(f"🔍 Traceback:\n{traceback.format_exc()}")
            logger.error(f"📝 Token for {to_email}: {reset_token}")
            return False
    
    def get_configuration_status(self) -> dict:
        """Return email service configuration status"""
        return {
            "configured": bool(self.smtp_username and self.smtp_password),
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username[:3] + "***" if self.smtp_username else "NOT SET",
            "username_length": len(self.smtp_username) if self.smtp_username else 0,
            "password_set": bool(self.smtp_password),
            "from_email": self.from_email,
            "using_ssl": True if self.smtp_port == 465 else False,
        }


# Global instance
email_service = EmailService()