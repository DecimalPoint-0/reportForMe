"""
Email Delivery Service
Handles sending reports via email
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from core.models import Report, DeliveryLog
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service to send reports via email"""

    @staticmethod
    def send_report(report: Report) -> bool:
        """
        Send report via email
        
        Args:
            report: Report model instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            recipient_email = report.user_config.email
            subject = f"📊 Daily Work Report — {report.report_date.strftime('%d %b %Y')}"

            # Create email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=report.content_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )

            # Attach HTML version
            msg.attach_alternative(report.content_html, "text/html")

            # Send email
            result = msg.send()

            if result > 0:
                # Log successful delivery
                DeliveryLog.objects.create(
                    report=report,
                    channel='email',
                    recipient=recipient_email,
                    status='success'
                )
                logger.info(f"Sent report {report.id} to {recipient_email}")
                return True
            else:
                raise Exception("Failed to send email (0 recipients)")

        except Exception as e:
            logger.error(f"Error sending email report {report.id}: {str(e)}")

            # Log failed delivery
            DeliveryLog.objects.create(
                report=report,
                channel='email',
                recipient=report.user_config.email,
                status='failed',
                error_message=str(e)
            )

            return False

    @staticmethod
    def send_test_email(recipient_email: str) -> bool:
        """
        Send a test email to verify configuration
        
        Args:
            recipient_email: Email address to send to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            subject = "🧪 ReportForMe — Test Email"
            message = """Hello! 

This is a test email from ReportForMe. Your email configuration is working correctly.

Your daily work reports will be delivered to this inbox at your configured time.

Best regards,
ReportForMe Team
"""

            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )

            html_message = f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #333;">
    <h2>🧪 ReportForMe — Test Email</h2>
    <p>Hello!</p>
    <p>This is a test email from <strong>ReportForMe</strong>. Your email configuration is working correctly.</p>
    <p>Your daily work reports will be delivered to this inbox at your configured time.</p>
    <p>Best regards,<br><strong>ReportForMe Team</strong></p>
</body>
</html>
            """

            msg.attach_alternative(html_message, "text/html")
            result = msg.send()

            return result > 0

        except Exception as e:
            logger.error(f"Error sending test email to {recipient_email}: {str(e)}")
            return False
