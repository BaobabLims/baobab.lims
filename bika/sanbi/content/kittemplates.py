from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.sanbi.interfaces import IKitTemplates


schema = ATFolderSchema.copy()
class KitTemplates(ATFolder):
    implements(IKitTemplates)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(KitTemplates, PROJECTNAME)
