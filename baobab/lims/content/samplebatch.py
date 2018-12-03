from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

from baobab.lims.config import PROJECTNAME
from baobab.lims.interfaces import IBatch
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import ISampleStorageLocation

from zope.component import queryUtility
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from plone.registry.interfaces import IRegistry
from Products.Archetypes.utils import DisplayList

import sys

class BatchTypeVocabulary(object):
    implements(IVocabulary)

    def getDisplayList(self, context):

        registry = queryUtility(IRegistry)
        batch_types = []
        if registry is not None:

            for batch_type in sorted(registry.get('baobab.lims.samplebatch.batch_types', ())):
                batch_types.append([batch_type, batch_type])

        return DisplayList(batch_types)

# BatchId = StringField(
#     'BatchId',
#     widget=StringWidget(
#         label=_('BatchId'),
#         description=_('Specify a batchId in order to differentiate this batch from others.'),
#         visible={'view': 'visible', 'edit': 'visible'}
#     )
# )

BatchType = StringField(
    'BatchType',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary=BatchTypeVocabulary(),
    widget=BikaSelectionWidget(
        format='select',
        label=_("Batch Type"),
        description=_("Select a batch type in order to differentiate this batch from others."),
        size=50,
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

Project = ReferenceField(
    'Project',
    required=True,
    allowed_types=('Project',),
    relationship='InvoiceProject',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Project"),
        # catalog_name='bika_catalog',
        visible={'edit': 'visible', 'view': 'visible'},
        size=50,
        showOn=True,
        render_own_label=True,
        description=_("Select the project of the sample batch."),
        colModel=[{"columnName": "UID", "hidden": True},
                  {"columnName": "Title", "align": "left", "width": "60", "label": "Title"},
                  {"columnName": "Description", "align": "left", "label": "Description", "width": "40"}
                  ],
    )
)

Subject_ID = StringField(
    'SubjectID',
    required=True,
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
)

ParentBiospecimen = ReferenceField(
    'ParentBiospecimen',
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
        description=_("The parent biospecimen of the aliquots."),
        showOn=True,
        visible={'view': 'visible', 'edit': 'visible'},
        base_query={
            'cancellation_state': 'active',
            'review_state': 'sample_received'
        },
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Title', 'width': '30', 'label': _('Title')},
                  {"columnName": "LocationTitle", "align": "left", "label": "Location", "width": "70"}
                  ],
    )
)

NumberBiospecimens = IntegerField('Quantity',
    required=True,
    widget=IntegerWidget(
        label=_("Number of Biospecimens"),
        description=_("Number of biospecimens in the batch."),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

# TODO: THE LOCATION MUST BE A MULTIVALUE. A USE SHOULD BE ABLE TO SELECT MORE THAN ONE LOCATION.

Location = ReferenceField(
        'StorageLocation',
        multiValued=1,
        allowed_types=('ManagedStorage'),
        referenceClass=HoldingReference,
        relationship='SampleShipmentSample',
        mode="rw",
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where biospecimens will be kept."),
            size=60,
            base_query={
                'inactive_state': 'active',
                'review_state': 'available',
                'object_provides': ISampleStorageLocation.__identifier__,
            },
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='portal_catalog',
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'Title', 'width': '20', 'label': _('Title')},
                {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "70"},
                {"columnName": "FreePositions", "align": "left", "label": "Free", "width": "10"},
            ],

        )
    )

DateCreation = DateTimeField(
    'DateCreated',
    mode="rw",
    required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the sample has been created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)


SerumColour = StringField(
    'SerumColour',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getSerumColours',
    widget=BikaSelectionWidget(
        format='select',
        label=_("Colour of Plasma or Serum"),
        description=_("Indicate the colour of plasma or serum"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

CfgDateTime = DateTimeField(
    'CfgDateTime',
    mode="rw",
    # required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Centrifuge/Formalin Start Time"),
        description=_("If applicable, indicate when sample centrifugation starts OR when the sample is put in formalin."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    BatchType,
    Project,
    Subject_ID,
    ParentBiospecimen,
    NumberBiospecimens,
    Location,
    DateCreation,
    SerumColour,
    CfgDateTime
))

schema['title'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['title'].default = 'Temporary title'
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].schemata = 'default'


class SampleBatch(BaseContent):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getSerumColours(self):
        return ['', 'golden (semi-transparent)', 'pink or red (haemolised)', 'opaque or white (lipaemic)']


def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified.
        Note from QC 2018-11-05:  As far as I can see this change happens after the object is modified.
        I tested by altering the Serum Colour and by the time it does a data dump here the object
        already has the new colour.
    """

    if instance.portal_type == 'SampleBatch':
        from baobab.lims.idserver import renameAfterEdit
        renameAfterEdit(instance)

registerType(SampleBatch, PROJECTNAME)

