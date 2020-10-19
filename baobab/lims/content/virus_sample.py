from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IVirusSample
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode


Project = ReferenceField(
    'Project',
    schemata='Baobab Data',
    allowed_types=('Project',),
    relationship='VirusSampleProjects',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Project"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the project of the sample."),
    )
)

SampleType = ReferenceField(
    'SampleType',
    schemata='Baobab Data',
    allowed_types=('SampleType',),
    relationship='VirusSampleSampleType',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Sample Type"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the specimen type."),
    )
)


StorageLocation = ReferenceField(
    'StorageLocation',
    schemata='Baobab Data',
    #required=True,
    allowed_types=('StoragePosition',),
    relationship='VirusSampleStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where item is kept"),
        size=40,
        visible={'edit': 'visible',
                 'view': 'visible',
                 # 'header_table': 'visible',
                 # 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 # 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 # 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 # 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 # 'expired': {'view': 'visible', 'edit': 'invisible'},
                 # 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='portal_catalog',
        showOn=True,
        render_own_label=True,
        base_query={'inactive_state': 'active',
                    'review_state': 'available',
                    # 'object_provides': ISampleStorageLocation.__identifier__
                    },
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Title', 'width': '50', 'label': _('Title')}
                  ],
    )
)

Volume = FixedPointField(
    'Volume',
    schemata='Baobab Data',
    required=1,
    default="0.00",
    widget=DecimalWidget(
        label=_("Volume"),
        size=15,
        description=_("The volume of the biospecimen taken from the subject."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 # 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 # 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 # 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 # 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 # 'expired': {'view': 'visible', 'edit': 'invisible'},
                 # 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True,
    )
)

Unit = StringField(
    'Unit',
    schemata='Baobab Data',
    default="ml",
    widget=StringWidget(
        label=_("Unit"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 # 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 # 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 # 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 # 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 # 'expired': {'view': 'visible', 'edit': 'invisible'},
                 # 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True,
    )
)

Kit = ReferenceField(
    'Kit',
    schemata='Baobab Data',
    allowed_types=('Kit',),
    relationship='VirusSampleKit',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Kit"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Kit."),
    )
)

AllowSharing = BooleanField(
    'AllowSharing',
    schemata='Baobab Data',
    default=False,
    # write_permission = ManageClients,
    widget=BooleanWidget(
        label=_("Allow Sharing"),
        description=_("Check to allow researchers to share sample freely."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 },
        render_own_label=True,
    ),
)

WillReturn = ExtBooleanField(
    'WillReturnFromShipment',
    schemata='Baobab Data',
    default=False,
    # write_permission = ManageClients,
    widget=BooleanWidget(
        label=_("Will Return From Shipment"),
        description=_("Indicates if sample will return if shipped."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 },
        render_own_label=True,
    ),
)

# InfoLink = StringField(
#         'InfoLink',
#         required=0,
#         searchable=True,
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         widget=StringWidget(
#             label=_("Information Link"),
#             description=_("The link to information for this sample donor."),
#             visible={'edit': 'visible', 'view': 'visible'},
#         )
#     )
#
# Sex = StringField(
#         'Sex',
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         vocabulary='getSexes',
#         widget=SelectionWidget(
#             format='select',
#             label=_("Sex"),
#             description=_("Select the sex of the sample donor"),
#             visible={'edit': 'visible', 'view': 'visible'},
#             render_own_label=True,
#         )
#     )
#
# Age = FixedPointField(
#         'Age',
#         required=0,
#         default="0.00",
#         widget=DecimalWidget(
#             label=_("Age"),
#             size=15,
#             description=_("The age of the sample donor."),
#             visible={'edit': 'visible', 'view': 'visible'}
#         )
#     )
#
# AgeUnit = StringField(
#         'AgeUnit',
#         mode="rw",
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         vocabulary='getAgeUnits',
#         widget=SelectionWidget(
#             format='select',
#             label=_("Age Unit"),
#             description=_("Whether the age is in years, months, weeks, days etc"),
#             visible={'edit': 'visible', 'view': 'visible'},
#             render_own_label=True,
#         )
#     )


schema = BikaSchema.copy() + Schema((
    Project,
    SampleType,
    StorageLocation,
    Volume,
    Unit,
    Kit,
    AllowSharing,
    WillReturn,
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class VirusSample(BaseContent):
    security = ClassSecurityInfo()
    implements(IVirusSample, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def Title(self):
    #     return safe_unicode(self.getField('SampleDonorID').get(self)).encode('utf-8')
    #
    # def Description(self):
    #     return "Gender %s : Age %s %s" % (self.getSex(), self.getAge(), self.getAgeUnit())
    #
    # def getSexes(self):
    #     return ['Male', 'Female', 'Unknown', 'Undifferentiated']
    #
    # def getAgeUnits(self):
    #     return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

registerType(VirusSample, config.PROJECTNAME)