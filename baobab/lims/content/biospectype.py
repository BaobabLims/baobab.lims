"""Product Category
Category of the product, for example, sampling containers and sampling
kits.
"""
from AccessControl import ClassSecurityInfo
from baobab.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims.interfaces import IBiospecType
from Products.Archetypes.public import *
from zope.interface import implements
from baobab.lims.browser.widgets import ProjectAnalysesWidget
from baobab.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    ReferenceField('Service',
                   required=1,
                   multiValued=1,
                   allowed_types=('AnalysisService',),
                   relationship='BiospecimenAnalysisService',
                   widget=ProjectAnalysesWidget(
                       label=_("Analyse Services"),
                       description=_("Multi-checkboxes table. Use the suitable services for the current "
                                     "biospecimen-type"),
                   )),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class BiospecType(BaseContent):
    implements(IBiospecType)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(BiospecType, PROJECTNAME)