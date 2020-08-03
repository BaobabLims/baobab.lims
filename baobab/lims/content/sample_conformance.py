from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import ISamplePackaging
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget

# SampleKingdom = ReferenceField(
#         'SampleKingdom',
#         allowed_types=('SampleKingdom',),
#         relationship='StrainSampleKingdom',
#         referenceClass=HoldingReference,
#         widget=bika_ReferenceWidget(
#             label=_("Select Sample Kingdom"),
#             visible={'edit': 'visible', 'view': 'visible'},
#             size=30,
#             showOn=True,
#             description=_("Select the sample kingdom of the strain."),
#         )
#     )

schema = BikaSchema.copy() + Schema((
    # SampleKingdom
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class SamplePackaging(BaseContent):
    security = ClassSecurityInfo()
    implements(ISamplePackaging, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(SamplePackaging, config.PROJECTNAME)