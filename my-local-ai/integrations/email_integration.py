import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
from datetime import datetime

class EmailIntegration:
    """Email integration for Orion."""
    
    def __init__(self, email, password, imap_server="imap.gmail.com", smtp_server="smtp.gmail.com"):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
    
    def send_email(self, to, subject, body):
        """Send email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, 587)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return {"success": True, "message": f"Email sent to {to}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recent_emails(self, limit=5):
        """Get recent emails."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            mail.select('INBOX')
            
            status, messages = mail.search(None, 'ALL')
            message_ids = messages[0].split()[-limit:]
            
            emails = []
            for msg_id in message_ids:
                status, msg = mail.fetch(msg_id, '(RFC822)')
                email_data = {}
                
                try:
                    from email import message_from_bytes
                    email_msg = message_from_bytes(msg[0][1])
                    
                    emails.append({
                        "from": email_msg.get('From'),
                        "subject": email_msg.get('Subject'),
                        "date": email_msg.get('Date'),
                        "snippet": str(email_msg.get_payload())[:200]
                    })
                except:
                    pass
            
            mail.close()
            mail.logout()
            
            return emails
        except Exception as e:
            return {"error": str(e)}
