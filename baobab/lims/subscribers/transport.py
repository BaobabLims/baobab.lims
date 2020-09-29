from baobab.lims.utils.audit_logger import AuditLogger

from baobab.lims.utils.send_email import send_email


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """

    if instance.portal_type == 'Transport':
        # audit_logger = AuditLogger(instance, 'Project')
        # audit_logger.perform_simple_audit(instance, 'New')

        client = instance.getClient()
        project = instance.getProject()
        sender = client.EmailAddress
        receiver = sender

        if instance.getField('ArrivalDate').get(instance):    # == "Accepted":
            subject = 'Project %s samples have arrived.' % project.Title()
            message = get_transport_message()

            send_email(instance, receiver, receiver, subject, message)

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """

    if instance.portal_type == 'Transport':
        client = instance.getClient()
        project = instance.getProject()
        sender = client.EmailAddress
        receiver = sender

        if instance.getField('ArrivalDate').get(instance):    # == "Accepted":
            subject = 'Project %s samples have arrived.' % project.Title()
            message = get_transport_message()

            send_email(instance, receiver, receiver, subject, message)


def get_accepted_message():
    return '''
    Dear Client,

    Your request has been accepted. It is being analyzed and you will receive an email 
    indicating the steps to follow soon.
    
    Cordially

    Secretariat of CeReB IPCI
    '''


def get_rejected_message(project):
    body = "Automatic email:\n"
    body += "Project %s has been rejected.\n" % project.Title()
    if project.getField("RefuseReason").get(project):
        body += project.getField("RefuseReason").get(project)

    return body


def get_transport_message():

    message='''
    Dear Client
    
    Dear Client,
    Your samples have been received. In accordance with our procedures your samples 
    undergo microbiological conformity tests before their collection and storage. In 
    the case were there are non-conformities, we will get back to you to put in place 
    the necessary corrective measures. Samples which have major non-conformities 
    will be destroyed. A certificate of deposit will be delivered to you subject to 
    the conformity of these tests.

    Cordially

    Secretariat of CeReB IPCI
    '''

    return message


# def send_email(project, title, message):
#     client = project.getClient()
#     sender = client.EmailAddress
#     receiver = sender
#
#     subject = 'Project \"%s\" has been rejected.' % project.Title()
#     body = "Automatic email:\n"
#     body += "Project %s has been rejected.\n" % project.Title()
#     if project.getField("RefuseReason").get(project):
#         body += project.getField("RefuseReason").get(project)
#
#     mime_msg = MIMEMultipart('related')
#     mime_msg['Subject'] = subject
#     mime_msg['From'] = sender
#     mime_msg['To'] = receiver
#     msg_txt = MIMEText(body, 'plain')
#     mime_msg.attach(msg_txt)
#
#     try:
#         # print('----mail host reached-----')
#         host = getToolByName(project, 'MailHost')
#         host.send(mime_msg.as_string(), immediate=True)
#     except SMTPServerDisconnected as msg:
#         logger.warn("SMTPServerDisconnected: %s." % msg)
#     except SMTPRecipientsRefused as msg:
#         raise WorkflowException(str(msg))
#     except Exception as e:
#         logger.warn('Receive sample email exception: %s' % str(e))