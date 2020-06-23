from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IMicrobeSampleRequest
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode


Identification = StringField(
    'Identification',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Identification"),
        description=_("Identification of this microbe sample request."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Strain = ReferenceField(
    'Strain',
    allowed_types=('Strain',),
    relationship='MicrobeSampleRequestStrain',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Microbe"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the microbe of this sample request."),
    )
)

OriginIsolatedFrom = StringField(
    'OriginIsolatedFrom',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getOriginIsolatedFrom',
    widget=SelectionWidget(
        format='select',
        label=_("Origin Isolated From"),
        description=_("Select the origin this microbe was isolated from"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

Phenotype = StringField(
    'Phenotype',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getPhenotype',
    widget=SelectionWidget(
        format='select',
        label=_("Phenotype"),
        description=_("Select the phenotype for this microbe"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
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
#
# Volume = StringField(
#     'Volume',
#     required=0,
#     # searchable=True,
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=StringWidget(
#         label=_("Volume"),
#         description=_("The volume to be collected for this requested sample."),
#         visible={'edit': 'visible', 'view': 'visible'},
#     )
# )



schema = BikaSchema.copy() + Schema((
    Identification,
    Strain,
    OriginIsolatedFrom,
    Phenotype,
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class MicrobeSampleRequest(BaseContent):
    security = ClassSecurityInfo()
    implements(IMicrobeSampleRequest, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getOriginIsolatedFrom(self):
        return ['Human', 'Animal', 'Plant', 'Environmental']

    def getPhenotype(self):
        return ['Unknown', 'WildType', 'Recombinant']

registerType(MicrobeSampleRequest, config.PROJECTNAME)