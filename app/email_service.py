# app/email_service.py - UPDATED FOR RESEND API
import os
import logging
from typing import Tuple, Optional
import resend

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResendEmailService:
    def __init__(self):
        # Get Resend API key from environment
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("RESEND_FROM", "onboarding@resend.dev")
        
        # Configure Resend
        if self.api_key:
            resend.api_key = self.api_key
        else:
            logger.warning("⚠️ RESEND_API_KEY not found in environment variables")
        
        logger.info("=" * 60)
        logger.info("📧 EMAIL SERVICE - RESEND API VERSION")
        logger.info("🔧 Using Resend API (No SMTP ports needed)")
        logger.info(f"🔐 API Key: {'SET' if self.api_key else 'NOT SET'}")
        logger.info(f"📤 From Email: {self.from_email}")
        logger.info(f"🌐 Service URL: https://fyp-auth-api.onrender.com")
        logger.info("=" * 60)
    
    def send_email(self, to_email: str, subject: str, content: str) -> Tuple[int, str]:
        """
        Send email using Resend API
        Returns: (status_code, response_text)
        """
        try:
            logger.info(f"📨 Sending email via Resend to: {to_email}")
            logger.info(f"📝 Subject: {subject}")
            
            # Make API call to Resend
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "text": content
            }
            
            response = resend.Emails.send(params)
            
            logger.info(f"📊 Resend Response: Email ID: {response.get('id', 'Unknown')}")
            logger.info("✅ Email accepted by Resend for delivery")
            
            return 202, f"Email queued: {response.get('id', 'Unknown')}"
            
        except resend.ResendError as e:
            logger.error(f"❌ Resend API Error: {e}")
            return 500, f"Resend Error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return 500, f"Unexpected error: {str(e)}"
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """
        Send password reset email with reset token using Resend
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 SENDING PASSWORD RESET EMAIL")
        logger.info(f"📧 To: {to_email}")
        logger.info(f"👤 User: {user_name}")
        logger.info(f"🔢 Token: {reset_token}")
        logger.info(f"🔄 Using Resend API")
        logger.info(f"{'='*60}")
        
        # Check if API key is configured
        if not self.api_key:
            logger.error("❌ Resend API Key not configured!")
            logger.info(f"📝 Token for debugging: {reset_token}")
            return False
        
        # Create email content
        subject = "Password Reset Code - Sure Step App"
        
        text_content = f"""Password Reset Request

Hello {user_name},

You requested a password reset for your Sure Step account.

Your reset code is: {reset_token}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Thanks,
Sure Step Team
"""
        
        # Send email using Resend API
        status_code, response_text = self.send_email(to_email, subject, text_content)
        
        # Check if email was successfully sent
        if status_code == 202:
            logger.info(f"🎉 Password reset email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"❌ Failed to send email. Status: {status_code}")
            logger.error(f"📝 Response: {response_text}")
            logger.info(f"📝 Token for debugging: {reset_token}")
            return False
    
    def get_configuration_status(self) -> dict:
        """Return email service configuration status"""
        return {
            "service": "Resend API",
            "configured": bool(self.api_key),
            "api_key_set": bool(self.api_key),
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "from_email": self.from_email,
            "uses_smtp": False,
            "uses_api": True,
            "port_requirements": "None (API based)",
            "render_compatible": True,
            "service_url": "https://fyp-auth-api.onrender.com"
        }


# Global instance
email_service = ResendEmailService()