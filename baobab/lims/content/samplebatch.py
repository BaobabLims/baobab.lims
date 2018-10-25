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

import sys

BatchId = StringField(
    'BatchId',
    widget=StringWidget(
        label=_('BatchId'),
        description=_('Specify a batchId in order to differentiate this batch from others.'),
        visible={'view': 'visible', 'edit': 'visible'}
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
        size=30,
        showOn=True,
        render_own_label=True,
        description=_("Select the project of the sample."),
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
                  {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                  {"columnName": "LocationTitle", "align": "left", "label": "Location", "width": "50"}
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

# SampleType = ReferenceField(
#     'SampleType',
#     # required=1,
#     vocabulary_display_path_bound=sys.maxsize,
#     allowed_types=('SampleType',),
#     relationship='SampleSampleType',
#     referenceClass=HoldingReference,
#     mode="rw",
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=ReferenceWidget(
#         label=_("Sample Type"),
#         visible={'edit': 'visible', 'view': 'visible'},
#         catalog_name='bika_setup_catalog',
#         base_query={'inactive_state': 'active'},
#         showOn=True,
#     )
# )
#
# Volume = FixedPointField(
#     'Volume',
#     # required=1,
#     default="0.00",
#     widget=DecimalWidget(
#         label=_("Volume"),
#         size=15,
#         description=_("Volume of Biospecimens in the batch."),
#         visible={'edit': 'visible', 'view': 'visible'},
#     )
# )

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
            size=40,
            base_query={
                'inactive_state': 'active',
                'review_state': 'available',
                'object_provides': ISampleStorageLocation.__identifier__
            },
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='portal_catalog',
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'Title', 'width': '10', 'label': _('Title')},
                {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "80"},
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
        label=_("Colour of Plasma or Serurm (If not normal)"),
        description=_("If Plasma or Serum is not golden in colour and semi transparent, indicate the colour"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

CfgDateTime = DateTimeField(
    'CfgDateTime',
    mode="rw",
    required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Centrifugation/Formalin Start Time"),
        description=_("If applicable, define when centrifugation of the sample starts OR when is the sample put in formalin."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    BatchId,
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
        return ['', 'pink or red (haemolised)', 'opaque or white (lipaemic)']

registerType(SampleBatch, PROJECTNAME)