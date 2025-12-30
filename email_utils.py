import imaplib
import email
from email.header import decode_header
import datetime

def connect_imap(server, email_id, email_pw):
    """
    Connects to the IMAP server and logs in.
    """
    imap_host = "imap.gmail.com" if server == "gmail" else "outlook.office365.com"
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(email_id, email_pw)
        return mail
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def get_email_body(msg):
    """
    Extracts the plain text body from the email message.
    """
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except:
            pass
    return body

def fetch_emails(mail, folder="INBOX", limit=10, search_criteria="ALL"):
    """
    Fetches the latest emails from the specified folder.
    """
    emails_list = []
    try:
        mail.select(folder)
        # Search for emails
        status, messages = mail.search(None, search_criteria)
        if status != "OK":
            return []

        email_ids = messages[0].split()
        # Get the latest 'limit' emails
        latest_email_ids = email_ids[-limit:]
        
        # Fetch in reverse order (newest first)
        for e_id in reversed(latest_email_ids):
            try:
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode Subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        # Decode Sender
                        sender = msg.get("From")
                        
                        # Get Date
                        date_str = msg.get("Date")

                        # Get Body
                        body = get_email_body(msg)

                        emails_list.append({
                            "id": e_id.decode(),
                            "subject": subject,
                            "sender": sender,
                            "date": date_str,
                            "body": body[:500] + "..." if len(body) > 500 else body, # Truncate for preview
                            "full_body": body
                        })
            except Exception as e:
                print(f"Error fetching email {e_id}: {e}")
                continue
                
    except Exception as e:
        print(f"Error in fetch_emails: {e}")
        
    return emails_list
