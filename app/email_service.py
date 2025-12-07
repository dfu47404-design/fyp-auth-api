
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

class EmailService:
    def __init__(self):
        # For production, use environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@yourapp.com")
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """
        Send password reset email with reset token/link
        """
        try:
            # Reset link (for web interface - Android app will handle differently)
            reset_link = f"https://your-app.com/reset-password?token={reset_token}"
            
            # Email content
            subject = "Password Reset Request - FYP App"
            
            # HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .token {{ background-color: #eee; padding: 10px; font-family: monospace; margin: 10px 0; }}
                    .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Password Reset Request</h2>
                    </div>
                    <div class="content">
                        <p>Hello {user_name},</p>
                        <p>We received a request to reset your password for your FYP App account.</p>
                        <p>Your password reset token is:</p>
                        <div class="token"><strong>{reset_token}</strong></div>
                        <p>Or click the button below to reset your password:</p>
                        <a href="{reset_link}" class="button">Reset Password</a>
                        <p>This token will expire in 15 minutes.</p>
                        <p>If you didn't request a password reset, please ignore this email.</p>
                        <p>Best regards,<br>FYP App Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Password Reset Request
            
            Hello {user_name},
            
            We received a request to reset your password for your FYP App account.
            
            Your password reset token is: {reset_token}
            
            This token will expire in 15 minutes.
            
            If you didn't request a password reset, please ignore this email.
            
            Best regards,
            FYP App Team
            """
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Attach both HTML and plain text
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            if self.smtp_username and self.smtp_password:
                # Real SMTP server
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # Development: Print token instead of sending email
                print(f"🔐 DEV MODE: Password reset token for {to_email}: {reset_token}")
                print(f"📧 Email would be sent with token: {reset_token}")
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

# Global instance
email_service = EmailService()