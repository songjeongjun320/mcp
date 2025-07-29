"""Mail to tool module."""

from typing import Optional, Dict, Any
import os
from datetime import datetime

def mail_to(recipient: str, subject: str, body: str, attachment_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Send email messages to specified recipients

    Parameters
    ----------
        recipient (str): Email address of the recipient
        subject (str): Subject line of the email
        body (str): Email message body content
        attachment_path (Optional[str]): Optional path to file attachment

    Returns
    -------
    Dict[str, Any]
        Result of the email sending operation.
    """
    try:
        # Validate email format (basic validation)
        if "@" not in recipient or "." not in recipient.split("@")[-1]:
            raise ValueError("Invalid email address format")
        
        # Check attachment if provided
        attachment_info = None
        if attachment_path:
            if os.path.exists(attachment_path):
                file_size = os.path.getsize(attachment_path)
                attachment_info = {
                    "path": attachment_path,
                    "filename": os.path.basename(attachment_path),
                    "size_bytes": file_size
                }
            else:
                return {
                    "success": False,
                    "error": f"Attachment file not found: {attachment_path}",
                    "operation": "mail_to"
                }
        
        # Simulate email sending (in real implementation, use SMTP)
        timestamp = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Email sent successfully (simulated)",
            "email_details": {
                "to": recipient,
                "subject": subject,
                "body_length": len(body),
                "attachment": attachment_info,
                "timestamp": timestamp
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "operation": "mail_to",
            "inputs": {
                "recipient": recipient,
                "subject": subject,
                "attachment_path": attachment_path
            }
        }
