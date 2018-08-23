from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from Products.CMFCore import permissions

from bika.lims.fields import *
from bika.lims.interfaces import ISample
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.content.sample import Sample as BaseSample
from bika.lims.workflow import doActionFor

from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import ISampleStorageLocation
from baobab.lims.browser.project import create_samplepartition
from baobab.lims.utils.email_utils import send_mail

import sys
import datetime
from time import strftime


class ExtFixedPointField(ExtensionField, FixedPointField):
    "Field extender"


class SampleSchemaExtender(object):
    adapts(ISample)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Project',
            required=True,
            allowed_types=('Project',),
            relationship='InvoiceProject',
            referenceClass=HoldingReference,
            widget=bika_ReferenceWidget(
                label=_("Project"),
                # catalog_name='bika_catalog',
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                size=30,
                showOn=True,
                render_own_label=True,
                description=_("Select the project of the sample."),
            )
        ),
        ExtBooleanField(
            'AllowSharing',
            default=False,
            # write_permission = ManageClients,
            widget=BooleanWidget(
                label=_("Allow Sharing"),
                description=_("Check to allow researchers to share sample freely."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         },
                render_own_label=True,
            ),
        ),
        ExtDateTimeField(
            'DateReceived',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=DateTimeWidget(
                label=_("Date Received in Baobab"),
                show_time=True,
                visible={
                    'edit': 'visible',
                    'view': 'visible',
                    'header_table': 'visible',
                    'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                    'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
                    'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                    'sampled': {'view': 'invisible', 'edit': 'invisible'},
                    'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
                    'sample_due': {'view': 'visible', 'edit': 'visible'},
                    'sample_received': {'view': 'visible', 'edit': 'invisible'},
                    'expired': {'view': 'visible', 'edit': 'invisible'},
                    'disposed': {'view': 'visible', 'edit': 'invisible'},
                    'rejected': {'view': 'visible', 'edit': 'invisible'},
                },
                render_own_label=True,
            ),
        ),
        ExtReferenceField(
            'Kit',
            vocabulary_display_path_bound=sys.maxint,
            allowed_types=('Kit',),
            relationship='SampleKit',
            referenceClass=HoldingReference,
            widget=bika_ReferenceWidget(
                label=_("Kit"),
                catalog_name='bika_catalog',
                visible={'view': 'visible',
                         'edit': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'visible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                showOn=True,
                render_own_label = True,
                description=_("Select the kit of the sample if exists."),
            ),
        ),
        ExtReferenceField(
            'StorageLocation',
            #required=True,
            allowed_types=('StoragePosition',),
            relationship='ItemStorageLocation',
            widget=bika_ReferenceWidget(
                label=_("Storage Location"),
                description=_("Location where item is kept"),
                size=40,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                catalog_name='portal_catalog',
                showOn=True,
                render_own_label=True,
                base_query={'inactive_state': 'active',
                            'review_state': 'available',
                            'object_provides': ISampleStorageLocation.__identifier__},
                colModel=[{'columnName': 'UID', 'hidden': True},
                          {'columnName': 'Title', 'width': '50', 'label': _('Title')}
                          ],
            )
        ),
        ExtStringField(
            'SubjectID',
            searchable=True,
            widget=StringWidget(
                label=_("Subject ID"),
                description=_("Human-subject ID the specimen is taken from."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtStringField(
            'Barcode',
            required=0,
            searchable=True,
            widget=StringWidget(
                label=_("Barcode"),
                description=_("Biospecimen barcode."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtFixedPointField(
            'Volume',
            required=1,
            default="0.00",
            widget=DecimalWidget(
                label=_("Volume"),
                size=15,
                description=_("The volume of the biospecimen taken from the subject."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtStringField(
            'Unit',
            default="ml",
            vocabulary='getUnits',
            # widget=SelectionWidget(
            widget=BikaSelectionWidget(
                format='select',
                label=_("Unit"),
                description=_('The unit for Volume'),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
                showOn=True,
            )
        ),
        ExtReferenceField(
            'LinkedSample',
            vocabulary_display_path_bound=sys.maxsize,
            multiValue=1,
            allowed_types=('Sample',),
            relationship='SampleSample',
            referenceClass=HoldingReference,
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=bika_ReferenceWidget(
                label=_("Parent Biospecimen"),
                description=_("Create an Aliquot of the biospecimen selected."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                showOn=True,
                render_own_label=True,
                base_query={
                    'cancellation_state': 'active',
                    'review_state': 'sample_received'
                },
                colModel=[{'columnName': 'UID', 'hidden': True},
                          {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                          {"columnName": "LocationTitle", "align": "left", "label": "Location", "width": "50"}
                          ],
            ),
        ),
        ExtDateTimeField(
            'DateCreated',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=DateTimeWidget(
                label=_("Date Created"),
                description=_("Define when the sample has been created."),
                show_time=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'invisible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            ),
        ),
        ExtComputedField(
            'LocationTitle',
            searchable=True,
            expression="here.getStorageLocation() and here.getStorageLocation().Title() or ''",
            widget=ComputedWidget(
                visible=False,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        sch = schematas['default']
        sch.remove('Project')
        sch.remove('Kit')
        sch.insert(sch.index('SampleType'), 'Project')
        sch.insert(sch.index('SampleType'), 'Kit')
        return schematas

    def getFields(self):
        return self.fields

class SampleSchemaModifier(object):
    adapts(ISample)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return schema


class Sample(BaseSample):
    """ Inherits from bika.lims.content.sample
    """
    _at_rename_after_creation = True

    def getUnits(self):
        return ['ml', 'ul', 'g', 'mg']

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getProjectUID(self):
        if self.aq_parent.Title() == 'Biospecimens':
            return self.getField('Project').get(self).UID()
        else:
            return self.aq_parent.UID()

    def getLastARNumber(self):
        ARs = self.getBackReferences("AnalysisRequestSample")
        prefix = self.getId() + '-' + self.getSampleType().getPrefix()
        ar_ids = sorted([AR.id for AR in ARs if AR.id.startswith(prefix)])
        try:
            last_ar_number = int(ar_ids[-1].split("-R")[-1])
        except:
            return 0
        return last_ar_number

    def update_box_status(self, location):
        box = location.aq_parent
        state = self.portal_workflow.getInfoFor(box, 'review_state')
        free_pos = box.get_free_positions()
        if not free_pos and state == 'available':
            doActionFor(box, 'occupy')
        elif free_pos and state == 'occupied':
            doActionFor(box, 'liberate')

    def workflow_script_receive(self):

        #set date received
        if not self.getDateReceived():
            self.setDateReceived(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
            self.reindexObject()

        # inform the client
        project = self.aq_parent
        client = project.getClient()

        sender = client.EmailAddress
        receiver = sender

        self.send_email(sender, receiver)

        # inform the lab contacts
        project = self.aq_parent
        print('----project--0--')
        print(project)
        lab_contacts = project.getLabContacts()
        print('---lab contacts-----')
        print(lab_contacts)
        for contact in lab_contacts:
            self.send_email(sender, contact.EmailAddress)
            print(contact.EmailAddress)


    def send_email(self, sender, receiver):
        print('sending a mail to {} from {}'.format(receiver, sender))
        subject = 'Sample \"%s\" received at \"%s\".' % (self.Title(), strftime("%Y-%m-%d %H:%M:%S"))

        body = "Automatic email:\n"
        body += 'The sample \"%s\" has been received at \"%s\".' % (self.Title(), strftime("%Y-%m-%d %H:%M:%S"))

        send_mail(self, sender, receiver, subject, body)


    def at_post_create_script(self):
        """Execute once the object is created (CHECK ObjectInitializedEventHandler)
        """
        # if self.aq_parent.Title() == 'Biospecimens':
        #     self.container = self.getField('Project').get(self)
        #     doActionFor(self, 'sample_due')
        #     doActionFor(self, 'receive')
        #
        # create_samplepartition(self, {'services': [], 'part_id': self.getId() + "-P"})
        #
        # location = self.getStorageLocation()
        # if location:
        #     doActionFor(location, 'occupy')
        #     self.update_box_status(location)

from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
# Overrides type bika.lims.content.sample
atapi.registerType(Sample, PROJECTNAME)
