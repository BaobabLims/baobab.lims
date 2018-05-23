from Products.CMFCore.WorkflowCore import WorkflowException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from bika.lims import logger


def send_mail(obj, sender, receiver, subject="", body=""):
    """Send email from sender to receiver
    """
    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = subject
    mime_msg['From'] = sender
    mime_msg['To'] = receiver
    msg_txt = MIMEText(body, 'plain')
    mime_msg.attach(msg_txt)
    try:
        host = getToolByName(obj, 'MailHost')
        host.send(mime_msg.as_string(), immediate=True)
    except SMTPServerDisconnected as msg:
        logger.warn("SMTPServerDisconnected: %s." % msg)
    except SMTPRecipientsRefused as msg:
        raise WorkflowException(str(msg))
