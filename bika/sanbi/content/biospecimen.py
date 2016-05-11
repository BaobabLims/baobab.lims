"""Product Category
Category of the product, for example, sampling containers and sampling
kits.
"""
from AccessControl import ClassSecurityInfo
from bika.sanbi.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.sanbi.interfaces import IBioSpecimen
from Products.Archetypes.public import *
from zope.interface import implements

schema = BikaSchema.copy()
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class BioSpecimen(BaseContent):
    implements(IBioSpecimen)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(BioSpecimen, PROJECTNAME)