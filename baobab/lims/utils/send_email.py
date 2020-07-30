from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from Products.CMFCore.WorkflowCore import WorkflowException

def send_email(context, sender, receiver, subject, email_message):
    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = subject
    mime_msg['From'] = sender
    mime_msg['To'] = receiver
    msg_txt = MIMEText(email_message, 'plain')
    mime_msg.attach(msg_txt)
    try:
        print('--------mail 1')
        host = getToolByName(context, 'MailHost')
        host.send(mime_msg.as_string(), immediate=True)
        print('--------mail 2')
    except SMTPServerDisconnected as msg:
        print('--------mail 3')
        logger.warn("SMTPServerDisconnected: %s." % msg)
    except SMTPRecipientsRefused as msg:
        print('--------mail 4')
        print(str(msg))
        raise WorkflowException(str(msg))
    except Exception as e:
        print('--------mail 2')
        print(str(e))
        logger.warn('Receive sample email exception: %s' % str(e))