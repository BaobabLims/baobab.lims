from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from time import strftime

from bika.lims.workflow import doActionFor
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from baobab.lims.utils.audit_logger import AuditLogger
from bika.lims import logger


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'Project':
        audit_logger = AuditLogger(instance, 'Project')
        audit_logger.perform_simple_audit(instance, 'New')

        if instance.getField('ProjectAccepted').get(instance) == "Accepted":
            doActionFor(instance, "approve")

        if instance.getField('ProjectAccepted').get(instance) == "Rejected":
            doActionFor(instance, "disapprove")
            send_email(instance)

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """

    if instance.portal_type == 'Project':
        if instance.getField('ProjectAccepted').get(instance) == "Accepted":
            doActionFor(instance, "approve")

        if instance.getField('ProjectAccepted').get(instance) == "Rejected":
            doActionFor(instance, "disapprove")
            send_email(instance)

def send_email(project):
    client = project.getClient()
    sender = client.EmailAddress
    receiver = sender

    subject = 'Project \"%s\" has been rejected.' % project.Title()
    body = "Automatic email:\n"
    body += "Project %s has been rejected.\n" % project.Title()
    if project.getField("RefuseReason").get(project):
        body += project.getField("RefuseReason").get(project)

    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = subject
    mime_msg['From'] = sender
    mime_msg['To'] = receiver
    msg_txt = MIMEText(body, 'plain')
    mime_msg.attach(msg_txt)

    try:
        # print('----mail host reached-----')
        host = getToolByName(project, 'MailHost')
        host.send(mime_msg.as_string(), immediate=True)
    except SMTPServerDisconnected as msg:
        logger.warn("SMTPServerDisconnected: %s." % msg)
    except SMTPRecipientsRefused as msg:
        raise WorkflowException(str(msg))
    except Exception as e:
        logger.warn('Receive sample email exception: %s' % str(e))
