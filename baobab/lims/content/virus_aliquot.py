from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IVirusAliquot
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode


ParentSample = ReferenceField(
    'ParentSample',
    allowed_types=('VirusSample',),
    relationship='VirusAliquotVirusSample',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Parent sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the parent sample of this aliquoting."),
    )
)

AliquotSample = ReferenceField(
    'AliquotSample',
    multiValued=1,
    allowed_types=('VirusSample',),
    relationship='VirusAliquotAliquotSample',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Aliquot Sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Aliquot Sample."),
    )
)


schema = BikaSchema.copy() + Schema((
    ParentSample,
    AliquotSample,
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class VirusAliquot(BaseContent):
    security = ClassSecurityInfo()
    implements(IVirusAliquot, IConstrainTypes)
    displayContentsTab = False
    schema = schema

registerType(VirusAliquot, config.PROJECTNAME)