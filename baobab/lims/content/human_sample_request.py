from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IHumanSampleRequest
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode

Approved = BooleanField(
    'Approved',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getApproved',
    widget=SelectionWidget(
        format='select',
        label=_("Approved"),
        description=_("Select approved or rejected for the requested sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

Barcode = StringField(
    'Barcode',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Barcode"),
        description=_("Barcode of this human sample request."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SampleType = ReferenceField(
    'SampleType',
    allowed_types=('SampleType',),
    relationship='HumanSampleRequestSampleType',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Sample Type"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the sample type of this sample request."),
    )
)

# Container = ReferenceField(
#     'Container',
#     allowed_types=('StoragePosition',),
#     relationship='HumanSampleRequestStoragePosition',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Container"),
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         description=_("Select the container of this requested sample."),
#     )
# )

Volume = StringField(
    'Volume',
    required=0,
    # searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Volume"),
        description=_("The volume to be collected for this requested sample."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Unit = StringField(
    'Unit',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getUnits',
    widget=SelectionWidget(
        format='select',
        label=_("Unit"),
        description=_("Select the unit of the requested sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

schema = BikaSchema.copy() + Schema((
    Approved,
    Barcode,
    SampleType,
    # Container,
    Volume,
    Unit,
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class HumanSampleRequest(BaseContent):
    security = ClassSecurityInfo()
    implements(IHumanSampleRequest, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getUnits(self):
        return ["ml", 'g']

    def getApproved(self):
        return ['', 'approved', 'rejected']

    # def Title(self):
    #     return safe_unicode(self.getField('SampleDonorID').get(self)).encode('utf-8')
    #
    # def Description(self):
    #     return "Gender %s : Age %s %s" % (self.getSex(), self.getAge(), self.getAgeUnit())
    #
    # def getSexes(self):
    #     return ['Male', 'Female', 'Unknown', 'Undifferentiated']

    # def getAgeUnits(self):
    #     return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

registerType(HumanSampleRequest, config.PROJECTNAME)