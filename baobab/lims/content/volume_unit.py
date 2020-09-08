from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import config
from baobab.lims.interfaces import IVolumeUnit

schema = BikaSchema.copy() + Schema((

))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class VolumeUnit(BaseContent):
    security = ClassSecurityInfo()
    implements(IVolumeUnit, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(VolumeUnit, config.PROJECTNAME)