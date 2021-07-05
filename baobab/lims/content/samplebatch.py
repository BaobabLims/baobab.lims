from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget

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

ParentBiospecimen = ReferenceField(
    'ParentBiospecimen',
    vocabulary_display_path_bound=sys.maxsize,
    multiValue=1,
    # allowed_types=('Sample', 'VirusSample'),
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

# BiospecimenType = StringField(
#     'BiospecimenType',
#     required=True,
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     vocabulary='getBiospecimenTypes',
#     widget=SelectionWidget(
#         format='select',
#         label=_("Human or Virus"),
#         description=_("""Indicate whether you are collecting a sample for human
#              process or for virus process."""),
#         render_own_label=True,
#     )
# )

NumberBiospecimens = IntegerField('Quantity',
    required=True,
    widget=IntegerWidget(
        label=_("Number of Biospecimens"),
        description=_("Number of biospecimens in the batch."),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

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
    #required=True,
    allowed_types=('ManagedStorage',),
    relationship='ItemStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where biospecimens will be kept."),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True,
        base_query={
            'inactive_state': 'active',
            'review_state': 'available',
            'object_provides': ISampleStorageLocation.__identifier__
        },
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
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the sample has been created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    BatchId,
    Project,
    ParentBiospecimen,
    # BiospecimenType,
    NumberBiospecimens,
    Location,
    DateCreation
))

schema['title'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].schemata = 'default'


class SampleBatch(BaseContent):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def getBiospecimenTypes(self):
    #     biospecimen_types = [
    #             ('Sample', 'Human Sample'), ('VirusSample','Virus Sample')]
    #     result = []
    #     for r in biospecimen_types:
    #         result.append((r[0], r[1]))
    #     return DisplayList(result)

registerType(SampleBatch, PROJECTNAME)
