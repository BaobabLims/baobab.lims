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
from baobab.lims.interfaces import ISampleShipment
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config

import sys


schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((

    ReferenceField(
        'SamplesList',
        multiValued=1,
        allowed_types=('Sample'),
        referenceClass=HoldingReference,
        relationship='SampleShipmentSample',
        mode="rw",
        widget=bika_ReferenceWidget(
            label=_("samples"),
            description=_("Select samples to ship"),
            size=40,
            base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_catalog',
            showOn=True
        )
    ),

    StringField(
        'FromEmailAddress',
        #schemata='Shipping Information',
        widget=StringWidget(
            label=_("Sender Email Address"),
            size=30,
        )
    ),

    StringField(
        'ToEmailAddress',
        #schemata='Shipping Information',
        widget=StringWidget(
            label=_("Receiver Email Address"),
            size=30,
        )
    ),

    ReferenceField(
        'Client',
        schemata='Delivery Info',
        required=1,
        allowed_types=('Client',),
        relationship='ClientSampleShipment',
        widget=bika_ReferenceWidget(
            label=_("Client"),
            description=_("Select client to ship to"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            #catalog_name='bika_catalog',
            showOn=True
        )
    ),

    TextField(
        'DeliveryAddress',
        schemata='Delivery Info',
        required=1,
        allowable_content_types=('text/plain',),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Delivery Address"),
            description=_("Indicate the client address to send the shipment to.")
        ),
    ),

    TextField(
        'BillingAddress',
        schemata='Delivery Info',
        searchable=True,
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Billing Address"),
        ),
    ),

    DateTimeField(
        'ShippingDate',
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
            label=_("Courier"),
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

    StringField(
        'TrackingURL',
        schemata='Shipping Information',
        widget = StringWidget(
            label=_("Tracking URL"),
            size=30,
        )
    ),

    StringField('ShipmentConditions',
        schemata='Shipping Information',
        widget = StringWidget(
            label=_("Shipment Conditions"),
            description=_("Eg: Fragile, chilled, room temp"),
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

schema['title'].widget.visible = True
schema['description'].widget.visible = True


class SampleShipment(ATFolder):
    security = ClassSecurityInfo()
    implements(ISampleShipment)
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

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

    # --------------------------------------------------------------------------
    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            elements_list.append(element.Title())

        elements_string = ', '.join(map(str, elements_list))

        return elements_string

    def free_storage_locations(self):
        wf = getToolByName(self, 'portal_workflow')
        samples = self.getSamplesList()

        for sample in samples:
            storage_location = sample.getStorageLocation()
            if storage_location:
                wf.doActionFor(storage_location, 'liberate')
                storage_location.reindexObject()

                if sample.WillReturnFromShipment:
                    wf.doActionFor(storage_location, 'reserve')
                    sample.update_box_status(storage_location)

                    sample.getField('ReservedLocation').set(sample, storage_location)

            wf.doActionFor(sample, 'ship')
            sample.reindexObject()


    def workflow_script_ready_to_ship(self):
        #send the email
        lab = self.bika_setup.laboratory
        sender = formataddr((encode_header(lab.getName()), self.getFromEmailAddress()))

        client = self.getClient()
        receiver = formataddr((encode_header(client.getName()), self.getToEmailAddress()))

        samples_text = self.getStringified(self.getSamplesList())

        subject = "Samples ready to ship"
        body = "Automatic email:\n"
        body += 'The samples \"%s\" are ready to ship.' % samples_text

        # print('------------')
        # print(sender)
        # print(receiver)
        # print(body)

        self.send_mail(sender, receiver, subject, body)

    def workflow_script_ship(self):
        #send the email
        lab = self.bika_setup.laboratory
        sender = formataddr((encode_header(lab.getName()), self.getFromEmailAddress()))

        client = self.getClient()
        receiver = formataddr((encode_header(client.getName()), self.getToEmailAddress()))

        subject = "Samples Shipped: %s" % self.Title()
        body = "Automatic email:\n"
        body += 'The samples \"%s\" has been shipped.' % self.getStringified(self.getSamplesList())
        body += 'This is an automatic email that indicates that sample shipment %s has been shipped.\n\n' % self.Title()
        self.send_mail(sender, receiver, subject, body)

        self.free_storage_locations()


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
registerType(SampleShipment, config.PROJECTNAME)
