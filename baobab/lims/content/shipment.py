from AccessControl import ClassSecurityInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from zope.interface import implements
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from plone.app.folder.folder import ATFolder
from Products.ATContentTypes.content import schemata
from DateTime import DateTime

from bika.lims import logger
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.utils import encode_header
from baobab.lims.interfaces import IShipment
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config

import sys


schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((

    ReferenceField(
        'FromContact',
        required=1,
        vocabulary='get_project_client_contacts',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('LabContact',),
        referenceClass=HoldingReference,
        relationship='ShipmentLabContact',
        mode="rw",
        read_permission=permissions.View,
        widget=bika_ReferenceWidget(
            label=_("From Contact"),
            description=_("Laboratory contact sending this shipment."),
            size=30,
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                      ],
        ),
    ),
    ReferenceField(
        'ToContact',
        required=1,
        vocabulary='get_project_client_contacts',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Contact',),
        referenceClass=HoldingReference,
        relationship='ShipmentContact',
        mode="rw",
        read_permission=permissions.View,
        widget=SelectionWidget(
            format="select",
            label=_("To Contact"),
            description=_("Client contact receiving this shipment."),
            size=30,
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                      ],
        ),
    ),

    TextField('DeliveryAddress',
        schemata='Correspondence',
        required=1,
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Delivery Address"),
            description=_("Indicate the client address to send the shipment to.")
        ),
    ),
    TextField('BillingAddress',
        schemata='Correspondence',
        searchable=True,
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Billing Address"),
        ),
    ),

    StringField('ShipmentConditions',
        schemata='Shipping Information',
        widget = StringWidget(
            label=_("Shipment Conditions"),
            description=_("Eg: Fragile, chilled, room temp"),
            size=30,

        )
    ),

    DateTimeField('ShippingDate',
        searchable=1,
        schemata="Dates",
        widget=bika_DateTimeWidget(
            label='Shipping Date',
            size=20
        ),
    ),

    DateTimeField(
        'DateDispatched',
        searchable=1,
        schemata="Dates",
        widget=bika_DateTimeWidget(
            label='Date Dispatched',
            size=20
        ),
    ),

    DateTimeField(
        'DateDelivered',
        searchable=1,
        schemata="Dates",
        widget=bika_DateTimeWidget(
            label='Date Delivered',
            description=_("Provide the expected expiry date of the kit product."),
            size=20
        ),
    ),

    StringField(
        'Courier',
        required=1,
        schemata="Correspondence",
        widget=StringWidget(
            format="select",
            label = _("Courier"),
            size=30,
            description=_("Start typing to filter the list of available couriers."),
        ),
    ),

    TextField(
        'CourierInstructions',
        schemata="Correspondence",
        allowable_content_types=('text/plain',),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Courier Instructions"),
        ),
    ),

    ReferenceField(
        'Kits',
        required=1,
        multiValued=1,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary='get_project_kits',
        allowed_types=('Kit',),
        relationship='ShipmentKits',
        referenceClass=HoldingReference,
        widget=MultiSelectionWidget(
            label = _("Kits"),
            description=_("Start typing to filter the list of available kits to ship."),
        ),
    ),

    StringField(
        'TrackingURL',
        schemata='Shipping Information',
        widget = StringWidget(
            label=_("Tracking URL"),
            size=30,
        )
    ),

    FixedPointField(
        'ShippingCost',
        schemata='Shipping Information',
        widget=DecimalWidget(
            label=_("Shipping Cost"),
        ),
    ),

    FixedPointField(
        'Weight',
        schemata='Shipping Information',
        widget=DecimalWidget(
            label=_("Weight"),
            description=_("Enter the weight in Kg"),
        ),
    ),

    StringField(
        'Volume',
        schemata='Shipping Information',
        widget = StringWidget(
            label=_("Volume"),
            description=_("Enter dimensions of the package (lxbxh) in CM"),
            size=30,
        )
    ),

))

schema['description'].widget.visible = True

class Shipment(ATFolder):
    security = ClassSecurityInfo()
    implements(IShipment)
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def get_project_kits(self):
        """ List of all kits belonging to the current project
        """
        items = []
        w_tool = getToolByName(self, 'portal_workflow')
        kits = self.aq_parent.objectValues('Kit')
        for kit in kits:
            st1 = w_tool.getStatusOf("bika_kit_assembly_workflow", kit)
            st2 = w_tool.getStatusOf("bika_inactive_workflow", kit)
            if st1.get('review_state', None) == 'generated' and \
                            st2.get('inactive_state', None) == 'active':
                items.append((kit.UID(), kit.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def get_project_client_contacts(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        client = self.aq_parent.aq_parent
        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type='Contact', path={'query': "/".join(client.getPhysicalPath()), 'level': 0})
        contacts = []
        for brain in brains:
            obj = brain.getObject()
            contacts.append((obj.UID(), obj.Title(), obj.getEmailAddress()))
        contacts.sort(lambda x, y: cmp(x[1], y[1]))

        return contacts

    def getDocuments(self):
        """Return all the multifile objects related with the shipment
        """
        return self.objectValues('Multifile')

    def send_mail(self, sender, receiver, subject="", body=""):
        """Send email from sender to receiver
        """
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = subject
        mime_msg['From'] = sender
        mime_msg['To'] = receiver
        msg_txt = MIMEText(body, 'plain')
        mime_msg.attach(msg_txt)
        try:
            host = getToolByName(self, 'MailHost')
            host.send(mime_msg.as_string(), immediate=True)
        except SMTPServerDisconnected as msg:
            logger.warn("SMTPServerDisconnected: %s." % msg)
        except SMTPRecipientsRefused as msg:
            raise WorkflowException(str(msg))

    def workflow_script_dispatch_shipment(self):
        """executed after shipment state transition "dispatch"
        """
        # free positions kits occupy
        kits = self.getKits()
        w_tool = getToolByName(self, 'portal_workflow')
        for kit in kits:
            kit.setStorageLocation('')
            w_tool.doActionFor(kit, 'ship')
            kit.reindexObject()

        # Set shipment's date dispatched
        now = DateTime()
        self.setDateDispatched(now)

        to_contact = self.getToContact()
        from_contact = self.getFromContact()
        client = to_contact.aq_parent
        lab = self.bika_setup.laboratory
        subject = "Kits dispatched from {}".format(lab.getName())
        sender = formataddr((lab.getName(), from_contact.getEmailAddress()))
        receiver = formataddr((encode_header(client.getName()), to_contact.getEmailAddress()))
        body = "Automatic email:\n"
        body += 'The shipment \"%s\" has been sent from the Biobank \"%s\".' % (self.Title(), lab.getName())
        self.send_mail(sender, receiver, subject, body)

    def workflow_script_receive_shipment(self):
        """ Executed after shipment received by the client
        """
        to_contact = self.getToContact()
        from_contact = self.getFromContact()
        client = to_contact.aq_parent
        subject = "Shipment Received"
        sender = formataddr((encode_header(client.getName()), to_contact.getEmailAddress()))
        lab = self.bika_setup.laboratory
        receiver = formataddr((lab.getName(), from_contact.getEmailAddress()))
        body = "Automatic email:\n"
        body += 'The shipment \"%s\" sent to the client \"%s\" has been received.' % (self.Title(), client.getName())
        self.send_mail(sender, receiver, subject, body)

    def workflow_script_collect(self):
        """ Executed after shipment ready for collection from the client
        """
        to_contact = self.getToContact()
        from_contact = self.getFromContact()
        client = to_contact.aq_parent
        subject = "Shipment ready for collection"
        sender = formataddr((encode_header(client.getName()), to_contact.getEmailAddress()))
        lab = self.bika_setup.laboratory
        receiver = formataddr((lab.getName(), from_contact.getEmailAddress()))
        body = "Automatic email:\n"
        body += 'The shipment \"%s\" sent to the client \"%s\" is ready for collection.' % (self.Title(), client.getName())
        self.send_mail(sender, receiver, subject, body)

    def workflow_script_receive_back(self):
        """ Executed after shipment received back by the biobank
        """
        to_contact = self.getToContact()
        from_contact = self.getFromContact()
        client = to_contact.aq_parent
        subject = "Shipment reached the Biobank"
        lab = self.bika_setup.laboratory
        sender = formataddr((lab.getName(), from_contact.getEmailAddress()))
        receiver = formataddr((encode_header(client.getName()), to_contact.getEmailAddress()))
        body = "Automatic email:\n"
        body += 'The shipment \"%s\" sent back is arrived at the Biobank \"%s\".' % (self.Title(), lab.getName())
        self.send_mail(sender, receiver, subject, body)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

registerType(Shipment, config.PROJECTNAME)
